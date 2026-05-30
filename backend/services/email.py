import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargamos automáticamente las variables del archivo .env oculto
load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Leemos de forma segura los datos reales del archivo secreto .env
EMAIL_REMITENTE = os.getenv("EMAIL_REMITENTE")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def enviar_correo_cancelacion(email_conductor: str, nombre_socio: str, destino_viaje: str, plazas: int):
    try:
        # Validación de seguridad por si las variables del .env no cargan
        if not EMAIL_REMITENTE or not EMAIL_PASSWORD:
            print("❌ Error: No se han configurado las credenciales de email en el archivo .env")
            return False

        # 1. Creamos el esqueleto del mensaje
        mensaje = MIMEMultipart()
        mensaje["From"] = EMAIL_REMITENTE
        mensaje["To"] = email_conductor
        mensaje["Subject"] = f"⚠️ ¡Baja en tu viaje a {destino_viaje}! - Peña Zaragocista"

        # 2. Diseñamos el cuerpo del correo en texto plano
        cuerpo = f"""
        Hola, Conductor/a:

        Te avisamos de que el socio {nombre_socio} ha cancelado su reserva para tu viaje con destino a {destino_viaje}.
        
        Se han liberado automáticamente {plazas} plaza(s) en tu coche, por lo que vuelven a estar disponibles en la web para que se apunte otra persona.

        Un saludo,
        El sistema automático de la Peña Zaragocista 🦁⚽
        """
        mensaje.attach(MIMEText(cuerpo, "plain", "utf-8"))

        # 3. Conexión segura con los servidores de Google y envío
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Cifrado de seguridad
        server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
        server.sendmail(EMAIL_REMITENTE, email_conductor, mensaje.as_string())
        server.quit()
        
        print(f"✅ Correo de aviso enviado correctamente a {email_conductor}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar el correo: {str(e)}")
        return False