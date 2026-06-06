// app.js - Versión mejorada de depuración
async function cargarViajes() {
    try {
        const response = await fetch("http://localhost:8000/viajes");
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const viajes = await response.json();
        console.log("Datos recibidos:", viajes); // Veremos qué llega aquí

        const contenedorViajes = document.getElementById("lista-viajes");
        contenedorViajes.innerHTML = "";

        if (viajes.length === 0) {
            contenedorViajes.innerHTML = "<p class='text-center'>No hay viajes programados.</p>";
            return;
        }

        viajes.forEach(viaje => {
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
        document.getElementById("lista-viajes").innerHTML = 
            `<div class="alert alert-danger">Error: ${error.message}. Verifica que el backend esté activo.</div>`;
    }
}