const API_URL = "http://127.0.0.1:8000"; 

// Variable global para almacenar las solicitudes y permitir ordenarlas
let solicitudesGlobales = [];

// =========================================================================
// 1. CARGAR LAS RESERVAS Y SOLICITUDES DEL SOCIO DESDE EL BACKEND
// =========================================================================
async function cargarSolicitudesDesdeBackend(socioId) {
    const contenedorTabla = document.getElementById("tabla-mis-solicitudes");
    if (!contenedorTabla) return;

    try {
        const response = await fetch(`${API_URL}/reservas`);
        if (!response.ok) throw new Error("Error en la respuesta del servidor");
        
        const reservas = await response.json();
        
        // Convertimos a número el ID del usuario para comparar de forma estricta
        const idUsuarioNum = Number(socioId);

        // Filtramos las reservas del usuario actual por usuario_id y las guardamos globalmente
        solicitudesGlobales = reservas.filter(r => Number(r.usuario_id) === idUsuarioNum);

        if (solicitudesGlobales.length === 0) {
            contenedorTabla.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-3">No tienes solicitudes ni viajes activos actualmente.</td></tr>`;
            return;
        }

        // Pintamos aplicando el orden predeterminado
        ordenarSolicitudesSocio();

    } catch (error) {
        console.error("Error al cargar la tabla:", error);
        contenedorTabla.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-3">⚠️ Error de comunicación con el servidor.</td></tr>`;
    }
}

// =========================================================================
// 2. ENVIAR AL BACKEND EL COCHE COMPARTIDO (CON NOMBRE REAL DE SOCIO)
// =========================================================================
async function ofrecerCocheSocio(e) {
    if (e && typeof e.preventDefault === 'function') e.preventDefault();

    const selectPartido = document.getElementById("coche-viaje-select");
    const selectPlazas = document.getElementById("coche-plazas-select"); 

    if (!selectPartido || !selectPartido.value) {
        alert("Por favor, selecciona un partido/viaje de la lista.");
        return;
    }

    // Recuperamos el ID del usuario logueado
    const usuarioId = parseInt(localStorage.getItem("usuario_id") || "2", 10);
    
    // Recuperamos el NOMBRE REAL del socio logueado (desde localStorage)
    const nombreSocio = localStorage.getItem("usuario_nombre") || 
                        localStorage.getItem("nombre_socio") || 
                        localStorage.getItem("nombre") || 
                        `Socio #${usuarioId}`;
    
    const viajeId = parseInt(selectPartido.value, 10);
    const plazas = parseInt(selectPlazas ? selectPlazas.value : "4", 10) || 4;

    const opcion = selectPartido.options[selectPartido.selectedIndex];
    let rivalDinamico = opcion ? (opcion.getAttribute("data-rival") || "Rival") : "Rival";
    
    // Limpieza de prefijos sobrantes por si acaso
    rivalDinamico = rivalDinamico.replace(/^vs\.?\s+/i, '').trim();

    const fechaRealPartido = opcion ? (opcion.getAttribute("data-fecha") || new Date().toISOString().split('T')[0]) : new Date().toISOString().split('T')[0];

    // Payload enviado con la información del conductor y plazas
    const payload = {
        usuario_id: usuarioId,
        nombre_conductor: nombreSocio, // 👈 Se envía el nombre real recuperado
        viaje_id: viajeId,
        tipo_reserva: "Coche",
        asientos_reservados: plazas,
        motivo_evento: `🚗 Coche ofrecido por ${nombreSocio} (${plazas} plazas libres) para ir contra ${rivalDinamico}`,
        fecha_solicitada: fechaRealPartido
    };

    try {
        const res = await fetch(`${API_URL}/reservas`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || "Error al registrar el vehículo");
        }

        alert("¡Vehículo registrado con éxito!");
        window.location.reload();

    } catch (err) {
        console.error("Error en ofrecerCocheSocio:", err);
        alert(`No se pudo registrar el vehículo:\n${err.message}`);
    }
}

// =========================================================================
// 3. CARGAR PARTIDOS EN EL SELECTOR DEL DESPLAZAMIENTO
// =========================================================================
async function cargarPartidosEnSelectorSocio() {
    const select = document.getElementById("coche-viaje-select");
    if (!select) return;

    const urlParams = new URLSearchParams(window.location.search);
    const partidoPreseleccionado = urlParams.get('partido');

    try {
        const res = await fetch(`${API_URL}/partidos-zaragoza`);
        if (!res.ok) throw new Error("Error al obtener partidos");
        
        const data = await res.json();
        const partidos = data.partidos || [];

        const partidosFuera = partidos.filter(p => {
            const fixture = p.fixture || {};
            const teams = p.teams || {};
            const haTerminado = ['FT', 'AET', 'PEN'].includes(fixture.status?.short);
            if (haTerminado) return false;

            const equipoLocal = (teams.home?.name || "").toLowerCase();
            const equipoVisitante = (teams.away?.name || "").toLowerCase();
            return equipoVisitante.includes("zaragoza") || (!equipoLocal.includes("zaragoza") && equipoLocal.length > 0);
        });

        if (partidosFuera.length === 0) {
            select.innerHTML = `<option value="">No hay partidos fuera disponibles</option>`;
            return;
        }

        select.innerHTML = `<option value="">-- Selecciona el próximo partido fuera --</option>`;
        partidosFuera.forEach(p => {
            const fixture = p.fixture || {};
            const teams = p.teams || {};
            let rival = (teams.home?.name || "").toLowerCase().includes("zaragoza") ? teams.away?.name : teams.home?.name;
            
            // Limpiamos el nombre del rival para que no repita "vs"
            rival = (rival || "Rival").replace(/^vs\.?\s+/i, '').trim();

            const fechaIso = fixture.date ? fixture.date.split('T')[0] : new Date().toISOString().split('T')[0];
            const fechaStr = fixture.date ? new Date(fixture.date).toLocaleDateString('es-ES') : "Sin fecha";
            const partidoId = String(fixture.id || p.id || "");

            const isSelected = (partidoPreseleccionado && partidoPreseleccionado === partidoId) ? "selected" : "";

            select.insertAdjacentHTML("beforeend", `
                <option value="${partidoId}" data-rival="${rival}" data-fecha="${fechaIso}" ${isSelected}>
                    ${rival} (${fechaStr})
                </option>
            `);
        });

        if (partidoPreseleccionado) {
            select.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

    } catch (err) {
        select.innerHTML = `<option value="">Error al cargar partidos</option>`;
    }
}

// =========================================================================
// 4. EVENTOS PRINCIPALES E INICIALIZACIÓN
// =========================================================================
document.addEventListener("DOMContentLoaded", async () => {
    const socioId = parseInt(localStorage.getItem("usuario_id") || "2", 10);
    await cargarPartidosEnSelectorSocio();

    const btnRegistrarVehiculo = document.getElementById("btn-registrar-vehiculo");
    if (btnRegistrarVehiculo) {
        btnRegistrarVehiculo.onclick = ofrecerCocheSocio;
    }

    // Cargar directamente las solicitudes usando el usuario_id (socioId)
    cargarSolicitudesDesdeBackend(socioId);
});

// =========================================================================
// 5. CANCELAR / ELIMINAR RESERVA
// =========================================================================
async function eliminarReservaBackend(reservaId) {
    if (!reservaId || isNaN(reservaId)) {
        alert("⚠️ ID de reserva no válido.");
        return;
    }

    if (!confirm("¿Seguro que deseas cancelar esta solicitud o retirar tu vehículo?")) return;

    try {
        const response = await fetch(`${API_URL}/reservas/${reservaId}`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (response.ok) {
            alert("Solicitud cancelada y eliminada.");
            window.location.reload();
        } else {
            const errData = await response.json().catch(() => ({}));
            alert(`No se pudo procesar la eliminación: ${errData.detail || "Error en el servidor"}`);
        }
    } catch (error) {
        console.error("Error al eliminar:", error);
        alert("Error de conexión al intentar borrar.");
    }
}

// =========================================================================
// 6. ORDENAR SOLICITUDES DEL SOCIO
// =========================================================================
function ordenarSolicitudesSocio() {
    const selectFiltro = document.getElementById("filtro-orden");
    const criterio = selectFiltro ? selectFiltro.value : "fecha-asc";

    solicitudesGlobales.sort((a, b) => {
        const fechaA = new Date(a.fecha_solicitada || a.fecha_evento || a.fecha_reserva || '9999-12-31');
        const fechaB = new Date(b.fecha_solicitada || b.fecha_evento || b.fecha_reserva || '9999-12-31');

        const estadoA = (a.estado_solicitud || a.estado || "").toLowerCase();
        const estadoB = (b.estado_solicitud || b.estado || "").toLowerCase();

        const tipoA = (a.tipo_reserva || "").toLowerCase();
        const tipoB = (b.tipo_reserva || "").toLowerCase();

        if (criterio === "fecha-asc") {
            return fechaA - fechaB; 
        } else if (criterio === "fecha-desc") {
            return fechaB - fechaA; 
        } else if (criterio === "estado-asc") {
            return estadoA.localeCompare(estadoB);
        } else if (criterio === "estado-desc") {
            return estadoB.localeCompare(estadoA);
        } else if (criterio === "tipo-asc") {
            return tipoA.localeCompare(tipoB);
        } else if (criterio === "tipo-desc") {
            return tipoB.localeCompare(tipoA);
        }
        return 0;
    });

    pintarTablaSolicitudesSocio(solicitudesGlobales);
}

// =========================================================================
// 7. PINTAR TABLA DE SOLICITUDES DEL SOCIO
// =========================================================================
function pintarTablaSolicitudesSocio(lista) {
    const contenedorTabla = document.getElementById("tabla-mis-solicitudes");
    if (!contenedorTabla) return;

    contenedorTabla.innerHTML = "";

    if (!Array.isArray(lista) || lista.length === 0) {
        contenedorTabla.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-3">No hay solicitudes registradas.</td></tr>`;
        return;
    }

    lista.forEach(res => {
        const fila = document.createElement("tr");
        let badgeTipo = "";
        let detalle = "";
        let badgeEstado = "";

        const idReservaBD = res.id;

        const esCoche = res.tipo_reserva === "Coche" || 
                        (res.motivo_evento && (
                            res.motivo_evento.toLowerCase().includes("coche") || 
                            res.motivo_evento.toLowerCase().includes("vehículo") ||
                            res.motivo_evento.toLowerCase().includes("ofrece")
                        ));

        if (res.tipo_reserva === "Viaje" || res.tipo_reserva === "Coche" || esCoche) {
            badgeTipo = '<span class="badge bg-info text-dark">🔹 Logística</span>';
            detalle = esCoche ? `🚗 ${res.motivo_evento || 'Coche Compartido'}` : `🚌 Autobús (Asientos: ${res.asientos_reservados || 1})`;
            const estadoTexto = res.estado_solicitud || 'Aprobada';
            badgeEstado = `<span class="badge bg-success">✓ ${estadoTexto}</span>`;
        } else {
            badgeTipo = '<span class="badge bg-warning text-dark">🏠 Sede Social</span>';
            detalle = `Reserva de Local: ${res.motivo_evento || 'Evento común'}`;
            const estadoLocal = res.estado_solicitud || "Pendiente";

            if (estadoLocal === "Pendiente") {
                badgeEstado = '<span class="badge bg-warning text-dark">⏳ Pendiente</span>';
            } else if (estadoLocal === "Aprobada") {
                badgeEstado = `<span class="badge bg-success">✓ Aprobada</span>`;
            } else {
                badgeEstado = '<span class="badge bg-danger">✕ Rechazada</span>';
            }
        }

        let fechaRaw = res.fecha_solicitada || res.fecha_evento || res.fecha_reserva;
        let fechaFormateada = fechaRaw ? String(fechaRaw).split("T")[0] : "Programada";

        fila.innerHTML = `
            <td>${badgeTipo}</td>
            <td class="fw-bold">${detalle}</td>
            <td>${fechaFormateada}</td>
            <td>${badgeEstado}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-outline-danger" onclick="eliminarReservaBackend(${idReservaBD})">
                    <i class="fas fa-trash-alt me-1"></i> Cancelar
                </button>
            </td>
        `;
        contenedorTabla.appendChild(fila);
    });
}