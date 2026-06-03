document.addEventListener("DOMContentLoaded", () => {
    const contenedorViajes = document.getElementById("lista-viajes");

    // Función para obtener viajes desde el backend
    async function cargarViajes() {
        try {
            // Asegúrate de que el puerto coincida con tu uvicorn (generalmente 8000)
            const response = await fetch("http://localhost:8000/viajes");
            if (!response.ok) throw new Error("Error al conectar con la API");
            
            const viajes = await response.json();

            // Limpiamos el contenedor
            contenedorViajes.innerHTML = "";

            // Renderizamos cada viaje
            viajes.forEach(viaje => {
                const card = `
                    <div class="col-md-4 mb-3">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Destino: ${viaje.destino}</h5>
                                <p class="card-text">Precio: ${viaje.precio}€</p>
                                <p class="card-text">Plazas: ${viaje.plazas_disponibles}/${viaje.plazas_totales}</p>
                                <button class="btn btn-primary">Reservar</button>
                            </div>
                        </div>
                    </div>
                `;
                contenedorViajes.innerHTML += card;
            });
        } catch (error) {
            console.error("Error:", error);
            contenedorViajes.innerHTML = `<p class="text-danger">No se pudieron cargar los viajes. Asegúrate de que el backend está encendido.</p>`;
        }
    }

    cargarViajes();
});