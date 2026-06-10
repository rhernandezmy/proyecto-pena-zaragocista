from fastapi import APIRouter, Depends, HTTPException, status, Header
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
    print(f"🔑 [LOGIN] Intentando entrar con: '{login_data.email}'")
    
    # Buscamos al usuario por su email
    socio = db.query(models.Usuario).filter(models.Usuario.email == login_data.email).first()
    
    if not socio:
        raise HTTPException(status_code=401, detail="El correo electrónico no está registrado")

    # Validamos la contraseña con control de errores para hashes corruptos
    try:
        passwd_bytes = login_data.password.encode('utf-8')
        hash_bytes = socio.password_hash.encode('utf-8') if isinstance(socio.password_hash, str) else socio.password_hash
        
        # Si el hash no empieza por el prefijo de bcrypt, algo fue mal en su inserción
        if not hash_bytes.startswith(b'$2b$') and not hash_bytes.startswith(b'$2a$'):
            raise ValueError("Hash con formato inválido")
            
        es_valida = bcrypt.checkpw(passwd_bytes, hash_bytes)
    except Exception as e:
        print(f"⚠️ [ERROR BCRYPT] El hash de {login_data.email} está corrupto en la DB: {e}")
        raise HTTPException(
            status_code=401, 
            detail="Error de autenticación: El perfil de usuario requiere actualizar sus credenciales."
        )

    if not es_valida:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    print(f"✅ [LOGIN ÉXITO] ¡Bienvenido {socio.nombre}! Rol: {socio.rol}")
    return {
        "id": socio.id,
        "nombre": socio.nombre,
        "apellidos": socio.apellidos,
        "email": socio.email,
        "rol": socio.rol, 
        "status": "success"
    }

class RegistroSchema(BaseModel):
    email: EmailStr
    password: str

@router.post("/registro")
def registrar_socio(registro_data: RegistroSchema, db: Session = Depends(database.get_db)):
    print(f"📝 [REGISTRO] Intentando dar de alta el correo: '{registro_data.email}'")
    
    # 🔍 1. BUSCAMOS SI EL SOCIO YA EXISTE EN LA BASE DE DATOS (Tu lista blanca)
    socio = db.query(models.Usuario).filter(models.Usuario.email == registro_data.email).first()
    
    # 🛡️ 2. SI NO EXISTE: Bloqueamos el acceso (No es peñista autorizado)
    if not socio:
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado: Este correo electrónico no está registrado como socio de la peña."
        )
    
    # 🔐 3. SI EXISTE: Encriptamos la contraseña que ha elegido el usuario en la web
    password_plana = registro_data.password.encode('utf-8')
    salt = bcrypt.gensalt(12)
    nuevo_hash = bcrypt.hashpw(password_plana, salt).decode('utf-8')
    
    # 💾 4. ACTUALIZAMOS SU HASH EN LA BASE DE DATOS
    socio.password_hash = nuevo_hash
    db.commit()
    
    print(f"✅ [REGISTRO ÉXITO] Cuenta activada para {socio.nombre} ({socio.email})")
    return {"status": "success", "message": "Cuenta de socio activada correctamente. Ya puedes iniciar sesión."}

# =========================================================================
# 🛡️ GUARDIÁN DE SEGURIDAD (Para proteger las rutas críticas en el Bloque C)
# =========================================================================
def get_current_admin(x_usuario_id: int = Header(...), db: Session = Depends(database.get_db)):
    """
    El frontend deberá enviar la cabecera 'X-Usuario-Id' en sus peticiones fetch.
    Ejemplo en JS: headers: { "X-Usuario-Id": localStorage.getItem("socio_id") }
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.id == x_usuario_id).first()
    if not usuario or usuario.rol != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de Administrador."
        )
    return usuario