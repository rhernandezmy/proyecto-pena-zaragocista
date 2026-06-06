document.addEventListener('DOMContentLoaded', () => {
    const contenedor = document.getElementById('lista-noticias');

    fetch('http://localhost:8000/noticias')
        .then(response => response.json())
        .then(data => {
            contenedor.innerHTML = '';
            const listaNoticias = data.noticias;
            
            if (!listaNoticias || listaNoticias.length === 0) {
                contenedor.innerHTML = '<p class="text-center">No hay noticias recientes.</p>';
                return;
            }

            listaNoticias.forEach(n => {
                contenedor.innerHTML += `
                    <div class="col-md-6 mb-4">
                        <div class="card h-100 shadow-sm">
                            <div class="card-body">
                                <span class="badge bg-primary mb-2">${n.fuente}</span>
                                <h5 class="card-title">${n.titulo}</h5>
                                <h6 class="card-subtitle mb-2 text-muted" style="font-size: 0.8rem;">${n.fecha}</h6>
                                <p class="card-text small">${n.resumen}</p>
                                <a href="${n.link}" target="_blank" class="btn btn-outline-primary btn-sm">Leer más</a>
                            </div>
                        </div>
                    </div>
                `;
            });
        })
        .catch(error => {
            console.error('Error:', error);
            contenedor.innerHTML = '<p class="text-danger">No se pudieron cargar las noticias.</p>';
        });
});