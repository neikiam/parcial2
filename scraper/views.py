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
            
            api_url = "https://es.wikipedia.org/w/api.php"
            
            headers = {
                'User-Agent': 'Parcial2App/1.0 (Django Educational Project; neikiam500@gmail.com)'
            }
            
            params = {
                'action': 'opensearch',
                'format': 'json',
                'search': palabra_clave,
                'limit': 10
            }
            
            try:
                response = requests.get(api_url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if len(data) >= 4:
                    titles = data[1]
                    descriptions = data[2]
                    urls = data[3]
                    
                    for i in range(len(titles)):
                        results.append({
                            'titulo': titles[i],
                            'descripcion': descriptions[i] if descriptions[i] else 'Artículo de Wikipedia',
                            'url': urls[i]
                        })
                    
                    if results:
                        messages.success(request, f'✓ Se encontraron {len(results)} artículos relacionados')
                    else:
                        messages.warning(request, f'No se encontraron artículos relacionados con "{palabra_clave}".')
                else:
                    messages.warning(request, 'No se encontraron resultados en Wikipedia.')
                    
            except requests.exceptions.Timeout:
                messages.error(request, 'Error: Tiempo de espera agotado.')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error de conexión: {str(e)[:100]}')
            except Exception as e:
                messages.error(request, f'Error inesperado: {str(e)[:100]}')
    else:
        form = ScraperForm()
    
    return render(request, 'scraper/scraper.html', {'form': form, 'results': results})
