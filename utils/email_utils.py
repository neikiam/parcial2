"""
Utilidades para envío de emails usando SendGrid
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
from django.conf import settings


def send_email_with_sendgrid(to_email, subject, message, attachment_content=None, attachment_filename=None):
    """
    Envía un email usando SendGrid API
    
    Args:
        to_email (str): Email del destinatario
        subject (str): Asunto del email
        message (str): Contenido del email
        attachment_content (bytes, optional): Contenido del archivo adjunto
        attachment_filename (str, optional): Nombre del archivo adjunto
    
    Returns:
        bool: True si el email se envió correctamente, False en caso contrario
    """
    try:
        sendgrid_api_key = settings.SENDGRID_API_KEY
        
        if not sendgrid_api_key or sendgrid_api_key == '':
            print("❌ ERROR: SENDGRID_API_KEY no configurada en las variables de entorno")
            return False
        
        print(f"📧 Intentando enviar email a {to_email}")
        print(f"   From: {settings.DEFAULT_FROM_EMAIL}")
        print(f"   Subject: {subject}")
        print(f"   API Key (primeros 10 chars): {sendgrid_api_key[:10]}...")
        
        email = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=message
        )
        
        # Desactivar sandbox mode explícitamente
        email.mail_settings = {
            'sandbox_mode': {
                'enable': False
            }
        }
        
        # Si hay un archivo adjunto, agregarlo
        if attachment_content and attachment_filename:
            print(f"   📎 Adjunto: {attachment_filename}")
            encoded_file = base64.b64encode(attachment_content).decode()
            
            attached_file = Attachment(
                FileContent(encoded_file),
                FileName(attachment_filename),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            email.attachment = attached_file
        
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(email)
        
        print(f"✅ SendGrid response: Status {response.status_code}")
        print(f"   Response body: {response.body}")
        print(f"   X-Message-Id: {response.headers.get('X-Message-Id', 'No ID')}")
        
        # Si hay X-Message-Id, el email fue procesado
        message_id = response.headers.get('X-Message-Id')
        if message_id:
            print(f"   ✅ Email procesado con ID: {message_id}")
            print(f"   📍 Búscalo en Activity: https://app.sendgrid.com/email_activity?filters=%5B%7B%22selectedIds%22%3A%5B%22{message_id}%22%5D%7D%5D")
        
        # Verificar si el código es 2xx (éxito)
        if 200 <= response.status_code < 300:
            print("✅ Email enviado correctamente!")
            return True
        else:
            print(f"⚠️ SendGrid retornó código no exitoso: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ ERROR enviando email con SendGrid:")
        print(f"   Tipo de error: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False
