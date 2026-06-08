from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(prefix="/reservas", tags=["Reservas"])

# 1. OBTENER TODAS LAS RESERVAS
@router.get("")
def obtener_reservas(db: Session = Depends(get_db)):
    return db.query(models.Reserva).all()


# 2. CREAR NUEVA RESERVA (Adaptado para Viajes y Local)
@router.post("")
def crear_reserva(reserva: schemas.ReservaCrear, db: Session = Depends(get_db)):
    # Validar que el usuario/socio existe obligatoriamente
    usuario = db.query(models.Usuario).filter(models.Usuario.id == reserva.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # CASO A: Es una reserva para un VIAJE On Tour
    if reserva.tipo_reserva == "Viaje":
        if not reserva.viaje_id:
            raise HTTPException(status_code=400, detail="El viaje_id es obligatorio para reservas de tipo 'Viaje'.")
            
        viaje = db.query(models.Viaje).filter(models.Viaje.id == reserva.viaje_id).first()
        if not viaje:
            raise HTTPException(status_code=404, detail="Viaje no encontrado.")
        
        # Validar disponibilidad de plazas
        if viaje.plazas_disponibles < reserva.asientos_reservados:
            raise HTTPException(status_code=400, detail=f"Plazas insuficientes. Quedan {viaje.plazas_disponibles}.")
        
        # Restar plazas del transporte
        viaje.plazas_disponibles -= reserva.asientos_reservados
        
        # Las reservas de viaje se aprueban automáticamente al tramitarse
        estado_inicial = "Aprobada"

    # CASO B: Es una solicitud para usar el LOCAL de la peña
    else:
        if not reserva.motivo_evento:
            raise HTTPException(status_code=400, detail="Debes especificar el motivo para reservar el local.")
        
        # Las solicitudes del local se quedan en "Pendiente" hasta que el admin las revise en el panel
        estado_inicial = "Pendiente"

    # Guardar en base de datos
    nueva_reserva = models.Reserva(
        **reserva.model_dump(),
        estado_solicitud=estado_inicial
    )
    
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    return {"ok": True, "reserva": nueva_reserva}


# 3. OBTENER VIAJEROS POR ID DE VIAJE
@router.get("/viaje/{viaje_id}")
def obtener_viajeros_por_viaje(viaje_id: int, db: Session = Depends(get_db)):
    return db.query(models.Reserva).filter(models.Reserva.viaje_id == viaje_id).all()


# 4. RESOLVER RESERVA DEL LOCAL (NUEVO: Para los botones "Aprobar" y "Rechazar" del admin)
@router.patch("/{reserva_id}/resolucion")
def resolver_reserva_local(reserva_id: int, estado: str, db: Session = Depends(get_db)):
    """
    Permite cambiar el estado de la reserva del local a 'Aprobada' o 'Rechazada'.
    Se espera recibir por parámetro de consulta el string 'Aprobada' o 'Rechazada'.
    """
    if estado not in ["Aprobada", "Rechazada"]:
        raise HTTPException(status_code=400, detail="Estado inválido. Debe ser 'Aprobada' o 'Rechazada'.")

    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="La solicitud de reserva no existe.")
        
    if reserva.tipo_reserva != "Local":
        raise HTTPException(status_code=400, detail="Esta ruta solo gestiona resoluciones de reservas del Local.")

    reserva.estado_solicitud = estado
    db.commit()
    return {"ok": True, "mensaje": f"Reserva del local marcada como: {estado}"}


# 5. CANCELAR / ELIMINAR RESERVA
@router.delete("/{reserva_id}")
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")
    
    # Si era de un viaje, devolvemos las plazas al bus/coche antes de borrarla
    if reserva.tipo_reserva == "Viaje" and reserva.viaje_id:
        viaje = db.query(models.Viaje).filter(models.Viaje.id == reserva.viaje_id).first()
        if viaje:
            viaje.plazas_disponibles += reserva.asientos_reservados
    
    db.delete(reserva)
    db.commit()
    return {"ok": True, "mensaje": "Reserva eliminada con éxito."}