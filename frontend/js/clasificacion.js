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

        if (Array.isArray(data.clasificacion)) {

            if (
                data.clasificacion.length > 0 && data.clasificacion[0].league?.standings
            ) {
                tabla = data.clasificacion[0].league.standings[0] || [];
            } else {
                tabla = data.clasificacion;
            }
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

            const posicion = item.rank ?? item.posicion ?? (index + 1);
            const equipo = item.team?.name || item.equipo || "Equipo";
            const escudo = item.team?.logo || item.escudo || "";
            const puntos = item.points ?? item.puntos ?? 0;
            const pj = item.all?.played ?? item.pj ?? 0;
            const pg = item.all?.win ?? item.pg ?? 0;
            const pe = item.all?.draw ?? item.pe ?? 0;
            const pp =item.all?.lose ?? item.pp ?? 0;
            const gf = item.all?.goals?.for ?? item.gf ?? 0;
            const gc = item.all?.goals?.against ?? item.gc ?? 0;
            const dg = item.goalsDiff ?? item.dg ?? (gf - gc);

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
