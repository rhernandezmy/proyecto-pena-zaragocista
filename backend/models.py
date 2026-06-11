from sqlalchemy import Boolean, Column, Float, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

# =====================================================================
# 1. GESTIÓN DE SOCIOS (Pestaña 1 del Admin)
# =====================================================================
class SocioPena(Base):
    __tablename__ = "socios_pena"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_socio = Column(Integer, unique=True, nullable=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(150), nullable=False)
    dni = Column(String(20), unique=True, nullable=True)
    telefono = Column(String(20), nullable=True)
    activo = Column(Boolean, default=True)
    fecha_alta = Column(DateTime, server_default=func.now())

    # Relación inversa: Permite saber si este socio físico tiene una cuenta de acceso web
    usuario_web = relationship("Usuario", back_populates="socio_interno", uselist=False)


# =====================================================================
# 2. CUENTAS DE ACCESO WEB (Pestaña 2 del Admin y Autenticación)
# =====================================================================
class Usuario(Base):
    __tablename__ = "usuarios_web"  # <--- Cambiado de "socios" a "usuarios_web"
    
    id = Column(Integer, primary_key=True, index=True)
    # Quitamos nombre y apellidos de aquí porque se consultarán a través de socio_interno si está vinculado
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(20), default="Socio")
    fecha_registro = Column(DateTime, server_default=func.now())
    activo = Column(Boolean, default=True)

    # El puente de conexión con la ficha física del socio (puede ser NULL)
    socio_pena_id = Column(Integer, ForeignKey("socios_pena.id", ondelete="SET NULL"), nullable=True)

    # Relaciones
    socio_interno = relationship("SocioPena", back_populates="usuario_web")
    cuotas = relationship("Cuota", back_populates="usuario")
    vehiculos = relationship("Vehiculo", back_populates="usuario", cascade="all, delete-orphan")
    reservas = relationship("Reserva", back_populates="usuario")


# =====================================================================
# 3. CUOTAS Y VEHÍCULOS (Apuntando a usuarios_web)
# =====================================================================
class Cuota(Base):
    __tablename__ = "cuotas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios_web.id", ondelete="RESTRICT"), nullable=False)
    ano_ejercicio = Column(Integer, nullable=False, default=2026)
    estado_pago = Column(String(20), default="Pendiente")
    stripe_intent_id = Column(String(100), nullable=True)
    fecha_pago = Column(DateTime, nullable=True)
    
    usuario = relationship("Usuario", back_populates="cuotas")


class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios_web.id", ondelete="CASCADE"), nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    plazas_totales = Column(Integer, nullable=False)
    
    usuario = relationship("Usuario", back_populates="vehiculos")


# =====================================================================
# 4. INFRAESTRUCTURA DE PARTIDOS Y VIAJES (Sin cambios estructurales)
# =====================================================================
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
    viaje_id = Column(Integer, ForeignKey("viajes.id", ondelete="CASCADE"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios_web.id", ondelete="CASCADE"), nullable=False)
    asientos_reservados = Column(Integer, default=1)
    
    tipo_reserva = Column(String(20), default="Viaje")
    motivo_evento = Column(String(255), nullable=True)
    estado_solicitud = Column(String(20), default="Pendiente")
    fecha_solicitada = Column(DateTime, server_default=func.now())
    
    viaje = relationship("Viaje", back_populates="reservas")
    usuario = relationship("Usuario", back_populates="reservas")


# =====================================================================
# 5. COMPLEMENTOS (Patrocinadores y Galería)
# =====================================================================
class Patrocinador(Base):
    __tablename__ = "patrocinadores"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    tipo_negocio = Column(String(50), default="Bar")
    logo_url = Column(String(255), nullable=True)
    enlace_web = Column(String(255), nullable=True)
    contribucion = Column(Float, default=0.0)


class FotoGaleria(Base):
    __tablename__ = "galeria_fotos"
    id = Column(Integer, primary_key=True, index=True)
    imagen_url = Column(String(255), nullable=False)
    titulo = Column(String(100), nullable=False)
    pie_foto = Column(String(255), nullable=True)
    fecha_subida = Column(DateTime, server_default=func.now())