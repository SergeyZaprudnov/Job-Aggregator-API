import django_filters
from .models import Vacancy


class VacancyFilter(django_filters.FilterSet):
    salary_min = django_filters.NumberFilter(field_name="salary_from", lookup_expr='gte')
    salary_max = django_filters.NumberFilter(field_name="salary_to", lookup_expr='lte')
    source = django_filters.CharFilter(name="source", lookup_expr='iexact')

    class Meta:
        model = Vacancy
        fields = ['source', 'salary_min', 'salary_max']