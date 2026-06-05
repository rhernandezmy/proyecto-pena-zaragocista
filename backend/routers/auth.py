from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, database

router = APIRouter(prefix="/login", tags=["Autenticación"])

# Esquema para el login
class LoginSchema(BaseModel):
    email: str
    password: str

@router.post("")
def login(login_data: LoginSchema, db: Session = Depends(database.get_db)):
    # Buscamos al usuario por su email
    socio = db.query(models.Usuario).filter(models.Usuario.email == login_data.email).first()
    
    # Comprobamos si existe y si la contraseña coincide
    if not socio or socio.password_hash != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Correo o contraseña incorrectos"
        )
    
    return {"nombre": socio.nombre}