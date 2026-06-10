from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import SQLALCHEMY_DATABASE_URL, engine
import models
from routers import (auth, contacto, panel, partidos, viajes, reservas, 
                     patrocinadores, rivales, cuotas, noticias, mundial, usuarios)

# Inicialización de tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Peña Zaragocista API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(partidos.router, prefix="/partidos", tags=["Partidos"])
app.include_router(viajes.router, prefix="/viajes", tags=["Viajes"])
app.include_router(reservas.router, prefix="/reservas", tags=["Reservas"])
app.include_router(patrocinadores.router, prefix="/patrocinadores", tags=["Patrocinadores"])
app.include_router(rivales.router, prefix="/rivales", tags=["Rivales"])
app.include_router(cuotas.router, prefix="/cuotas", tags=["Cuotas"])
app.include_router(noticias.router, prefix="/noticias", tags=["Noticias"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios y Socios"])
app.include_router(panel.router, prefix="/panel", tags=["Panel"])
app.include_router(mundial.router, prefix="/mundial", tags=["Mundial"])
app.include_router(contacto.router, prefix="/contacto", tags=["Contacto"])

@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "online"}