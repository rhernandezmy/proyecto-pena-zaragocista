document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM cargado. Buscando contenedor...");
    const contenedorViajes = document.getElementById("lista-viajes");
    
    if (!contenedorViajes) {
        console.error("¡ERROR! No encuentro el elemento con id 'lista-viajes' en el HTML.");
        return;
    }

    async function cargarViajes() {
        console.log("Iniciando fetch a la API...");
        try {
            const response = await fetch("http://localhost:8000/viajes");
            console.log("Estado de la respuesta:", response.status);
            
            const viajes = await response.json();
            console.log("Viajes recibidos:", viajes);

            contenedorViajes.innerHTML = "";
            viajes.forEach(viaje => {
                console.log("Renderizando destino:", viaje.destino); // Para confirmar qué datos llegan
                
                const card = `
                    <div class="col-md-4 mb-3">
                        <div class="card shadow">
                            <div class="card-body">
                                <h5 class="card-title">Destino: ${viaje.destino}</h5>
                                <p class="card-text">Precio: ${viaje.precio}€</p>
                                <p class="card-text">Plazas: ${viaje.plazas_disponibles}/${viaje.plazas_totales}</p>
                                <button class="btn btn-primary w-100">Reservar</button>
                            </div>
                        </div>
                    </div>
                `;
                contenedorViajes.insertAdjacentHTML('beforeend', card);
            });
        } catch (error) {
            console.error("DEBUG CRÍTICO:", error);
            contenedorViajes.innerHTML = `<p>Error al conectar con la API.</p>`;
        }
    }

    cargarViajes();
});