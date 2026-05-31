from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
# Importamos el servicio de correo que creamos en el paso anterior
from services.email import enviar_correo_cancelacion

router = APIRouter(prefix="/reservas", tags=["Reservas"])

# 1. RUTA GET: Obtener todas las reservas de la peña
@router.get("")
def obtener_reservas(db: Session = Depends(get_db)):
    return db.query(models.Reserva).all()

# 2. RUTA POST: Crear una reserva de plaza y restar asientos del viaje automáticamente
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

# 3. RUTA GET: Obtener la lista de socios apuntados a un viaje concreto (Para el "cotilleo" de la peña)
@router.get("/viaje/{viaje_id}")
def obtener_viajeros_por_viaje(viaje_id: int, db: Session = Depends(get_db)):
    lista_reservas = db.query(models.Reserva).filter(models.Reserva.viaje_id == viaje_id).all()
    return lista_reservas

# 4. RUTA DELETE: Cancelar reserva, devolver plazas al coche y avisar al conductor por email
@router.delete("/{reserva_id}")
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    # A. Buscamos la reserva
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="La reserva que intentas cancelar no existe.")
    
    # B. Buscamos el viaje asociado para devolverle las plazas libres
    viaje = db.query(models.Viaje).filter(models.Viaje.id == reserva.viaje_id).first()
    if viaje:
        viaje.plazas_disponibles += reserva.asientos_reservados
    
    socio_afectado = reserva.nombre_socio
    asientos_liberados = reserva.asientos_reservados
    destino = viaje.destino if viaje else "Destino Desconocido"
    
    # C. Borramos la reserva físicamente de PostgreSQL
    db.delete(reserva)
    db.commit()
    
    # D. DISPARO DEL EMAIL AUTOMÁTICO DE ALERTA
    # De momento mandamos el correo a un email de prueba simulando el del conductor de ese coche
    email_conductor_real = viaje.email_conductor if viaje else "presentesxelescudo@gmail.com" # Fallback por si el viaje no existe (aunque debería existir)
    
    enviar_correo_cancelacion(
        email_conductor=email_conductor_real,
        nombre_socio=socio_afectado,
        destino_viaje=destino,
        plazas=asientos_liberados
    )
    
    return {
        "ok": True, 
        "mensaje": f"Reserva de {socio_afectado} cancelada con éxito. Se han devuelto {asientos_liberados} plazas al coche. ¡Email de alerta enviado al conductor!"
    }