from sqlalchemy import Boolean, Column, Float, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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
    cuotas = relationship("Cuota", back_populates="usuario", cascade="all, delete-orphan")

# Definimos el modelo de datos para los partidos
class Partido(Base):
    __tablename__ = "partidos"

    id = Column(Integer, primary_key=True, index=True)
    rival = Column(String(100), nullable=False)
    fecha = Column(DateTime, nullable=False)
    lugar = Column(String(100), default="La Romareda")  # Por defecto jugamos en casa
    estado = Column(String(20), default="Programado")   # Programado, Jugado, Aplazado
    latitud = Column(Float, nullable=True)   # Para mostrar el partido en un mapa (Ej: 41.656)
    longitud = Column(Float, nullable=True)  # Para mostrar el partido en un mapa (Ej: -0.877)

    rival_maestro_id = Column(Integer, ForeignKey("rivales_maestros.id", ondelete="SET NULL"), nullable=True) # Relación opcional con el rival maestro
    
    # Relaciones
    viajes = relationship("Viaje", back_populates="partido", cascade="all, delete-orphan") # Un partido puede tener varios viajes asociados
    rival_maestro = relationship("RivalMaestro", back_populates="partidos")
   

# Definimos el modelo de datos para los viajes
# Definimos el modelo de datos para los viajes
class Viaje(Base):
    __tablename__ = "viajes"

    id = Column(Integer, primary_key=True, index=True)
    destino = Column(String(100), nullable=False)
    
    # 🌟 NUEVA COLUMNA: Correo de la persona que conduce el coche
    email_conductor = Column(String(100), nullable=False, default="presentesxelescudo@gmail.com")

    # CLAVE FORÁNEA: Conecta este viaje con un ID de la tabla partidos. Si el partido se borra, sus viajes asociados se borran en cascada.
    partido_id = Column(Integer, ForeignKey("partidos.id", ondelete="CASCADE"), nullable=False)

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

    partido = relationship("Partido", back_populates="viajes")     # Relación directa: cada viaje pertenece a un único partido
    reservas = relationship("Reserva", back_populates="viaje", cascade="all, delete-orphan") # Un viaje puede tener varias reservas asociadas, si el viaje se borra, sus reservas también se borran en cascada
    # Coordenadas para mostrar el destino en un mapa (Ej: Estadio de El Alcoraz)
    latitud = Column(Float, nullable=True)   # Para la chincheta del mapa (Ej: 39.494)
    longitud = Column(Float, nullable=True)  # Para la chincheta del mapa (Ej: -0.364)

# MODELO DE RESERVAS: Para controlar qué socios van en cada coche/viaje
class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    viaje_id = Column(Integer, ForeignKey("viajes.id", ondelete="CASCADE"), nullable=False)
    nombre_socio = Column(String, nullable=False)
    asientos_reservados = Column(Integer, default=1)

    # Relación: Cada reserva pertenece a un viaje
    viaje = relationship("Viaje", back_populates="reservas")

# MODELO DE PATROCINADORES: Negocios o bares colaboradores de la peña
class Patrocinador(Base):
    __tablename__ = "patrocinadores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    tipo_negocio = Column(String, default="Bar")  # Bar, Tienda, Gimnasio, etc.
    logo_url = Column(String, nullable=True)       # Enlace a la imagen de su logo
    contribucion = Column(Float, default=0.0)      # Cuánto aporta al año a la peña

# TABLA MAESTRA DE RIVALES: Agenda fija de equipos, estadios y coordenadas
class RivalMaestro(Base):
    __tablename__ = "rivales_maestros"

    id = Column(Integer, primary_key=True, index=True)
    nombre_equipo = Column(String, unique=True, nullable=False) # Ej: "Levante UD"
    estadio = Column(String, nullable=False)                    # Ej: "Estadio Ciutat de València"
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)

    # Relación: Un rival maestro puede tener muchos partidos a lo largo de las temporadas
    partidos = relationship("Partido", back_populates="rival_maestro")

# MODELO DE CUOTAS: Registro de anualidades y pasarela Stripe
class Cuota(Base):
    __tablename__ = "cuotas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    ano_ejercicio = Column(Integer, nullable=False)              # Ej: 2026
    estado_pago = Column(String(20), default="Pendiente")         # 'Pendiente' o 'Pagado'
    stripe_intent_id = Column(String(100), nullable=True)         # ID de la transacción simulada de Stripe
    fecha_pago = Column(DateTime, nullable=True)                  # Cuándo pagó efectivamente

    # Relación inversa hacia el usuario dueño de la cuota
    usuario = relationship("Usuario", back_populates="cuotas")