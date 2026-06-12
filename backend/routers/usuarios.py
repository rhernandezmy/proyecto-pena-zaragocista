from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import database 
import schemas
import datetime # Importado para hacer dinámica la comprobación de cuotas

router = APIRouter(
    prefix="", 
    tags=["Usuarios y Socios"]
)

# =========================================================================
# 👥 PESTAÑA 1: GESTIÓN DE SOCIOS DE LA PEÑA (Fichas Administrativas)
# =========================================================================

@router.get("/socios", response_model=List[dict])
def obtener_todos_los_socios(db: Session = Depends(database.get_db)):
    """
    Retorna el listado completo de socios. 
    Usa el año actual para determinar el estado de la cuota.
    """
    año_actual = datetime.datetime.now().year
    socios = db.query(models.SocioPena).order_by(models.SocioPena.numero_socio.asc().nullslast()).all()
    
    resultado = []
    for s in socios:
        estado_pago = "Pendiente"
        email_web = "Sin Cuenta Web"
        usuario_id = None
        
        if s.usuario_web:
            usuario_id = s.usuario_web.id
            email_web = s.usuario_web.email
            
            cuotas_lista = getattr(s.usuario_web, 'cuotas', [])
            if cuotas_lista:
                cuota_actual = next((c for c in cuotas_lista if c.ano_ejercicio == año_actual), None)
                if cuota_actual:
                    estado_pago = cuota_actual.estado_pago

        resultado.append({
            "id": s.id,
            "numero_socio": s.numero_socio,
            "nombre": s.nombre,
            "apellidos": s.apellidos,
            "nombre_completo": f"{s.nombre} {s.apellidos}",
            "dni": s.dni if s.dni else "Sin DNI",
            "telefono": s.telefono if s.telefono else "Sin Teléfono",
            "email_web": email_web,
            "usuario_id": usuario_id,
            "estado_cuota": estado_pago,
            "activo": s.activo
        })
    return resultado

@router.post("/crear-socio", status_code=status.HTTP_201_CREATED)
def admin_crear_socio_pena(socio_in: schemas.SocioPenaCreate, db: Session = Depends(database.get_db)):
    if socio_in.numero_socio:
        if db.query(models.SocioPena).filter(models.SocioPena.numero_socio == socio_in.numero_socio).first():
            raise HTTPException(status_code=400, detail="El número de socio ya está asignado.")
            
    if socio_in.dni and db.query(models.SocioPena).filter(models.SocioPena.dni == socio_in.dni).first():
        raise HTTPException(status_code=400, detail="El DNI ya pertenece a otro socio.")

    try:
        nuevo_socio = models.SocioPena(**socio_in.model_dump())
        db.add(nuevo_socio)
        db.commit()
        return {"status": "success", "message": "Socio creado correctamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/socios/{socio_id}")
def actualizar_socio_pena(socio_id: int, payload: dict, db: Session = Depends(database.get_db)):
    socio = db.query(models.SocioPena).filter(models.SocioPena.id == socio_id).first()
    if not socio: raise HTTPException(status_code=404, detail="Socio no encontrado.")
    
    try:
        for key, value in payload.items():
            if hasattr(socio, key): setattr(socio, key, value)
        db.commit()
        return {"status": "success", "message": "Ficha actualizada."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/socios/{socio_id}")
def dar_baja_socio_pena(socio_id: int, db: Session = Depends(database.get_db)):
    """
    ELIMINAR = DESACTIVAR (Baja lógica).
    Mantiene todos los datos para contabilidad histórica.
    """
    socio = db.query(models.SocioPena).filter(models.SocioPena.id == socio_id).first()
    if not socio: raise HTTPException(status_code=404, detail="Socio no existe.")
    
    try:
        socio.activo = False
        if socio.usuario_web:
            socio.usuario_web.activo = False
        db.commit()
        return {"status": "success", "message": "Socio dado de baja (desactivado) para contabilidad."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/socios/{socio_id}/destruir-total")
def eliminar_fisicamente_socio_pena(socio_id: int, payload: dict, db: Session = Depends(database.get_db)):
    """
    Solo para uso interno técnico. Requiere API_TOKEN.
    """
    import os
    if payload.get("codigo_seguridad") != os.getenv("API_TOKEN"):
        raise HTTPException(status_code=401, detail="Autorización denegada.")
        
    socio = db.query(models.SocioPena).filter(models.SocioPena.id == socio_id).first()
    if not socio: raise HTTPException(status_code=404, detail="No existe.")
    
    try:
        if socio.usuario_web:
            db.query(models.Cuota).filter(models.Cuota.usuario_id == socio.usuario_web.id).delete()
            db.query(models.Vehiculo).filter(models.Vehiculo.usuario_id == socio.usuario_web.id).delete()
            db.query(models.Reserva).filter(models.Reserva.usuario_id == socio.usuario_web.id).delete()
            db.delete(socio.usuario_web)
        db.delete(socio)
        db.commit()
        return {"status": "success", "message": "Registro destruido físicamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================================
# 🌐 PESTAÑA 2: GESTIÓN DE USUARIOS WEB (Cuentas y Accesos Online)
# =========================================================================

@router.get("/usuarios-web", response_model=List[schemas.UsuarioWebResponse])
def listar_usuarios_web(db: Session = Depends(database.get_db)):
    """
    Retorna el listado de todas las personas registradas en la plataforma web (Pestaña 2).
    Incluye dinámicamente si están vinculadas a un socio físico o no.
    """
    return db.query(models.Usuario).order_by(models.Usuario.fecha_registro.desc()).all()


@router.put("/usuarios-web/{usuario_id}/estado")
def cambiar_estado_acceso_web(usuario_id: int, payload: dict, db: Session = Depends(database.get_db)):
    """
    Permite banear o activar los accesos web de un usuario (activo: true/false).
    No borra al socio de la peña, solo le quita el login.
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Cuenta web no encontrada.")
    
    if "activo" not in payload:
        raise HTTPException(status_code=400, detail="Falta el campo 'activo' en la solicitud.")
        
    try:
        usuario.activo = payload["activo"]
        db.commit()
        estado = "habilitado" if usuario.activo else "deshabilitado"
        return {"status": "success", "message": f"Acceso web {estado} correctamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en el sistema: {str(e)}")


@router.put("/usuarios-web/{usuario_id}/vincular", response_model=schemas.UsuarioWebResponse)
def vincular_cuenta_web_a_socio(usuario_id: int, req: schemas.VincularSocioRequest, db: Session = Depends(database.get_db)):
    """
    Endpoint estratégico: Vincula un email registrado en la web con un Socio físico existente.
    Si se pasa 'socio_pena_id': null, se desvincula la cuenta.
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Cuenta web no encontrada.")
        
    if req.socio_pena_id:
        socio = db.query(models.SocioPena).filter(models.SocioPena.id == req.socio_pena_id).first()
        if not socio:
            raise HTTPException(status_code=404, detail="La ficha de socio físico seleccionada no existe.")
            
    try:
        usuario.socio_pena_id = req.socio_pena_id
        db.commit()
        db.refresh(usuario)
        return usuario
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar el vínculo: {str(e)}")