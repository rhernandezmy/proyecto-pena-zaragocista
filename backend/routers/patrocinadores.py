from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(prefix="/patrocinadores", tags=["Patrocinadores"])

@router.get("")
def obtener_patrocinadores(db: Session = Depends(get_db)):
    return db.query(models.Patrocinador).all()

@router.post("")
def crear_patrocinador(patrocinador: schemas.PatrocinadorCrear, db: Session = Depends(get_db)):
    nuevo_patro = models.Patrocinador(**patrocinador.model_dump())
    db.add(nuevo_patro)
    db.commit()
    db.refresh(nuevo_patro)
    return nuevo_patro