from database import SessionLocal
from models import Usuario
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

try:
    password_plana = "1234"
    hashed_password = pwd_context.hash(password_plana)

    nuevo_socio = Usuario(
        nombre="Roberto",
        apellidos="Zaragocista",
        email="rhernandezmy@fpvirtualaragon.es",
        password_hash=hashed_password, 
        rol="Socio"
    )

    db.add(nuevo_socio)
    db.commit()
    db.refresh(nuevo_socio)
    print(f"✅ Socio creado con éxito: {nuevo_socio.nombre}")

except IntegrityError:
    db.rollback()
    print("⚠️ El socio ya existe en la base de datos.")
except Exception as e:
    db.rollback()
    print(f"❌ Error inesperado: {e}")
finally:
    db.close()