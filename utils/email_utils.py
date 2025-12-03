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
        
        if not sendgrid_api_key:
            print("Error: SENDGRID_API_KEY no configurada")
            return False
        
        email = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=message
        )
        
        # Si hay un archivo adjunto, agregarlo
        if attachment_content and attachment_filename:
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
        
        print(f"Email enviado exitosamente. Status code: {response.status_code}")
        return True
        
    except Exception as e:
        print(f"Error enviando email con SendGrid: {e}")
        return False
