import pytest
from rest_framework.test import APIClient
from .models import Vacancy


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_vacancy(db):
    return Vacancy.objects.create(
        external_id='123',
        source='superjob',
        title='Python Developer',
        company='Test Company',
        salary_from=100000,
        salary_to=150000,
        currency='rub',
        url='https://example.com/vacancy/123',
    )


@pytest.mark.django_db
def test_vacancy_list_empty(api_client):
    response = api_client.get('/api/vacancies/')
    assert response.status_code == 200
    assert response.json()['count'] == 0
    assert response.json()['results'] == []


@pytest.mark.django_db
def test_vacancy_list_with_data(api_client, sample_vacancy):
    response = api_client.get('/api/vacancies/')
    assert response.status_code == 200
    data = response.json()
    assert data['count'] == 1
    assert data['results'][0]['title'] == 'Python Developer'
    assert data['results'][0]['company'] == 'Test Company'


@pytest.mark.django_db
def test_vacancy_search(api_client, sample_vacancy):
    response = api_client.get('/api/vacancies/?search=Python')
    assert response.status_code == 200
    assert response.json()['count'] == 1

    response = api_client.get('/api/vacancies/?search=Java')
    assert response.status_code == 200
    assert response.json()['count'] == 0


@pytest.mark.django_db
def test_vacancy_ordering(api_client, sample_vacancy):
    Vacancy.objects.create(
        external_id='456',
        source='superjob',
        title='Junior Python Developer',
        company='Another Company',
        salary_from=50000,
        url='https://example.com/vacancy/456',
    )
    response = api_client.get('/api/vacancies/?ordering=salary_from')
    assert response.status_code == 200
    results = response.json()['results']
    assert results[0]['salary_from'] == 50000
    assert results[1]['salary_from'] == 100000