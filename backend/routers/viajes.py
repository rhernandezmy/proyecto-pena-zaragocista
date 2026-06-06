from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(prefix="/viajes", tags=["Viajes"])

@router.get("")
def obtener_viajes(db: Session = Depends(get_db)):
    return db.query(models.Viaje).all()

@router.post("")
def crear_viaje(viaje: schemas.ViajeCrear, db: Session = Depends(get_db)):
    partido = db.query(models.Partido).filter(models.Partido.id == viaje.partido_id).first()
    
    if not partido:
        raise HTTPException(status_code=404, detail="Partido no encontrado.")
    
    if "Ibercaja estadio" in partido.lugar:
        raise HTTPException(status_code=400, detail="No se permiten viajes a partidos locales.")

    nuevo_viaje = models.Viaje(**viaje.model_dump())
    db.add(nuevo_viaje)
    db.commit()
    db.refresh(nuevo_viaje)
    return nuevo_viaje

@router.delete("/{viaje_id}")
def borrar_viaje(viaje_id: int, db: Session = Depends(get_db)):
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado.")
    db.delete(viaje)
    db.commit()
    return {"mensaje": "Viaje cancelado correctamente."}