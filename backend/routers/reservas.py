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
    viaje = db.query(models.Viaje).filter(models.Viaje.id == reserva.viaje_id).first()
    if not viaje:
        raise HTTPException(status_code=404, detail="El viaje al que intentas apuntarte no existe.")
    
    if viaje.plazas_disponibles < reserva.asientos_reservados:
        raise HTTPException(status_code=400, detail=f"¡No hay plazas! Solo quedan {viaje.plazas_disponibles} asientos.")
    
    viaje.plazas_disponibles -= reserva.asientos_reservados
    
    nueva_reserva = models.Reserva(
        viaje_id=reserva.viaje_id,
        nombre_socio=reserva.nombre_socio,
        asientos_reservados=reserva.asientos_reservados
    )
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    return {"ok": True, "mensaje": "¡Reserva realizada con éxito!", "reserva": nueva_reserva}

@router.get("/viaje/{viaje_id}")
def obtener_viajeros_por_viaje(viaje_id: int, db: Session = Depends(get_db)):
    lista_reservas = db.query(models.Reserva).filter(models.Reserva.viaje_id == viaje_id).all()
    return lista_reservas

@router.delete("/{reserva_id}")
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="La reserva que intentas cancelar no existe.")
    
    viaje = db.query(models.Viaje).filter(models.Viaje.id == reserva.viaje_id).first()
    if viaje:
        viaje.plazas_disponibles += reserva.asientos_reservados
    
    db.delete(reserva)
    db.commit()
    
    return {"ok": True, "mensaje": f"Reserva {reserva_id} cancelada con éxito."}