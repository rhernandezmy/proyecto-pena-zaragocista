import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carga las variables desde el archivo .env
load_dotenv()

# Obtenemos las variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Validación estricta: si falta algo, el programa te dirá exactamente qué falta
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError(
        "Error: Faltan variables de entorno para la base de datos en el archivo .env. "
        "Asegúrate de tener configurados: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME."
    )

# Construcción de la URL de conexión
SQLALCHEMY_DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuración del motor con gestión de pool (ideal para FastAPI)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,   # Verifica que la conexión esté viva antes de usarla
    pool_size=10,         # Número de conexiones permanentes en el pool
    max_overflow=20       # Conexiones extra temporales bajo alta carga
)

# Sesión local para las consultas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para los modelos
Base = declarative_base()

# Dependencia para usar en los endpoints (FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()