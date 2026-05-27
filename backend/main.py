from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
import models

# Inicializamos la aplicación
app = FastAPI(title="Peña Zaragocista API")

# Nueva ruta para obtener los usuarios de la base de datos
@app.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    # Hacemos una consulta mágica: "Trae todos los registros de la tabla Usuario"
    usuarios_db = db.query(models.Usuario).all()
    return usuarios_db

@app.get("/")
def read_root():
    return {"message": "¡Hola, Roberto! El backend de la Peña Zaragocista está funcionando"}