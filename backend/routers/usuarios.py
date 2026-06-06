from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter(prefix="/usuarios", tags=["General"])

@router.get("/socios")
def obtener_socios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()