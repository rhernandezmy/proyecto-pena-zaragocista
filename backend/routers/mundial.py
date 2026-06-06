from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter(prefix="/mundial", tags=["Mundial"])
API_TOKEN = os.getenv("API_TOKEN")

@router.get("/partidos-espana")
async def obtener_partidos():
    if not API_TOKEN:
        raise HTTPException(status_code=500, detail="API_TOKEN no configurado.")
        
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    headers = {'X-Auth-Token': API_TOKEN}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            espana = [
                m for m in data.get('matches', []) 
                if m['homeTeam']['name'] == "Spain" or m['awayTeam']['name'] == "Spain"
            ]
            return {"partidos": espana}
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Error al conectar con API externa.")
        except Exception:
            raise HTTPException(status_code=500, detail="Error interno al procesar datos.")