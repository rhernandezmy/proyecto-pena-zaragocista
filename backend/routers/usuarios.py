from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import database 

# Definimos el router con un único prefijo limpio
router = APIRouter(
    prefix="", 
    tags=["Usuarios y Socios"]
)

# -------------------------------------------------------------------------
# CORRECCIÓN GET: Dejamos la ruta limpia para que no se duplique
# Ahora en Swagger se leerá limpiamente como: GET /usuarios/socios
# -------------------------------------------------------------------------
@router.get("/socios", response_model=List[dict])
def obtener_todos_los_socios(db: Session = Depends(database.get_db)):
    """
    Retorna el listado completo de socios registrados en el sistema
    para la explotación de datos del Dashboard de Administración.
    """
    usuarios = db.query(models.Usuario).filter(models.Usuario.rol == "socio").all()
    
    # Mapeo defensivo para asegurar que el JSON entregue lo que el frontend necesita
    resultado = []
    for u in usuarios:
        resultado.append({
            "id": u.id,
            "nombre_completo": getattr(u, "nombre_completo", getattr(u, "nombre", "Sin Nombre")),
            "email": u.email,
            "telefono": getattr(u, "telefono", "600000000"),
            "estado_cuota": getattr(u, "estado_cuota", "Pendiente"),
            "rol": u.rol
        })
    return resultado


# ----------------------------------------------------------------=========
# NUEVO ENDPOINT POST: La tubería que le faltaba a tu formulario de la web
# Ahora en Swagger aparecerá en VERDE como: POST /usuarios/crear-socio
# ----------------------------------------------------------------=========
@router.post("/crear-socio", status_code=status.HTTP_201_CREATED)
def admin_pre_registrar_socio(payload: dict, db: Session = Depends(database.get_db)):
    """
    Endpoint final sincronizado al 100% con las columnas reales de PostgreSQL.
    """
    # 1. Control de duplicados usando la columna real 'email'
    email_existente = db.query(models.Usuario).filter(models.Usuario.email == payload.get("email")).first()
    if email_existente:
        raise HTTPException(
            status_code=400, 
            detail="El correo electrónico ya corresponde a un socio dado de alta."
        )
    
    # 2. Inserción con las columnas exactas reveladas por el error de Psycopg2
    try:
        nuevo_usuario = models.Usuario(
            nombre=payload.get("nombre"),
            apellidos=payload.get("apellidos"),
            email=payload.get("email"),
            password_hash="PENDIENTE_ACTIVACION", # Nombre de columna corregido
            rol="socio"
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return {"status": "success", "message": "¡Socio guardado correctamente!"}
        
    except Exception as e:
        db.rollback()
        error_detallado = str(e).replace("\n", " ").replace('"', "'")
        raise HTTPException(
            status_code=400, 
            detail=f"FALLO_SISTEMA_BD: {error_detallado}"
        )