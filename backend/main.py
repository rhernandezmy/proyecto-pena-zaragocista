from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine
import models
from routers import partidos, viajes, reservas, patrocinadores, rivales, cuotas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Peña Zaragocista API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(partidos.router)
app.include_router(viajes.router)
app.include_router(reservas.router)
app.include_router(patrocinadores.router)
app.include_router(rivales.router)
app.include_router(cuotas.router)

@app.get("/", tags=["General"])
def read_root():
    return {"message": "¡Hola, Roberto! Backend en marcha."}

@app.get("/socios", tags=["General"])
def obtener_socios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()