from fastapi import APIRouter
import feedparser

router = APIRouter(prefix="/noticias", tags=["Noticias"])

@router.get("")
def obtener_noticias():
    fuentes = [
        "https://www.realzaragoza.com/rss",
        "https://www.heraldo.es/rss/deportes/futbol/real-zaragoza.xml"
    ]
    
    noticias = []
    for url in fuentes:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            noticias.append({
                "titulo": entry.get('title', 'Sin título'),
                "fecha": entry.get('published', 'N/A'),
                "resumen": (entry.get('summary', '')[:147] + "...") if 'summary' in entry else "Sin resumen",
                "link": entry.get('link', '#')
            })
    return {"noticias": noticias}