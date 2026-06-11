// URL base unificada para conectar con tu servidor de FastAPI
const API_URL = "http://localhost:8000"; 

// =========================================================================
// 1. CARGAR LAS RESERVAS DEL SOCIO DESDE EL BACKEND
// =========================================================================
async function cargarSolicitudesDesdeBackend(socio) {
    const contenedorTabla = document.getElementById("tabla-mis-solicitudes");
    if (!contenedorTabla) return;

    try {
        // Petición al GET /reservas de tu FastAPI
        const response = await fetch(`${API_URL}/reservas`);
        if (!response.ok) throw new Error("Error en la respuesta del servidor");
        
        const reservas = await response.json();
        contenedorTabla.innerHTML = "";
        
        // Filtramos para mostrar únicamente las reservas del socio logueado
        const misReservas = reservas.filter(r => r.usuario_id === socio.id);

        if (misReservas.length === 0) {
            contenedorTabla.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-3">No tienes solicitudes ni viajes activos actualmente.</td></tr>`;
            return;
        }

        misReservas.forEach(res => {
            const fila = document.createElement("tr");
            let badgeTipo = "";
            let detalle = "";
            let badgeEstado = "";

            if (res.tipo_reserva === "Viaje") {
                badgeTipo = '<span class="badge bg-info text-dark">🔹 Logística</span>';
                
                // Detectamos si es un alta de coche a través de la cadena de texto
                if (res.motivo_evento && res.motivo_evento.includes("vehículo")) {
                    detalle = `🚗 Coche Compartido: ${res.motivo_evento}`;
                } else {
                    detalle = `🚌 Autobús (Asientos reservados: ${res.asientos_reservados || 1})`;
                }
                
                // Mapeamos el estado según tu backend ("Aprobada" por defecto)
                badgeEstado = `<span class="badge bg-success">✓ ${res.estado_solicitud || 'Aprobada'}</span>`;
            } else {
                badgeTipo = '<span class="badge bg-warning text-dark">🏠 Sede Social</span>';
                detalle = `Reserva de Local: ${res.motivo_evento || 'Evento común'}`;
                
                if (res.estado_solicitud === "Pendiente") {
                    badgeEstado = '<span class="badge bg-warning text-dark">⏳ Pendiente</span>';
                } else if (res.estado_solicitud === "Aprobada" || res.estado_solicitud === "Aprobada") {
                    badgeEstado = '<span class="badge bg-success">✓ Aprobada</span>';
                } else {
                    badgeEstado = '<span class="badge bg-danger">✕ Rechazada</span>';
                }
            }

            // Usamos la columna real de tu base de datos para la fecha o un fallback por si viene nula
            let fechaFormateada = res.fecha_reserva || "Programada";

            fila.innerHTML = `
                <td>${badgeTipo}</td>
                <td class="fw-bold">${detalle}</td>
                <td>${fechaFormateada}</td>
                <td>${badgeEstado}</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-danger" onclick="eliminarReservaBackend(${res.id})">
                        <i class="fas fa-trash-alt me-1"></i> Cancelar
                    </button>
                </td>
            `;
            contenedorTabla.appendChild(fila);
        });

    } catch (error) {
        console.error("Error al cargar la tabla:", error);
        contenedorTabla.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-3">⚠️ Error de comunicación con el servidor FastAPI.</td></tr>`;
    }
}

// =========================================================================
// 2. ENVIAR AL BACKEND EL COCHE COMPARTIDO
// =========================================================================
async function ofrecerCocheSocio(viajeId, plazasCoche) {
    // Obtenemos el ID del socio dinámicamente del almacenamiento del Login
    const socioId = parseInt(localStorage.getItem("socio_id")) || 1;

    // Payload perfectamente adaptado a tu schemas.ReservaCrear
    const payload = {
        usuario_id: socioId,
        tipo_reserva: "Viaje",
        viaje_id: parseInt(viajeId),
        asientos_reservados: 1, // El conductor ocupa su asiento
        motivo_evento: `Ofrece vehículo con ${plazasCoche} plazas.`
    };

    try {
        const response = await fetch(`${API_URL}/reservas`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (response.status === 404) {
            alert("⚠️ Error 404: El ID del viaje proporcionado no existe en la base de datos.");
            return;
        }

        const data = await response.json();

        if (response.ok) {
            alert("🚗 ¡Vehículo registrado con éxito en el viaje!");
            window.location.reload(); // Recarga limpia para actualizar la tabla
        } else {
            alert(`⚠️ Error del servidor: ${data.detail || "Verifica las restricciones de plazas."}`);
        }
    } catch (error) {
        console.error("Error en la conexión POST:", error);
        alert("Error de red: No se pudo contactar con el backend.");
    }
}

// =========================================================================
// 3. CANCELAR / ELIMINAR RESERVA (Conectado a tu @router.delete)
// =========================================================================
async function eliminarReservaBackend(reservaId) {
    if (!confirm("¿Seguro que deseas cancelar esta solicitud o retirar tu vehículo?")) return;

    try {
        const response = await fetch(`${API_URL}/reservas/${reservaId}`, {
            method: "DELETE"
        });

        if (response.ok) {
            alert("Solicitud cancelada y eliminada de PostgreSQL.");
            window.location.reload();
        } else {
            alert("No se pudo procesar la eliminación en el servidor.");
        }
    } catch (error) {
        console.error("Error al eliminar:", error);
        alert("Error de conexión al intentar borrar.");
    }
}