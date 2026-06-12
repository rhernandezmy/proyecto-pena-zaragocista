from fastapi import APIRouter
import feedparser
from datetime import datetime, timedelta

router = APIRouter()

# Estructura de caché en memoria para no saturar las webs de noticias ni ralentizar tu defensa
cache_noticias = {
    "datos": [],
    "ultima_actualizacion": None
}

@router.get("")
def obtener_noticias():
    feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    ahora = datetime.now()
    
    # 1. Si tenemos noticias en caché y no han pasado 15 minutos, las devolvemos al instante
    if cache_noticias["ultima_actualizacion"] and ahora - cache_noticias["ultima_actualizacion"] < timedelta(minutes=15):
        return {"noticias": cache_noticias["datos"]}
    
    # 2. Si no hay caché o ha caducado, consultamos los feeds reales
    fuentes = [
        {"nombre": "Real Zaragoza", "url": "https://www.realzaragoza.com/rss"},
        {"nombre": "Heraldo", "url": "https://www.heraldo.es/rss/deportes/futbol/real-zaragoza.xml"},
        {"nombre": "Marca", "url": "https://e00-marca.uecdn.es/rss/futbol/zaragoza.xml"}
    ]
    
    noticias = []
    for fuente in fuentes:
        try:
            feed = feedparser.parse(fuente["url"])
            for entry in feed.entries[:3]: # Seguimos cogiendo las 3 últimas de cada medio
                
                # 🌟 EXTRACCIÓN DINÁMICA DE IMÁGENES (Para que las tarjetas de Bootstrap queden espectaculares)
                imagen = "assets/img/noticia-defecto.jpg" # Tu ruta por defecto si el RSS no trae foto
                if "media_content" in entry and entry.media_content:
                    imagen = entry.media_content[0]["url"]
                elif "enclosure" in entry:
                    imagen = entry.enclosure.url
                elif "links" in entry:
                    for link in entry.links:
                        if "image" in link.get("type", ""):
                            imagen = link.get("href")
                
                noticias.append({
                    "titulo": entry.get('title', 'Sin título'),
                    "fecha": entry.get('published', 'N/A'),
                    "resumen": (entry.get('summary', '')[:120] + "...") if 'summary' in entry else "Sin resumen",
                    "link": entry.get('link', '#'),
                    "fuente": fuente["nombre"],
                    "imagen": imagen # <-- Añadimos la imagen real parseada
                })
        except Exception as e:
            print(f"⚠️ Error controlado al leer el RSS de {fuente['nombre']}: {str(e)}")
            
    # 3. Guardamos los resultados frescos en la caché
    cache_noticias["datos"] = noticias
    cache_noticias["ultima_actualizacion"] = ahora
    
    return {"noticias": noticias}