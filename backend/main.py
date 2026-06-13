import os
import sys
import httpx
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import csv
from fastapi.responses import StreamingResponse
import io

# 🌟 PARCHE DE EMERGENCIA DE ENTORNO PARA WINDOWS (Acentos y Ñs)
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    os.environ["PGCLIENTENCODING"] = "utf-8"

from fastapi import FastAPI, HTTPException, status, Form, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Herramientas de SQLAlchemy 2.0 y Postgres
from sqlalchemy import create_engine, Column, Integer, String, select, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Importaciones de tu arquitectura local (Base de datos y Modelos)
import database
import models

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
    apellidos: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    dni: Optional[str] = None
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
async def obtener_datos_globales_admin(db: Session = Depends(get_db)):
    """
    Envía los socios al panel incluyendo el DNI real y el número de socio real de la BD.
    """
    try:
        # Los ordenamos por número de socio para que salgan perfectos en la tabla
        socios_db = db.query(models.SocioPena).order_by(models.SocioPena.numero_socio).all()
        
        lista_socios_formateada = [
            {
                "id": socio.id,
                "numero_socio": socio.numero_socio,  # ◄ Enviamos el número limpio de la base de datos
                "nombre": socio.nombre,
                "apellidos": socio.apellidos,
                "dni": socio.dni or "-",          
                "email": socio.email or "",      
                "telefono": socio.telefono or "",
                "activo": socio.activo,  
                "cuota": socio.estado_cuota if socio.estado_cuota else "Pendiente" 
            }
            for socio in socios_db
        ]
        
        return {
            "lista_socios": lista_socios_formateada,
            "usuarios_web": DB_USUARIOS_WEB
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos globales: {str(e)}")

@app.post("/socios", status_code=status.HTTP_201_CREATED)
async def registrar_socio_fisico(socio: SocioNuevo, db: Session = Depends(get_db)):
    """
    Guarda el socio asignando número automático garantizado sin duplicados, 
    almacenando el DNI real y la cuota.
    """
    try:
        # 🚨 CÁLCULO BLINDADO DE NÚMERO DE SOCIO:
        # Buscamos el número más alto asignado
        max_numero = db.query(func.max(models.SocioPena.numero_socio)).scalar() or 0
        # Buscamos el conteo total de filas por si acaso hay nulos
        total_socios = db.query(func.count(models.SocioPena.id)).scalar() or 0
        
        # El siguiente número será el mayor entre el máximo encontrado y el total de registros + 1
        siguiente_numero = max(max_numero, total_socios) + 1

        nuevo_socio = models.SocioPena(
            numero_socio=siguiente_numero, # Asegura 4, 5, 6, 7... de forma estrictamente correlativa
            nombre=socio.nombre,
            apellidos=socio.apellidos,
            dni=socio.dni or None,           
            telefono=socio.telefono or None,
            email=socio.email or None,  
            estado_cuota=socio.cuota,        
            activo=True      
        )
        
        db.add(nuevo_socio)
        db.commit()      
        db.refresh(nuevo_socio)
        
        return {
            "status": "ok",
            "socio": {
                "id": nuevo_socio.id,
                "numero_socio": nuevo_socio.numero_socio,
                "nombre": nuevo_socio.nombre,
                "cuota": nuevo_socio.estado_cuota
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar socio en Postgres: {str(e)}")

@app.patch("/socios/{socio_id}/cuota")
async def actualizar_cuota_socio(socio_id: int, payload: CuotaActualizacion, db: Session = Depends(get_db)):
    """
    Actualiza el estado de la cuota en su columna correspondiente.
    """
    try:
        socio = db.query(models.SocioPena).filter(models.SocioPena.id == socio_id).first()
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        
        socio.estado_cuota = payload.cuota # Guardamos en la columna correcta
        db.commit()
        return {"status": "ok"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/socios/{socio_id}")
async def dar_de_baja_socio(socio_id: int, db: Session = Depends(get_db)):
    try:
        socio = db.query(models.SocioPena).filter(models.SocioPena.id == socio_id).first()
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        
        socio.activo = False
        db.commit()
        return {"status": "ok", "message": "Socio desactivado para el histórico"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/socios/{socio_id}/reactivar")
async def reactivar_socio(socio_id: int, db: Session = Depends(get_db)):
    try:
        socio = db.query(models.SocioPena).filter(models.SocioPena.id == socio_id).first()
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        
        socio.activo = True
        db.commit()
        return {"status": "ok", "message": "Socio reactivado con éxito"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/socios/exportar-csv")
async def exportar_socios_csv(db: Session = Depends(get_db)):
    """
    Genera un archivo CSV descargable utilizando .zfill() de Python de forma correcta.
    """
    try:
        socios = db.query(models.SocioPena).order_by(models.SocioPena.numero_socio).all()
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        writer.writerow(["Numero Socio", "Nombre", "Apellidos", "DNI", "Email", "Telefono", "Estado Cuota", "Activo"])
        
        for s in socios:
            # 🚨 CORRECCIÓN: Usamos str(...).zfill(3) que es el método correcto en Python
            num_socio_formateado = f"#{str(s.numero_socio or s.id).zfill(3)}"
            
            writer.writerow([
                num_socio_formateado,
                s.nombre,
                s.apellidos,
                s.dni or "-",
                s.email or "-",
                s.telefono or "-",
                s.estado_cuota or "Pendiente",
                "Alta" if s.activo else "Baja"
            ])
            
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')), 
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=libro_oficial_socios.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
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