import bcrypt
from database import SessionLocal
from models import Usuario

def resetear_password():
    db = SessionLocal()
    
    # Solicitar datos de forma segura en la consola
    email_usuario = input("Introduce el email del usuario: ").strip()
    nueva_pass = input("Introduce la nueva contraseña: ").strip()

    if not email_usuario or not nueva_pass:
        print("❌ El email y la contraseña no pueden estar vacíos.")
        return

    # Generar el hash con bcrypt
    bytes_password = nueva_pass.encode('utf-8')
    hashed_password = bcrypt.hashpw(bytes_password, bcrypt.gensalt())

    # Buscar y actualizar en la base de datos
    socio = db.query(Usuario).filter(Usuario.email == email_usuario).first()

    if socio:
        socio.password_hash = hashed_password.decode('utf-8')
        db.commit()
        print(f"✅ Contraseña actualizada correctamente para {email_usuario}")
    else:
        print("❌ No se encontró al usuario con ese email.")

    db.close()

if __name__ == "__main__":
    resetear_password()