from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Vacancy
from .serializers import VacancySerializer
from .filters import VacancyFilter


class VacancyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class= VacancySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VacancyFilter
    search_fields = ['title', 'company']
    ordering_fields = ['published_at', 'salary_from']