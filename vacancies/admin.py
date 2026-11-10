from django.contrib import admin
from .models import Vacancy


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'source', 'salary_from', 'salary_to', 'published_at')
    list_filter = ('source',)
    search_fields = ('title', 'company')
    