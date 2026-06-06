from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class PartidoCrear(BaseModel):
    rival: str
    fecha: datetime
    lugar: str
    rival_maestro_id: Optional[int] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

    class Config:
        from_attributes = True

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

class ReservaCrear(BaseModel):
    viaje_id: int
    usuario_id: int  # Ahora usamos ID en lugar de nombre_socio
    asientos_reservados: int

    class Config:
        from_attributes = True

class PatrocinadorCrear(BaseModel):
    nombre: str
    tipo_negocio: str = "Bar"
    logo_url: Optional[str] = None
    contribucion: float = 0.0

    class Config:
        from_attributes = True

class RivalMaestroCrear(BaseModel):
    nombre_equipo: str
    estadio: str
    latitud: float
    longitud: float

    class Config:
        from_attributes = True

class CuotaPagoCrear(BaseModel):
    usuario_id: int
    ano_ejercicio: int

    class Config:
        from_attributes = True