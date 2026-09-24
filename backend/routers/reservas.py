from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import models, schemas
from database import get_db

router = APIRouter(prefix="", tags=["Reservas"])

# =========================================================================
# 1. OBTENER TODAS LAS RESERVAS
# =========================================================================
@router.get("")
def obtener_reservas(db: Session = Depends(get_db)):
    """
    Retorna todas las reservas mapeando los datos del usuario y/o socio interno
    para asegurar la compatibilidad con el frontend sin fallos de objeto nulo.
    """
    reservas = db.query(models.Reserva).all()
    resultado = []
    
    for r in reservas:
        socio_nombre = "Socio Desconocido"
        socio_email = "Sin Email"
        
        if r.usuario:
            socio_email = r.usuario.email
            if r.usuario.socio_interno:
                socio_nombre = f"{r.usuario.socio_interno.nombre} {r.usuario.socio_interno.apellidos}".strip()
            else:
                socio_nombre = r.usuario.username

        resultado.append({
            "id": r.id,
            "viaje_id": r.viaje_id,
            "usuario_id": r.usuario_id,
            "socio_nombre": socio_nombre,
            "socio_email": socio_email,
            "asientos_reservados": r.asientos_reservados,
            "tipo_reserva": r.tipo_reserva,
            "motivo_evento": r.motivo_evento if r.motivo_evento else "Sin motivo especificado",
            "estado_solicitud": r.estado_solicitud,
            "fecha_solicitada": r.fecha_solicitada.isoformat() if r.fecha_solicitada else None
        })
    return resultado


# =========================================================================
# 2. CREAR NUEVA RESERVA (Viajes, Coche Compartido y Local)
# =========================================================================
@router.post("")
def crear_reserva(reserva: schemas.ReservaCrear, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == reserva.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    motivo_texto = reserva.motivo_evento or ""
    es_oferta_coche = "Ofrece" in motivo_texto or reserva.tipo_reserva == "Coche"
    es_viaje = reserva.tipo_reserva in ["Viaje", "Coche", "Logistica"] or es_oferta_coche or bool(reserva.viaje_id)

    if es_viaje:
        if not reserva.viaje_id:
            raise HTTPException(status_code=400, detail="El viaje_id es obligatorio para reservas de viajes o vehículos.")
        
        plazas_ofrecidas = reserva.asientos_reservados or 4
        viaje = db.query(models.Viaje).filter(models.Viaje.id == reserva.viaje_id).first()
        
        fecha_dt = datetime.now()
        if reserva.fecha_solicitada:
            try:
                fecha_clean = str(reserva.fecha_solicitada).split("T")[0]
                fecha_dt = datetime.strptime(fecha_clean, "%Y-%m-%d")
            except Exception:
                fecha_dt = datetime.now()

        # Si el viaje NO existe en la BD, lo insertamos dinámicamente
        if not viaje:
            rival_nombre = "Partido Fuera"
            if "ir a ver al" in motivo_texto:
                rival_nombre = motivo_texto.split("ir a ver al")[-1].strip()
            elif "ir a ver" in motivo_texto:
                rival_nombre = motivo_texto.split("ir a ver")[-1].strip()
            elif "contra" in motivo_texto:
                rival_nombre = motivo_texto.split("contra")[-1].strip()

            rival_nombre = rival_nombre.rstrip(".")

            # Nombre real del usuario logueado
            nombre_real_socio = usuario.username
            if usuario.socio_interno and usuario.socio_interno.nombre:
                nombre_real_socio = f"{usuario.socio_interno.nombre} {usuario.socio_interno.apellidos}".strip()

            viaje = models.Viaje(
                id=reserva.viaje_id,
                partido_id=reserva.viaje_id,
                partido_api_id=reserva.viaje_id,
                destino=f"vs {rival_nombre}",
                rival=rival_nombre,
                fecha_partido=fecha_dt,
                tipo_transporte="Coche",
                plazas_totales=plazas_ofrecidas,
                plazas_disponibles=plazas_ofrecidas,
                email_conductor=nombre_real_socio,  # 👈 Guardamos directamente el Nombre Completo del Socio
                precio=0.0
            )
            db.add(viaje)
            db.commit()
            db.refresh(viaje)

        else:
            if es_oferta_coche:
                viaje.plazas_disponibles += plazas_ofrecidas
            else:
                if viaje.plazas_disponibles < reserva.asientos_reservados:
                    raise HTTPException(status_code=400, detail="Plazas insuficientes.")
                viaje.plazas_disponibles -= reserva.asientos_reservados
            db.commit()

        estado_inicial = "Aprobada"
    else:
        estado_inicial = "Pendiente"

    fecha_reserva_dt = datetime.now()
    if reserva.fecha_solicitada:
        try:
            fecha_clean = str(reserva.fecha_solicitada).split("T")[0]
            fecha_reserva_dt = datetime.strptime(fecha_clean, "%Y-%m-%d")
        except Exception:
            pass

    nueva_reserva = models.Reserva(
        usuario_id=reserva.usuario_id,
        viaje_id=reserva.viaje_id,
        asientos_reservados=reserva.asientos_reservados,
        tipo_reserva="Viaje" if es_viaje else "Local",
        motivo_evento=reserva.motivo_evento,
        fecha_solicitada=fecha_reserva_dt,
        estado_solicitud=estado_inicial
    )
    
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)

    return {"ok": True, "reserva_id": nueva_reserva.id, "viaje_id": reserva.viaje_id}


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
# 5. CANCELAR / ELIMINAR RESERVA (LÓGICA DE BORRADO SEGURO)
# =========================================================================
@router.delete("/{reserva_id}")
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail=f"Reserva con ID {reserva_id} no encontrada.")
    
    # Si la reserva tenía un viaje/coche asociado
    if reserva.viaje_id:
        viaje = db.query(models.Viaje).filter(models.Viaje.id == reserva.viaje_id).first()
        if viaje:
            es_oferta_coche = (reserva.tipo_reserva == "Coche") or (reserva.motivo_evento and "Ofrece" in reserva.motivo_evento)
            if es_oferta_coche:
                # Si se cancela la oferta del coche, eliminamos la expedición/viaje asociada al coche
                db.delete(viaje)
            else:
                viaje.plazas_disponibles += (reserva.asientos_reservados or 1)

    db.delete(reserva)
    db.commit()
    return {"ok": True, "mensaje": "Reserva eliminada con éxito."}