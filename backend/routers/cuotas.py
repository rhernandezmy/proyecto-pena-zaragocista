import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
import stripe

# Cargamos la clave secreta de Stripe desde el .env seguro
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_simulada")

router = APIRouter(prefix="/cuotas", tags=["Cuotas y Pagos (Stripe)"])

@router.get("/usuario/{usuario_id}")
def obtener_historial_cuotas(usuario_id: int, db: Session = Depends(get_db)):
    """Devuelve el registro histórico de cuotas y estados de pago de un socio."""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="El socio especificado no existe.")
    return db.query(models.Cuota).filter(models.Cuota.usuario_id == usuario_id).all()

@router.post("/pagar")
def procesar_pago_cuota(pago: schemas.CuotaPagoCrear, db: Session = Depends(get_db)):
    """Simula la pasarela transaccional de Stripe y liquida la cuota anual del socio."""
    # 1. Verificar si el usuario existe en el censo de la base de datos
    usuario = db.query(models.Usuario).filter(models.Usuario.id == pago.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="El usuario/socio no está registrado.")

    # 2. Verificar si el socio ya tiene pagada la cuota de ese año concreto
    cuota_existente = db.query(models.Cuota).filter(
        models.Cuota.usuario_id == pago.usuario_id,
        models.Cuota.ano_ejercicio == pago.ano_ejercicio
    ).first()

    if cuota_existente and cuota_existente.estado_pago == "Pagado":
        raise HTTPException(
            status_code=400, 
            detail=f"El socio ya se encuentra al corriente de pago para el año fiscal {pago.ano_ejercicio}."
        )

    try:
        # 3. CONEXIÓN AL SDK DE STRIPE (Simulación Sandbox Educativo)
        # Generamos un ID de intento de pago seguro e imaginamos que Stripe devuelve el estado 'succeeded'
        intencion_pago = {
            "id": f"pi_sim_{os.urandom(8).hex()}",
            "status": "succeeded",
            "amount": 3000  # Ejemplo: 30.00 EUR expresado en céntimos
        }
        
        # 4. ACTUALIZACIÓN TRANSACCIONAL EN POSTGRESQL
        if cuota_existente:
            # Si la cuota existía en estado 'Pendiente', la actualizamos a 'Pagado'
            cuota_existente.estado_pago = "Pagado"
            cuota_existente.stripe_intent_id = intencion_pago["id"]
            cuota_existente.fecha_pago = datetime.now()
            cuota_actualizada = cuota_existente
        else:
            # Si no existía registro previo, creamos una nueva entrada en la tabla cuotas
            cuota_actualizada = models.Cuota(
                usuario_id=pago.usuario_id,
                ano_ejercicio=pago.ano_ejercicio,
                estado_pago = "Pagado",
                stripe_intent_id = intencion_pago["id"],
                fecha_pago = datetime.now()
            )
            db.add(cuota_actualizada)
        
        db.commit()
        db.refresh(cuota_actualizada)
        
        return {
            "ok": True,
            "mensaje": f"¡Pasarela Stripe autorizada! Cuota del año {pago.ano_ejercicio} liquidada con éxito.",
            "transaccion_id": intencion_pago["id"],
            "cuota": cuota_actualizada
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error crítico en la comunicación con la pasarela financiera: {str(e)}"
        )