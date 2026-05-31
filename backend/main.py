from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
import database
import models

from routers import partidos, viajes, reservas, patrocinadores, rivales, cuotas

# Creamos las tablas en la base de datos (si no existen)
models.Base.metadata.create_all(bind=database.engine)

# Inicializamos la aplicación
app = FastAPI(title="Peña Zaragocista API", version="2.0")

# Conectamos las rutas modulares a la aplicación principal
app.include_router(partidos.router)
app.include_router(viajes.router)
app.include_router(reservas.router)
app.include_router(patrocinadores.router)
app.include_router(rivales.router)
app.include_router(cuotas.router)

# Ruta base de bienvenida
@app.get("/", tags=["General"])
def read_root():
    return {"message": "¡Hola, Roberto! El backend modular de la Peña Zaragocista está funcionando a nivel experto."}

# Ruta temporal para usuarios (la dejamos aquí de momento)
@app.get("/usuarios", tags=["General"])
def obtener_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()