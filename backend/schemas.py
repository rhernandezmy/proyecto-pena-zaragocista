from pydantic import BaseModel
from typing import Optional

# 1. FORMULARIO PARA PARTIDOS
class PartidoCrear(BaseModel):
    rival: str
    fecha: str
    lugar: str
    rival_maestro_id: Optional[int] = None  # Para conectar con un rival maestro si se desea
    latitud: Optional[float] = None  # Opcional si no sabemos la coordenada exacta al momento
    longitud: Optional[float] = None # Opcional si no sabemos la coordenada exacta al momento

    class Config:
        from_attributes = True

# 2. FORMULARIO PARA VIAJES
class ViajeCrear(BaseModel):
    partido_id: int
    destino: str
    email_conductor: str
    tipo_transporte: str = "Coche"
    plazas_totales: int
    plazas_disponibles: int
    precio: float = 0.0
    detalles_precio: Optional[str] = None
    hace_noche: bool = False

    class Config:
        from_attributes = True

# 3. FORMULARIO PARA RESERVAS
class ReservaCrear(BaseModel):
    viaje_id: int
    nombre_socio: str
    asientos_reservados: int

    class Config:
        from_attributes = True

# 4. FORMULARIO PARA PATROCINADORES
class PatrocinadorCrear(BaseModel):
    nombre: str
    tipo_negocio: str = "Bar"
    logo_url: Optional[str] = None
    contribucion: float = 0.0

    class Config:
        from_attributes = True

# 5. FORMULARIO PARA RIVALES MAESTROS
class RivalMaestroCrear(BaseModel):
    nombre_equipo: str
    estadio: str
    latitud: float
    longitud: float

    class Config:
        from_attributes = True

# 6. FORMULARIO PARA LA SIMULACIÓN DE PAGOS DE CUOTAS (Stripe)
class CuotaPagoCrear(BaseModel):
    usuario_id: int
    ano_ejercicio: int

    class Config:
        from_attributes = True