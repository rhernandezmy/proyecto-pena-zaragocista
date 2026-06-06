from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(prefix="/rivales-maestros", tags=["Agenda de Rivales"])

@router.get("")
def obtener_agenda_rivales(db: Session = Depends(get_db)):
    return db.query(models.RivalMaestro).all()

@router.post("")
def añadir_rival_a_agenda(rival: schemas.RivalMaestroCrear, db: Session = Depends(get_db)):
    nuevo_rival = models.RivalMaestro(**rival.model_dump())
    db.add(nuevo_rival)
    db.commit()
    db.refresh(nuevo_rival)
    return nuevo_rival