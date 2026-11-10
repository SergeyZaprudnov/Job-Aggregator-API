from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Vacancy
from .serializers import VacancySerializer


class VacancyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class= VacancySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'company']
    ordering_fields = ['published_at', 'salary_from']