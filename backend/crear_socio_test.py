from database import SessionLocal
from models import Usuario

# Abrimos la conexión con la base de datos
db = SessionLocal()

# Creamos un socio de prueba
nuevo_socio = Usuario(
    nombre="Roberto",
    apellidos="Zaragocista",
    email="rhernandezmy@fpvirtualaragon.es",
    password_hash="1234", 
    rol="Socio"
)

# Guardamos el cambio
db.add(nuevo_socio)
db.commit()
db.refresh(nuevo_socio)

print(f"✅ Socio creado con éxito: {nuevo_socio.nombre} {nuevo_socio.apellidos}")