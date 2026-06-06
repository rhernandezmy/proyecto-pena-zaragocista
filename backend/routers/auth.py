from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import bcrypt
import models, database
from pydantic import BaseModel, EmailStr

router = APIRouter() # Sin prefix aquí

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

@router.post("/login") # La ruta se define aquí
def login(login_data: LoginSchema, db: Session = Depends(database.get_db)):
    print("¡Ha llegado la petición al servidor!") # Si sale esto en la consola, ya funciona
    socio = db.query(models.Usuario).filter(models.Usuario.email == login_data.email).first()
    
    if not socio:
        raise HTTPException(status_code=401, detail="Correo incorrecto")

    if not bcrypt.checkpw(login_data.password.encode('utf-8'), socio.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    return {"nombre": socio.nombre, "rol": socio.rol, "id": socio.id}