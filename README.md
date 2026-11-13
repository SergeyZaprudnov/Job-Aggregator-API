![CI](https://github.com/SergeyZaprudnov/Job-Aggregator-API/actions/workflows/ci.yml/badge.svg)

# Job Aggregator API — Production Deployment

Backend service for aggregating job vacancies from SuperJob.  
This document describes how to deploy the service to a production server.

## Stack
- Python 3.11, Django, Django REST Framework
- PostgreSQL 15, Redis 7, Celery
- Docker, Docker Compose
- Nginx (reverse proxy), Gunicorn (WSGI)
- GitHub Actions (CI)

## Production Architecture
Client → Nginx (443/80) → Gunicorn (web:8000) → Django
                                  │
                                  ├── PostgreSQL (db:5432)
                                  └── Redis (redis:6379) → Celery worker / beat

## Prerequisites
- Ubuntu 22.04+ server (or similar)
- Docker Engine 24+ and Docker Compose v2
- Domain name pointed to the server IP
- Open ports: 80, 443
- (Optional) TLS certificates via Let's Encrypt

## 1. Server Preparation
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER

## 2. Clone the Repository
git clone https://github.com/SergeyZaprudnov/Job-Aggregator-API.git
cd Job-Aggregator-API
git checkout main

## 3. Configure Environment
Create .env in the project root (do not commit it):
cp .env.example .env
nano .env

Fill in production values:
SECRET_KEY=<long-random-string>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
POSTGRES_DB=job_aggregator
POSTGRES_USER=job_user
POSTGRES_PASSWORD=<strong-password>
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
SUPERJOB_APP_KEY=<your-superjob-key>

## 4. Production Docker Compose
Create docker-compose.prod.yml in the project root:
services:
  db:
    image: postgres:15-alpine
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
  redis:
    image: redis:7-alpine
    restart: always
  web:
    build: .
    restart: always
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
    volumes:
      - static_volume:/app/staticfiles
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
  worker:
    build: .
    restart: always
    command: celery -A config worker --loglevel=info
    env_file:
      - .env
    depends_on:
      - web
      - redis
  beat:
    build: .
    restart: always
    command: celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file:
      - .env
    depends_on:
      - web
      - redis
  nginx:
    image: nginx:1.25-alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - static_volume:/app/staticfiles:ro
      - ./nginx/certs:/etc/nginx/certs:ro
    depends_on:
      - web
volumes:
  postgres_data:
  static_volume:

## 5. Dockerfile (Production)
Ensure Dockerfile uses Gunicorn-compatible setup:
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000

## 6. Nginx Configuration
Create nginx/nginx.conf:
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    location /static/ {
        alias /app/staticfiles/;
    }
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}

## 7. Build and Start
docker compose -f docker-compose.prod.yml up -d --build

## 8. Apply Migrations and Create Superuser
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

## 9. Collect Static Files
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

## 10. Verify Deployment
docker compose -f docker-compose.prod.yml ps
curl -I http://your-domain.com/api/vacancies/

## 11. Logs and Monitoring
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f worker
docker compose -f docker-compose.prod.yml logs -f beat

## 12. Update / Redeploy
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

## 13. Rollback
git checkout <previous-commit>
docker compose -f docker-compose.prod.yml up -d --build

## Security Checklist
- [ ] DEBUG=False
- [ ] SECRET_KEY is long and random
- [ ] ALLOWED_HOSTS restricted to the real domain
- [ ] PostgreSQL password is strong
- [ ] .env is not committed
- [ ] HTTPS enabled (Let's Encrypt / certbot)
- [ ] Firewall allows only 22, 80, 443
- [ ] Regular database backups configured

## Backup (example)
docker compose -f docker-compose.prod.yml exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup_$(date +%F).sql

## CI
GitHub Actions runs linter and tests on every push to main. Deployment is manual (see steps above).