from sqlalchemy import Boolean, Column, Float, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

# Definimos el modelo de datos para los usuarios
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    apellidos = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String(20), default="Socio")
    fecha_registro = Column(DateTime, server_default=func.now())

# Definimos el modelo de datos para los partidos
class Partido(Base):
    __tablename__ = "partidos"

    id = Column(Integer, primary_key=True, index=True)
    rival = Column(String(100), nullable=False)
    fecha = Column(DateTime, nullable=False)
    lugar = Column(String(100), default="La Romareda")  # Por defecto jugamos en casa
    estado = Column(String(20), default="Programado")   # Programado, Jugado, Aplazado

# Definimos el modelo de datos para los viajes
class Viaje(Base):
    __tablename__ = "viajes"

    id = Column(Integer, primary_key=True, index=True)
    destino = Column(String(100), nullable=False)
    
    # TIPO DE TRANSPORTE: Por defecto será 'Coche', pero permite 'Autobús'
    tipo_transporte = Column(String(30), default="Coche")
    
    # PLAZAS: Flexibilidad para controlar el aforo inicial y los huecos libres
    plazas_totales = Column(Integer, nullable=False)
    plazas_disponibles = Column(Integer, nullable=False)
    
    # PRECIO Y CONDICIONES: Precio base numérico y texto libre para especificar escalas o acuerdos
    precio = Column(Float, default=0.0)
    detalles_precio = Column(String(255), nullable=True)
    
    # ALOJAMIENTO: Check booleano (True = Hace noche / False = En el día)
    hace_noche = Column(Boolean, default=False)