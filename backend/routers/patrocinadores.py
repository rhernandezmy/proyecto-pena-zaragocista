import os
import shutil
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(prefix="/patrocinadores", tags=["Patrocinadores"])

UPLOAD_DIR = "static/uploads/patrocinadores"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("", response_model=list[schemas.Patrocinador])
def obtener_patrocinadores(db: Session = Depends(get_db)):
    return db.query(models.Patrocinador).all()

@router.post("", response_model=schemas.Patrocinador, status_code=status.HTTP_201_CREATED)
def crear_patrocinador(
    nombre: str = Form(...),
    tipo_negocio: str = Form("Bar"),
    enlace_web: Optional[str] = Form(None),
    contribucion: float = Form(0.0),
    imagen: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    logo_url = None
    if imagen and imagen.filename:
        ext = os.path.splitext(imagen.filename)[1].lower()
        nombre_archivo = f"{uuid.uuid4().hex}{ext}"
        ruta_destino = os.path.join(UPLOAD_DIR, nombre_archivo)
        
        with open(ruta_destino, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
            
        logo_url = f"/static/uploads/patrocinadores/{nombre_archivo}"

    nuevo_patro = models.Patrocinador(
        nombre=nombre,
        tipo_negocio=tipo_negocio,
        logo_url=logo_url,
        enlace_web=enlace_web if enlace_web else None,
        contribucion=contribucion
    )
    db.add(nuevo_patro)
    db.commit()
    db.refresh(nuevo_patro)
    return nuevo_patro

@router.delete("/{patrocinador_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_patrocinador(patrocinador_id: int, db: Session = Depends(get_db)):
    patrocinador = db.query(models.Patrocinador).filter(models.Patrocinador.id == patrocinador_id).first()
    
    if not patrocinador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="El patrocinador que intentas eliminar no existe."
        )
    
    # Borra también la imagen física del servidor si existía
    if patrocinador.logo_url and patrocinador.logo_url.startswith("/static/"):
        ruta_fisica = patrocinador.logo_url.lstrip("/")
        if os.path.exists(ruta_fisica):
            os.remove(ruta_fisica)
            
    db.delete(patrocinador)
    db.commit()
    return None