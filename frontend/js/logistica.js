// URL base de tu servidor backend de FastAPI
const API_URL = "http://localhost:8000"; 

// Ejecutar automáticamente al cargar la página para dar vida a los formularios y tablas
document.addEventListener("DOMContentLoaded", () => {
    // Verificamos si estamos en la interfaz que contiene los elementos de logística de viajes
    if (document.getElementById("tabla-viajes-admin") || document.getElementById("viaje-partido-select")) {
        cargarViajesAdmin();
        cargarPartidosEnDesplegable();
        configurarFormularioViajeAdmin();
    }

    // NUEVO: Verificamos si existe el contenedor de solicitudes del LOCAL para activarlo
    if (document.getElementById("tabla-reservas-local-admin")) {
        cargarReservasLocalAdmin();
    }
});

// =========================================================================
// 1. CARGAR PARTIDOS EN EL SELECT DESPLEGABLE (Mantenido)
// =========================================================================
async function cargarPartidosEnDesplegable() {
    const selectPartido = document.getElementById("viaje-partido-select");
    if (!selectPartido) return;

    try {
        const response = await fetch(`${API_URL}/partidos`);
        if (!response.ok) throw new Error("No se pudieron cargar los partidos");

        const partidos = await response.json();
        selectPartido.innerHTML = '<option value="">-- Selecciona un Partido / Destino --</option>';

        if (partidos.length === 0) {
            selectPartido.innerHTML = '<option value="">⚠️ Crea primero un partido en la sección de Partidos</option>';
            return;
        }

        partidos.forEach(p => {
            const nombreRival = p.rival || "Rival Desconocido";
            const lugarPartido = p.lugar || "Fuera";
            const fechaPartido = p.fecha || "";
            
            const textoPartido = `${nombreRival} (${lugarPartido}) - ${fechaPartido}`;
            selectPartido.innerHTML += `<option value="${p.id}">${textoPartido}</option>`;
        });
    } catch (error) {
        console.error("Error al poblar el select de partidos:", error);
        selectPartido.innerHTML = '<option value="">⚠️ Error de conexión al cargar partidos</option>';
    }
}

// =========================================================================
// 2. OBTENER Y PINTAR VIAJES EN LA TABLA DE ADMINISTRACIÓN (Mantenido)
// =========================================================================
async function cargarViajesAdmin() {
    const tablaViajes = document.getElementById("tabla-viajes-admin");
    if (!tablaViajes) return;

    try {
        const response = await fetch(`${API_URL}/viajes`);
        if (!response.ok) throw new Error("Error al obtener los viajes");
        
        const viajes = await response.json();
        tablaViajes.innerHTML = "";

        if (viajes.length === 0) {
            tablaViajes.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-3">No hay viajes reales en la base de datos. ¡Crea el primero!</td></tr>`;
            return;
        }

        viajes.forEach(v => {
            const fila = document.createElement("tr");
            const iconoTransporte = v.tipo_transporte === "Autobús" ? "🚌 Autobús" : "🚗 Coche";

            fila.innerHTML = `
                <td class="fw-bold">#${v.id}</td>
                <td><strong>${v.destino || 'Destino Vinculado'}</strong></td>
                <td>${v.fecha || 'Sin fecha'}</td>
                <td><span class="badge bg-secondary">${iconoTransporte}</span></td>
                <td><span class="badge bg-primary">${v.plazas_totales} disponibles</span></td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-danger" onclick="eliminarViajeBackend(${v.id})">
                        <i class="fas fa-trash-alt"></i> Cancelar
                    </button>
                </td>
            `;
            tablaViajes.appendChild(fila);
        });
    } catch (error) {
        console.error("Error al cargar viajes:", error);
        tablaViajes.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-3">⚠️ Error de conexión con FastAPI al cargar la lista.</td></tr>`;
    }
}

// =========================================================================
// 3. CONFIGURAR EL FORMULARIO DE CREACIÓN DE VIAJES (Mantenido)
// =========================================================================
function configurarFormularioViajeAdmin() {
    const formViaje = document.getElementById("form-nuevo-viaje");
    if (!formViaje) return;

    const antiguoForm = formViaje;
    const nuevoForm = antiguoForm.cloneNode(true);
    antiguoForm.parentNode.replaceChild(nuevoForm, antiguoForm);

    nuevoForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const selectPartido = nuevoForm.querySelector("#viaje-partido-select");
        const fechaInput = nuevoForm.querySelector("#viaje-fecha");
        const transporteSelect = nuevoForm.querySelector("#viaje-transporte");
        const plazasInput = nuevoForm.querySelector("#viaje-plazas");

        if (!selectPartido.value) {
            alert("Por favor, selecciona un partido válido de la lista.");
            return;
        }

        const textoCompletoPartido = selectPartido.options[selectPartido.selectedIndex].text;
        const destinoTextoLimpio = textoCompletoPartido.split("-")[0].trim();

        const payload = {
            partido_id: parseInt(selectPartido.value),
            destino: destinoTextoLimpio,
            fecha: fechaInput.value,
            tipo_transporte: transporteSelect.value,
            plazas_totales: parseInt(plazasInput.value) || 0
        };

        try {
            const response = await fetch(`${API_URL}/viajes`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert("🚀 ¡Viaje publicado On Tour con éxito en la base de datos!");
                nuevoForm.reset();
                cargarViajesAdmin();
            } else {
                const errData = await response.json();
                alert(`⚠️ Error al guardar: ${errData.detail || "No se pudo procesar."}`);
            }
        } catch (error) {
            console.error("Error de red:", error);
            alert("Error crítico de red: No se pudo conectar con el servidor.");
        }
    });
}

// =========================================================================
// 4. ELIMINAR VIAJE DE LA BASE DE DATOS (Mantenido)
// =========================================================================
async function eliminarViajeBackend(idViaje) {
    if (!confirm(`¿Seguro que deseas eliminar el viaje con ID #${idViaje}?`)) return;

    try {
        const response = await fetch(`${API_URL}/viajes/${idViaje}`, {
            method: "DELETE"
        });

        if (response.ok) {
            alert("Viaje eliminado correctamente.");
            cargarViajesAdmin(); 
        } else {
            alert("El servidor denegó la eliminación.");
        }
    } catch (error) {
        console.error("Error al intentar borrar el viaje:", error);
        alert("Error de conexión al intentar borrar.");
    }
}


// =========================================================================
// NUEVO -> 5. CARGAR Y PINTAR SOLICITUDES DEL LOCAL EN EL PANEL DEL ADMIN
// =========================================================================
async function cargarReservasLocalAdmin() {
    const tablaLocal = document.getElementById("tabla-reservas-local-admin");
    if (!tablaLocal) return;

    try {
        // Consultamos el endpoint unificado de reservas
        const response = await fetch(`${API_URL}/reservas`);
        if (!response.ok) throw new Error("Error al descargar reservas");

        const todasLasReservas = await response.json();
        tablaLocal.innerHTML = "";

        // Filtramos para quedarnos estrictamente con las peticiones del LOCAL
        const reservasLocal = todasLasReservas.filter(r => r.tipo_reserva === "Local");

        if (reservasLocal.length === 0) {
            tablaLocal.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-3">No hay solicitudes de uso del local pendientes ni registradas.</td></tr>`;
            return;
        }

        reservasLocal.forEach(res => {
            const fila = document.createElement("tr");
            
            // Tratamiento visual de las fechas
            let fechaLimpia = "Sin fecha";
            if (res.fecha_solicitada) {
                fechaLimpia = res.fecha_solicitada.split("T")[0];
            }

            // Tratamiento visual según el estado de la solicitud
            let badgeEstado = "";
            if (res.estado_solicitud === "Pendiente") {
                badgeEstado = `<span class="badge bg-warning text-dark">⏳ Pendiente</span>`;
            } else if (res.estado_solicitud === "Aprobada") {
                badgeEstado = `<span class="badge bg-success">✅ Aprobada</span>`;
            } else {
                badgeEstado = `<span class="badge bg-danger">❌ Rechazada</span>`;
            }

            fila.innerHTML = `
                <td class="fw-bold">#${res.id}</td>
                <td><strong>${res.socio_nombre}</strong><br><small class="text-muted">${res.socio_email}</small></td>
                <td><span class="badge bg-light text-dark border">${fechaLimpia}</span></td>
                <td><em>"${res.motivo_evento}"</em></td>
                <td class="text-center">${badgeEstado}</td>
                <td class="text-center">
                    <button class="btn btn-xs btn-success me-1" onclick="resolverLocalBackend(${res.id}, 'Aprobada')" title="Aprobar Solicitud" ${res.estado_solicitud !== 'Pendiente' ? 'disabled' : ''}>
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn btn-xs btn-warning me-1" onclick="resolverLocalBackend(${res.id}, 'Rechazada')" title="Rechazar Solicitud" ${res.estado_solicitud !== 'Pendiente' ? 'disabled' : ''}>
                        <i class="fas fa-times"></i>
                    </button>
                    <button class="btn btn-xs btn-outline-danger" onclick="eliminarReservaLocalBackend(${res.id})" title="Eliminar Registro">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            `;
            tablaLocal.appendChild(fila);
        });

    } catch (error) {
        console.error("Error al renderizar el local:", error);
        tablaLocal.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-3">⚠️ Error al conectar con el módulo de reservas del local.</td></tr>`;
    }
}

// =========================================================================
// NUEVO -> 6. ENVIAR RESOLUCIÓN AL BACKEND (PATCH)
// =========================================================================
async function resolverLocalBackend(reservaId, nuevoEstado) {
    try {
        // Apuntamos al endpoint estructurado: /reservas/{id}/resolucion?estado=...
        const response = await fetch(`${API_URL}/reservas/${reservaId}/resolucion?estado=${nuevoEstado}`, {
            method: "PATCH"
        });

        if (response.ok) {
            alert(`📍 Solicitud procesada y marcada como: ${nuevoEstado}`);
            cargarReservasLocalAdmin(); // Refresca la tabla automáticamente en caliente
        } else {
            const err = await response.json();
            alert(`⚠️ Error al resolver la solicitud: ${err.detail}`);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Fallo de red al enviar la resolución del local.");
    }
}

// =========================================================================
// NUEVO -> 7. ELIMINAR / CANCELAR RESERVA DE LOCAL DEFINITIVAMENTE (DELETE)
// =========================================================================
async function eliminarReservaLocalBackend(reservaId) {
    if (!confirm("⚠️ ¿Estás seguro de que deseas eliminar permanentemente este registro de reserva del local?")) return;

    try {
        const response = await fetch(`${API_URL}/reservas/${reservaId}`, {
            method: "DELETE"
        });

        if (response.ok) {
            alert("🗑️ Registro eliminado de la base de datos con éxito.");
            cargarReservasLocalAdmin();
        } else {
            alert("No se pudo eliminar la reserva solicitada.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Fallo en la comunicación de red.");
    }
}