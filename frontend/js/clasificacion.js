document.addEventListener("DOMContentLoaded", async () => {
    const tbody = document.getElementById("clasificacion-body");

    if (!tbody) {
        console.error("No se encuentra el elemento clasificacion-body");
        return;
    }

    // ==================================================
    // CONFIGURACIÓN AUTOMÁTICA DEL BACKEND
    // ==================================================

    const urlBackend =
        (window.location.hostname === "localhost" ||
         window.location.hostname === "127.0.0.1")
            ? "http://localhost:8000"
            : "https://proyecto-pena-zaragocista.onrender.com";

    console.log("Backend de clasificación:", urlBackend);

    try {

        // ==================================================
        // CONSULTAR CLASIFICACIÓN
        // ==================================================

        const response = await fetch(
            `${urlBackend}/clasificacion-zaragoza`
        );

        if (!response.ok) {
            throw new Error(
                `Error HTTP ${response.status} al consultar la clasificación`
            );
        }

        const data = await response.json();

        // ==================================================
        // OBTENER TABLA
        // ==================================================

        let tabla = [];

        // El backend devuelve directamente un array
        if (Array.isArray(data)) {
            tabla = data;
        }

        // Compatibilidad con respuestas que contienen clasificacion
        else if (Array.isArray(data.clasificacion)) {
            tabla = data.clasificacion;
        }

        tbody.innerHTML = "";

        if (!tabla || tabla.length === 0) {

            tbody.innerHTML = `
                <tr>
                    <td colspan="10" class="text-center text-muted py-4">
                        No hay datos de clasificación disponibles en este momento.
                    </td>
                </tr>
            `;

            return;
        }

        // ==================================================
        // GENERAR CLASIFICACIÓN
        // ==================================================

        tabla.forEach((item, index) => {

            const posicion = item.posicion ?? item.rank ?? (index + 1);

            const equipo = item.equipo || item.team?.name || "Equipo";

            const escudo = item.escudo || item.team?.logo || "";

            // Obtener estadísticas del array datos
            const datos = item.datos || [];

            const puntos = datos[0] ?? item.points ?? 0;
            const pj = datos[1] ?? item.pj ?? 0;
            const pg = datos[2] ?? item.pg ?? 0;
            const pe = datos[3] ?? item.pe ?? 0;
            const pp = datos[4] ?? item.pp ?? 0;
            const gf = datos[5] ?? item.gf ?? 0;
            const gc = datos[6] ?? item.gc ?? 0;
            const dg = datos[7] ?? item.dg ?? (gf - gc);

            // ==============================================
            // DETECTAR REAL ZARAGOZA
            // ==============================================

            const esZaragoza = equipo.toLowerCase().includes("zaragoza");

            // ==============================================
            // CLASES VISUALES DE LAS FILAS
            // ==============================================

            let claseFila = "";

            if (esZaragoza) {
                claseFila = "fila-zaragoza";
            } else if (posicion === 1) {
                claseFila = "fila-ascenso";
            } else if (posicion >= 2 && posicion <= 5) {
                claseFila = "fila-playoff";
            } else if (posicion >= 16) {
                claseFila = "fila-descenso";
            }

            // ==============================================
            // INSERTAR FILA
            // ==============================================

            tbody.innerHTML += `
                <tr class="${claseFila}">
                    <td class="text-center fw-bold">
                        ${posicion}
                    </td>

                    <td>
                        <div class="d-flex align-items-center">
                            ${
                                escudo
                                    ? `<img
                                        src="${escudo}"
                                        width="18"
                                        height="18"
                                        class="me-2"
                                        alt="escudo"
                                    >`
                                    : ''
                            }

                            <span>${equipo}</span>
                        </div>
                    </td>

                    <td class="text-center fw-bold">${puntos}</td>
                    <td class="text-center">${pj}</td>
                    <td class="text-center">${pg}</td>
                    <td class="text-center">${pe}</td>
                    <td class="text-center">${pp}</td>

                    <td class="text-center d-none d-md-table-cell">
                        ${gf}
                    </td>

                    <td class="text-center d-none d-md-table-cell">
                        ${gc}
                    </td>

                    <td class="text-center fw-bold">
                        ${dg > 0 ? '+' + dg : dg}
                    </td>
                </tr>
            `;
        });

        console.log(
            `Clasificación cargada correctamente: ${tabla.length} equipos`
        );

        console.log(
            "Última actualización:",
            data.ultima_actualizacion || "No disponible"
        );

    } catch (error) {

        console.error(
            "Error al cargar la clasificación:",
            error
        );

        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center text-danger py-4">
                    ⚠️ Error al conectar con el servidor de la clasificación.
                </td>
            </tr>
        `;
    }
});
