from fastapi import APIRouter
import feedparser

router = APIRouter(prefix="/noticias", tags=["Noticias"])

@router.get("/")
def obtener_noticias():
    fuentes = [
        "https://www.realzaragoza.com/rss",
        "https://www.heraldo.es/rss/deportes/futbol/real-zaragoza.xml"
    ]
    
    noticias = []
    for url in fuentes:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]: # 3 de cada fuente
            noticias.append({
                "titulo": entry.title,
                "fecha": getattr(entry, 'published', 'Fecha no disponible'),
                "resumen": getattr(entry, 'summary', 'Sin resumen disponible')[:150] + "...",
                "link": entry.link
            })
    return noticias