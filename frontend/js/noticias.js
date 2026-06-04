document.addEventListener('DOMContentLoaded', () => {
    const contenedor = document.getElementById('lista-noticias');

    fetch('http://localhost:8000/noticias')
        .then(response => response.json())
        .then(data => {
            contenedor.innerHTML = '';
            
            if (!data || data.length === 0) {
                contenedor.innerHTML = '<p class="text-center">No hay noticias recientes.</p>';
                return;
            }

            data.forEach(noticia => {
                // Asegúrate de que tu backend esté enviando el campo 'link'
                // Si no, añádelo en el backend primero (te pongo cómo abajo)
                const link = noticia.link || '#'; 

                contenedor.innerHTML += `
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-body">
                                <h5 class="card-title">${noticia.titulo}</h5>
                                <h6 class="card-subtitle mb-2 text-muted">${noticia.fecha}</h6>
                                <p class="card-text">${noticia.resumen}</p>
                                <a href="${link}" target="_blank" class="btn btn-primary">Leer más</a>
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