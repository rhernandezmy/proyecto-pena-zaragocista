import smtplib
import ssl
from email.message import EmailMessage
from config import settings

async def enviar_correo_verificacion(email_destino, username):
    try:
        # Configuración del mensaje
        mensaje = EmailMessage()
        mensaje["From"] = settings.email_host_user
        mensaje["To"] = email_destino
        mensaje["Subject"] = "Activa tu cuenta de socio - Peña Zaragocista"
        
        contenido = f"""
        Hola {username},
        
        Para activar tu cuenta, haz clic en el siguiente enlace:
        http://localhost:8000/auth/verificar?email={email_destino}
        
        Si no has solicitado este registro, ignora este correo.
        """
        mensaje.set_content(contenido)

        # Usamos SSL directo en el puerto 465 (más seguro y sin errores de STARTTLS)
        context = ssl.create_default_context()
        
        # Ejecución sincrónica dentro de un hilo (para no bloquear FastAPI)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(settings.email_host_user, settings.email_host_password)
            server.send_message(mensaje)
            
        print(f"📧 [EMAIL] Correo enviado correctamente a {email_destino}")
        
    except Exception as e:
        print(f"❌ [ERROR EMAIL DETALLADO]: {type(e).__name__} - {str(e)}")
        raise Exception("Error al enviar el correo.")