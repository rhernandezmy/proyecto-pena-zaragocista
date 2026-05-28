from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
import database
import models

# Creamos las tablas en la base de datos (si no existen)
models.Base.metadata.create_all(bind=database.engine)

# Inicializamos la aplicación
app = FastAPI(title="Peña Zaragocista API")

# Nueva ruta para obtener los usuarios de la base de datos
@app.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    # Hacemos una consulta mágica: "Trae todos los registros de la tabla Usuario"
    usuarios_db = db.query(models.Usuario).all()
    return usuarios_db

# Ruta de prueba para verificar que el backend funciona
@app.get("/")
def read_root():
    return {"message": "¡Hola, Roberto! El backend de la Peña Zaragocista está funcionando"}

# Nueva ruta para obtener todos los partidos de la base de datos
@app.get("/partidos")
def obtener_partidos(db: Session = Depends(get_db)):
    # Le pedimos a la base de datos todos los registros de la tabla Partido
    partidos_db = db.query(models.Partido).all()
    return partidos_db

# Nueva ruta para obtener todos los viajes de la base de datos
@app.get("/viajes")
def obtener_viajes(db: Session = Depends(get_db)):
    # Le pedimos a la base de datos todos los registros de la tabla Viaje
    viajes_db = db.query(models.Viaje).all()
    return viajes_db