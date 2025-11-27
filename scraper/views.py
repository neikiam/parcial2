from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import requests
from .forms import ScraperForm
from .models import ScraperResult

@login_required
def scraper_view(request):
    results = []
    if request.method == 'POST':
        form = ScraperForm(request.POST)
        if form.is_valid():
            palabra_clave = form.cleaned_data['palabra_clave']
            
            ScraperResult.objects.filter(palabra_clave=palabra_clave).delete()
            
            # Usar Semantic Scholar API (sin límites estrictos)
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                'query': palabra_clave,
                'limit': 10,
                'fields': 'title,abstract,url,authors,year,citationCount'
            }
            
            try:
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                papers = data.get('data', [])
                
                for paper in papers:
                    try:
                        titulo = paper.get('title', 'Sin título')
                        paper_url = paper.get('url', 'N/A')
                        
                        # Construir descripción con información disponible
                        abstract = paper.get('abstract', '')
                        authors = paper.get('authors', [])
                        year = paper.get('year', '')
                        citations = paper.get('citationCount', 0)
                        
                        # Nombres de autores
                        author_names = [a.get('name', '') for a in authors[:3]]
                        author_str = ', '.join(author_names)
                        if len(authors) > 3:
                            author_str += f' et al.'
                        
                        # Descripción combinada
                        descripcion_parts = []
                        if author_str:
                            descripcion_parts.append(f"Autores: {author_str}")
                        if year:
                            descripcion_parts.append(f"Año: {year}")
                        if citations:
                            descripcion_parts.append(f"Citaciones: {citations}")
                        if abstract:
                            descripcion_parts.append(abstract[:300])
                        
                        descripcion = ' | '.join(descripcion_parts) if descripcion_parts else 'Sin descripción disponible'
                        
                        if titulo and len(titulo) > 3:
                            result = ScraperResult.objects.create(
                                palabra_clave=palabra_clave,
                                titulo=titulo[:300],
                                url=paper_url[:500] if paper_url else 'N/A',
                                descripcion=descripcion[:500]
                            )
                            results.append(result)
                    except Exception:
                        continue
                
                if results:
                    messages.success(request, f'✓ Se encontraron {len(results)} artículos académicos')
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
