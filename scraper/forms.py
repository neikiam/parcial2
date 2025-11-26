from django import forms

class ScraperForm(forms.Form):
    palabra_clave = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa una palabra clave educativa...'
        }),
        label='Palabra Clave'
    )
    email_destino = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        }),
        label='Email de Destino'
    )
