from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegisterForm
from .models import EmailVerification

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False  
            user.save()
            
            # Crear verificación (genera código automáticamente)
            verification = EmailVerification.objects.create(user=user)
            
            # Intentar enviar email (sin bloquear)
            try:
                send_mail(
                    subject='¡Verifica tu cuenta en Parcial2!',
                    message=f'Hola {user.username},\n\nTu código de verificación es: {verification.verification_code}\n\nEste código expira en 15 minutos.\n\n¡Bienvenido a nuestra plataforma!',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except:
                pass
            
            # Siempre mostrar el código por seguridad (en caso de que el email falle)
            messages.success(request, f'¡Registro exitoso! Hemos intentado enviar un email a {user.email}')
            messages.info(request, f'Tu código de verificación es: {verification.verification_code} (expira en 15 min)')
            request.session['user_id_to_verify'] = user.id
            return redirect('accounts:verify_email')
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
                # Verificar si el email está verificado
                try:
                    verification = user.email_verification
                    if not verification.is_verified:
                        messages.error(request, 'Debes verificar tu email antes de iniciar sesión. Revisa tu correo.')
                        request.session['user_id_to_verify'] = user.id
                        return redirect('accounts:verify_email')
                except EmailVerification.DoesNotExist:
                    pass  # Usuario antiguo sin verificación
                
                login(request, user)
                messages.success(request, f'Bienvenido {username}!')
                return redirect('estudiantes:dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def verify_email_view(request):
    user_id = request.session.get('user_id_to_verify')
    if not user_id:
        messages.error(request, 'Sesión inválida')
        return redirect('accounts:register')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        code = request.POST.get('verification_code', '').strip()
        try:
            verification = user.email_verification
            
            if verification.is_verified:
                messages.info(request, 'Tu cuenta ya está verificada')
                del request.session['user_id_to_verify']
                return redirect('accounts:login')
            
            if verification.is_expired():
                messages.error(request, 'El código ha expirado. Solicítalo nuevamente.')
                return render(request, 'accounts/verify_email.html', {'user': user, 'expired': True})
            
            if code == verification.verification_code:
                verification.is_verified = True
                verification.save()
                user.is_active = True
                user.save()
                del request.session['user_id_to_verify']
                messages.success(request, '¡Email verificado exitosamente! Ya puedes iniciar sesión.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Código incorrecto. Inténtalo de nuevo.')
        except EmailVerification.DoesNotExist:
            messages.error(request, 'Error de verificación')
            return redirect('accounts:register')
    
    return render(request, 'accounts/verify_email.html', {'user': user})

def resend_verification_code(request):
    user_id = request.session.get('user_id_to_verify')
    if not user_id:
        messages.error(request, 'Sesión inválida')
        return redirect('accounts:register')
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        verification = user.email_verification
        verification.generate_code()
        
        # Intentar enviar email (sin bloquear)
        try:
            send_mail(
                subject='¡Nuevo código de verificación!',
                message=f'Hola {user.username},\n\nTu nuevo código de verificación es: {verification.verification_code}\n\nEste código expira en 15 minutos.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except:
            pass
        
        # Siempre mostrar el código
        messages.success(request, 'Se ha generado un nuevo código')
        messages.info(request, f'Tu código es: {verification.verification_code} (expira en 15 min)')
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Error de verificación')
    
    return redirect('accounts:verify_email')

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente')
    return redirect('accounts:login')
