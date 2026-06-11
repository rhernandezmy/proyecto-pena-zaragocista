from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import database 
import schemas  # Importamos los esquemas que dejamos listos en el paso anterior

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
    Retorna el listado completo de socios reales de la peña (Pestaña 1).
    Lee dinámicamente el estado de pago de las cuotas a través del usuario web enlazado.
    """
    socios = db.query(models.SocioPena).order_by(models.SocioPena.numero_socio.asc().nullslast()).all()
    
    resultado = []
    for s in socios:
        # Por defecto la cuota estará Pendiente a menos que tenga un usuario web enlazado con cuota pagada
        estado_pago = "Pendiente"
        email_web = "Sin Cuenta Web"
        usuario_id = None
        
        if s.usuario_web:
            usuario_id = s.usuario_web.id
            email_web = s.usuario_web.email
            cuota_actual = next((c for c in s.usuario_web.cuotas if c.ano_ejercicio == 2026), None)
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
            "email_web": email_web,  # Para saber informativamente qué cuenta usa en la web
            "usuario_id": usuario_id,
            "estado_cuota": estado_pago,
            "activo": s.activo
        })
    return resultado


@router.post("/crear-socio", status_code=status.HTTP_201_CREATED)
def admin_crear_socio_pena(socio_in: schemas.SocioPenaCreate, db: Session = Depends(database.get_db)):
    """
    Crea un nuevo socio de la peña de forma puramente física/administrativa.
    Ya no requiere emails obligatorios ni contraseñas temporales por defecto.
    """
    if socio_in.numero_socio:
        numero_existente = db.query(models.SocioPena).filter(models.SocioPena.numero_socio == socio_in.numero_socio).first()
        if numero_existente:
            raise HTTPException(status_code=400, detail="El número de socio ya está asignado.")
            
    if socio_in.dni:
        dni_existente = db.query(models.SocioPena).filter(models.SocioPena.dni == socio_in.dni).first()
        if dni_existente:
            raise HTTPException(status_code=400, detail="El DNI introducido ya pertenece a otro socio.")

    try:
        nuevo_socio = models.SocioPena(**socio_in.model_dump())
        db.add(nuevo_socio)
        db.commit()
        db.refresh(nuevo_socio)
        
        return {"status": "success", "message": "¡Socio de la peña creado correctamente en el libro de registro!"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"FALLO_SISTEMA_BD: {str(e)}")


@router.put("/socios/{socio_id}")
def actualizar_socio_pena(socio_id: int, payload: dict, db: Session = Depends(database.get_db)):
    """
    Modifica los datos de la ficha administrativa del socio.
    """
    socio = db.query(models.SocioPena).filter(models.SocioPena.id == socio_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado en el sistema.")
    
    try:
        if "numero_socio" in payload: socio.numero_socio = payload["numero_socio"]
        if "nombre" in payload: socio.nombre = payload["nombre"]
        if "apellidos" in payload: socio.apellidos = payload["apellidos"]
        if "dni" in payload: socio.dni = payload["dni"]
        if "telefono" in payload: socio.telefono = payload["telefono"]
        if "activo" in payload: socio.activo = payload["activo"]
        
        db.commit()
        return {"status": "success", "message": "¡Ficha de socio modificada correctamente!"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al actualizar persistencia: {str(e)}")


@router.delete("/socios/{socio_id}")
def dar_baja_socio_pena(socio_id: int, db: Session = Depends(database.get_db)):
    """
    Baja lógica de un socio de la peña (activo=False).
    """
    socio = db.query(models.SocioPena).filter(models.SocioPena.id == socio_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="El socio seleccionado no existe.")
    
    try:
        socio.activo = False
        db.commit()
        return {"status": "success", "message": "Socio desactivado del libro de registro correctamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"No se pudo procesar la baja en BD: {str(e)}")


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