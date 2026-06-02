from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

# Inicializamos el enrutador modular
router = APIRouter(prefix="/partidos", tags=["Partidos"])

@router.get("")
def obtener_partidos(db: Session = Depends(get_db)):
    return db.query(models.Partido).all()

@router.post("")
def crear_partido(partido: schemas.PartidoCrear, db: Session = Depends(get_db)):
    # Inicializamos las variables con lo que venga del formulario manual
    nombre_rival = partido.rival
    estadio_lugar = partido.lugar
    lat = partido.latitud
    lon = partido.longitud

    # Si nos pasan un ID de la agenda, autocompletamos con los datos fijos
    if partido.rival_maestro_id:
        rival_fijo = db.query(models.RivalMaestro).filter(models.RivalMaestro.id == partido.rival_maestro_id).first()
        if rival_fijo:
            nombre_rival = rival_fijo.nombre_equipo
            estadio_lugar = rival_fijo.estadio
            lat = rival_fijo.latitud
            lon = rival_fijo.longitud

    nuevo_partido = models.Partido(
        rival=nombre_rival,
        fecha=partido.fecha,
        lugar=estadio_lugar,
        latitud=lat,
        longitud=lon,
        rival_maestro_id=partido.rival_maestro_id
    )
    db.add(nuevo_partido)
    db.commit()
    db.refresh(nuevo_partido)
    return nuevo_partido

@router.put("/{partido_id}")
def actualizar_partido(partido_id: int, partido_editado: schemas.PartidoCrear, db: Session = Depends(get_db)):
    db_partido = db.query(models.Partido).filter(models.Partido.id == partido_id).first()
    if not db_partido:
        raise HTTPException(status_code=404, detail="No se puede actualizar porque el partido no existe.")
    db_partido.rival = partido_editado.rival
    db_partido.fecha = partido_editado.fecha
    db_partido.lugar = partido_editado.lugar
    db_partido.latitud = partido_editado.latitud
    db_partido.longitud = partido_editado.longitud
    db.commit()
    db.refresh(db_partido)
    return db_partido

@router.delete("/{partido_id}")
def borrar_partido(partido_id: int, db: Session = Depends(get_db)):
    partido = db.query(models.Partido).filter(models.Partido.id == partido_id).first()
    if not partido:
        raise HTTPException(status_code=404, detail="El partido que intentas borrar no existe.")
    
    # Capturar correos de conductores afectados antes de que actúe el CASCADE físico
    correos_afectados = set()
    for viaje in partido.viajes:
        if viaje.email_conductor:
            correos_afectados.add(viaje.email_conductor)
            
    if correos_afectados:
        print(f"\n[ALERTA INTERNA] Enviando correos automáticos de cancelación de viaje a: {list(correos_afectados)}")

    db.delete(partido)
    db.commit()
    return {"ok": True, "mensaje": f"Partido con ID {partido_id} eliminado con éxito."}