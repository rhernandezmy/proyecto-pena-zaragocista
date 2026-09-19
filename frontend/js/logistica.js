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

    // Verificamos si existe el contenedor de solicitudes del LOCAL para activarlo
    if (document.getElementById("tabla-reservas-local-admin")) {
        cargarReservasLocalAdmin();
    }
});

// =========================================================================
// 1. CARGAR PARTIDOS EN EL SELECT DESPLEGABLE
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
// 2. OBTENER Y PINTAR VIAJES EN LA TABLA DE ADMINISTRACIÓN
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
// 3. CONFIGURAR EL FORMULARIO DE CREACIÓN DE VIAJES
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
// 4. ELIMINAR VIAJE DE LA BASE DE DATOS
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
// 5. CARGAR Y PINTAR SOLICITUDES DEL LOCAL EN EL PANEL DEL ADMIN
// =========================================================================
async function cargarReservasLocalAdmin() {
    const tablaLocal = document.getElementById("tabla-reservas-local-admin");
    if (!tablaLocal) return;

    try {
        const response = await fetch(`${API_URL}/reservas`);
        if (!response.ok) throw new Error("Error al descargar reservas");

        const todasLasReservas = await response.json();
        tablaLocal.innerHTML = "";

        const reservasLocal = todasLasReservas.filter(r => r.tipo_reserva === "Local");

        if (reservasLocal.length === 0) {
            tablaLocal.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-3">No hay solicitudes pendientes o registradas.</td></tr>`;
            return;
        }

        reservasLocal.forEach(res => {
            const fila = document.createElement("tr");

            // 1. Mapeo del Nombre del Socio
            const nombreSocio = res.socio_nombre || res.nombre_socio || res.socio || (res.usuario_id ? `Socio #${res.usuario_id}` : "Socio registrado");
            const emailSocio = res.socio_email || res.email_socio || "";

            // 2. CORRECCIÓN DE FECHA: Priorizamos la fecha SOLICITADA (Elegida por el usuario)
            let fechaRaw = res.fecha_solicitada || res.fecha_evento || res.fecha_reserva;
            let fechaLimpia = "Sin fecha";

            if (fechaRaw) {
                fechaLimpia = fechaRaw.split("T")[0];
            }

            // 3. Mapeo del Motivo
            const motivo = res.motivo_evento || res.motivo || "Uso de Sede";

            // 4. Mapeo del Estado (evitando undefined)
            const estado = res.estado_solicitud || res.estado || "Pendiente";

            // Tratamiento visual según el estado obtenido
            let badgeEstado = `<span class="badge bg-warning text-dark">⏳ ${estado}</span>`;
            if (estado === "Aprobada" || estado === "Aceptada") {
                badgeEstado = `<span class="badge bg-success">✅ Aprobada</span>`;
            } else if (estado === "Rechazada") {
                badgeEstado = `<span class="badge bg-danger">❌ Rechazada</span>`;
            }

            fila.innerHTML = `
                <td class="fw-bold">#${res.id}</td>
                <td><strong>${nombreSocio}</strong>${emailSocio ? `<br><small class="text-muted">${emailSocio}</small>` : ''}</td>
                <td><span class="badge bg-light text-dark border">${fechaLimpia}</span></td>
                <td><em>"${motivo}"</em></td>
                <td class="text-center">${badgeEstado}</td>
                <td class="text-center">
                    <button class="btn btn-xs btn-success me-1" onclick="resolverLocalBackend(${res.id}, 'Aprobada')" title="Aprobar Solicitud" ${estado !== 'Pendiente' ? 'disabled' : ''}>
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn btn-xs btn-warning me-1" onclick="resolverLocalBackend(${res.id}, 'Rechazada')" title="Rechazar Solicitud" ${estado !== 'Pendiente' ? 'disabled' : ''}>
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
        tablaLocal.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-3">⚠️ Error al conectar con el módulo de reservas.</td></tr>`;
    }
}

// =========================================================================
// 6. ENVIAR RESOLUCIÓN AL BACKEND (PATCH)
// =========================================================================
async function resolverLocalBackend(idReserva, nuevoEstado) {
    try {
        const response = await fetch(`${API_URL}/reservas/${idReserva}/resolucion?estado=${nuevoEstado}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" }
        });

        if (response.ok) {
            cargarReservasLocalAdmin(); // Refresca la tabla tras actualizar
        } else {
            const err = await response.json();
            alert(`Error al actualizar la reserva: ${err.detail || 'Operación no permitida.'}`);
        }
    } catch (error) {
        console.error("Error al resolver la reserva:", error);
        alert("Error al conectar con el servidor.");
    }
}

// =========================================================================
// 7. ELIMINAR / CANCELAR RESERVA DE LOCAL DEFINITIVAMENTE
// =========================================================================
async function eliminarReservaLocalBackend(idReserva) {
    if (!confirm("¿Seguro que deseas borrar este registro de reserva?")) return;

    try {
        const response = await fetch(`${API_URL}/reservas/${idReserva}`, {
            method: "DELETE"
        });

        if (response.ok) {
            cargarReservasLocalAdmin();
        } else {
            alert("No se pudo eliminar el registro.");
        }
    } catch (error) {
        console.error("Error al eliminar la reserva:", error);
    }
}