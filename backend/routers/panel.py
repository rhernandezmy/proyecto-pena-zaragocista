from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models 

router = APIRouter(prefix="/panel", tags=["Panel"])

@router.get("/data/{email}")
def get_panel_data(email: str, db: Session = Depends(get_db)):
    # 1. Buscamos al socio
    socio = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    # 2. Retornamos los datos usando las relaciones que ya definiste en models.py
    return {
        "nombre": socio.nombre,
        "cuotas": [{"ano": c.ano_ejercicio, "estado": c.estado_pago} for c in socio.cuotas],
        "reservas": [
            {
                "destino": r.viaje.destino, 
                "asientos": r.asientos_reservados
            } for r in socio.reservas # Usamos la relación directa del objeto socio
        ]
    }