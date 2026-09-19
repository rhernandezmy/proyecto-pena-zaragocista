from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# =========================================================================
# 🚌 VIAJES
# =========================================================================
class ViajeCrear(BaseModel):
    rival: str
    destino: str
    partido_api_id: Optional[int] = None
    fecha_partido: Optional[datetime] = None
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
# 📅 RESERVAS
# =========================================================================
class ReservaCrear(BaseModel):
    usuario_id: int  
    viaje_id: Optional[int] = None       # Opcional si es reserva del local
    asientos_reservados: int = 1
    tipo_reserva: str = "Viaje"          # "Viaje" o "Local"
    motivo_evento: Optional[str] = None  # Ej: "Ver partido contra Castellón"
    fecha_solicitada: Optional[str] = None # 👈 ¡AGREGAR ESTA LÍNEA! (Formato YYYY-MM-DD o ISO)

    class Config:
        from_attributes = True


# =========================================================================
# 🤝 PATROCINADORES
# =========================================================================
class PatrocinadorCrear(BaseModel):
    nombre: str
    tipo_negocio: str = "Bar"
    logo_url: Optional[str] = None
    enlace_web: Optional[str] = None
    contribucion: float = 0.0

    class Config:
        from_attributes = True

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
# 👥 GESTIÓN DE SOCIOS Y USUARIOS WEB (Admin)
# =========================================================================

# --- Ficha del Socio Físico ---
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

# --- Cuentas de la Web ---
class UsuarioWebResponse(BaseModel):
    id: int
    email: EmailStr
    rol: str
    activo: bool
    fecha_registro: datetime
    socio_pena_id: Optional[int] = None
    socio_interno: Optional[SocioPenaResponse] = None

    class Config:
        from_attributes = True

class VincularSocioRequest(BaseModel):
    socio_pena_id: Optional[int] = None