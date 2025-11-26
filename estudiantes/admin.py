from django.contrib import admin
from .models import Alumno

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'carrera', 'usuario', 'fecha_creacion']
    list_filter = ['carrera', 'fecha_creacion']
    search_fields = ['nombre', 'email']
