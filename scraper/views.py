from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import requests
from bs4 import BeautifulSoup
from .forms import ScraperForm

@login_required
def scraper_view(request):
    results = []
    if request.method == 'POST':
        form = ScraperForm(request.POST)
        
        if 'enviar_email' in request.POST:
            resultados_texto = request.POST.get('resultados_texto', '')
            palabra = request.POST.get('palabra_busqueda', '')
            
            try:
                send_mail(
                    subject=f'Resultados de búsqueda: {palabra}',
                    message=resultados_texto,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
                messages.success(request, f'Resultados enviados a {request.user.email}')
            except:
                messages.error(request, 'No se pudo enviar el email')
            
            return render(request, 'scraper/scraper.html', {'form': form, 'results': []})
        
        if form.is_valid():
            palabra_clave = form.cleaned_data['palabra_clave']
            
            url = f"https://es.wikipedia.org/wiki/{palabra_clave.replace(' ', '_')}"
            
            try:
                response = requests.get(url, timeout=10)
                
                if response.status_code == 404:
                    messages.warning(request, 'No se encontró el artículo en Wikipedia. Intenta con otra palabra.')
                else:
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    content = soup.find('div', {'id': 'mw-content-text'})
                    
                    if content:
                        paragraphs = content.find_all('p', limit=3)
                        for p in paragraphs:
                            text = p.get_text(strip=True)
                            if len(text) > 50:
                                results.append({
                                    'titulo': 'Párrafo',
                                    'descripcion': text[:500]
                                })
                        
                        headings = content.find_all(['h2', 'h3'], limit=10)
                        for h in headings:
                            span = h.find('span', {'class': 'mw-headline'})
                            if span:
                                titulo = span.get_text(strip=True)
                                if titulo and titulo not in ['Referencias', 'Enlaces externos', 'Véase también']:
                                    results.append({
                                        'titulo': titulo,
                                        'descripcion': 'Sección del artículo'
                                    })
                    
                    if results:
                        messages.success(request, f'✓ Se encontraron {len(results)} elementos')
                    else:
                        messages.warning(request, 'No se encontró contenido. Intenta con otra palabra.')
                    
            except requests.exceptions.Timeout:
                messages.error(request, 'Error: Tiempo de espera agotado.')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error de conexión: {str(e)[:100]}')
            except Exception as e:
                messages.error(request, f'Error inesperado: {str(e)[:100]}')
    else:
        form = ScraperForm()
    
    return render(request, 'scraper/scraper.html', {'form': form, 'results': results})
