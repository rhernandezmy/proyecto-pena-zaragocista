from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import HTMLResponse # Importamos para dar una respuesta visual bonita
from sqlalchemy.orm import Session
import bcrypt
import models, database
from pydantic import BaseModel, EmailStr
import email_service 

router = APIRouter()

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login(login_data: LoginSchema, db: Session = Depends(database.get_db)):
    print(f"🔑 [LOGIN] Intentando entrar con: '{login_data.email}'")
    
    socio = db.query(models.Usuario).filter(models.Usuario.email == login_data.email).first()
    
    if not socio:
        raise HTTPException(status_code=401, detail="El correo electrónico no está registrado")

    try:
        passwd_bytes = login_data.password.encode('utf-8')
        hash_bytes = socio.password_hash.encode('utf-8') if isinstance(socio.password_hash, str) else socio.password_hash
        
        if not hash_bytes.startswith(b'$2b$') and not hash_bytes.startswith(b'$2a$'):
            raise ValueError("Hash con formato inválido")
            
        es_valida = bcrypt.checkpw(passwd_bytes, hash_bytes)
    except Exception as e:
        print(f"⚠️ [ERROR BCRYPT] El hash de {login_data.email} falló en la DB: {e}")
        raise HTTPException(
            status_code=401, 
            detail="Error de autenticación: El perfil de usuario requiere actualizar sus credenciales."
        )

    if not es_valida:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    if not socio.verificado and socio.rol.lower() != "admin":
        print(f"🚫 [LOGIN BLOQUEADO] '{login_data.email}' intentó acceder sin verificar el correo.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta no verificada: Por favor, confirma tu correo electrónico antes de iniciar sesión."
        )
    
    nombre_usuario = "Administrador"
    apellidos_usuario = "Peña"
    if socio.socio_interno:
        nombre_usuario = socio.socio_interno.nombre
        apellidos_usuario = socio.socio_interno.apellidos
    
    print(f"✅ [LOGIN ÉXITO] ¡Bienvenido {nombre_usuario}! Rol: {socio.rol}")
    
    return {
        "id": socio.id,
        "nombre": nombre_usuario,
        "apellidos": apellidos_usuario,
        "email": socio.email,
        "rol": socio.rol, 
        "status": "success"
    }


class RegistroSchema(BaseModel):
    email: EmailStr
    password: str

@router.post("/registro")
async def registrar_socio(registro_data: RegistroSchema, db: Session = Depends(database.get_db)):
    print(f"📝 [REGISTRO] Validando alta para: '{registro_data.email}'")
    
    socio_existente = db.query(models.SocioPena).filter(models.SocioPena.email == registro_data.email).first()
    
    if not socio_existente:
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado: Este correo electrónico no consta en la lista oficial de socios de la peña."
        )
    
    usuario_web = db.query(models.Usuario).filter(models.Usuario.email == registro_data.email).first()
    
    if usuario_web:
        raise HTTPException(
            status_code=409, 
            detail="Usuario ya registrado: Este perfil ya está activo. Ve al Área Privada para iniciar sesión."
        )
    
    password_plana = registro_data.password.encode('utf-8')
    salt = bcrypt.gensalt(12)
    nuevo_hash = bcrypt.hashpw(password_plana, salt).decode('utf-8')
    
    username_automatico = registro_data.email.split("@")[0]
    
    nuevo_usuario = models.Usuario(
        username=username_automatico,
        email=registro_data.email,
        password_hash=nuevo_hash,
        rol="Socio",
        activo=True,
        verificado=False,  
        socio_pena_id=socio_existente.id
    )
    
    try:
        db.add(nuevo_usuario)
        db.commit()
        print(f"✅ [ÉXITO] Cuenta web creada (pendiente de verificación) para {socio_existente.nombre}")
        
        await email_service.enviar_correo_verificacion(registro_data.email, username_automatico)
        
        return {
            "status": "success", 
            "message": "¡Cuenta creada con éxito! Te hemos enviado un correo de confirmación."
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ [ERROR DB] Error al insertar en usuarios_web: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al procesar el alta. Por favor, inténtalo más tarde."
        )

# =====================================================================
# 🆕 NUEVO ENDPOINT: VERIFICACIÓN DE CORREO ELECTRÓNICO
# =====================================================================
@router.get("/verificar", response_class=HTMLResponse)
def verificar_cuenta(email: str, db: Session = Depends(database.get_db)):
    print(f"🔍 [VERIFICACIÓN] Procesando enlace para email: '{email}'")
    
    # Buscamos al usuario en la base de datos
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    
    if not usuario:
        return """
        <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px; background-color: #f0f4f8;">
                <h2 style="color: #da2a1d;">❌ Error de verificación</h2>
                <p>El enlace no es válido o el usuario no existe en el sistema.</p>
                <a href="http://localhost:5500/index.html" style="color: #003da5; font-weight: bold;">Volver al inicio</a>
            </body>
        </html>
        """
        
    if usuario.verificado:
        return """
        <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px; background-color: #f0f4f8;">
                <h2 style="color: #003da5;">ℹ️ Cuenta ya activa</h2>
                <p>Tu cuenta ya había sido verificada anteriormente. No es necesario repetir el proceso.</p>
                <a href="http://localhost:5500/index.html" style="color: #003da5; font-weight: bold; text-decoration: none;">Ir a Iniciar Sesión</a>
            </body>
        </html>
        """
    
    # Cambiamos el estado a Verificado y guardamos
    usuario.verificado = True
    db.commit()
    print(f"📢 [CUENTA ACTIVADA] El usuario '{email}' ahora está verificado.")
    
    # Devolvemos un HTML limpio avisando al usuario de que todo ha ido genial
    return """
    <html>
        <body style="font-family: sans-serif; text-align: center; padding: 50px; background-color: #f0f4f8;">
            <div style="background: white; max-width: 500px; margin: auto; padding: 40px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 5px solid #003da5;">
                <h2 style="color: #003da5;">✅ ¡Cuenta activada con éxito!</h2>
                <p style="color: #6c757d; margin-bottom: 25px;">Tu correo electrónico ha sido confirmado. Ya puedes acceder al Área Privada de la Peña.</p>
                <a href="http://localhost:5500/index.html" style="background-color: #003da5; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">INICIAR SESIÓN</a>
            </div>
        </body>
    </html>
    """

def get_current_admin(x_usuario_id: int = Header(...), db: Session = Depends(database.get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == x_usuario_id).first()
    if not usuario or usuario.rol.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de Administrador."
        )
    return usuario