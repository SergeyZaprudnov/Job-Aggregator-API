from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import VacancyFilter
from .models import Vacancy
from .serializers import VacancySerializer


class VacancyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VacancyFilter
    search_fields = ['title', 'company']
    ordering_fields = ['published_at', 'salary_from']


class VacancyStatsView(APIView):
    def get(self, request):
        total = Vacancy.objects.count()
        avg_salary = Vacancy.objects.aggregate(avg = Avg('salary_from'))['avg']

        top_companies = (
            Vacancy.objects.values('company').annotate(count = Count('id')).order_by('-count')[:5]
        )

        return Response({
            'total_vacancies': total,
            'average_salary_from': round(avg_salary, 2) if avg_salary else None,
            'top_companies': list(top_companies),
        })
    