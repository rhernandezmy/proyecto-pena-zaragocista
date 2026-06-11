from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import database 

router = APIRouter(
    prefix="", 
    tags=["Usuarios y Socios"]
)

# -------------------------------------------------------------------------
# CORRECCIÓN GET: Ahora lee el estado de pago REAL de la tabla Cuotas
# -------------------------------------------------------------------------
@router.get("/socios", response_model=List[dict])
def obtener_todos_los_socios(db: Session = Depends(database.get_db)):
    """
    Retorna el listado completo de socios leyendo dinámicamente sus cuotas.
    """
    usuarios = db.query(models.Usuario).filter(models.Usuario.rol.ilike("socio")).all()
    
    resultado = []
    for u in usuarios:
        # Buscamos si tiene cuota para el ejercicio actual (2026)
        cuota_actual = next((c for c in u.cuotas if c.ano_ejercicio == 2026), None)
        estado_pago = cuota_actual.estado_pago if cuota_actual else "Pendiente"

        resultado.append({
            "id": u.id,
            "nombre": u.nombre,
            "apellidos": u.apellidos,
            "nombre_completo": f"{u.nombre} {u.apellidos}",
            "email": u.email,
            "telefono": getattr(u, "telefono", "Sin Teléfono") if hasattr(u, "telefono") else "600000000",
            "estado_cuota": estado_pago,
            "rol": u.rol,
            "activo": u.activo
        })
    return resultado


# -------------------------------------------------------------------------
# POST: Registro / Alta desde el Panel del Admin
# -------------------------------------------------------------------------
@router.post("/crear-socio", status_code=status.HTTP_201_CREATED)
def admin_pre_registrar_socio(payload: dict, db: Session = Depends(database.get_db)):
    email_existente = db.query(models.Usuario).filter(models.Usuario.email == payload.get("email")).first()
    if email_existente:
        raise HTTPException(
            status_code=400, 
            detail="El correo electrónico ya corresponde a un socio dado de alta."
        )
    
    try:
        nuevo_usuario = models.Usuario(
            nombre=payload.get("nombre"),
            apellidos=payload.get("apellidos"),
            email=payload.get("email"),
            password_hash="PENDIENTE_ACTIVACION",
            rol="socio",
            activo=True
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        # Generamos automáticamente su registro de cuota 2026 en estado 'Pendiente'
        nueva_cuota = models.Cuota(usuario_id=nuevo_usuario.id, ano_ejercicio=2026, estado_pago="Pendiente")
        db.add(nueva_cuota)
        db.commit()

        return {"status": "success", "message": "¡Socio guardado correctamente con su cuota inicial!"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"FALLO_SISTEMA_BD: {str(e)}")


# -------------------------------------------------------------------------
# NUEVO ENDPOINT PUT: Para que el Admin y el Socio puedan MODIFICAR de verdad
# -------------------------------------------------------------------------
@router.put("/socios/{socio_id}")
def actualizar_socio(socio_id: int, payload: dict, db: Session = Depends(database.get_db)):
    """
    Modifica los datos de un socio y persiste los cambios de forma inmediata.
    """
    socio = db.query(models.Usuario).filter(models.Usuario.id == socio_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado en el sistema.")
    
    try:
        # Actualizamos solo los campos que vengan en el payload de forma segura
        if "nombre" in payload: socio.nombre = payload["nombre"]
        if "apellidos" in payload: socio.apellidos = payload["apellidos"]
        if "email" in payload: socio.email = payload["email"]
        if "rol" in payload: socio.rol = payload["rol"]
        
        # Guardado imperativo en la Base de Datos
        db.commit()
        db.refresh(socio)
        return {"status": "success", "message": "¡Socio actualizado correctamente en la base de datos!"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al actualizar persistencia: {str(e)}")


# -------------------------------------------------------------------------
# ENDPOINT OPTIMIZADO: Baja lógica (Desactivación) para conservar datos
# -------------------------------------------------------------------------
@router.delete("/socios/{socio_id}")
def dar_baja_socio(socio_id: int, db: Session = Depends(database.get_db)):
    """
    Desactiva al socio del sistema (activo=False) para preservar su historial de cuotas y pagos.
    """
    socio = db.query(models.Usuario).filter(models.Usuario.id == socio_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="El socio seleccionado no existe.")
    
    try:
        # En lugar de db.delete(socio), cambiamos su estado a inactivo
        socio.activo = False
        db.commit() # Guardamos el cambio en caliente
        
        return {"status": "success", "message": "Socio dado de baja (desactivado) correctamente. Datos preservados."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"No se pudo procesar la baja en BD: {str(e)}")