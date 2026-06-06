from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter(tags=["Mundial"]) 
API_TOKEN = os.getenv("API_TOKEN")

@router.get("/partidos-espana")
async def obtener_partidos():
    if not API_TOKEN:
        raise HTTPException(status_code=500, detail="API_TOKEN no configurado en el servidor.")
        
    # URL de la API (WC es World Cup)
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    headers = {'X-Auth-Token': API_TOKEN}
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url, headers=headers)
            
            # Si el token es inválido o se alcanzó el límite de peticiones
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Error de la API externa: {response.text}"
                )
            
            data = response.json()
            
            # Filtrado de partidos de España
            # Buscamos 'Spain' en homeTeam o awayTeam
            partidos_espana = [
                m for m in data.get('matches', []) 
                if (m.get('homeTeam', {}).get('name') == "Spain" or 
                    m.get('awayTeam', {}).get('name') == "Spain")
            ]
            
            return {"partidos": partidos_espana}
            
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503, 
                detail=f"No se pudo conectar con el servicio de deportes: {str(exc)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error inesperado al obtener los partidos: {str(e)}"
            )