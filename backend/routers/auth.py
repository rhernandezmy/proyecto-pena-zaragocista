from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import models, database

router = APIRouter(prefix="/login", tags=["Autenticación"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

@router.post("")
def login(login_data: LoginSchema, db: Session = Depends(database.get_db)):
    socio = db.query(models.Usuario).filter(models.Usuario.email == login_data.email).first()
    
    if not socio or not pwd_context.verify(login_data.password, socio.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Correo o contraseña incorrectos"
        )
    
    return {"nombre": socio.nombre, "rol": socio.rol}