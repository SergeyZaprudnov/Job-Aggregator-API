from django.db import models


# Create your models here.
class Vacancy(models.Model):
    SOURCE_CHOICES = [
        ('hh', 'HeadHunter'),
        ('superjob', 'SuperJob'),
    ]

    external_id = models.CharField(max_length=100, db_index=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)
    salary_from = models.IntegerField(null=True, blank=True)
    salary_to = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=10, blank=True)
    url = models.URLField(max_length=500)
    description = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('external_id', 'source')
        ordering = ['-published_at']

    def __str__(self):
        return f"{self.title} @ {self.company}"
    