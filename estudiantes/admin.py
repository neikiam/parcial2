from django.contrib import admin
from .models import Alumno

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'nota', 'usuario', 'fecha_creacion']
    list_filter = ['fecha_creacion']
    search_fields = ['nombre', 'apellido']
