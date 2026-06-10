from fastapi import APIRouter
import feedparser

router = APIRouter()

@router.get("")
def obtener_noticias():
    feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # Lista de fuentes con un nombre amigable para identificar el medio
    fuentes = [
        {"nombre": "Real Zaragoza", "url": "https://www.realzaragoza.com/rss"},
        {"nombre": "Heraldo", "url": "https://www.heraldo.es/rss/deportes/futbol/real-zaragoza.xml"},
        {"nombre": "Marca", "url": "https://e00-marca.uecdn.es/rss/futbol/zaragoza.xml"}
    ]
    
    noticias = []
    for fuente in fuentes:
        feed = feedparser.parse(fuente["url"])
        for entry in feed.entries[:3]: # Cogemos 3 de cada una
            noticias.append({
                "titulo": entry.get('title', 'Sin título'),
                "fecha": entry.get('published', 'N/A'),
                "resumen": (entry.get('summary', '')[:100] + "...") if 'summary' in entry else "Sin resumen",
                "link": entry.get('link', '#'),
                "fuente": fuente["nombre"] # <-- Aquí añadimos el medio
            })
    return {"noticias": noticias}