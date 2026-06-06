import bcrypt
from database import SessionLocal
from models import Usuario

# 1. Configuración
db = SessionLocal()
email_usuario = "rhernandezmy@fpvirtualaragon.es"
nueva_pass = "1234"

# 2. Generar el hash usando bcrypt directamente (la forma moderna)
# .encode('utf-8') es necesario porque bcrypt trabaja con bytes
bytes_password = nueva_pass.encode('utf-8')
hashed_password = bcrypt.hashpw(bytes_password, bcrypt.gensalt())

# 3. Actualizar en la base de datos
# Como el hash de bcrypt devuelve bytes, lo convertimos a string (utf-8) para guardarlo
socio = db.query(Usuario).filter(Usuario.email == email_usuario).first()

if socio:
    socio.password_hash = hashed_password.decode('utf-8')
    db.commit()
    print(f"✅ Contraseña actualizada correctamente para {email_usuario}")
else:
    print("❌ No se encontró al usuario con ese email.")

db.close()