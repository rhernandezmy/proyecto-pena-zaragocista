from sqlalchemy import Boolean, Column, Float, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "socios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(20), default="Socio")
    fecha_registro = Column(DateTime, server_default=func.now())
    activo = Column(Boolean, default=True)

    cuotas = relationship("Cuota", back_populates="usuario")
    vehiculos = relationship("Vehiculo", back_populates="usuario", cascade="all, delete-orphan")

class Cuota(Base):
    __tablename__ = "cuotas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("socios.id", ondelete="RESTRICT"), nullable=False)
    ano_ejercicio = Column(Integer, nullable=False, default=2026)
    estado_pago = Column(String(20), default="Pendiente")
    stripe_intent_id = Column(String(100), nullable=True)
    fecha_pago = Column(DateTime, nullable=True)
    usuario = relationship("Usuario", back_populates="cuotas")

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("socios.id", ondelete="CASCADE"), nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    plazas_totales = Column(Integer, nullable=False)
    usuario = relationship("Usuario", back_populates="vehiculos")

class RivalMaestro(Base):
    __tablename__ = "rivales_maestros"
    id = Column(Integer, primary_key=True, index=True)
    nombre_equipo = Column(String(100), unique=True, nullable=False)
    estadio = Column(String(100), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    partidos = relationship("Partido", back_populates="rival_maestro")

class Partido(Base):
    __tablename__ = "partidos"
    id = Column(Integer, primary_key=True, index=True)
    rival = Column(String(100), nullable=False)
    fecha = Column(DateTime, nullable=False)
    lugar = Column(String(100), default="La Romareda")
    estado = Column(String(20), default="Programado")
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    rival_maestro_id = Column(Integer, ForeignKey("rivales_maestros.id", ondelete="SET NULL"), nullable=True)
    viajes = relationship("Viaje", back_populates="partido", cascade="all, delete-orphan")
    rival_maestro = relationship("RivalMaestro", back_populates="partidos")

class Viaje(Base):
    __tablename__ = "viajes"
    id = Column(Integer, primary_key=True, index=True)
    destino = Column(String(100), nullable=False)
    email_conductor = Column(String(100), nullable=False, default="presentesxelescudo@gmail.com")
    partido_id = Column(Integer, ForeignKey("partidos.id", ondelete="CASCADE"), nullable=False)
    tipo_transporte = Column(String(30), default="Coche")
    plazas_totales = Column(Integer, nullable=False)
    plazas_disponibles = Column(Integer, nullable=False)
    precio = Column(Float, default=0.0)
    detalles_precio = Column(String(255), nullable=True)
    hace_noche = Column(Boolean, default=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    partido = relationship("Partido", back_populates="viajes")
    reservas = relationship("Reserva", back_populates="viaje", cascade="all, delete-orphan")

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    viaje_id = Column(Integer, ForeignKey("viajes.id", ondelete="CASCADE"), nullable=False)
    nombre_socio = Column(String(150), nullable=False)
    asientos_reservados = Column(Integer, default=1)
    viaje = relationship("Viaje", back_populates="reservas")

class Patrocinador(Base):
    __tablename__ = "patrocinadores"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    tipo_negocio = Column(String(50), default="Bar")
    logo_url = Column(String(255), nullable=True)
    contribucion = Column(Float, default=0.0)