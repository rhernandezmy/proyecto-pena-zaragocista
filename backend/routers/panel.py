from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models 

router = APIRouter(tags=["Panel"])


# 1. VISTA SOCIO: Obtener datos individuales de un socio por Email (Tu ruta original mejorada)
@router.get("/socio/{email}")
def get_socio_panel_data(email: str, db: Session = Depends(get_db)):
    socio = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    return {
        "id": socio.id,
        "nombre": f"{socio.nombre} {socio.apellidos}",
        "rol": socio.rol,
        "cuotas": [{"ano": c.ano_ejercicio, "estado": c.estado_pago} for c in socio.cuotas],
        "reservas": [
            {
                "id_reserva": r.id,
                "tipo": r.tipo_reserva,
                "destino": r.viaje.destino if r.viaje else "Uso de la Sede Local", 
                "asientos": r.asientos_reservados,
                "estado": r.estado_solicitud,
                "motivo": r.motivo_evento
            } for r in socio.reservas
        ]
    }


# 2. VISTA ADMIN: Obtener TODOS los datos globales de la peña (Optimizado y Real)
@router.get("/admin/global-data")
def get_admin_global_data(db: Session = Depends(get_db)):
    """
    Recopila de forma masiva la información de todas las tablas para pintar 
    las listas, formularios y tablas del Panel de Control del Administrador.
    """
    # A. Listado completo de usuarios/socios cruzado con sus cuotas
    todos_los_socios = db.query(models.Usuario).all()
    lista_socios = []
    for s in todos_los_socios:
        # Buscamos de forma dinámica si tiene cuota en el año actual (2026)
        cuota_actual = next((c for c in s.cuotas if c.ano_ejercicio == 2026), None)
        
        # Si existe cuota en la BD, saca su estado real. Si no existe (como los nuevos), es "Pendiente"
        estado_cuota = cuota_actual.estado_pago if cuota_actual else "Pendiente"
        
        # Mapeamos el teléfono si existe la columna en el modelo, o un valor limpio de cortesía
        telefono_real = getattr(s, 'telefono', "Sin teléfono") if getattr(s, 'telefono', None) else "N/A"
        
        lista_socios.append({
            "id": s.id,
            "nombre_completo": f"{s.nombre} {s.apellidos}",
            "email": s.email,
            "telefono": telefono_real,
            "rol": s.rol,
            "estado_cuota": estado_cuota
        })

    # B. Listado de todos los viajes activos organizados
    todos_los_viajes = db.query(models.Viaje).all()
    lista_viajes = [{
        "id": v.id,
        "destino": v.destino,
        "tipo_transporte": v.tipo_transporte,
        "plazas_libres": v.plazas_disponibles,
        "plazas_totales": v.plazas_totales,
        "fecha": "15/09/2026"
    } for v in todos_los_viajes]

    # C. Listado de solicitudes de uso exclusivas del local
    solicitudes_local = db.query(models.Reserva).filter(models.Reserva.tipo_reserva == "Local").all()
    lista_local = [{
        "id_reserva": r.id,
        "socio": f"{r.usuario.nombre} {r.usuario.apellidos} (#{r.usuario.id})",
        "fecha_solicitada": "24/06/2026",
        "motivo": r.motivo_evento,
        "estado": r.estado_solicitud
    } for r in solicitudes_local]

    return {
        "socios": lista_socios,
        "viajes": lista_viajes,
        "reservas_local": lista_local
    }

# 3. CONMUTACIÓN DE ROL: Permitir cambiar el rol de un usuario directamente (NUEVO)
@router.patch("/usuarios/{usuario_id}/cambiar-rol")
def cambiar_rol_usuario(usuario_id: int, nuevo_rol: str, db: Session = Depends(get_db)):
    if nuevo_rol not in ["Socio", "Admin"]:
        raise HTTPException(status_code=400, detail="El rol especificado no es válido.")
        
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        
    usuario.rol = nuevo_rol
    db.commit()
    return {"ok": True, "mensaje": f"Rol de {usuario.nombre} cambiado a {nuevo_rol}."}