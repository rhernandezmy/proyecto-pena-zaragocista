document.addEventListener('DOMContentLoaded', () => {
    const contenedor = document.getElementById('lista-partidos');

    // 1. CARGA DE PARTIDOS DEL REAL ZARAGOZA (Tu código original intacto)
    fetch('http://localhost:8000/partidos')
        .then(response => response.json())
        .then(data => {
            contenedor.innerHTML = '';
            
            if (!data || data.length === 0) {
                contenedor.innerHTML = '<p class="text-center">Actualmente no hay partidos programados.</p>';
                return;
            }

            // Ordenamos los partidos por fecha (del más cercano al más lejano)
            data.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));

            data.forEach(partido => {
                const local = partido.equipo_local || 'Real Zaragoza';
                const visitante = partido.equipo_visitante || 'Rival';
                const estadio = partido.estadio || 'Estadio por confirmar';
                
                // Formateamos la fecha a algo legible
                const fechaFormateada = new Date(partido.fecha).toLocaleDateString('es-ES', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                });

                contenedor.innerHTML += `
                    <div class="col-md-4 mb-4">
                        <div class="card shadow-sm">
                            <div class="card-body">
                                <h5 class="card-title">${local} vs ${visitante}</h5>
                                <p class="card-text text-muted">
                                    <strong>Fecha:</strong> ${fechaFormateada}<br>
                                    <strong>Estadio:</strong> ${estadio}
                                </p>
                                <button class="btn btn-outline-primary btn-sm">Más información</button>
                            </div>
                        </div>
                    </div>
                `;
            });
        })
        .catch(error => {
            console.error('Error cargando partidos:', error);
            contenedor.innerHTML = '<p class="text-danger text-center">No se pudieron cargar los partidos.</p>';
        });

    // 2. NUEVA FUNCIÓN: CARGA SUBTIL DE OTROS MARCADORES DEL MUNDIAL
    cargarMarcadoresGlobalesMundial();
});

async function cargarMarcadoresGlobalesMundial() {
    // Buscamos el contenedor sutil que pondremos en el HTML
    const contenedorMundial = document.getElementById('contenedor-partidos-globales');
    if (!contenedorMundial) return;

    try {
        const res = await fetch("http://localhost:8000/mundial/partidos-globales");
        const datos = await res.json();
        
        contenedorMundial.innerHTML = "";
        
        // Creamos la línea pequeña, grisácea y muy elegante
        let htmlContenido = `
            <div class="text-center text-muted small border-top pt-3 mt-4" style="font-size: 0.82rem; letter-spacing: 0.5px;">
                <span class="fw-bold text-uppercase text-secondary me-2">Otros marcadores del Mundial:</span> `;
        
        datos.partidos.forEach((partido, index) => {
            const golesHome = partido.score?.fullTime?.home !== null ? partido.score.fullTime.home : "-";
            const golesAway = partido.score?.fullTime?.away !== null ? partido.score.fullTime.away : "-";
            
            htmlContenido += `
                <span class="mx-2">
                    ${partido.homeTeam.name} <b class="text-dark">${golesHome}-${golesAway}</b> ${partido.awayTeam.name}
                </span>`;
                
            // Añadimos la barrita de separación menos en el último
            if (index < datos.partidos.length - 1) {
                htmlContenido += ` <span class="text-muted">|</span> `;
            }
        });
        
        htmlContenido += `</div>`;
        contenedorMundial.innerHTML = htmlContenido;
        
    } catch (err) {
        console.error("Error silencioso cargando marcadores del mundial:", err);
    }
}