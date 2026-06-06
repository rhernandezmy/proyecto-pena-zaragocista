from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario, Reserva

router = APIRouter(prefix="/panel", tags=["Panel"])

@router.get("/data/{email}")
def get_panel_data(email: str, db: Session = Depends(get_db)):
    socio = db.query(Usuario).filter(Usuario.email == email).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    # Optimizamos consultas usando los atributos relacionales definidos en models.py
    return {
        "nombre": socio.nombre,
        "cuotas": [{"ano": c.ano_ejercicio, "estado": c.estado_pago} for c in socio.cuotas],
        "reservas": [
            {"destino": r.viaje.destino, "asientos": r.asientos_reservados} 
            for r in db.query(Reserva).filter(Reserva.nombre_socio == socio.nombre).all()
        ]
    }