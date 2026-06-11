from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# =========================================================================
# ⚽ PARTIDOS Y RIVALES
# =========================================================================
class PartidoCrear(BaseModel):
    rival: str
    fecha: datetime
    lugar: str
    rival_maestro_id: Optional[int] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

    class Config:
        from_attributes = True

class RivalMaestroCrear(BaseModel):
    nombre_equipo: str
    estadio: str
    latitud: float
    longitud: float

    class Config:
        from_attributes = True


# =========================================================================
# 🚌 VIAJES
# =========================================================================
class ViajeCrear(BaseModel):
    partido_id: int
    destino: str
    email_conductor: EmailStr
    tipo_transporte: str = "Coche"
    plazas_totales: int
    plazas_disponibles: int
    precio: float = 0.0
    detalles_precio: Optional[str] = None
    hace_noche: bool = False

    class Config:
        from_attributes = True


# =========================================================================
# 📅 RESERVAS (Actualizado para admitir Reservas de Local)
# =========================================================================
class ReservaCrear(BaseModel):
    usuario_id: int  
    viaje_id: Optional[int] = None       # Ahora es opcional por si es reserva de Local
    asientos_reservados: int = 1
    tipo_reserva: str = "Viaje"          # "Viaje" o "Local"
    motivo_evento: Optional[str] = None  # Ej: "Ver partido contra Castellón"

    class Config:
        from_attributes = True


# =========================================================================
# 🤝 PATROCINADORES (Actualizado con enlace web y lectura completa)
# =========================================================================
class PatrocinadorCrear(BaseModel):
    nombre: str
    tipo_negocio: str = "Bar"
    logo_url: Optional[str] = None
    enlace_web: Optional[str] = None     # NUEVO: Para redirigir al pulsar en el sponsor
    contribucion: float = 0.0

    class Config:
        from_attributes = True

# Esquema de salida (lectura) que incluye el ID generado por la Base de Datos
class Patrocinador(PatrocinadorCrear):
    id: int

    class Config:
        from_attributes = True


# =========================================================================
# 📸 GALERÍA DE FOTOS
# =========================================================================
class FotoGaleriaCrear(BaseModel):
    titulo: str
    pie_foto: Optional[str] = None

    class Config:
        from_attributes = True

class FotoGaleria(FotoGaleriaCrear):
    id: int
    imagen_url: str
    fecha_subida: datetime

    class Config:
        from_attributes = True


# =========================================================================
# 💳 CUOTAS
# =========================================================================
class CuotaPagoCrear(BaseModel):
    usuario_id: int
    ano_ejercicio: int

    class Config:
        from_attributes = True


# =========================================================================
# 👥 NUEVOS SCHEMAS: GESTIÓN DE SOCIOS Y USUARIOS WEB (Para el Admin)
# =========================================================================

# --- Esquemas Pestaña 1: Ficha del Socio Físico ---
class SocioPenaBase(BaseModel):
    numero_socio: Optional[int] = None
    nombre: str
    apellidos: str
    dni: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = True

class SocioPenaCreate(SocioPenaBase):
    pass

class SocioPenaResponse(SocioPenaBase):
    id: int
    fecha_alta: datetime

    class Config:
        from_attributes = True

# --- Esquemas Pestaña 2: Cuentas de la Web ---
class UsuarioWebResponse(BaseModel):
    id: int
    email: EmailStr
    rol: str
    activo: bool
    fecha_registro: datetime
    socio_pena_id: Optional[int] = None
    # Si está vinculado, incluye la información de su ficha física de socio
    socio_interno: Optional[SocioPenaResponse] = None

    class Config:
        from_attributes = True

class VincularSocioRequest(BaseModel):
    socio_pena_id: Optional[int] = None  # ID de la ficha a vincular (o None para desvincular)