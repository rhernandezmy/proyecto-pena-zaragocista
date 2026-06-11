from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

# Dejamos el prefijo vacío porque main.py ya le añade "/reservas"
router = APIRouter(prefix="", tags=["Reservas"])

# =========================================================================
# 1. OBTENER TODAS LAS RESERVAS
# =========================================================================
@router.get("")
def obtener_reservas(db: Session = Depends(get_db)):
    return db.query(models.Reserva).all()


# =========================================================================
# 2. CREAR NUEVA RESERVA (Adaptado para Viajes y Local)
# =========================================================================
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
        
        # 🚗 LÓGICA DE COCHE COMPARTIDO: Si el socio OFRECE su coche
        if reserva.motivo_evento and "Ofrece" in reserva.motivo_evento:
            # Extraemos el número de plazas del texto (ej: "Ofrece vehículo con 4 plazas." -> extrae el 4)
            try:
                palabras = reserva.motivo_evento.split()
                # Buscamos la posición de la palabra "plazas" y miramos el número anterior
                idx = palabras.index("plazas.") if "plazas." in palabras else palabras.index("plazas")
                plazas_ofrecidas = int(palabras[idx - 1])
            except (ValueError, IndexError):
                plazas_ofrecidas = 4 # Valor por defecto seguro si falla el texto
            
            # Al ofrecer un coche, sumamos las nuevas plazas libres al total del viaje
            viaje.plazas_disponibles += plazas_ofrecidas
            
        # 🚌 LÓGICA DE AUTOBÚS: Si es una reserva normal de plaza
        else:
            if viaje.plazas_disponibles < reserva.asientos_reservados:
                raise HTTPException(status_code=400, detail=f"Plazas insuficientes. Quedan {viaje.plazas_disponibles}.")
            
            # Restamos la plaza que va a ocupar el socio en el autobús
            viaje.plazas_disponibles -= reserva.asientos_reservados
        
        # Las reservas de viaje se aprueban automáticamente al tramitarse
        estado_inicial = "Aprobada"

    # CASO B: Es una solicitud para usar el LOCAL de la peña
    else:
        if not reserva.motivo_evento:
            raise HTTPException(status_code=400, detail="Debes especificar el motivo para reservar el local.")
        
        # Las solicitudes del local se quedan en "Pendiente" hasta que el admin las revise
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


# =========================================================================
# 3. OBTENER VIAJEROS POR ID DE VIAJE
# =========================================================================
@router.get("/viaje/{viaje_id}")
def obtener_viajeros_por_viaje(viaje_id: int, db: Session = Depends(get_db)):
    return db.query(models.Reserva).filter(models.Reserva.viaje_id == viaje_id).all()


# =========================================================================
# 4. RESOLVER RESERVA DEL LOCAL
# =========================================================================
@router.patch("/{reserva_id}/resolucion")
def resolver_reserva_local(reserva_id: int, estado: str, db: Session = Depends(get_db)):
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


# =========================================================================
# 5. CANCELAR / ELIMINAR RESERVA
# =========================================================================
@router.delete("/{reserva_id}")
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")
    
    # Si cancelamos un viaje, devolvemos el estado correcto de las plazas
    if reserva.tipo_reserva == "Viaje" and reserva.viaje_id:
        viaje = db.query(models.Viaje).filter(models.Viaje.id == reserva.viaje_id).first()
        if viaje:
            if reserva.motivo_evento and "Ofrece" in reserva.motivo_evento:
                # Si el socio retira su coche, restamos esas plazas del viaje general
                try:
                    palabras = reserva.motivo_evento.split()
                    idx = palabras.index("plazas.") if "plazas." in palabras else palabras.index("plazas")
                    plazas_ofrecidas = int(palabras[idx - 1])
                except (ValueError, IndexError):
                    plazas_ofrecidas = 4
                viaje.plazas_disponibles -= plazas_ofrecidas
            else:
                # Si era una reserva ordinaria, devolvemos su asiento
                viaje.plazas_disponibles += reserva.asientos_reservados
    
    db.delete(reserva)
    db.commit()
    return {"ok": True, "mensaje": "Reserva eliminada con éxito."}