from django.contrib import admin
from .models import ScraperResult

@admin.register(ScraperResult)
class ScraperResultAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'palabra_clave', 'fecha_scraping']
    list_filter = ['palabra_clave', 'fecha_scraping']
    search_fields = ['titulo', 'palabra_clave']
