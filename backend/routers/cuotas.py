import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_simulada")
router = APIRouter(prefix="/cuotas", tags=["Cuotas y Pagos (Stripe)"])

@router.get("/usuario/{usuario_id}")
def obtener_historial_cuotas(usuario_id: int, db: Session = Depends(get_db)):
    if not db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first():
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    return db.query(models.Cuota).filter(models.Cuota.usuario_id == usuario_id).all()

@router.post("/pagar")
def procesar_pago_cuota(pago: schemas.CuotaPagoCrear, db: Session = Depends(get_db)):
    cuota = db.query(models.Cuota).filter(
        models.Cuota.usuario_id == pago.usuario_id,
        models.Cuota.ano_ejercicio == pago.ano_ejercicio
    ).first()

    if cuota and cuota.estado_pago == "Pagado":
        raise HTTPException(status_code=400, detail="Cuota ya pagada.")

    try:
        # Simulacro Stripe
        intent_id = f"pi_sim_{os.urandom(8).hex()}"
        
        if cuota:
            cuota.estado_pago = "Pagado"
            cuota.stripe_intent_id = intent_id
            cuota.fecha_pago = datetime.now()
        else:
            cuota = models.Cuota(
                usuario_id=pago.usuario_id,
                ano_ejercicio=pago.ano_ejercicio,
                estado_pago="Pagado",
                stripe_intent_id=intent_id,
                fecha_pago=datetime.now()
            )
            db.add(cuota)
        
        db.commit()
        db.refresh(cuota)
        return {"ok": True, "transaccion_id": intent_id, "cuota": cuota}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))