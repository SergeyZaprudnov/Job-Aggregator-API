from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import VacancyStatsView, VacancyViewSet

router = DefaultRouter()
router.register(r'vacancies', VacancyViewSet, basename='vacancy')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', VacancyStatsView.as_view(), name='vacancy-stats'),
]