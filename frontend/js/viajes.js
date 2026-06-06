document.addEventListener("DOMContentLoaded", () => {
    // Obtenemos el ID del socio logado desde localStorage
    const usuarioId = localStorage.getItem("socio_id"); 

    if (!usuarioId) {
        alert("Área privada. Por favor, inicia sesión para gestionar reservas.");
        window.location.href = "login.html"; 
        return;
    }

    cargarViajes();
});

async function cargarViajes() {
    const contenedor = document.getElementById("contenedor-viajes");
    
    try {
        const response = await fetch("http://localhost:8000/viajes");
        if (!response.ok) throw new Error("Error al obtener los viajes");
        
        const viajes = await response.json();
        contenedor.innerHTML = "";

        if (viajes.length === 0) {
            contenedor.innerHTML = `<p class="text-center text-muted">No hay viajes programados.</p>`;
            return;
        }

        viajes.forEach(viaje => {
            contenedor.innerHTML += `
                <div class="col-md-4 mb-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title text-primary">Destino: ${viaje.destino}</h5>
                            <p class="card-text mb-1"><strong>Precio:</strong> ${viaje.precio}€</p>
                            <p class="card-text mb-1"><strong>Plazas disponibles:</strong> ${viaje.plazas_disponibles}</p>
                            <button class="btn btn-success w-100 btn-reservar" data-id="${viaje.id}">
                                Reservar Plaza
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        configurarBotonesReserva();
    } catch (error) {
        contenedor.innerHTML = `<p class="text-center text-danger">No se pudo conectar con el servidor.</p>`;
    }
}

function configurarBotonesReserva() {
    document.querySelectorAll(".btn-reservar").forEach(boton => {
        boton.addEventListener("click", async (e) => {
            const viajeId = e.target.getAttribute("data-id");
            const asientosInput = prompt("¿Cuántos asientos deseas reservar?", "1");
            const asientos = parseInt(asientosInput);

            if (isNaN(asientos) || asientos <= 0) return;

            // Enviamos el usuarioId que ya tenemos en localStorage
            const usuarioId = localStorage.getItem("socio_id");
            await realizarReserva(viajeId, usuarioId, asientos);
        });
    });
}

async function realizarReserva(viajeId, usuarioId, asientos) {
    try {
        const response = await fetch("http://localhost:8000/reservas", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                viaje_id: parseInt(viajeId),
                usuario_id: parseInt(usuarioId), // Ahora usamos usuario_id (entero)
                asientos_reservados: asientos
            })
        });

        const resultado = await response.json();

        if (response.ok) {
            alert("¡Reserva realizada con éxito!");
            cargarViajes();
        } else {
            alert(`Error: ${resultado.detail || 'No se pudo procesar la reserva.'}`);
        }
    } catch (error) {
        alert("Error de conexión con el servidor.");
    }
}