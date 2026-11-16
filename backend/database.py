import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carga las variables desde el archivo .env (solo para entorno local)
load_dotenv()

# 1. Intentamos leer DATABASE_URL primero (ideal para Render / Producción)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if SQLALCHEMY_DATABASE_URL:
    # Render suele dar URLs que empiezan por postgres:// o postgresql://. 
    # Las adaptamos para que funcionen perfectamente con el driver postgresql+pg8000://
    if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
    elif SQLALCHEMY_DATABASE_URL.startswith("postgresql://") and not SQLALCHEMY_DATABASE_URL.startswith("postgresql+pg8000://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)
else:
    # 2. Si no existe DATABASE_URL, leemos las variables individuales (para tu PC / desarrollo local)
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    # Validación estricta para desarrollo local
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        raise ValueError(
            "Error: Faltan variables de entorno para la base de datos. "
            "Configura DATABASE_URL o bien DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME."
        )
    
    SQLALCHEMY_DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuración del motor con gestión de pool (ideal para FastAPI)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,    # Verifica que la conexión esté viva antes de usarla
    pool_size=10,          # Número de conexiones permanentes en el pool
    max_overflow=20        # Conexiones extra temporales bajo alta carga
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