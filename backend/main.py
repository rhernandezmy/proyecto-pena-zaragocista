from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import database
import models

# Creamos las tablas en la base de datos (si no existen)
models.Base.metadata.create_all(bind=database.engine)

# Inicializamos la aplicación
app = FastAPI(title="Peña Zaragocista API")

from pydantic import BaseModel

# ESQUEMA DE VALIDACIÓN: Definimos la plantilla de datos que Python 
# va a exigir para poder crear un partido nuevo.
class PartidoCrear(BaseModel):
    rival: str
    fecha: str
    lugar: str

# ESQUEMA DE VALIDACIÓN PARA VIAJES: Definimos qué datos son obligatorios
# enviar para poder dar de alta un viaje nuevo en la peña.
class ViajeCrear(BaseModel):
    partido_id: int                      # ID del partido obligatorio al que pertenece el viaje
    destino: str
    tipo_transporte: str = "Coche"       # Por defecto, viaje en coche particular
    plazas_totales: int
    plazas_disponibles: int
    precio: float = 0.0                  # Coste por defecto cero (a escotar)
    detalles_precio: str = None          # Texto opcional para aclarar las opciones de pago
    hace_noche: bool = False             # Por defecto se vuelve en el día del partido

# Nueva ruta para obtener los usuarios de la base de datos
@app.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    # Hacemos una consulta mágica: "Trae todos los registros de la tabla Usuario"
    usuarios_db = db.query(models.Usuario).all()
    return usuarios_db

# Ruta de prueba para verificar que el backend funciona
@app.get("/")
def read_root():
    return {"message": "¡Hola, Roberto! El backend de la Peña Zaragocista está funcionando"}

# Nueva ruta para obtener todos los partidos de la base de datos
@app.get("/partidos")
def obtener_partidos(db: Session = Depends(get_db)):
    # Le pedimos a la base de datos todos los registros de la tabla Partido
    partidos_db = db.query(models.Partido).all()
    return partidos_db

# Nueva ruta para obtener todos los viajes de la base de datos
@app.get("/viajes")
def obtener_viajes(db: Session = Depends(get_db)):
    # Le pedimos a la base de datos todos los registros de la tabla Viaje
    viajes_db = db.query(models.Viaje).all()
    return viajes_db

# RUTA POST: Permite registrar un nuevo partido en la base de datos
@app.post("/partidos")
def crear_partido(partido: PartidoCrear, db: Session = Depends(get_db)):
    # 1. Transformamos los datos que envía el usuario en un modelo de SQLAlchemy
    nuevo_partido = models.Partido(
        rival=partido.rival,
        fecha=partido.fecha,
        lugar=partido.lugar
    )
    # 2. Le decimos a la sesión de la base de datos que prepare el nuevo registro
    db.add(nuevo_partido)
    # 3. Guardamos los cambios definitivamente en PostgreSQL (Commit)
    db.commit()
    # 4. Refrescamos el objeto para que contenga el ID automático que le da la base de datos
    db.refresh(nuevo_partido)
    
    # 5. Devolvemos el partido recién creado para confirmar que todo está bien
    return nuevo_partido

# RUTA POST: Permite registrar un nuevo viaje organizado en la base de datos
@app.post("/viajes")
def crear_viaje(viaje: ViajeCrear, db: Session = Depends(get_db)):
    # 1. CONTROL DE SEGURIDAD: Buscamos en la base de datos el partido asociado
    partido_asociado = db.query(models.Partido).filter(models.Partido.id == viaje.partido_id).first()
    
    # Si el partido no existe, lanzamos un error 404
    if not partido_asociado:
        raise HTTPException(status_code=404, detail="El partido especificado no existe.")
        
    # 2. REGLA DE NEGOCIO: Si el partido es en casa, prohibimos crear el viaje
    if "Ibercaja estadio" in partido_asociado.lugar:
        raise HTTPException(
            status_code=400, 
            detail="No se pueden organizar viajes para partidos en el Ibercaja Estadio (Local)."
        )

    # 3. Si pasa los controles, mapeamos y guardamos el viaje
    nuevo_viaje = models.Viaje(
        partido_id=viaje.partido_id,  # Guardamos la relación
        destino=viaje.destino,
        tipo_transporte=viaje.tipo_transporte,
        plazas_totales=viaje.plazas_totales,
        plazas_disponibles=viaje.plazas_disponibles,
        precio=viaje.precio,
        detalles_precio=viaje.detalles_precio,
        hace_noche=viaje.hace_noche
    )
    db.add(nuevo_viaje)
    db.commit()
    db.refresh(nuevo_viaje)
    
    return nuevo_viaje

# RUTA DELETE: Elimina un partido específico usando su ID
@app.delete("/partidos/{partido_id}")
def borrar_partido(partido_id: int, db: Session = Depends(get_db)):
    # 1. Buscamos el partido en la base de datos por su ID
    partido = db.query(models.Partido).filter(models.Partido.id == partido_id).first()
    
    # 2. CONTROL DE SEGURIDAD: Si el partido no existe, lanzamos un error 404
    if not partido:
        raise HTTPException(status_code=404, detail="El partido que intentas borrar no existe.")
    
    # 3. Si existe, le decimos a la sesión que lo elimine
    db.delete(partido)
    # 4. Consolidamos los cambios en PostgreSQL (aquí actúa el CASCADE y borra sus viajes)
    db.commit()
    
    # 5. Devolvemos un mensaje de confirmación
    return {"ok": True, "mensaje": f"Partido con ID {partido_id} eliminado con éxito de la base de datos."}

# RUTA DELETE: Elimina un viaje específico de la peña usando su ID
@app.delete("/viajes/{viaje_id}")
def borrar_viaje(viaje_id: int, db: Session = Depends(get_db)):
    # 1. Buscamos el viaje por su ID en la base de datos
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    
    # 2. CONTROL DE SEGURIDAD: Si no existe, lanzamos error 404
    if not viaje:
        raise HTTPException(status_code=404, detail="El viaje que intentas borrar no existe o ya ha sido eliminado.")
    
    # 3. Si existe, lo borramos de la sesión
    db.delete(viaje)
    # 4. Confirmamos los cambios en PostgreSQL
    db.commit()
    
    # 5. Respuesta de éxito
    return {"ok": True, "mensaje": f"Viaje con ID {viaje_id} cancelado y eliminado correctamente."}

# RUTA PUT: Permite modificar los datos de un partido existente
@app.put("/partidos/{partido_id}")
def actualizar_partido(partido_id: int, partido_editado: PartidoCrear, db: Session = Depends(get_db)):
    # 1. Buscamos el partido original en la base de datos
    db_partido = db.query(models.Partido).filter(models.Partido.id == partido_id).first()
    
    # 2. CONTROL DE SEGURIDAD: Si no existe, avisamos
    if not db_partido:
        raise HTTPException(status_code=404, detail="No se puede actualizar porque el partido no existe.")
    
    # 3. Sobrescribimos los campos con los nuevos datos que nos envía el usuario
    db_partido.rival = partido_editado.rival
    db_partido.fecha = partido_editado.fecha
    db_partido.lugar = partido_editado.lugar
    
    # 4. Guardamos los cambios en la base de datos a través de la sesión (CORREGIDO)
    db.commit()
    # 5. Refrescamos para ver cómo ha quedado
    db.refresh(db_partido)
    
    # 6. Devolvemos el partido ya modificado
    return db_partido