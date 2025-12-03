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
                'action': 'query',
                'format': 'json',
                'titles': palabra_clave,
                'prop': 'extracts|sections',
                'exintro': True,
                'explaintext': True,
                'redirects': 1
            }
            
            try:
                response = requests.get(api_url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                pages = data.get('query', {}).get('pages', {})
                
                if not pages:
                    messages.warning(request, 'No se encontraron resultados en Wikipedia.')
                else:
                    page = list(pages.values())[0]
                    
                    if 'missing' in page:
                        messages.warning(request, f'No se encontró el artículo "{palabra_clave}" en Wikipedia. Intenta con otra palabra.')
                    else:
                        extract = page.get('extract', '')
                        
                        if extract:
                            sentences = extract.split('.')
                            for i, sentence in enumerate(sentences[:5], 1):
                                if len(sentence.strip()) > 20:
                                    results.append({
                                        'titulo': f'Párrafo {i}',
                                        'descripcion': sentence.strip()[:500]
                                    })
                        
                        try:
                            params_sections = {
                                'action': 'parse',
                                'format': 'json',
                                'page': palabra_clave,
                                'prop': 'sections',
                                'redirects': 1
                            }
                            
                            response_sections = requests.get(api_url, params=params_sections, headers=headers, timeout=10)
                            sections_data = response_sections.json()
                            
                            if 'parse' in sections_data:
                                sections = sections_data.get('parse', {}).get('sections', [])
                                for section in sections[:8]:
                                    titulo = section.get('line', '')
                                    if titulo and titulo not in ['Referencias', 'Enlaces externos', 'Véase también', 'Bibliografía']:
                                        results.append({
                                            'titulo': titulo,
                                            'descripcion': 'Sección del artículo'
                                        })
                        except:
                            pass
                        
                        if results:
                            messages.success(request, f'✓ Se encontraron {len(results)} elementos de Wikipedia')
                        else:
                            messages.warning(request, 'El artículo existe pero no se pudo extraer contenido. Intenta con otra palabra.')
                    
            except requests.exceptions.Timeout:
                messages.error(request, 'Error: Tiempo de espera agotado.')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error de conexión: {str(e)[:100]}')
            except Exception as e:
                messages.error(request, f'Error inesperado: {str(e)[:100]}')
    else:
        form = ScraperForm()
    
    return render(request, 'scraper/scraper.html', {'form': form, 'results': results})
