from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(prefix="/patrocinadores", tags=["Patrocinadores"])

# 1. OBTENER TODOS LOS PATROCINADORES (Para listarlos en la tabla del panel)
@router.get("", response_model=list[schemas.Patrocinador])
def obtener_patrocinadores(db: Session = Depends(get_db)):
    return db.query(models.Patrocinador).all()

# 2. CREAR UN NUEVO PATROCINADOR (Desde el formulario del panel)
@router.post("", response_model=schemas.Patrocinador, status_code=status.HTTP_201_CREATED)
def crear_patrocinador(patrocinador: schemas.PatrocinadorCrear, db: Session = Depends(get_db)):
    nuevo_patro = models.Patrocinador(**patrocinador.model_dump())
    db.add(nuevo_patro)
    db.commit()
    db.refresh(nuevo_patro)
    return nuevo_patro

# 3. ELIMINAR UN PATROCINADOR (NUEVO: Para la acción del botón de quitar)
@router.delete("/{patrocinador_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_patrocinador(patrocinador_id: int, db: Session = Depends(get_db)):
    # Buscamos si existe el partner en la base de datos
    patrocinador = db.query(models.Patrocinador).filter(models.Patrocinador.id == patrocinador_id).first()
    
    if not patrocinador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="El patrocinador que intentas eliminar no existe."
        )
        
    db.delete(patrocinador)
    db.commit()
    return None