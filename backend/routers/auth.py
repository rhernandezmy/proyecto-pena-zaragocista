from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import bcrypt
import models, database
from pydantic import BaseModel, EmailStr

router = APIRouter()

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login(login_data: LoginSchema, db: Session = Depends(database.get_db)):
    print(f"🔑 Intento de login para: {login_data.email}")
    
    # Buscamos al socio en la base de datos
    socio = db.query(models.Usuario).filter(models.Usuario.email == login_data.email).first()
    
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="El correo electrónico no está registrado"
        )

    # Verificación segura de la contraseña con bcrypt
    if not bcrypt.checkpw(login_data.password.encode('utf-8'), socio.password_hash.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Contraseña incorrecta"
        )
    
    if not socio.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Esta cuenta de socio ha sido desactivada temporalmente"
        )
    
    # Enviamos los datos necesarios para que el JavaScript controle los botones de cambio de rol
    return {
        "id": socio.id,
        "nombre": socio.nombre,
        "apellidos": socio.apellidos,
        "email": socio.email,
        "rol": socio.rol, # Retorna "Socio" o "Admin"
        "status": "success"
    }

# =========================================================================
# 🛡️ GUARDIÁN DE SEGURIDAD (Para proteger las rutas críticas en el Bloque C)
# =========================================================================
def get_current_admin(usuario_id: int, db: Session = Depends(database.get_db)):
    """
    Función de dependencia que verifica si un usuario concreto es Administrador.
    Bloquea las peticiones si el usuario no tiene permisos.
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario or usuario.rol != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de Administrador."
        )
    return usuario