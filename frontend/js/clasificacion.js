document.addEventListener("DOMContentLoaded", async () => {
    const tbody = document.getElementById("clasificacion-body");
    const urlBackend = typeof BACKEND_URL !== "undefined" ? BACKEND_URL : "http://localhost:8000";

    try {
        const response = await fetch(`${urlBackend}/clasificacion-zaragoza`);
        if (!response.ok) throw new Error("Error al consultar la API de clasificación");

        const data = await response.json();
        
        let tabla = [];
        if (Array.isArray(data.clasificacion)) {
            if (data.clasificacion.length > 0 && data.clasificacion[0].league?.standings) {
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
                </tr>`;
            return;
        }

        tabla.forEach((item, index) => {
            const posicion = item.rank || item.posicion || (index + 1);
            const equipo = item.team?.name || item.equipo || "Equipo";
            const escudo = item.team?.logo || item.escudo || "";
            const puntos = item.points ?? item.puntos ?? 0;
            const pj = item.all?.played ?? item.pj ?? 0;
            const pg = item.all?.win ?? item.pg ?? 0;
            const pe = item.all?.draw ?? item.pe ?? 0;
            const pp = item.all?.lose ?? item.pp ?? 0;
            const gf = item.all?.goals?.for ?? item.gf ?? 0;
            const gc = item.all?.goals?.against ?? item.gc ?? 0;
            const dg = item.goalsDiff ?? item.dg ?? (gf - gc);

            // Detectar Real Zaragoza
            const esZaragoza = equipo.toLowerCase().includes("zaragoza");

            // Selección de clase según la posición
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

            tbody.innerHTML += `
                <tr class="${claseFila}">
                    <td class="text-center fw-bold">${posicion}</td>
                    <td>
                        <div class="d-flex align-items-center">
                            ${escudo ? `<img src="${escudo}" width="18" height="18" class="me-2" alt="escudo">` : ''}
                            <span class="${esZaragoza ? 'text-primary fw-bold' : ''}">${equipo} ${esZaragoza ? '💙' : ''}</span>
                        </div>
                    </td>
                    <td class="text-center fw-bold text-primary">${puntos}</td>
                    <td class="text-center">${pj}</td>
                    <td class="text-center text-success">${pg}</td>
                    <td class="text-center text-muted">${pe}</td>
                    <td class="text-center text-danger">${pp}</td>
                    <td class="text-center d-none d-md-table-cell text-muted">${gf}</td>
                    <td class="text-center d-none d-md-table-cell text-muted">${gc}</td>
                    <td class="text-center ${dg > 0 ? 'text-success fw-bold' : (dg < 0 ? 'text-danger' : 'text-muted')}">${dg > 0 ? '+' + dg : dg}</td>
                </tr>
            `;
        });

    } catch (error) {
        console.error("Error al cargar la clasificación:", error);
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center text-danger py-4">
                    ⚠️ Error al conectar con el servidor de la clasificación.
                </td>
            </tr>`;
    }
});