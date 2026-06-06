import os
from fastapi import APIRouter
import httpx
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

router = APIRouter(prefix="/mundial", tags=["Mundial"])

# Leer el token desde las variables de entorno
API_TOKEN = os.getenv("API_TOKEN")

@router.get("/partidos-espana")
async def obtener_partidos():
    if not API_TOKEN:
        return {"error": "API_TOKEN no configurado en el servidor"}
        
    async with httpx.AsyncClient() as client:
        url = "https://api.football-data.org/v4/competitions/WC/matches"
        headers = {'X-Auth-Token': API_TOKEN}
        
        try:
            response = await client.get(url, headers=headers)
            data = response.json()
            
            # Filtro
            espana = [m for m in data.get('matches', []) 
                      if m['homeTeam']['name'] == "Spain" or m['awayTeam']['name'] == "Spain"]
            
            return {"partidos": espana}
        except Exception as e:
            return {"error": "No se pudieron obtener los datos", "detalle": str(e)}