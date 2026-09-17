import re
import asyncio
from datetime import datetime
from fastapi import APIRouter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from playwright.sync_api import sync_playwright

router = APIRouter(tags=["Real Zaragoza"])

cache_zaragoza = {
    "partidos": [],
    "clasificacion": [],
    "ultima_actualizacion": None,
    "temporada": 2026
}

scheduler = AsyncIOScheduler()
MARCA_URL = "https://www.marca.com/futbol/primera-rfef/calendario/grupo-2.html?intcmp=MENUMIGA&s_kw=grupo-2"

def extraer_partidos_marca_sync():
    global cache_zaragoza

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(MARCA_URL, wait_until="domcontentloaded", timeout=30000)
            
            # Aceptar cookies si aparece el aviso
            try:
                btn_cookies = page.locator("#didomi-notice-agree-button")
                if btn_cookies.is_visible(timeout=3000):
                    btn_cookies.click()
            except Exception:
                pass

            partidos_extraidos = []
            
            # Evaluamos con JavaScript interno el DOM renderizado por MARCA
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

                    # 1. Analizar Fecha (Día y Mes)
                    dia, mes, anio = "01", "09", "2026"
                    match_fecha = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?', fecha_cabecera + " " + raw_texto)
                    if match_fecha:
                        dia = match_fecha.group(1).zfill(2)
                        mes = match_fecha.group(2).zfill(2)
                        if match_fecha.group(3):
                            anio = match_fecha.group(3)
                            if len(anio) == 2:
                                anio = f"20{anio}"

                    # 2. Analizar Hora (ej: "20:30")
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

                            # Determinar Victoria / Empate / Derrota para el Real Zaragoza
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

            if partidos_extraidos:
                cache_zaragoza["partidos"] = partidos_extraidos
                cache_zaragoza["ultima_actualizacion"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"⚽ MARCA sincronizado ({datetime.now().strftime('%H:%M:%S')}) - Fechas y signos cargados.")

    except Exception as e:
        print(f"⚠️ Error al conectar con MARCA mediante Playwright: {str(e)}")

async def extraer_partidos_marca():
    await asyncio.to_thread(extraer_partidos_marca_sync)

def iniciar_cron():
    scheduler.add_job(extraer_partidos_marca, 'interval', hours=12, id='job_marca_zaragoza')
    scheduler.start()
    asyncio.create_task(extraer_partidos_marca())

@router.get("/partidos-zaragoza")
async def obtener_partidos_zaragoza():
    return {
        "partidos": cache_zaragoza["partidos"],
        "temporada": cache_zaragoza["temporada"],
        "ultima_actualizacion": cache_zaragoza["ultima_actualizacion"]
    }

@router.get("/clasificacion-zaragoza")
async def obtener_clasificacion_zaragoza():
    return {"clasificacion": cache_zaragoza["clasificacion"]}