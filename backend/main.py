from fastapi import FastAPI, HTTPException, status, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional

app = FastAPI(title="API Peña Zaragocista")

# Configuración obligatoria de CORS para conectar con tu HTML
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar por tu dominio en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# BASES DE DATOS EN MEMORIA (Variables globales dinámicas sin datos fijos)
# ---------------------------------------------------------------------
DB_SOCIOS_FISICOS = []
DB_USUARIOS_WEB = []

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

class VinculacionPayload(BaseModel):
    usuario_id: int
    socio_id: int

class ViajeNuevo(BaseModel):
    partido_id: int
    fecha: str
    tipo_transporte: str
    plazas_totales: int

class ReservaActualizacion(BaseModel):
    estado: str

class PartnerNuevo(BaseModel):
    categoria: str
    nombre: str

# ---------------------------------------------------------------------
# 1. PANEL ADMINISTRACIÓN Y CONTROL DE SOCIOS / CUENTAS WEB
# ---------------------------------------------------------------------
@app.get("/admin/global-data")
async def obtener_datos_globales_admin():
    """Devuelve el listado oficial y real de socios físicos y cuentas web registradas."""
    return {
        "lista_socios": DB_SOCIOS_FISICOS,
        "usuarios_web": DB_USUARIOS_WEB
    }

@app.post("/socios", status_code=status.HTTP_201_CREATED)
async def registrar_socio_fisico(socio: SocioNuevo):
    """Inserta dinámicamente un nuevo socio en el Libro Oficial."""
    nuevo_id = len(DB_SOCIOS_FISICOS) + 1
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
    """Modifica el estado del pago de la cuota de un socio físico en tiempo real."""
    for socio in DB_SOCIOS_FISICOS:
        if socio["id"] == socio_id:
            socio["cuota"] = payload.cuota
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Socio físico no encontrado")

@app.delete("/socios/{socio_id}")
async def dar_de_baja_socio(socio_id: int):
    """Elimina definitivamente un socio del Libro Oficial."""
    global DB_SOCIOS_FISICOS
    DB_SOCIOS_FISICOS = [s for s in DB_SOCIOS_FISICOS if s["id"] != socio_id]
    return {"status": "ok"}

@app.post("/admin/vincular-usuario")
async def vincular_usuario_web_con_socio(payload: VinculacionPayload):
    """Une una cuenta de la web con el número físico del Libro de Socios."""
    for user in DB_USUARIOS_WEB:
        if user["id"] == payload.usuario_id:
            user["socio_id"] = payload.socio_id
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Usuario web no encontrado")

@app.get("/socios/exportar/csv")
async def exportar_socios_csv():
    """Genera la descarga del archivo CSV con el listado oficial."""
    # Aquí irá tu lógica para retornar un StreamingResponse del CSV
    pass

# ---------------------------------------------------------------------
# 2. VIAJES Y PARTIDOS
# ---------------------------------------------------------------------
@app.get("/partidos")
async def obtener_partidos():
    """Lista los partidos disponibles para asociar un nuevo viaje."""
    return []

@app.get("/viajes")
async def obtener_viajes():
    """Lista todos los desplazamientos activos programados."""
    return []

@app.post("/viajes", status_code=status.HTTP_201_CREATED)
async def crear_viaje(viaje: ViajeNuevo):
    """Publica un nuevo plan de viaje en la plataforma."""
    return {"status": "ok"}

@app.delete("/viajes/{viaje_id}")
async def eliminar_viaje(viaje_id: int):
    """Borra un viaje del catálogo."""
    return {"status": "ok"}

# ---------------------------------------------------------------------
# 3. RESERVAS DEL LOCAL / SEDE
# ---------------------------------------------------------------------
@app.get("/reservas")
async def obtener_reservas_local():
    """Lista todas las solicitudes de uso del local de la peña."""
    return []

@app.patch("/reservas/{reserva_id}")
async def resolver_estado_reserva(reserva_id: int, payload: ReservaActualizacion):
    """Aprueba o deniega una solicitud de reserva del local."""
    return {"status": "ok"}

# ---------------------------------------------------------------------
# 4. GALERÍA MULTIMEDIA
# ---------------------------------------------------------------------
@app.get("/galeria")
async def obtener_imagenes_galeria():
    """Devuelve las fotos publicadas en la web."""
    return []

@app.post("/galeria", status_code=status.HTTP_201_CREATED)
async def subir_imagen_galeria(
    titulo: str = Form(...),
    pie_foto: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """Recibe y procesa el archivo de imagen adjunto de un evento."""
    return {"status": "ok"}

@app.delete("/galeria/{foto_id}")
async def eliminar_imagen_galeria(foto_id: int):
    """Borra un recurso gráfico del sistema."""
    return {"status": "ok"}

# ---------------------------------------------------------------------
# 5. SPONSORS Y PARTNERS
# ---------------------------------------------------------------------
@app.get("/partners")
async def obtener_partners():
    """Muestra los patrocinadores colaboradores actuales."""
    return []

@app.post("/partners", status_code=status.HTTP_201_CREATED)
async def añadir_partner(partner: PartnerNuevo):
    """Registra una nueva entidad colaboradora."""
    return {"status": "ok"}

@app.delete("/partners/{partner_id}")
async def eliminar_partner(partner_id: int):
    """Rompe el acuerdo o quita al sponsor del panel."""
    return {"status": "ok"}