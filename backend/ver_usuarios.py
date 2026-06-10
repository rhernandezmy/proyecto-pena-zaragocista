from database import SessionLocal
import models

db = SessionLocal()
usuarios = db.query(models.Usuario).all()

print("\n📋 USUARIOS REALES QUE VE PYTHON:")
for u in usuarios:
    print(f"ID: {u.id} | Nombre: {u.nombre} | Email: {u.email} | Rol: {u.rol}")
db.close()