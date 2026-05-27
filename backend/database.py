from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Definimos la URL de conexión a tu base de datos local pena_db
# Formato: postgresql://usuario:contraseña@servidor:puerto/nombre_bd
# NOTA: Cambia 'tu_contraseña' por la contraseña real que pusiste en tu PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Aqmdla22@localhost:5432/pena_db"

# 2. Creamos el motor de conexión
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Creamos la fábrica de sesiones (las que usaremos para hacer consultas)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Creamos la clase Base de la que heredarán nuestros futuros modelos de tablas
Base = declarative_base()

# 5. Función auxiliar (dependencia) para abrir y cerrar la conexión automáticamente
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()