import bcrypt
from sqlalchemy.orm import Session
# Importamos la conexión real y el modelo que usa tu FastAPI
from database import SessionLocal
import models

def crear_socio_real():
    # 1. Abrimos la conexión exacta que usa el servidor
    db: Session = SessionLocal()
    
    email_nuevo = "socio_real@fpvirtualaragon.es"
    
    try:
        # 2. Comprobamos si ya existe para no duplicarlo
        existe = db.query(models.Usuario).filter(models.Usuario.email == email_nuevo).first()
        if existe:
            print(f"⚠️ El usuario {email_nuevo} ya existe en la base de datos real con el ID {existe.id}.")
            return

        # 3. Encriptamos la contraseña de forma nativa
        print("🔐 Encriptando contraseña...")
        salt = bcrypt.gensalt(12)
        hash_password = bcrypt.hashpw("123456".encode('utf-8'), salt).decode('utf-8')

        # 4. Creamos el objeto Usuario con rol Socio
        nuevo_usuario = models.Usuario(
            nombre="Carlos",
            apellidos="Martínez Socio",
            email=email_nuevo,
            password_hash=hash_password,
            rol="Socio",  # 👈 Rol asignado correctamente
            activo=True
        )

        # 5. Guardamos físicamente en la base de datos
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        print("\n========================================================")
        print("✅ ¡USUARIO CREADO CON ÉXITO EN LA BASE DE DATOS REAL!")
        print(f"   - ID asignado por la DB: {nuevo_usuario.id}")
        print(f"   - Nombre: {nuevo_usuario.nombre}")
        print(f"   - Email: {nuevo_usuario.email}")
        print(f"   - Rol: {nuevo_usuario.rol}")
        print("========================================================\n")

    except Exception as e:
        db.rollback()
        print(f"❌ Error al insertar en la base de datos: {e}")
    finally:
        # 6. Cerramos la conexión de forma segura
        db.close()

if __name__ == "__main__":
    crear_socio_real()