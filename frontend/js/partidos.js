
document.addEventListener('DOMContentLoaded', async () => {
    const contenedor = document.getElementById('lista-partidos');

    if (!contenedor) {
        console.error('No se encuentra el contenedor lista-partidos');
        return;
    }

    // Backend local o producción
    const BACKEND = (
        window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1'
    )
        ? 'http://localhost:8000'
        : 'https://proyecto-pena-zaragocista.onrender.com';

    try {
        const response = await fetch(`${BACKEND}/partidos-zaragoza`);

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();
        const partidos = data.partidos || [];

        contenedor.innerHTML = '';

        if (!partidos.length) {
            contenedor.innerHTML = `
                <p class="text-center">
                    Actualmente no hay partidos disponibles.
                </p>`;
            return;
        }

        // Ordenar por jornada
        partidos.sort((a, b) =>
            a.fixture.id - b.fixture.id
        );

        partidos.forEach(partido => {

            const local = partido.teams?.home?.name || 'Equipo local';
            const visitante = partido.teams?.away?.name || 'Equipo visitante';

            const golesLocal = partido.goals?.home;
            const golesVisitante = partido.goals?.away;

            const jornada = partido.league?.round || '';

            const fecha = partido.fixture?.date;
            const estado = partido.fixture?.status?.short || 'NS';

            const esZaragozaLocal = local.toLowerCase().includes('zaragoza');

            const esJugado =
                golesLocal !== null &&
                golesLocal !== undefined &&
                golesVisitante !== null &&
                golesVisitante !== undefined;

            // Resultado desde el punto de vista del Zaragoza
            let resultado = '';
            let claseResultado = '';

            if (esJugado) {

                if (golesLocal === golesVisitante) {
                    resultado = 'Empate';
                    claseResultado = 'bg-warning text-dark';

                } else {
                    const zaragozaGana = esZaragozaLocal
                        ? golesLocal > golesVisitante
                        : golesVisitante > golesLocal;

                    resultado = zaragozaGana ? 'Victoria' : 'Derrota';

                    claseResultado = zaragozaGana
                        ? 'bg-success text-white'
                        : 'bg-danger text-white';
                }
            }

            // Fecha y hora
            let fechaFormateada = 'Fecha por confirmar';
            let horaFormateada = '';

            if (fecha) {
                const fechaObj = new Date(fecha);

                if (!isNaN(fechaObj.getTime())) {
                    fechaFormateada = fechaObj.toLocaleDateString('es-ES', {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric'
                    });

                    if (fecha.includes('T')) {
                        horaFormateada = fechaObj.toLocaleTimeString('es-ES', {
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                    }
                }
            }

            const logoLocal = partido.teams?.home?.logo || '';
            const logoVisitante = partido.teams?.away?.logo || '';

            // Marcador o partido pendiente
            const marcador = esJugado
                ? `${golesLocal} - ${golesVisitante}`
                : 'VS';

            const estadoHTML = esJugado
                ? `<span class="badge ${claseResultado}">${resultado}</span>`
                : `<span class="badge bg-warning text-dark">Pendiente</span>`;

            // Construir tarjeta
            const tarjeta = document.createElement('div');

            tarjeta.className = 'col-md-4 col-6 mb-4';

            tarjeta.innerHTML = `
                <div class="card shadow-sm h-100">

                    <div class="card-body text-center p-2 d-flex flex-column justify-content-between">

                        <div>

                            <div class="d-flex justify-content-between align-items-center mb-2">

                                <span class="badge bg-light text-dark border">
                                    J${partido.fixture.id}
                                </span>

                                ${estadoHTML}

                            </div>

                            <div class="d-flex align-items-center justify-content-center gap-1 my-2">

                                ${logoLocal
                                    ? `<img src="${logoLocal}" width="22" height="22" alt="">`
                                    : ''
                                }

                                <span class="fw-bold text-dark" style="font-size:0.8rem">
                                    ${local}
                                </span>

                            </div>

                            <h4 class="my-2 fw-bold ${esJugado ? 'text-dark' : 'text-secondary'}">
                                ${marcador}
                            </h4>

                            <div class="d-flex align-items-center justify-content-center gap-1 my-2">

                                ${logoVisitante
                                    ? `<img src="${logoVisitante}" width="22" height="22" alt="">`
                                    : ''
                                }

                                <span class="fw-bold text-dark" style="font-size:0.8rem">
                                    ${visitante}
                                </span>

                            </div>

                        </div>

                        <div class="text-muted border-top pt-2 mt-2"
                             style="font-size:0.7rem">

                            <i class="far fa-calendar-alt me-1"></i>
                            ${fechaFormateada}

                            ${horaFormateada ? ` | ${horaFormateada}` : ''}

                        </div>

                    </div>

                </div>
            `;

            contenedor.appendChild(tarjeta);
        });

        console.log(`✅ ${partidos.length} partidos cargados correctamente`);

    } catch (error) {

        console.error('Error cargando partidos:', error);

        contenedor.innerHTML = `
            <p class="text-danger text-center">
                No se pudieron cargar los partidos del Real Zaragoza.
            </p>`;
    }
});
