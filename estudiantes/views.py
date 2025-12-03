from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import Alumno
from .forms import AlumnoForm

@login_required
def dashboard(request):
    alumnos = Alumno.objects.filter(usuario=request.user)
    return render(request, 'estudiantes/dashboard.html', {'alumnos': alumnos})

@login_required
def create_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save(commit=False)
            alumno.usuario = request.user
            alumno.save()
            messages.success(request, 'Alumno creado exitosamente')
            return redirect('estudiantes:dashboard')
    else:
        form = AlumnoForm()
    return render(request, 'estudiantes/form.html', {'form': form, 'action': 'Crear'})

@login_required
def edit_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alumno actualizado exitosamente')
            return redirect('estudiantes:dashboard')
    else:
        form = AlumnoForm(instance=alumno)
    return render(request, 'estudiantes/form.html', {'form': form, 'action': 'Editar'})

@login_required
def delete_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    if request.method == 'POST':
        alumno.delete()
        messages.success(request, 'Alumno eliminado exitosamente')
        return redirect('estudiantes:dashboard')
    return render(request, 'estudiantes/confirm_delete.html', {'alumno': alumno})

@login_required
def send_pdf(request, pk):
    from django.http import HttpResponse
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    p.setFont("Helvetica-Bold", 24)
    p.drawString(100, height - 100, "Información del Alumno")
    
    p.setFont("Helvetica", 12)
    y_position = height - 150
    
    p.drawString(100, y_position, f"Nombre: {alumno.nombre}")
    y_position -= 30
    p.drawString(100, y_position, f"Apellido: {alumno.apellido}")
    y_position -= 30
    p.drawString(100, y_position, f"Nota: {alumno.nota}")
    y_position -= 30
    p.drawString(100, y_position, f"Fecha de registro: {alumno.fecha_creacion.strftime('%d/%m/%Y %H:%M')}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    pdf_content = buffer.read()
    
    try:
        email = EmailMessage(
            subject=f'PDF - Alumno {alumno.nombre} {alumno.apellido}',
            body=f'Adjunto encontrarás el PDF con la información del alumno {alumno.nombre} {alumno.apellido}.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[request.user.email],
        )
        email.attach(f'alumno_{alumno.nombre}_{alumno.apellido}.pdf', pdf_content, 'application/pdf')
        email.send(fail_silently=True)
        messages.success(request, f'PDF enviado a {request.user.email}')
        return redirect('estudiantes:dashboard')
    except:
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="alumno_{alumno.nombre}_{alumno.apellido}.pdf"'
        return response

@login_required
def export_csv(request):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="alumnos.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['nombre', 'apellido', 'nota'])
    
    alumnos = Alumno.objects.filter(usuario=request.user)
    for alumno in alumnos:
        writer.writerow([alumno.nombre, alumno.apellido, alumno.nota])
    
    return response
