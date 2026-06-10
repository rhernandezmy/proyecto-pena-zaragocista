from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean
from database import Base

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
        from_attributes = True  # Permite a Pydantic leer los modelos de SQLAlchemy


# ==========================================
# RUTAS DEL ENDPOINT
# ==========================================

# 1. POST /api/contacto -> Guarda un nuevo mensaje en PostgreSQL
@router.post("", status_code=status.HTTP_201_CREATED)
def crear_mensaje(payload: MensajeContactoCreate, db: Session = Depends(get_db)):
    try:
        nuevo_mensaje = Contacto(
            nombre=payload.nombre,
            email=payload.email,
            asunto=payload.asunto,
            mensaje=payload.mensaje
        )
        db.add(nuevo_mensaje)
        db.commit()
        db.refresh(nuevo_mensaje)
        return {"status": "success", "message": "Mensaje registrado correctamente en PostgreSQL"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")


# 2. GET /api/contacto/list -> Lista mensajes organizados para el Panel (Admin)
@router.get("/list", response_model=List[MensajeContactoOut])
def listar_mensajes(db: Session = Depends(get_db)):
    try:
        # Traemos ordenados por no archivados primero, y luego por ID descendente
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