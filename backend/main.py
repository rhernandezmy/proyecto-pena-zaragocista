import os
import sys
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr

# 🌟 PARCHE DE EMERGENCIA DE ENTORNO PARA WINDOWS (Acentos y Ñs)
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    os.environ["PGCLIENTENCODING"] = "utf-8"

from fastapi import FastAPI, HTTPException, status, Form, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Herramientas de SQLAlchemy 2.0 y Postgres
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Importamos los routers modulares
from routers import noticias
from routers import mundial

# ---------------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS Y ESTRUCTURA DE ARCHIVOS
# ---------------------------------------------------------------------
RUTA_FRONTEND_ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "assets"))

if not os.path.exists(RUTA_FRONTEND_ASSETS):
    os.makedirs(RUTA_FRONTEND_ASSETS, exist_ok=True)

# ---------------------------------------------------------------------
# CONFIGURACIÓN DE BASE DE DATOS (POSTGRESQL CON .ENV)
# ---------------------------------------------------------------------
from dotenv import load_dotenv
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "pena_zaragocista")

DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ImagenGaleria(Base):
    __tablename__ = "galeria"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    pie_foto = Column(String, nullable=True)
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------
# CONFIGURACIÓN DE APIS EXTERNAS Y CACHÉ DE LIGA
# ---------------------------------------------------------------------
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "TU_MINI_API_KEY_AQUI")
ZARAGOZA_TEAM_ID = 541                     # ID del Real Zaragoza
SEGUNDA_DIV_ID = 141                       # ID de Segunda División (LaLiga Hypermotion)

cache_futbol = {
    "clasificacion": None,
    "partidos": [],
    "ultima_actualizacion": None
}

# ---------------------------------------------------------------------
# BASES DE DATOS EN MEMORIA (Locales para administración)
# ---------------------------------------------------------------------
DB_SOCIOS_FISICOS = []
DB_USUARIOS_WEB = []
DB_VIAJES = []
DB_RESERVAS = []
DB_PARTNERS = [
    {
        "id": 1,
        "categoria": "Desinfecciones",
        "nombre_comercial": "Desinfecciones Herrera"
    }
]

# ---------------------------------------------------------------------
# MODELOS DE ENTRADA (Pydantic)
# ---------------------------------------------------------------------
class SocioNuevo(BaseModel):
    nombre: str
    apellidos: Optional[str] = None
    email: EmailStr
    telefono: Optional[str] = None
    cuota: str

class CuotaActualizacion(BaseModel):
    cuota: str

class ViajeNuevo(BaseModel):
    partido_id: Optional[int] = None
    destino: Optional[str] = None
    fecha: str
    tipo_transporte: str
    plazas_totales: int

class ReservaActualizacion(BaseModel):
    estado: str

class PartnerNuevo(BaseModel):
    categoria: str
    nombre_comercial: str

# ---------------------------------------------------------------------
# INSTANCIA DE FASTAPI Y MIDDELWARES
# ---------------------------------------------------------------------
app = FastAPI(title="API Peña Zaragocista")

app.mount("/assets", StaticFiles(directory=RUTA_FRONTEND_ASSETS), name="assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# INCLUSIÓN DE LOS ROUTERS EXTERNOS MODULARES
app.include_router(noticias.router, prefix="/noticias")
app.include_router(mundial.router, prefix="/mundial")

# ---------------------------------------------------------------------
# LÓGICA DE ACTUALIZACIÓN ASÍNCRONA (API-FOOTBALL LIGA)
# ---------------------------------------------------------------------
async def actualizar_liga_si_es_necesario():
    ahora = datetime.now()
    if (cache_futbol["ultima_actualizacion"] is None or 
            ahora - cache_futbol["ultima_actualizacion"] > timedelta(minutes=30)):
        
        headers = {
            "x-rapidapi-host": "v3.football.api-sports.io",
            "x-rapidapi-key": API_FOOTBALL_KEY
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # 1. Clasificación de Segunda División
                url_clasi = f"https://v3.football.api-sports.io/standings?league={SEGUNDA_DIV_ID}&season={datetime.now().year - 1}"
                res_clasi = await client.get(url_clasi, headers=headers, timeout=10.0)
                if res_clasi.status_code == 200 and "response" in res_clasi.json():
                    datos = res_clasi.json()
                    if datos["response"]:
                        cache_futbol["clasificacion"] = datos["response"][0]["league"]["standings"][0]

                # 2. Calendario de partidos para sincronizar la logística de viajes
                url_fixtures = f"https://v3.football.api-sports.io/fixtures?team={ZARAGOZA_TEAM_ID}&season={datetime.now().year - 1}"
                res_fix = await client.get(url_fixtures, headers=headers, timeout=10.0)
                if res_fix.status_code == 200 and "response" in res_fix.json():
                    datos_fix = res_fix.json()
                    partidos_limpios = []
                    for item in datos_fix["response"]:
                        fixture = item["fixture"]
                        teams = item["teams"]
                        es_home = teams["home"]["id"] == ZARAGOZA_TEAM_ID
                        rival = teams["away"]["name"] if es_home else teams["home"]["name"]
                        
                        partidos_limpios.append({
                            "id": fixture["id"],
                            "rival": rival,
                            "fecha": datetime.fromisoformat(fixture["date"].replace("+00:00", "")).strftime("%d/%m/%Y %H:%M"),
                            "estado": fixture["status"]["short"],
                            "timestamp": fixture["timestamp"]
                        })
                    partidos_limpios.sort(key=lambda x: x["timestamp"])
                    cache_futbol["partidos"] = partidos_limpios

                cache_futbol["ultima_actualizacion"] = ahora
                print("⚽ Caché interna de LaLiga actualizada.")
            except Exception as e:
                print(f"⚠️ API Fútbol (Liga) no disponible temporalmente: {str(e)}")

# ---------------------------------------------------------------------
# ENDPOINTS: PANEL ADMINISTRACIÓN Y CONTROL DE SOCIOS
# ---------------------------------------------------------------------
@app.get("/admin/global-data")
async def obtener_datos_globales_admin():
    return {
        "lista_socios": DB_SOCIOS_FISICOS,
        "usuarios_web": DB_USUARIOS_WEB
    }

@app.post("/socios", status_code=status.HTTP_201_CREATED)
async def registrar_socio_fisico(socio: SocioNuevo):
    nuevo_id = max([s["id"] for s in DB_SOCIOS_FISICOS], default=0) + 1
    socio_dict = {
        "id": nuevo_id,
        "nombre": socio.nombre,
        "apellidos": socio.apellidos,
        "email": socio.email,
        "telefono": socio.telefono,
        "cuota": socio.cuota
    }
    DB_SOCIOS_FISICOS.append(socio_dict)
    return {"status": "ok", "socio": socio_dict}

@app.patch("/socios/{socio_id}/cuota")
async def actualizar_cuota_socio(socio_id: int, payload: CuotaActualizacion):
    for socio in DB_SOCIOS_FISICOS:
        if socio["id"] == socio_id:
            socio["cuota"] = payload.cuota
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Socio físico no encontrado")

@app.delete("/socios/{socio_id}")
async def dar_de_baja_socio(socio_id: int):
    global DB_SOCIOS_FISICOS
    DB_SOCIOS_FISICOS = [s for s in DB_SOCIOS_FISICOS if s["id"] != socio_id]
    return {"status": "ok"}

# ---------------------------------------------------------------------
# ENDPOINTS: VIAJES Y DINÁMICA DE PARTIDOS
# ---------------------------------------------------------------------
@app.get("/partidos")
async def obtener_partidos():
    await actualizar_liga_si_es_necesario()
    proximos = [p for p in cache_futbol["partidos"] if p["estado"] in ["NS", "TBD"]]
    if not proximos:
        return [
            {"id": 101, "rival": "Burgos CF", "fecha": "22/06/2026 18:30"},
            {"id": 102, "rival": "SD Huesca", "fecha": "29/06/2026 21:00"}
        ]
    return proximos

@app.get("/clasificacion")
async def obtener_clasificacion_liga():
    await actualizar_liga_si_es_necesario()
    return cache_futbol["clasificacion"] if cache_futbol["clasificacion"] else []

@app.get("/viajes")
async def obtener_viajes():
    return DB_VIAJES

@app.post("/viajes", status_code=status.HTTP_201_CREATED)
async def crear_viaje(viaje: ViajeNuevo):
    destino_final = "Destino no especificado"
    if viaje.partido_id:
        for partido in cache_futbol["partidos"]:
            if partido["id"] == viaje.partido_id:
                destino_final = partido["rival"]
                break
    elif viaje.destino:
        destino_final = viaje.destino

    nuevo_id = len(DB_VIAJES) + 1
    viaje_dict = {
        "id": nuevo_id,
        "id_viaje": nuevo_id,
        "destino": destino_final,
        "rival": destino_final,
        "fecha": viaje.fecha,
        "tipo": viaje.tipo_transporte,
        "tipo_transporte": viaje.tipo_transporte,
        "plazas_totales": viaje.plazas_totales,
        "plazas_libres": viaje.plazas_totales,
        "plazas_disponibles": viaje.plazas_totales,
        "disponibles": viaje.plazas_totales,
        "precio": 15,
        "precio_viaje": 15
    }
    DB_VIAJES.append(viaje_dict)
    return {"status": "ok", "viaje": viaje_dict}

@app.delete("/viajes/{viaje_id}")
async def eliminar_viaje(viaje_id: int):
    global DB_VIAJES
    DB_VIAJES = [v for v in DB_VIAJES if v["id"] != viaje_id]
    return {"status": "ok"}

# ---------------------------------------------------------------------
# ENDPOINTS: RESERVAS DEL LOCAL / SEDE
# ---------------------------------------------------------------------
@app.get("/reservas")
async def obtener_reservas_local():
    return DB_RESERVAS

@app.patch("/reservas/{reserva_id}")
async def resolver_estado_reserva(reserva_id: int, payload: ReservaActualizacion):
    for reserva in DB_RESERVAS:
        if reserva["id"] == reserva_id:
            reserva["estado"] = payload.estado
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Reserva no encontrada")

# ---------------------------------------------------------------------
# ENDPOINTS: GALERÍA MULTIMEDIA (INTEGRACIÓN EN POSTGRESQL)
# ---------------------------------------------------------------------
@app.get("/galeria")
async def obtener_imagenes_galeria(db: Session = Depends(get_db)):
    stmt = select(ImagenGaleria).order_by(ImagenGaleria.id.desc())
    resultado = db.execute(stmt)
    fotos_db = resultado.scalars().all()
    
    galeria_con_rutas_reales = []
    for foto in fotos_db:
        url_servidor = f"http://localhost:8000/assets/{foto.filename}"
        galeria_con_rutas_reales.append({
            "id": foto.id,
            "titulo": foto.titulo,
            "pie_foto": foto.pie_foto,
            "filename": foto.filename,
            "url": foto.url,
            "url_local": url_servidor
        })
    return galeria_con_rutas_reales

@app.post("/galeria", status_code=status.HTTP_201_CREATED)
async def subir_imagen_galeria(
    titulo: str = Form(...),
    pie_foto: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    os.makedirs(RUTA_FRONTEND_ASSETS, exist_ok=True)
    ruta_guardado = os.path.join(RUTA_FRONTEND_ASSETS, file.filename)
    try:
        await file.seek(0)
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="El archivo subido está vacío")
        with open(ruta_guardado, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error escribiendo archivo: {str(e)}")

    try:
        url_relativa = f"assets/{file.filename}"
        pie = pie_foto if pie_foto else titulo
        nueva_foto = ImagenGaleria(titulo=titulo, pie_foto=pie, filename=file.filename, url=url_relativa)
        db.add(nueva_foto)
        db.commit()          
        db.refresh(nueva_foto) 
    except Exception as e:
        db.rollback() 
        if os.path.exists(ruta_guardado):
            os.remove(ruta_guardado)
        raise HTTPException(status_code=500, detail=f"Error en base de datos: {str(e)}")

    return {"status": "ok", "imagen": nueva_foto}

@app.delete("/galeria/{foto_id}")
async def eliminar_imagen_galeria(foto_id: int, db: Session = Depends(get_db)):
    stmt_buscar = select(ImagenGaleria).where(ImagenGaleria.id == foto_id)
    foto = db.execute(stmt_buscar).scalar_one_or_none()
    if not foto:
        raise HTTPException(status_code=404, detail="La imagen no existe")
    try:
        ruta_archivo = os.path.join(RUTA_FRONTEND_ASSETS, foto.filename)
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
        db.delete(foto)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")
    return {"status": "ok"}

# ---------------------------------------------------------------------
# ENDPOINTS: SPONSORS Y PARTNERS
# ---------------------------------------------------------------------
@app.get("/partners")
async def obtener_partners():
    return DB_PARTNERS

@app.post("/partners", status_code=status.HTTP_201_CREATED)
async def añadir_partner(partner: PartnerNuevo):
    nuevo_id = len(DB_PARTNERS) + 1
    partner_dict = {
        "id": nuevo_id,
        "categoria": partner.categoria,
        "nombre_comercial": partner.nombre_comercial
    }
    DB_PARTNERS.append(partner_dict)
    return {"status": "ok", "partner": partner_dict}

@app.delete("/partners/{partner_id}")
async def eliminar_partner(partner_id: int):
    global DB_PARTNERS
    DB_PARTNERS = [p for p in DB_PARTNERS if p["id"] != partner_id]
    return {"status": "ok"}