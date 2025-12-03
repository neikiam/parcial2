from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.conf import settings
from .forms import RegisterForm
from utils.email_utils import send_email_with_sendgrid

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Enviar email de bienvenida usando SendGrid
            email_sent = send_email_with_sendgrid(
                to_email=user.email,
                subject='¡Bienvenido a Parcial2!',
                message=f'Hola {user.username},\n\nGracias por registrarte en nuestra plataforma.\n\n¡Esperamos que disfrutes de todas las funcionalidades!'
            )
            
            if email_sent:
                messages.success(request, f'¡Registro exitoso! Se ha enviado un email de bienvenida a {user.email}')
            else:
                messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
            
            login(request, user)
            return redirect('estudiantes:dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {username}!')
                return redirect('estudiantes:dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente')
    return redirect('accounts:login')
