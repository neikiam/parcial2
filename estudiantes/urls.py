from django.urls import path
from . import views

app_name = 'estudiantes'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_alumno, name='create'),
    path('edit/<int:pk>/', views.edit_alumno, name='edit'),
    path('delete/<int:pk>/', views.delete_alumno, name='delete'),
    path('send-pdf/<int:pk>/', views.send_pdf, name='send_pdf'),
]
