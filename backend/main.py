import os
import sys
import httpx
import csv
import io

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, status, HTTPException, Depends, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 🌟 PARCHE DE ENTORNO PARA WINDOWS (Acentos y Ñs)
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    os.environ["PGCLIENTENCODING"] = "utf-8"

# Herramientas de SQLAlchemy y Base de Datos Centralizada
from sqlalchemy import Column, Integer, String, select, func
from sqlalchemy.orm import Session

import models
from database import engine, Base, get_db

# Importamos los routers modulares
from routers import auth, usuarios, noticias, reservas, contacto
from routers.zaragoza import router as zaragoza_router, iniciar_cron

# ---------------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS Y ESTRUCTURA DE ARCHIVOS
# ---------------------------------------------------------------------
RUTA_FRONTEND_ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "assets"))

if not os.path.exists(RUTA_FRONTEND_ASSETS):
    os.makedirs(RUTA_FRONTEND_ASSETS, exist_ok=True)

# ---------------------------------------------------------------------
# MODELOS DE BASE DE DATOS LOCALES
# ---------------------------------------------------------------------
class ImagenGaleria(Base):
    __tablename__ = "galeria"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    pie_foto = Column(String, nullable=True)
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------
# BASES DE DATOS EN MEMORIA (Locales para administración)
# ---------------------------------------------------------------------
DB_SOCIOS_FISICOS = []
DB_USUARIOS_WEB = []
DB_VIAJES = []
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

class PartnerNuevo(BaseModel):
    categoria: str
    nombre_comercial: str

# ---------------------------------------------------------------------
# INSTANCIA DE FASTAPI Y MIDDLEWARES
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

# =========================================================================
# CONTROL DE ENRUTAMIENTO (Routers Modulares)
# =========================================================================
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(usuarios.router, tags=["Usuarios"])
app.include_router(noticias.router, prefix="/noticias", tags=["Noticias"])
app.include_router(zaragoza_router)
app.include_router(reservas.router, prefix="/reservas", tags=["Reservas"])
app.include_router(contacto.router, prefix="/api/contacto", tags=["Contacto"])

# ---------------------------------------------------------------------
# Activar el Cron para actualizar datos de Zaragoza
# ---------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    iniciar_cron()

# ---------------------------------------------------------------------
# ENDPOINTS: PANEL ADMINISTRACIÓN Y CONTROL DE SOCIOS
# ---------------------------------------------------------------------
@app.get("/admin/global-data")
async def obtener_datos_globales_admin(db: Session = Depends(get_db)):
    try:
        socios_db = db.query(models.SocioPena).order_by(models.SocioPena.numero_socio).all()
        lista_socios_formateada = [
            {
                "id": socio.id,
                "numero_socio": socio.numero_socio if socio.numero_socio is not None else socio.id,
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
        
        usuarios_db = db.query(models.Usuario).all()
        lista_usuarios_formateada = [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "rol": u.rol,
                "activo": u.activo,
                "verificado": u.verificado,
                "socio_vinculado": f"#{str(u.socio_interno.numero_socio).zfill(3)}" if u.socio_interno else "-"
            }
            for u in usuarios_db
        ]
        
        return {
            "lista_socios": lista_socios_formateada,
            "usuarios_web": lista_usuarios_formateada
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos globales: {str(e)}")

@app.post("/socios", status_code=status.HTTP_201_CREATED)
async def registrar_socio_fisico(socio: SocioNuevo, db: Session = Depends(get_db)):
    try:
        max_numero = db.query(func.max(models.SocioPena.numero_socio)).scalar() or 0
        total_socios = db.query(func.count(models.SocioPena.id)).scalar() or 0
        siguiente_numero = max(max_numero, total_socios) + 1

        nuevo_socio = models.SocioPena(
            numero_socio=siguiente_numero,
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
    try:
        socio = db.query(models.SocioPena).filter(models.SocioPena.id == socio_id).first()
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        
        socio.estado_cuota = payload.cuota
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
    try:
        socios = db.query(models.SocioPena).order_by(models.SocioPena.numero_socio).all()
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        writer.writerow(["Numero Socio", "Nombre", "Apellidos", "DNI", "Email", "Telefono", "Estado Cuota", "Activo"])
        
        for s in socios:
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
    
class RegistroUsuarioWeb(BaseModel):
    username: str
    email: EmailStr
    password: str

@app.post("/auth/registro-web", status_code=status.HTTP_201_CREATED)
async def registrar_usuario_web(datos: RegistroUsuarioWeb, db: Session = Depends(get_db)):
    try:
        usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == datos.email).first()
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Este correo electrónico ya tiene una cuenta web registrada."
            )
            
        socio_oficial = db.query(models.SocioPena).filter(
            models.SocioPena.email == datos.email,
            models.SocioPena.activo == True
        ).first()
        
        if not socio_oficial:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Lo sentimos, este correo no figura en el Libro Oficial de Socios de la Peña."
            )
            
        pwd_encriptada = datos.password
        
        nuevo_usuario = models.Usuario(
            username=datos.username,
            email=datos.email,
            hashed_password=pwd_encriptada,
            rol="socio",
            activo=True,
            verificado=False,
            socio_id=socio_oficial.id
        )
        
        db.add(nuevo_usuario)
        db.commit()
        
        return {
            "status": "ok", 
            "message": "Cuenta creada. Por favor, verifica tu correo electrónico para activarla.",
            "socio_vinculado": f"#{str(socio_oficial.numero_socio).zfill(3)}"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en el registro: {str(e)}")

# ---------------------------------------------------------------------
# ENDPOINTS: VIAJES Y CLASIFICACIÓN
# ---------------------------------------------------------------------
@app.get("/clasificacion")
async def obtener_clasificacion_liga():
    from routers.zaragoza import cache_zaragoza
    return cache_zaragoza.get("clasificacion", [])

@app.get("/viajes")
async def obtener_viajes():
    return DB_VIAJES

@app.post("/viajes", status_code=status.HTTP_201_CREATED)
async def crear_viaje(viaje: ViajeNuevo, db: Session = Depends(get_db)):
    destino_final = "Destino no especificado"
    
    if viaje.partido_id:
        partido_db = db.query(models.Partido).filter(models.Partido.id == viaje.partido_id).first()
        if partido_db:
            destino_final = partido_db.rival
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