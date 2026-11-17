import re
import asyncio
from datetime import datetime
from xmlrpc import client

import httpx
from bs4 import BeautifulSoup, soup
from fastapi import APIRouter, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler


# ============================================================
# CONFIGURACIÓN
# ============================================================

router = APIRouter(tags=["Real Zaragoza"])
scheduler = AsyncIOScheduler()

cache_zaragoza = {
    "partidos": [],
    "clasificacion": [],
    "ultima_actualizacion": None,
    "temporada": 2026
}

FUTBOLME_CALENDARIO_URL = (
    "https://futbolme.com/resultados-directo/"
    "equipo/real-zaragoza/382/calendario"
)

FUTBOLME_CLASIFICACION_URL = (
    "https://futbolme.com/resultados-directo/"
    "torneo/primera-federacion-grupo-2/3056/"
)

ZARAGOZA_LOGO = (
    "https://media.api-sports.io/football/teams/732.png"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9"
}

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3,
    "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9,
    "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def limpiar_texto(texto):
    return re.sub(r"\s+", " ", str(texto or "")).strip()


def es_real_zaragoza(nombre):
    return "zaragoza" in limpiar_texto(nombre).lower()


def normalizar_equipo(nombre):
    nombre = limpiar_texto(nombre)

    if not nombre:
        return ""

    # Separar palabras y eliminar repeticiones consecutivas
    palabras = nombre.split()
    palabras_limpias = []

    for palabra in palabras:
        if (
            not palabras_limpias
            or palabras_limpias[-1].casefold() != palabra.casefold()
        ):
            palabras_limpias.append(palabra)

    nombre = " ".join(palabras_limpias)

    # Normalizar el nombre del Real Zaragoza
    if "zaragoza" in nombre.casefold():
        return "Real Zaragoza"

    return nombre


def parsear_fecha_texto(texto):
    """Convierte fechas españolas a ISO sin inventar fechas."""

    if not texto:
        return None

    texto = limpiar_texto(texto)

    m = re.search(r"\b(20\d{2})-(\d{1,2})-(\d{1,2})\b", texto)

    if m:
        anio, mes, dia = map(int, m.groups())
    else:
        m = re.search(
            r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b",
            texto
        )

        if m:
            dia, mes, anio = map(int, m.groups())
            if anio < 100:
                anio += 2000
        else:
            m = re.search(
                r"(\d{1,2})\s+DE\s+([A-ZÁÉÍÓÚ]+)\s+DE\s+(\d{4})",
                texto,
                re.I
            )

            if not m:
                return None

            dia = int(m.group(1))
            mes = MESES.get(m.group(2).lower())
            anio = int(m.group(3))

            if not mes:
                return None

    try:
        fecha = datetime(anio, mes, dia)

        hora = re.search(
            r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b",
            texto
        )

        if hora:
            return fecha.strftime("%Y-%m-%d") + f"T{hora.group()}:00"

        return fecha.strftime("%Y-%m-%d")

    except ValueError:
        return None


def crear_resultado(home_goals, away_goals, zaragoza_local):

    if home_goals is None or away_goals is None:
        return None

    gz = home_goals if zaragoza_local else away_goals
    gr = away_goals if zaragoza_local else home_goals

    if gz > gr:
        return "Victoria"
    if gz < gr:
        return "Derrota"

    return "Empate"


def es_linea_equipo(linea):

    linea = limpiar_texto(linea)

    if len(linea) < 3 or len(linea) > 65:
        return False

    if re.search(r"\d", linea):
        return False

    exclusiones = [
        "jornada", "clasificacion", "clasificación",
        "calendario", "enlaces", "cerrar enlaces",
        "primera federacion", "primera federación",
        "alineaciones", "eventos", "partidos",
        "volver", "local", "visitante",
        "resultado", "horario", "fecha",
        "televisión", "goles", "ver enfrentamientos"
    ]

    return not any(x in linea.lower() for x in exclusiones)


def extraer_marcador_bloque(bloque):

    for i in range(len(bloque) - 2):

        a = limpiar_texto(bloque[i])
        b = limpiar_texto(bloque[i + 1])
        c = limpiar_texto(bloque[i + 2])

        if (
            re.fullmatch(r"\d{1,2}", a)
            and b == "-"
            and re.fullmatch(r"\d{1,2}", c)
        ):
            return int(a), int(c)

        m = re.fullmatch(r"(\d{1,2})\s*-\s*(\d{1,2})", a)

        if m:
            return int(m.group(1)), int(m.group(2))

    return None


def obtener_jornadas(lineas):

    jornadas = []

    for i, linea in enumerate(lineas):

        m = re.search(r"\bJORNADA\s+(\d+)\b", linea, re.I)

        if m:
            jornadas.append({
                "numero": int(m.group(1)),
                "indice": i
            })

    return jornadas


def obtener_fecha_jornada(lineas, inicio, bloque):
    """Busca fecha y hora sin utilizar fechas predeterminadas."""

    for linea in bloque:
        fecha = parsear_fecha_texto(linea)
        if fecha:
            return fecha

    # Buscar fecha inmediatamente anterior al encabezado.
    for i in range(inicio - 1, max(-1, inicio - 6), -1):
        fecha = parsear_fecha_texto(lineas[i])
        if fecha:
            return fecha

    return None


def obtener_hora_bloque(bloque):

    for linea in bloque:
        if re.fullmatch(r"(?:[01]?\d|2[0-3]):[0-5]\d", linea):
            return linea

    return None

# ============================================================
# EXTRACCIÓN DEL CALENDARIO
# ============================================================



def extraer_calendario_zaragoza(client):
    """Extrae calendario, fechas y resultados del Real Zaragoza."""

    respuesta = client.get(FUTBOLME_CALENDARIO_URL)

    print("ESTADO FUTBOLME:", respuesta.status_code, flush=True)
    print("URL FINAL:", respuesta.url, flush=True)
    print("LONGITUD HTML:", len(respuesta.text), flush=True)
    print("CONTENEDORES:", respuesta.text.count("contenedorPrimeraLinea"), flush=True)

    respuesta.raise_for_status()

    soup = BeautifulSoup(respuesta.text, "html.parser")
    print("========== DIAGNÓSTICO FUTBOLME ==========")
    print("URL:", respuesta.url)
    print("STATUS:", respuesta.status_code)
    print("HTML RECIBIDO:", len(respuesta.text))
    print("CAJAS ENCONTRADAS:", len(soup.select("div.cajaPartido")))
    print("TÍTULO:", soup.title.get_text(strip=True) if soup.title else "SIN TÍTULO")
    print("INICIO HTML:", respuesta.text[:500])
    print("==========================================")
    partidos = []
    jornadas_vistas = set()

    for caja in soup.select("div.cajaPartido"):

        # JORNADA
        enlace = caja.select_one("a.nombreJornada")
        if not enlace:
            continue

        match = re.search(r"/jornada/(\d+)", enlace.get("href", ""))
        if not match:
            continue

        jornada = int(match.group(1))

        if jornada in jornadas_vistas:
            continue

        # EQUIPOS
        local_elemento = caja.select_one(
            ".equipoPartidoLocal [itemprop='name']"
        )
        visitante_elemento = caja.select_one(
            ".equipoPartidoVisitante [itemprop='name']"
        )

        if not local_elemento or not visitante_elemento:
            continue

        # Extraer solo una versión del nombre.
        # Futbolme incluye una versión móvil y otra de escritorio.
        def extraer_nombre_unico(elemento):

            versiones = elemento.select(
                ".d-block.d-sm-none, .d-none.d-sm-block"
            )

            if versiones:
                nombre = versiones[0].get_text(" ", strip=True)
            else:
                nombre = elemento.get_text(" ", strip=True)

            return normalizar_equipo(nombre)

        local = extraer_nombre_unico(local_elemento)
        visitante = extraer_nombre_unico(visitante_elemento)

        zaragoza_local = es_real_zaragoza(local)
        zaragoza_visitante = es_real_zaragoza(visitante)

        # Solo partidos del Real Zaragoza
        if zaragoza_local == zaragoza_visitante:
            continue

        # FECHA: PRIORIDAD A startDate
        fecha_elemento = caja.select_one("meta[itemprop='startDate']")
        fecha_partido = None

        if fecha_elemento:
            fecha_partido = fecha_elemento.get("content")

        if not fecha_partido:
            fecha_elemento = caja.select_one(".horaPrevistaPartido")

            if fecha_elemento:
                fecha_partido = parsear_fecha_texto(
                    fecha_elemento.get_text(" ", strip=True)
                )

        if not fecha_partido:
            print(f"⚠️ Jornada {jornada}: sin fecha.")
            continue

        # MARCADOR
        home_goals = None
        away_goals = None
        status_short = "NS"

        marcador = caja.select(".resultadoPartido span")

        if len(marcador) >= 2:
            try:
                home_goals = int(marcador[0].get_text(strip=True))
                away_goals = int(marcador[1].get_text(strip=True))
                status_short = "FT"
            except (ValueError, TypeError):
                home_goals = None
                away_goals = None

        # RESULTADO DEL ZARAGOZA
        resultado_signo = crear_resultado(
            home_goals,
            away_goals,
            zaragoza_local
        )

        partido = {
            "fixture": {
                "id": jornada,
                "date": fecha_partido,
                "status": {
                    "short": status_short
                },
                "resultado_signo": resultado_signo
            },
            "league": {
                "name": "Primera Federación - Grupo 2",
                "round": f"Jornada {jornada}"
            },
            "teams": {
                "home": {
                    "name": local,
                    "logo": ZARAGOZA_LOGO if zaragoza_local else ""
                },
                "away": {
                    "name": visitante,
                    "logo": ZARAGOZA_LOGO if zaragoza_visitante else ""
                }
            },
            "goals": {
                "home": home_goals,
                "away": away_goals
            }
        }

        partidos.append(partido)
        jornadas_vistas.add(jornada)

        marcador_texto = (
            f"{home_goals}-{away_goals}"
            if home_goals is not None
            else "Pendiente"
        )

        print(
            f"⚽ Jornada {jornada}: {local} "
            f"{marcador_texto} {visitante} | {fecha_partido}"
            f" | {resultado_signo or 'Sin resultado'}"
        )

    partidos.sort(key=lambda p: p["fixture"]["id"])

    print(f"\n✅ Total partidos extraídos: {len(partidos)}")

    return partidos

# ============================================================
# EXTRACCIÓN DE CLASIFICACIÓN
# ============================================================

def extraer_clasificacion(client):

    respuesta = client.get(FUTBOLME_CLASIFICACION_URL)
    respuesta.raise_for_status()

    soup = BeautifulSoup(respuesta.text, "html.parser")

    clasificacion = []

    for tabla in soup.find_all("table"):

        for fila in tabla.find_all("tr"):

            celdas = fila.find_all(["td", "th"])

            if len(celdas) < 5:
                continue

            valores = [
                limpiar_texto(c.get_text(" ", strip=True))
                for c in celdas
            ]

            if not valores or not valores[0].isdigit():
                continue

            posicion = int(valores[0])

            nombre = next(
                (
                    v for v in valores[1:]
                    if v and not re.fullmatch(r"[+-]?\d+", v)
                ),
                None
            )

            if not nombre:
                continue

            numeros = [
                int(v)
                for v in valores
                if re.fullmatch(r"-?\d+", v)
            ]

            if len(numeros) < 5:
                continue

            clasificacion.append({
                "posicion": posicion,
                "equipo": normalizar_equipo(nombre),
                "datos": numeros[1:]
            })

    # Eliminar posiciones duplicadas.
    unicos = {
        x["posicion"]: x
        for x in clasificacion
    }

    resultado = sorted(
        unicos.values(),
        key=lambda x: x["posicion"]
    )

    print(f"🏆 Equipos encontrados: {len(resultado)}")

    return resultado

# ============================================================
# SINCRONIZACIÓN GENERAL
# ============================================================

def extraer_datos_futbolme_sync():

    global cache_zaragoza

    partidos = []
    clasificacion = []

    try:

        with httpx.Client(
            timeout=30,
            headers=HEADERS,
            follow_redirects=True
        ) as client:

            try:
                partidos = extraer_calendario_zaragoza(client)
            except Exception as e:
                print(f"⚠️ Error extrayendo partidos: {e}")

            try:
                clasificacion = extraer_clasificacion(client)
            except Exception as e:
                print(f"⚠️ Error extrayendo clasificación: {e}")

    except Exception as e:
        print(f"⚠️ Error de conexión: {e}")

    # Actualizar caché únicamente si hay datos nuevos.
    if partidos:
        cache_zaragoza["partidos"] = partidos

    if clasificacion:
        cache_zaragoza["clasificacion"] = clasificacion

    if partidos or clasificacion:
        cache_zaragoza["ultima_actualizacion"] = (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    jornadas = {
        p["fixture"]["id"]
        for p in cache_zaragoza["partidos"]
    }

    faltantes = [
        n for n in range(1, 39)
        if n not in jornadas
    ]

    print("\n===================================")
    print("REAL ZARAGOZA - SINCRONIZACIÓN")
    print("===================================")

    print(
        f"Partidos cargados: "
        f"{len(cache_zaragoza['partidos'])}/38"
    )

    print(
        f"Equipos clasificación: "
        f"{len(cache_zaragoza['clasificacion'])}"
    )

    if faltantes:
        print(f"⚠️ Jornadas pendientes: {faltantes}")
    else:
        print("✅ Las 38 jornadas están cargadas.")

    print(
        f"Última actualización: "
        f"{cache_zaragoza['ultima_actualizacion']}"
    )

    print("===================================\n")


# ============================================================
# EJECUCIÓN ASÍNCRONA
# ============================================================

async def extraer_datos_marca():

    await asyncio.to_thread(
        extraer_datos_futbolme_sync
    )


# ============================================================
# PROGRAMADOR AUTOMÁTICO
# ============================================================

def iniciar_cron():

    if not scheduler.running:

        scheduler.add_job(
            extraer_datos_marca,
            "interval",
            minutes=30,
            id="job_marca_zaragoza",
            replace_existing=True
        )

        scheduler.start()

    try:
        asyncio.get_running_loop().create_task(
            extraer_datos_marca()
        )
    except RuntimeError:
        print("⚠️ No hay un bucle asyncio activo.")


# ============================================================
# ENDPOINTS
# ============================================================

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

        await asyncio.to_thread(
            extraer_datos_futbolme_sync
        )

        jornadas = {
            p["fixture"]["id"]
            for p in cache_zaragoza["partidos"]
        }

        faltantes = [
            n for n in range(1, 39)
            if n not in jornadas
        ]

        return {
            "status": "success",
            "message": "Sincronización ejecutada",
            "ultima_actualizacion": cache_zaragoza["ultima_actualizacion"],
            "partidos_cargados": len(cache_zaragoza["partidos"]),
            "equipos_clasificacion": len(cache_zaragoza["clasificacion"]),
            "jornadas_faltantes": faltantes
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )