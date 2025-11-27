from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import requests
from bs4 import BeautifulSoup
from .forms import ScraperForm
from .models import ScraperResult
import time
import random

@login_required
def scraper_view(request):
    results = []
    if request.method == 'POST':
        form = ScraperForm(request.POST)
        if form.is_valid():
            palabra_clave = form.cleaned_data['palabra_clave']
            
            ScraperResult.objects.filter(palabra_clave=palabra_clave).delete()
            
            # Headers más realistas para evitar bloqueo
            url = f"https://scholar.google.com/scholar?q={palabra_clave}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            }
            
            # Delay aleatorio para simular comportamiento humano
            time.sleep(random.uniform(1, 3))
            
            try:
                response = requests.get(url, headers=headers, timeout=15)
                
                # Detectar bloqueo de Google
                if response.status_code == 429 or 'sorry/index' in response.url:
                    messages.error(request, '⚠️ Google está bloqueando las peticiones temporalmente. Intenta de nuevo en unos minutos.')
                    form = ScraperForm()
                    recent_results = ScraperResult.objects.all().order_by('-fecha_scraping')[:10]
                    return render(request, 'scraper/scraper.html', {'form': form, 'results': results, 'recent_results': recent_results})
                
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                articulos = soup.find_all('div', class_='gs_ri')
                
                if not articulos:
                    articulos = soup.find_all('div', {'data-rp': True})
                
                for articulo in articulos[:10]:
                    try:
                        titulo_elem = articulo.find('h3', class_='gs_rt') or articulo.find('h3')
                        if titulo_elem:
                            link_elem = titulo_elem.find('a')
                            titulo = titulo_elem.get_text(strip=True).replace('[PDF]', '').replace('[HTML]', '')
                            url_articulo = link_elem.get('href', 'N/A') if link_elem else 'N/A'
                            
                            desc_elem = articulo.find('div', class_='gs_rs') or articulo.find('div', class_='gs_a')
                            descripcion = desc_elem.get_text(strip=True) if desc_elem else 'Sin descripción disponible'
                            
                            if titulo and len(titulo) > 3:
                                result = ScraperResult.objects.create(
                                    palabra_clave=palabra_clave,
                                    titulo=titulo[:300],
                                    url=url_articulo[:500],
                                    descripcion=descripcion[:500]
                                )
                                results.append(result)
                    except Exception:
                        continue
                
                if results:
                    messages.success(request, f'✓ Se encontraron {len(results)} resultados')
                else:
                    messages.warning(request, 'No se encontraron resultados. Intenta con otras palabras clave.')
                    
            except requests.exceptions.Timeout:
                messages.error(request, 'Error: Tiempo de espera agotado. Intenta nuevamente.')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error de conexión: {str(e)[:100]}')
            except Exception as e:
                messages.error(request, f'Error inesperado: {str(e)[:100]}')
    else:
        form = ScraperForm()
    
    recent_results = ScraperResult.objects.all().order_by('-fecha_scraping')[:10]
    return render(request, 'scraper/scraper.html', {'form': form, 'results': results, 'recent_results': recent_results})
