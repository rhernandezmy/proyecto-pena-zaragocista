from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db

router = APIRouter(prefix="/viajes", tags=["Viajes"])

# =========================================================================
# 1. OBTENER TODOS LOS VIAJES Y COCHES
# =========================================================================
@router.get("", response_model=None)
@router.get("/", response_model=None)
def obtener_viajes(db: Session = Depends(get_db)):
    return db.query(models.Viaje).order_by(models.Viaje.id.desc()).all()

# =========================================================================
# 2. CREAR UN NUEVO VIAJE (Peña o Coche Compartido)
# =========================================================================
@router.post("", response_model=schemas.Viaje, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=schemas.Viaje, status_code=status.HTTP_201_CREATED)
def crear_viaje(viaje: schemas.ViajeCrear, db: Session = Depends(get_db)):
    # Asignamos de forma flexible partido_id / partido_api_id si no vienen informados
    datos_viaje = viaje.model_dump()
    
    # 1. Asegurar que el objeto Viaje tenga mapeados sus IDs clave
    if not datos_viaje.get("partido_api_id") and datos_viaje.get("partido_id"):
        datos_viaje["partido_api_id"] = datos_viaje["partido_id"]
    elif not datos_viaje.get("partido_id") and datos_viaje.get("partido_api_id"):
        datos_viaje["partido_id"] = datos_viaje["partido_api_id"]

    # 2. Crear y guardar el viaje sin bloqueos
    nuevo_viaje = models.Viaje(**datos_viaje)
    db.add(nuevo_viaje)
    db.commit()
    db.refresh(nuevo_viaje)
    return nuevo_viaje

# =========================================================================
# 3. BORRAR VIAJE (Permite al Admin gestionar la lista)
# =========================================================================
@router.delete("/{viaje_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_viaje(viaje_id: int, db: Session = Depends(get_db)):
    viaje = db.query(models.Viaje).filter(models.Viaje.id == viaje_id).first()
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado.")
    
    # Borramos primero las reservas vinculadas a este viaje para evitar error de clave foránea
    db.query(models.Reserva).filter(models.Reserva.viaje_id == viaje_id).delete()
    
    db.delete(viaje)
    db.commit()
    return None