import re
import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx
from bs4 import BeautifulSoup

router = APIRouter(tags=["Real Zaragoza"])

cache_zaragoza = {
    "partidos": [],
    "clasificacion": [],
    "ultima_actualizacion": None,
    "temporada": 2026
}

scheduler = AsyncIOScheduler()

# Usamos Futbolme para ambas cosas: es rápido, ligero y no sufre bloqueos de Cloudflare como Marca en la nube.
FUTBOLME_CALENDARIO_URL = "https://futbolme.com/resultados-directo/torneo/primera-federacion-grupo-2/3056/calendario"
FUTBOLME_CLASIFICACION_URL = "https://futbolme.com/resultados-directo/torneo/primera-federacion-grupo-2/3056/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9"
}

def extraer_datos_futbolme_sync():
    global cache_zaragoza

    partidos_extraidos = []
    clasificacion_extraida = []

    try:
        with httpx.Client(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
            
            # -----------------------------------------------------------------
            # 1. CLASIFICACIÓN VÍA BEAUTIFULSOUP
            # -----------------------------------------------------------------
            try:
                res_clas = client.get(FUTBOLME_CLASIFICACION_URL)
                if res_clas.status_code == 200:
                    soup = BeautifulSoup(res_clas.text, "html.parser")
                    filas = soup.select("table tbody tr")
                    
                    equipos_temporales = []

                    for fila in filas:
                        celdas = fila.find_all(["td", "th"])
                        if len(celdas) < 7:
                            continue

                        celda_equipo = celdas[1]
                        span_largo = celda_equipo.select_one(".hidden-xs, .nombre-largo, span:last-child")
                        
                        if span_largo and len(span_largo.get_text(strip=True)) > 2:
                            equipo_nombre = span_largo.get_text(strip=True)
                        else:
                            link = celda_equipo.find("a")
                            equipo_nombre = link.get_text(strip=True) if link else celda_equipo.get_text(strip=True)

                        # Deduplicaciones de nombres
                        palabras = equipo_nombre.split()
                        if len(palabras) > 2 and palabras[0].lower() == palabras[-1].lower():
                            equipo_nombre = " ".join(palabras[1:])
                        
                        mitad = len(equipo_nombre) // 2
                        if mitad > 3 and equipo_nombre[:mitad].strip().lower() in equipo_nombre[mitad:].strip().lower():
                            equipo_nombre = equipo_nombre[mitad:].strip()

                        if not equipo_nombre or len(equipo_nombre) < 2:
                            continue

                        numeros = []
                        for c in celdas[2:]:
                            val = re.sub(r'[^\d-]', '', c.get_text(strip=True))
                            if val.replace('-', '').isdigit() and val != '':
                                numeros.append(int(val))

                        if len(numeros) >= 7:
                            pts = numeros[0]
                            pj = numeros[1]
                            pg = numeros[2]
                            pe = numeros[3]
                            pp = numeros[4]
                            gf = numeros[5]
                            gc = numeros[6]

                            equipos_temporales.append({
                                "name": equipo_nombre,
                                "points": pts,
                                "pj": pj, "pg": pg, "pe": pe, "pp": pp,
                                "gf": gf, "gc": gc, "dg": gf - gc
                            })

                    equipos_temporales.sort(key=lambda x: (x["points"], x["dg"], x["gf"]), reverse=True)

                    for pos_real, eq in enumerate(equipos_temporales, 1):
                        if pos_real > 20:
                            break

                        clasificacion_extraida.append({
                            "rank": pos_real,
                            "team": {
                                "name": eq["name"],
                                "logo": "https://media.api-sports.io/football/teams/732.png" if "zaragoza" in eq["name"].lower() else ""
                            },
                            "points": eq["points"],
                            "all": {
                                "played": eq["pj"],
                                "win": eq["pg"],
                                "draw": eq["pe"],
                                "lose": eq["pp"],
                                "goals": {"for": eq["gf"], "against": eq["gc"]}
                            },
                            "goalsDiff": eq["dg"]
                        })
            except Exception as e_clas:
                print(f"⚠️ Error obteniendo clasificación: {str(e_clas)}")

            # -----------------------------------------------------------------
            # 2. CALENDARIO / PARTIDOS VÍA BEAUTIFULSOUP (FUTBOLME)
            # -----------------------------------------------------------------
            try:
                res_cal = client.get(FUTBOLME_CALENDARIO_URL)
                if res_cal.status_code == 200:
                    soup_cal = BeautifulSoup(res_cal.text, "html.parser")
                    
                    # Buscamos bloques de partidos o filas donde aparezca el Zaragoza
                    filas_partidos = soup_cal.select("tr, .match-row, .partido-item, li")
                    id_counter = 1

                    for fila in filas_partidos:
                        texto_fila = fila.get_text(" ", strip=True)
                        if "zaragoza" in texto_fila.lower():
                            # Intentamos extraer los equipos y el marcador de la fila o contenedor
                            links_equipos = fila.find_all("a")
                            nombres_encontrados = [l.get_text(strip=True) for l in links_equipos if len(l.get_text(strip=True)) > 2]
                            
                            local = "Real Zaragoza"
                            visitante = "Rival"
                            if len(nombres_encontrados) >= 2:
                                local = nombres_encontrados[0]
                                visitante = nombres_encontrados[1]
                            elif len(nombres_encontrados) == 1:
                                if "zaragoza" in nombres_encontrados[0].lower():
                                    local = nombres_encontrados[0]
                                    visitante = "Rival"
                                else:
                                    local = "Real Zaragoza"
                                    visitante = nombres_encontrados[0]

                            # Buscar goles o resultado si ya se jugó
                            home_goals, away_goals = None, None
                            status_short = "NS"
                            resultado_signo = None

                            match_goles = re.search(r'(\d+)\s*[-–]\s*(\d+)', texto_fila)
                            if match_goles:
                                home_goals = int(match_goles.group(1))
                                away_goals = int(match_goles.group(2))
                                status_short = "FT"

                                zaragoza_es_local = "zaragoza" in local.lower()
                                g_zaragoza = home_goals if zaragoza_es_local else away_goals
                                g_rival = away_goals if zaragoza_es_local else home_goals

                                if g_zaragoza > g_rival:
                                    resultado_signo = "Victoria"
                                elif g_zaragoza < g_rival:
                                    resultado_signo = "Derrota"
                                else:
                                    resultado_signo = "Empate"

                            # Intentar buscar fecha u hora aproximada
                            fecha_iso = "2026-09-01T20:00:00"
                            match_fecha = re.search(r'(\d{1,2})/(\d{1,2})', texto_fila)
                            if match_fecha:
                                d = match_fecha.group(1).zfill(2)
                                m = match_fecha.group(2).zfill(2)
                                fecha_iso = f"2026-{m}-{d}T20:00:00"

                            # Evitar duplicados exactos en la lista
                            partido_obj = {
                                "fixture": {
                                    "id": id_counter,
                                    "date": fecha_iso,
                                    "status": {"short": status_short},
                                    "resultado_signo": resultado_signo
                                },
                                "league": {
                                    "name": "Primera Federación - Grupo 2",
                                    "round": f"Jornada {id_counter}"
                                },
                                "teams": {
                                    "home": {
                                        "name": local,
                                        "logo": "https://media.api-sports.io/football/teams/732.png" if "zaragoza" in local.lower() else ""
                                    },
                                    "away": {
                                        "name": visitante,
                                        "logo": "https://media.api-sports.io/football/teams/732.png" if "zaragoza" in visitante.lower() else ""
                                    }
                                },
                                "goals": {
                                    "home": home_goals,
                                    "away": away_goals
                                }
                            }

                            if not any(p["teams"]["home"]["name"] == local and p["teams"]["away"]["name"] == visitante for p in partidos_extraidos):
                                partidos_extraidos.append(partido_obj)
                                id_counter += 1

            except Exception as e_cal:
                print(f"⚠️ Error obteniendo calendario: {str(e_cal)}")

    except Exception as e:
        print(f"⚠️ Error general en scraping de Futbolme: {str(e)}")

    if partidos_extraidos:
        cache_zaragoza["partidos"] = partidos_extraidos

    if clasificacion_extraida:
        cache_zaragoza["clasificacion"] = clasificacion_extraida

    if partidos_extraidos or clasificacion_extraida:
        cache_zaragoza["ultima_actualizacion"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"⚽ Sincronizado ({datetime.now().strftime('%H:%M:%S')}) - {len(cache_zaragoza['partidos'])} partidos / {len(cache_zaragoza['clasificacion'])} equipos clasif.")
    else:
        print("⚠️ No se obtuvieron datos nuevos. Se mantiene el contenido en caché.")

async def extraer_datos_marca():
    await asyncio.to_thread(extraer_datos_futbolme_sync)

def iniciar_cron():
    scheduler.add_job(extraer_datos_marca, 'interval', minutes=30, id='job_marca_zaragoza')
    scheduler.start()
    asyncio.create_task(extraer_datos_marca())

@router.get("/partidos-zaragoza")
async def obtener_partidos_zaragoza():
    return {
        "partidos": cache_zaragoza["partidos"],
        "temporada": cache_zaragoza["temporada"],
        "ultima_actualizacion": cache_zaragoza["ultima_actualizacion"]
    }

@router.get("/clasificacion-zaragoza")
async def obtener_clasificacion_zaragoza():
    return {
        "clasificacion": cache_zaragoza["clasificacion"],
        "ultima_actualizacion": cache_zaragoza["ultima_actualizacion"]
    }

@router.post("/fuerza-sincronizacion-zaragoza")
async def forzar_sincronizacion_zaragoza():
    try:
        await extraer_datos_marca()
        return {
            "status": "success",
            "message": "Sincronización manual ejecutada con éxito",
            "ultima_actualizacion": cache_zaragoza["ultima_actualizacion"],
            "partidos_cargados": len(cache_zaragoza["partidos"]),
            "equipos_clasificacion": len(cache_zaragoza["clasificacion"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al sincronizar: {str(e)}")