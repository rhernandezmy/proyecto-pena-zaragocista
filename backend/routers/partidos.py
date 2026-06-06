from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(prefix="/partidos", tags=["Partidos"])

@router.get("")
def obtener_partidos(db: Session = Depends(get_db)):
    return db.query(models.Partido).all()

@router.post("")
def crear_partido(partido: schemas.PartidoCrear, db: Session = Depends(get_db)):
    datos = partido.model_dump()
    
    if partido.rival_maestro_id:
        maestro = db.query(models.RivalMaestro).filter(models.RivalMaestro.id == partido.rival_maestro_id).first()
        if maestro:
            datos.update({
                "rival": maestro.nombre_equipo,
                "lugar": maestro.estadio,
                "latitud": maestro.latitud,
                "longitud": maestro.longitud
            })

    nuevo_partido = models.Partido(**datos)
    db.add(nuevo_partido)
    db.commit()
    db.refresh(nuevo_partido)
    return nuevo_partido

@router.put("/{partido_id}")
def actualizar_partido(partido_id: int, partido_editado: schemas.PartidoCrear, db: Session = Depends(get_db)):
    db_partido = db.query(models.Partido).filter(models.Partido.id == partido_id).first()
    if not db_partido:
        raise HTTPException(status_code=404, detail="Partido no encontrado.")
    
    # Actualizar campos
    for key, value in partido_editado.model_dump().items():
        setattr(db_partido, key, value)
        
    db.commit()
    db.refresh(db_partido)
    return db_partido

@router.delete("/{partido_id}")
def borrar_partido(partido_id: int, db: Session = Depends(get_db)):
    partido = db.query(models.Partido).filter(models.Partido.id == partido_id).first()
    if not partido:
        raise HTTPException(status_code=404, detail="Partido no encontrado.")
    
    db.delete(partido)
    db.commit()
    return {"mensaje": "Partido eliminado correctamente."}