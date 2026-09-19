import os
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List
from database import get_db, Base
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean

# Localizar la raíz del proyecto para encontrar el archivo .env sin fallar
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

if not env_path.exists():
    # Si contacto.py estuviera en la raíz en lugar de la carpeta /routers
    env_path = Path(__file__).resolve().parent / ".env"

load_dotenv(dotenv_path=env_path)

router = APIRouter()

# ==========================================
# MODELO DE LA TABLA EN POSTGRESQL (SQLAlchemy)
# ==========================================
class Contacto(Base):
    __tablename__ = "contactos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False)
    asunto = Column(String, nullable=False)
    mensaje = Column(String, nullable=False)
    archivado = Column(Boolean, default=False)


# ==========================================
# SCHEMAS DE VALIDACIÓN (Pydantic)
# ==========================================
class MensajeContactoCreate(BaseModel):
    nombre: str
    email: EmailStr
    asunto: str
    mensaje: str

class MensajeContactoOut(BaseModel):
    id: int
    nombre: str
    email: str
    asunto: str
    mensaje: str
    archivado: bool

    class Config:
        from_attributes = True


# ==========================================
# FUNCIÓN AUXILIAR DE ENVÍO DE EMAIL
# ==========================================
def enviar_notificacion_email(nombre: str, email_remitente: str, asunto_msg: str, mensaje_txt: str):
    email_pena = os.getenv("MAIL_USERNAME", "presentesxelescudo@gmail.com")
    password_app = os.getenv("MAIL_PASSWORD")

    if not password_app:
        print("⚠️ Notificación no enviada: Falta MAIL_PASSWORD en el archivo .env")
        return

    msg = MIMEMultipart()
    msg['From'] = email_pena
    msg['To'] = email_pena
    msg['Reply-To'] = email_remitente
    msg['Subject'] = f"📩 Contacto Web: {asunto_msg}"

    cuerpo = f"""
Has recibido un nuevo mensaje desde el formulario web:

• Nombre: {nombre}
• Email: {email_remitente}
• Asunto: {asunto_msg}

--------------------------------------------------
Mensaje:
{mensaje_txt}
--------------------------------------------------
    """
    msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_pena, password_app)
        server.send_message(msg)
        server.quit()
        print("✅ Correo enviado con éxito a la peña.")
    except Exception as e:
        print(f"⚠️ Error al enviar correo de notificación: {e}")


# ==========================================
# RUTAS DEL ENDPOINT
# ==========================================

# 1. POST /api/contacto -> Guarda en BD y notifica por email
@router.post("", status_code=status.HTTP_201_CREATED)
def crear_mensaje(payload: MensajeContactoCreate, db: Session = Depends(get_db)):
    try:
        # Guardar registro en PostgreSQL
        nuevo_mensaje = Contacto(
            nombre=payload.nombre,
            email=payload.email,
            asunto=payload.asunto,
            mensaje=payload.mensaje
        )
        db.add(nuevo_mensaje)
        db.commit()
        db.refresh(nuevo_mensaje)

        # Enviar notificación por correo
        enviar_notificacion_email(
            nombre=payload.nombre,
            email_remitente=payload.email,
            asunto_msg=payload.asunto,
            mensaje_txt=payload.mensaje
        )

        return {"status": "success", "message": "Mensaje registrado y notificación enviada"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")


# 2. GET /api/contacto/list -> Lista mensajes para el Panel (Admin)
@router.get("/list", response_model=List[MensajeContactoOut])
def listar_mensajes(db: Session = Depends(get_db)):
    try:
        mensajes = db.query(Contacto).order_by(Contacto.archivado.asc(), Contacto.id.desc()).all()
        return mensajes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener mensajes: {str(e)}")


# 3. PUT /api/contacto/{id}/archivar -> Archiva un mensaje procesado (Admin)
@router.put("/{mensaje_id}/archivar")
def archivar_mensaje(mensaje_id: int, db: Session = Depends(get_db)):
    mensaje = db.query(Contacto).filter(Contacto.id == mensaje_id).first()
    
    if not mensaje:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    
    try:
        mensaje.archivado = True
        db.commit()
        return {"status": "success", "message": "Mensaje archivado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al archivar el mensaje: {str(e)}")