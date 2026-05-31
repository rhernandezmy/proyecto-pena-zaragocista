import os
from dotenv import load_dotenv  # 🌟 Importamos la librería para leer el archivo .env
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 🌟 Cargamos el archivo .env desde la raíz del proyecto
load_dotenv()

# 🌟 Leemos la URL de la base de datos de forma segura desde las variables de entorno.
# Si no encuentra la variable en el .env, levantará un error indicando que falta configurar el entorno.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "❌ ERROR DE CONFIGURACIÓN: No se ha encontrado la variable DATABASE_URL en el archivo .env. "
        "Por favor, asegúrate de que el archivo .env está en la raíz del proyecto y contiene la cadena de conexión."
    )

# 2. Creamos el motor de conexión utilizando la variable de entorno segura
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Creamos la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Creamos la clase Base de la que heredarán nuestros modelos
Base = declarative_base()

# 5. Función auxiliar para abrir y cerrar la conexión automáticamente
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()