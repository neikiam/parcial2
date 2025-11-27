from django.db import models
from django.contrib.auth.models import User
import random
from django.utils import timezone
from datetime import timedelta

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    verification_code = models.CharField(max_length=6, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """Genera código automáticamente al crear"""
        if not self.verification_code:
            self.verification_code = str(random.randint(100000, 999999))
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)
    
    def generate_code(self):
        """Regenera un código de 6 dígitos"""
        self.verification_code = str(random.randint(100000, 999999))
        self.expires_at = timezone.now() + timedelta(minutes=15)
        self.save()
    
    def is_expired(self):
        """Verifica si el código ha expirado"""
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.user.username} - {'Verificado' if self.is_verified else 'Pendiente'}"
