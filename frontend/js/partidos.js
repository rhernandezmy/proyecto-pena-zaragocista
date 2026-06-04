document.addEventListener('DOMContentLoaded', () => {
    const contenedor = document.getElementById('lista-partidos');

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
});