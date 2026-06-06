from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(prefix="/reservas", tags=["Reservas"])

@router.get("")
def obtener_reservas(db: Session = Depends(get_db)):
    return db.query(models.Reserva).all()

@router.post("")
def crear_reserva(reserva: schemas.ReservaCrear, db: Session = Depends(get_db)):
    # 1. Validar existencia del viaje
    viaje = db.query(models.Viaje).filter(models.Viaje.id == reserva.viaje_id).first()
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado.")
    
    # 2. Validar que el usuario existe (para asegurar integridad)
    usuario = db.query(models.Usuario).filter(models.Usuario.id == reserva.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # 3. Validar disponibilidad
    if viaje.plazas_disponibles < reserva.asientos_reservados:
        raise HTTPException(status_code=400, detail=f"Plazas insuficientes. Quedan {viaje.plazas_disponibles}.")
    
    # 4. Procesar reserva
    viaje.plazas_disponibles -= reserva.asientos_reservados
    nueva_reserva = models.Reserva(**reserva.model_dump())
    
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    return {"ok": True, "reserva": nueva_reserva}

@router.get("/viaje/{viaje_id}")
def obtener_viajeros_por_viaje(viaje_id: int, db: Session = Depends(get_db)):
    return db.query(models.Reserva).filter(models.Reserva.viaje_id == viaje_id).all()

@router.delete("/{reserva_id}")
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")
    
    viaje = db.query(models.Viaje).filter(models.Viaje.id == reserva.viaje_id).first()
    if viaje:
        viaje.plazas_disponibles += reserva.asientos_reservados
    
    db.delete(reserva)
    db.commit()
    return {"ok": True, "mensaje": "Reserva cancelada."}