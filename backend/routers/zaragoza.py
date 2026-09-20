import re
import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from playwright.sync_api import sync_playwright
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

MARCA_CALENDARIO_URL = "https://www.marca.com/futbol/primera-rfef/calendario/grupo-2.html?intcmp=MENUMIGA&s_kw=grupo-2"
FUTBOLME_CLASIFICACION_URL = "https://futbolme.com/resultados-directo/torneo/primera-federacion-grupo-2/3056/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9"
}

def extraer_datos_marca_sync():
    global cache_zaragoza

    partidos_extraidos = []
    clasificacion_extraida = []

    # -----------------------------------------------------------------
    # 1. CLASIFICACIÓN VÍA BEAUTIFULSOUP
    # -----------------------------------------------------------------
    try:
        with httpx.Client(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
            res = client.get(FUTBOLME_CLASIFICACION_URL)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                filas = soup.select("table tbody tr")
                
                equipos_temporales = []

                for fila in filas:
                    celdas = fila.find_all(["td", "th"])
                    if len(celdas) < 7:
                        continue

                    # --- A. NOMBRE LIMPIO (Obtener sólo la etiqueta de texto visible más larga) ---
                    celda_equipo = celdas[1]
                    # Buscar elementos dentro de la celda del equipo
                    span_largo = celda_equipo.select_one(".hidden-xs, .nombre-largo, span:last-child")
                    
                    if span_largo and len(span_largo.get_text(strip=True)) > 2:
                        equipo_nombre = span_largo.get_text(strip=True)
                    else:
                        # Si no hay etiqueta específica, tomar el texto del enlace principal
                        link = celda_equipo.find("a")
                        equipo_nombre = link.get_text(strip=True) if link else celda_equipo.get_text(strip=True)

                    # Deduplicación por palabras si viene pegado tipo "Zaragoza Real Zaragoza"
                    palabras = equipo_nombre.split()
                    if len(palabras) > 2 and palabras[0].lower() == palabras[-1].lower():
                        equipo_nombre = " ".join(palabras[1:])
                    
                    # Deduplicación por mitad de cadena tipo "Villarreal BVillarreal CF B"
                    mitad = len(equipo_nombre) // 2
                    if mitad > 3 and equipo_nombre[:mitad].strip().lower() in equipo_nombre[mitad:].strip().lower():
                        equipo_nombre = equipo_nombre[mitad:].strip()

                    if not equipo_nombre or len(equipo_nombre) < 2:
                        continue

                    # --- B. EXTRAER ESTADÍSTICAS OMITIENDO LA POSICIÓN (CELDA 0) ---
                    # Celdas numéricas a partir de la columna de Puntos/PJ (índice >= 2)
                    numeros = []
                    for c in celdas[2:]:
                        val = re.sub(r'[^\d-]', '', c.get_text(strip=True))
                        if val.replace('-', '').isdigit() and val != '':
                            numeros.append(int(val))

                    # Se necesitan exactamente las 7 métricas clave: [PTS, PJ, PG, PE, PP, GF, GC]
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

                # --- C. REORDENAR POR PUNTOS Y DIFERENCIA DE GOLES (1 A 20) ---
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

    except Exception as e_clas_bs4:
        print(f"⚠️ Error obteniendo clasificación BS4: {str(e_clas_bs4)}")

    # -----------------------------------------------------------------
    # 2. SCRAPING DE PARTIDOS CON PLAYWRIGHT
    # -----------------------------------------------------------------
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()

            page.goto(MARCA_CALENDARIO_URL, wait_until="domcontentloaded", timeout=25000)

            try:
                btn_cookies = page.locator("#didomi-notice-agree-button")
                if btn_cookies.is_visible(timeout=3000):
                    btn_cookies.click()
            except Exception:
                pass

            partidos_dom = page.evaluate("""() => {
                const resultados = [];
                const contenedores = document.querySelectorAll('.jornada, .tabla-datos, .jornada-container, section');
                
                contenedores.forEach((contenedor) => {
                    const textoContenedor = contenedor.innerText || "";
                    if (!textoContenedor.toLowerCase().includes("zaragoza")) return;

                    let fechaTexto = "";
                    const cabecera = contenedor.querySelector('caption, h2, h3, .tit-jornada, thead');
                    if (cabecera) {
                        fechaTexto = cabecera.innerText;
                    }

                    const filas = contenedor.querySelectorAll('tr, .fila-partido, li');
                    filas.forEach((fila) => {
                        const txtFila = fila.innerText || "";
                        if (txtFila.toLowerCase().includes("zaragoza")) {
                            let horaTexto = "00:00";
                            const elemHora = fila.querySelector('.hora, .fecha, .time, .estado');
                            if (elemHora) {
                                horaTexto = elemHora.innerText.trim();
                            }

                            resultados.push({
                                rawTexto: txtFila,
                                fechaCabecera: fechaTexto,
                                horaDetalle: horaTexto
                            });
                        }
                    });
                });
                return resultados;
            }""")

            id_counter = 1
            for p_data in partidos_dom:
                raw_texto = p_data["rawTexto"]
                fecha_cabecera = p_data["fechaCabecera"]
                lineas = [l.strip() for l in raw_texto.split("\n") if l.strip()]

                if len(lineas) >= 2:
                    local = lineas[0]
                    visitante = lineas[-1] if len(lineas) > 2 else "Rival"
                    marcador = lineas[1] if len(lineas) > 2 else "- - -"

                    dia, mes, anio = "01", "09", "2026"
                    match_fecha = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?', fecha_cabecera + " " + raw_texto)
                    if match_fecha:
                        dia = match_fecha.group(1).zfill(2)
                        mes = match_fecha.group(2).zfill(2)
                        if match_fecha.group(3):
                            anio = match_fecha.group(3)
                            if len(anio) == 2:
                                anio = f"20{anio}"

                    hora, minuto = "00", "00"
                    match_hora = re.search(r'(\d{1,2}):(\d{2})', raw_texto + " " + p_data["horaDetalle"])
                    if match_hora:
                        hora = match_hora.group(1).zfill(2)
                        minuto = match_hora.group(2)

                    fecha_iso = f"{anio}-{mes}-{dia}T{hora}:{minuto}:00"

                    home_goals = None
                    away_goals = None
                    status_short = "NS"
                    resultado_signo = None

                    if "-" in marcador and any(char.isdigit() for char in marcador):
                        partes = marcador.split("-")
                        if len(partes) == 2 and partes[0].strip().isdigit():
                            home_goals = int(partes[0].strip())
                            away_goals = int(partes[1].strip())
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

                    partidos_extraidos.append({
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
                    })
                    id_counter += 1

            browser.close()

    except Exception as e:
        print(f"⚠️ Error general en Playwright: {str(e)}")

    if partidos_extraidos:
        cache_zaragoza["partidos"] = partidos_extraidos

    if clasificacion_extraida:
        cache_zaragoza["clasificacion"] = clasificacion_extraida

    if partidos_extraidos or clasificacion_extraida:
        cache_zaragoza["ultima_actualizacion"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"⚽ Sincronizado ({datetime.now().strftime('%H:%M:%S')}) - {len(cache_zaragoza['partidos'])} partidos / {len(cache_zaragoza['clasificacion'])} equipos clasif.")
    else:
        print("⚠️ No se obtuvieron datos. Se mantiene el contenido en caché.")

async def extraer_datos_marca():
    await asyncio.to_thread(extraer_datos_marca_sync)

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
            "message": "Sincronización manual ejecutada",
            "ultima_actualizacion": cache_zaragoza["ultima_actualizacion"],
            "partidos_cargados": len(cache_zaragoza["partidos"]),
            "equipos_clasificacion": len(cache_zaragoza["clasificacion"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al sincronizar: {str(e)}")