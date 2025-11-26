from django.db import models

class ScraperResult(models.Model):
    palabra_clave = models.CharField(max_length=200)
    titulo = models.CharField(max_length=300)
    url = models.URLField()
    descripcion = models.TextField(blank=True)
    fecha_scraping = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_scraping']

    def __str__(self):
        return f"{self.titulo} - {self.palabra_clave}"
