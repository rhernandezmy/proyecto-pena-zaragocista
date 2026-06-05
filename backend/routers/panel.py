from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario, Viaje, Reserva, Cuota

router = APIRouter()

@router.get("/panel-data/{email}")
def get_panel_data(email: str, db: Session = Depends(get_db)):
    # 1. Buscamos al socio
    socio = db.query(Usuario).filter(Usuario.email == email).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    # 2. Obtenemos sus cuotas
    cuotas = [{"ano": c.ano_ejercicio, "estado": c.estado_pago} for c in socio.cuotas]
    
    # 3. Obtenemos sus reservas (buscando por nombre o email)
    reservas = db.query(Reserva).filter(Reserva.nombre_socio == socio.nombre).all()
    lista_reservas = [{"destino": r.viaje.destino, "asientos": r.asientos_reservados} for r in reservas]
    
    return {
        "nombre": socio.nombre,
        "cuotas": cuotas,
        "reservas": lista_reservas
    }