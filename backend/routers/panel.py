from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models 

router = APIRouter(tags=["Panel"])


# 1. VISTA SOCIO: Obtener datos individuales de un socio por Email (¡Blindado!)
@router.get("/socio/{email}")
def get_socio_panel_data(email: str, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    # Extraemos el nombre real si tiene ficha de socio, o ponemos uno de cortesía si es admin suelto
    nombre_completo = "Administrador"
    cuotas_lista = []
    
    if usuario.socio_interno:
        nombre_completo = f"{usuario.socio_interno.nombre} {usuario.socio_interno.apellidos}"
        cuotas_lista = [{"ano": c.ano_ejercicio, "estado": c.estado_pago} for c in usuario.socio_interno.cuotas]
    elif usuario.rol.lower() == "admin":
        nombre_completo = "Administrador de la Peña"

    return {
        "id": usuario.id,
        "nombre": nombre_completo,
        "rol": usuario.rol,
        "cuotas": cuotas_lista,
        "reservas": [
            {
                "id_reserva": r.id,
                "tipo": r.tipo_reserva,
                "destino": r.viaje.destino if r.viaje else "Uso de la Sede Local", 
                "asientos": r.asientos_reservados,
                "estado": r.estado_solicitud,
                "motivo": r.motivo_evento
            } for r in usuario.reservas
        ]
    }


# 2. VISTA ADMIN: Obtener TODOS los datos globales de la peña (¡Corregido y Cruzado!)
@router.get("/admin/global-data")
def get_admin_global_data(db: Session = Depends(get_db)):
    """
    Recopila la información basándose en el Libro de Socios Reales 
    para alimentar las tablas y estadísticas globales del Administrador.
    """
    # A. Consultamos la tabla real de socios físicos (SocioPena) para el listado global
    todos_los_socios = db.query(models.SocioPena).all()
    lista_socios = []
    
    for s in todos_los_socios:
        # Buscamos de forma dinámica si tiene cuota en el año actual (2026) en base a sus cuotas
        cuota_actual = next((c for c in s.cuotas if c.ano_ejercicio == 2026), None)
        estado_cuota = cuota_actual.estado_pago if cuota_actual else "Pendiente"
        
        # Sacamos el email de la cuenta web vinculada si existe
        email_real = s.usuario_web.email if s.usuario_web else "Sin cuenta web"
        rol_real = s.usuario_web.rol if s.usuario_web else "Socio"
        
        lista_socios.append({
            "id": s.id,
            "nombre_completo": f"{s.nombre} {s.apellidos}",
            "email": email_real,
            "telefono": s.telefono if s.telefono else "N/A",
            "rol": rol_real,
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

    # C. Listado de solicitudes de uso exclusivas del local (Mapeo seguro de nombres)
    solicitudes_local = db.query(models.Reserva).filter(models.Reserva.tipo_reserva == "Local").all()
    lista_local = []
    for r in solicitudes_local:
        # Extraemos el nombre del solicitante de manera segura buscando su ficha física
        nombre_solicitante = "Usuario Web"
        if r.usuario:
            if r.usuario.socio_interno:
                nombre_solicitante = f"{r.usuario.socio_interno.nombre} {r.usuario.socio_interno.apellidos}"
            else:
                nombre_solicitante = r.usuario.email

        lista_local.append({
            "id_reserva": r.id,
            "socio": f"{nombre_solicitante} (#{r.usuario_id})",
            "fecha_solicitada": "24/06/2026",
            "motivo": r.motivo_evento,
            "estado": r.estado_solicitud
        })

    return {
        "socios": lista_socios,
        "viajes": lista_viajes,
        "reservas_local": lista_local
    }


# 3. CONMUTACIÓN DE ROL: Cambiar el rol de una cuenta de acceso web de forma segura
@router.patch("/usuarios/{usuario_id}/cambiar-rol")
def cambiar_rol_usuario(usuario_id: int, nuevo_rol: str, db: Session = Depends(get_db)):
    if nuevo_rol.capitalize() not in ["Socio", "Admin"]:
        raise HTTPException(status_code=400, detail="El rol especificado no es válido.")
        
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        
    usuario.rol = nuevo_rol.capitalize()
    db.commit()
    
    nombre_log = usuario.socio_interno.nombre if usuario.socio_interno else usuario.email
    return {"ok": True, "mensaje": f"Rol de {nombre_log} cambiado a {usuario.rol}."}