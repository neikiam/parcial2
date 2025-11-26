from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import requests
from bs4 import BeautifulSoup
from .forms import ScraperForm
from .models import ScraperResult

@login_required
def scraper_view(request):
    results = []
    if request.method == 'POST':
        form = ScraperForm(request.POST)
        if form.is_valid():
            palabra_clave = form.cleaned_data['palabra_clave']
            email_destino = form.cleaned_data['email_destino']
            
            ScraperResult.objects.filter(palabra_clave=palabra_clave).delete()
            
            url = f"https://scholar.google.com/scholar?q={palabra_clave}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                articulos = soup.find_all('div', class_='gs_ri')
                
                for articulo in articulos[:10]:
                    try:
                        titulo_elem = articulo.find('h3', class_='gs_rt')
                        if titulo_elem:
                            link_elem = titulo_elem.find('a')
                            titulo = titulo_elem.get_text(strip=True)
                            url_articulo = link_elem['href'] if link_elem and 'href' in link_elem.attrs else 'N/A'
                            
                            desc_elem = articulo.find('div', class_='gs_rs')
                            descripcion = desc_elem.get_text(strip=True) if desc_elem else 'Sin descripción'
                            
                            result = ScraperResult.objects.create(
                                palabra_clave=palabra_clave,
                                titulo=titulo,
                                url=url_articulo,
                                descripcion=descripcion[:500]
                            )
                            results.append(result)
                    except Exception:
                        continue
                
                if results:
                    email_body = f"Resultados de búsqueda para: {palabra_clave}\n\n"
                    for idx, result in enumerate(results, 1):
                        email_body += f"{idx}. {result.titulo}\n"
                        email_body += f"   URL: {result.url}\n"
                        email_body += f"   Descripción: {result.descripcion[:200]}...\n\n"
                    
                    send_mail(
                        subject=f'Resultados de Scraping: {palabra_clave}',
                        message=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email_destino],
                        fail_silently=True,
                    )
                    
                    messages.success(request, f'Se encontraron {len(results)} resultados y se enviaron a {email_destino}')
                else:
                    messages.warning(request, 'No se encontraron resultados')
                    
            except Exception as e:
                messages.error(request, f'Error al realizar el scraping: {str(e)}')
    else:
        form = ScraperForm()
    
    return render(request, 'scraper/scraper.html', {'form': form, 'results': results})
