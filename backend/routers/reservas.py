from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import models, schemas
from database import get_db

# Dejamos el prefijo vacío porque main.py ya le añade "/reservas"
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
            # Comprobamos si la cuenta web está vinculada a una ficha de SocioPena
            if r.usuario.socio_interno:
                socio_nombre = f"{r.usuario.socio_interno.nombre} {r.usuario.socio_interno.apellidos}".strip()
            else:
                # Si es un usuario web sin ficha de socio asociada aún, mostramos su username
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
# 2. CREAR NUEVA RESERVA (Viajes y Local)
# =========================================================================
@router.post("")
def crear_reserva(reserva: schemas.ReservaCrear, db: Session = Depends(get_db)):
    # Validar que el usuario existe obligatoriamente en usuarios_web
    usuario = db.query(models.Usuario).filter(models.Usuario.id == reserva.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # CASO A: Reserva para VIAJE On Tour
    if reserva.tipo_reserva == "Viaje":
        if not reserva.viaje_id:
            raise HTTPException(status_code=400, detail="El viaje_id es obligatorio para reservas de tipo 'Viaje'.")
            
        viaje = db.query(models.Viaje).filter(models.Viaje.id == reserva.viaje_id).first()
        if not viaje:
            raise HTTPException(status_code=404, detail="Viaje no encontrado.")
        
        # Lógica de coche compartido: Si ofrece plazas
        if reserva.motivo_evento and "Ofrece" in reserva.motivo_evento:
            try:
                palabras = reserva.motivo_evento.split()
                idx = palabras.index("plazas.") if "plazas." in palabras else palabras.index("plazas")
                plazas_ofrecidas = int(palabras[idx - 1])
            except (ValueError, IndexError):
                plazas_ofrecidas = 4
            
            viaje.plazas_disponibles += plazas_ofrecidas
            
        # Lógica de reserva normal
        else:
            if viaje.plazas_disponibles < reserva.asientos_reservados:
                raise HTTPException(status_code=400, detail=f"Plazas insuficientes. Quedan {viaje.plazas_disponibles}.")
            
            viaje.plazas_disponibles -= reserva.asientos_reservados
        
        estado_inicial = "Aprobada"

    # CASO B: Solicitud para usar el LOCAL
    else:
        if not reserva.motivo_evento:
            raise HTTPException(status_code=400, detail="Debes especificar el motivo para reservar el local.")
        
        estado_inicial = "Pendiente"

    # 🔧 PROCESAMIENTO DE LA FECHA SELECCIONADA
    datos_reserva = reserva.model_dump()
    
    if reserva.fecha_solicitada:
        try:
            # Extrae la parte YYYY-MM-DD y la convierte a objeto datetime
            fecha_str = str(reserva.fecha_solicitada).split("T")[0]
            datos_reserva["fecha_solicitada"] = datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD")

    nueva_reserva = models.Reserva(
        **datos_reserva,
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
    
    if reserva.tipo_reserva == "Viaje" and reserva.viaje_id:
        viaje = db.query(models.Viaje).filter(models.Viaje.id == reserva.viaje_id).first()
        if viaje:
            if reserva.motivo_evento and "Ofrece" in reserva.motivo_evento:
                try:
                    palabras = reserva.motivo_evento.split()
                    idx = palabras.index("plazas.") if "plazas." in palabras else palabras.index("plazas")
                    plazas_ofrecidas = int(palabras[idx - 1])
                except (ValueError, IndexError):
                    plazas_ofrecidas = 4
                viaje.plazas_disponibles -= plazas_ofrecidas
            else:
                viaje.plazas_disponibles += reserva.asientos_reservados
    
    db.delete(reserva)
    db.commit()
    return {"ok": True, "mensaje": "Reserva eliminada con éxito."}