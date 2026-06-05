document.addEventListener("DOMContentLoaded", () => {
    // Comprobamos si el socio se ha logado (buscando su token o nombre en el almacenamiento del navegador)
    const socioLogado = localStorage.getItem("socio_nombre"); // Esto lo guardaremos cuando hagamos el Login

    if (!socioLogado) {
        // Si no está logado, le avisamos y lo redirigimos fuera de aquí
        alert("Área privada. Por favor, inicia sesión para ver los viajes y gestionar reservas.");
        window.location.href = "login.html"; 
        return; // Detiene la ejecución del script para que no cargue los viajes por detrás
    }

    // Si pasa el control, entonces sí, cargamos la cartelera
    cargarViajes();
});

// FASE 1: Traer los viajes de la API y pintarlos
async function cargarViajes() {
    const contenedor = document.getElementById("contenedor-viajes"); // Asegúrate de que este ID exista en tu HTML
    
    try {
        const response = await fetch("http://localhost:8000/viajes/");
        if (!response.ok) throw new Error("Error al obtener los viajes");
        
        const viajes = await response.json();
        contenedor.innerHTML = ""; // Limpiamos el cargando...

        if (viajes.length === 0) {
            contenedor.innerHTML = `<p class="text-center text-muted">No hay viajes programados en este momento.</p>`;
            return;
        }

        viajes.forEach(viaje => {
            contenedor.innerHTML += `
                <div class="col-md-4 mb-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title text-primary">Destino: ${viaje.destino}</h5>
                            <p class="card-text mb-1"><strong>Fecha:</strong> ${viaje.fecha}</p>
                            <p class="card-text mb-1"><strong>Precio:</strong> ${viaje.precio}€</p>
                            <p class="card-text text-muted flex-grow-1">${viaje.descripcion || 'Sin descripción disponible.'}</p>
                            
                            <!-- Guardamos el ID del viaje en un atributo 'data-id' -->
                            <button class="btn btn-success w-100 btn-reservar" data-id="${viaje.id}">
                                Reservar Plaza
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });

        // Una vez pintados los botones, les añadimos el "escuchador" de clics
        configurarBotonesReserva();

    } catch (error) {
        console.error("Error:", error);
        contenedor.innerHTML = `<p class="text-center text-danger">No se pudo conectar con el servidor de la Peña.</p>`;
    }
}

// FASE 2: Capturar el clic del botón Reservar
function configurarBotonesReserva() {
    const botones = document.querySelectorAll(".btn-reservar");
    
    botones.forEach(boton => {
        boton.addEventListener("click", async (e) => {
            const viajeId = e.target.getAttribute("data-id");
            
            // 1. Pedimos el nombre del socio
            const nombreSocio = prompt("Por favor, introduce tu Nombre y Apellidos para la reserva:");
            if (!nombreSocio || nombreSocio.trim() === "") {
                alert("Reserva cancelada: El nombre es obligatorio.");
                return;
            }

            // 2. Pedimos cuántos asientos quiere (por defecto ponemos 1)
            const asientosInput = prompt("¿Cuántos asientos deseas reservar?", "1");
            const asientos = parseInt(asientosInput);

            if (isNaN(asientos) || asientos <= 0) {
                alert("Reserva cancelada: El número de asientos debe ser mayor que 0.");
                return;
            }

            // Llamamos a la función que conecta con tu API real
            await realizarReserva(viajeId, nombreSocio, asientos);
        });
    });
}

// FASE 3: Enviar el POST a la API de FastAPI (POST /reservas)
async function realizarReserva(viajeId, nombreSocio, asientos) {
    try {
        const response = await fetch("http://localhost:8000/reservas", { // Tu prefijo es /reservas
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                viaje_id: parseInt(viajeId),
                nombre_socio: nombreSocio,
                asientos_reservados: asientos
            })
        });

        const resultado = await response.json();

        if (response.ok) {
            // Tu backend devuelve: {"ok": true, "mensaje": "...", "reserva": ...}
            alert(`¡Excelente! ${resultado.mensaje}`);
            
            // Refrescamos los viajes para que se vea reflejado que quedan menos plazas disponibles
            cargarViajes();
        } else {
            // Captura los errores de HTTPException de tu backend (404, 400 sin plazas, etc.)
            alert(`Error del servidor: ${resultado.detail || 'No se pudo procesar la reserva.'}`);
        }

    } catch (error) {
        console.error("Error en la petición POST:", error);
        alert("Hubo un problema de conexión con el servidor de la Peña.");
    }
}