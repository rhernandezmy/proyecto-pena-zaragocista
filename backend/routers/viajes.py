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
    partido_asociado = db.query(models.Partido).filter(models.Partido.id == viaje.partido_id).first()
    if not partido_asociado:
        raise HTTPException(status_code=404, detail="El partido especificado no existe.")
        
    if "Ibercaja estadio" in partido_asociado.lugar:
        raise HTTPException(
            status_code=400, 
            detail="No se pueden organizar viajes para partidos en el Ibercaja Estadio (Local)."
        )

    nuevo_viaje = models.Viaje(
        partido_id=viaje.partido_id,
        destino=viaje.destino,
        email_conductor=viaje.email_conductor,  # 🌟 NUEVA LÍNEA: Guardamos el correo real
        tipo_transporte=viaje.tipo_transporte,
        plazas_totales=viaje.plazas_totales,
        plazas_disponibles=viaje.plazas_disponibles,
        precio=viaje.precio,
        detalles_precio=viaje.detalles_precio,
        hace_noche=viaje.hace_noche
    )
    db.add(nuevo_viaje)
    db.commit()
    db.refresh(nuevo_viaje)
    return nuevo_viaje

@router.delete("/{viaje_id}")
def borrar_viaje(viaje_id: int, db: Session = Depends(get_db)):
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        raise HTTPException(status_code=404, detail="El viaje que intentas borrar no existe.")
    db.delete(viaje)
    db.commit()
    return {"ok": True, "mensaje": f"Viaje con ID {viaje_id} cancelado correctamente."}