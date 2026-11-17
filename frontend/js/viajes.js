// Variable global para almacenar las solicitudes y permitir ordenarlas sin errores
let solicitudesGlobales = [];

document.addEventListener("DOMContentLoaded", () => {
    console.log("Cargando módulo de viajes...");
    cargarModuloViajes();
});

// Función para cargar los viajes y partidos desde el backend y la API de partidos
async function cargarModuloViajes() {
    const contenedor = document.getElementById("contenedor-viajes");
    if (!contenedor) {
        console.error("No se encontró el contenedor #contenedor-viajes en el DOM.");
        return;
    }

    try {
        // Peticiones paralelas al backend y a la API de partidos
        const [resViajes, resPartidos] = await Promise.all([
            fetch("/viajes").catch(err => { console.error("Error fetch viajes:", err); return null; }),
            fetch("/partidos-zaragoza").catch(err => { console.error("Error fetch partidos:", err); return null; })
        ]);

        const viajes = (resViajes && resViajes.ok) ? await resViajes.json() : [];
        const dataPartidos = (resPartidos && resPartidos.ok) ? await resPartidos.json() : {};
        const partidos = dataPartidos.partidos || [];

        console.log("Viajes obtenidos de la BD:", viajes);

        // Filtrar partidos del Real Zaragoza jugando fuera de casa
        const partidosFuera = partidos.filter(p => {
            const fixture = p.fixture || {};
            const teams = p.teams || {};
            const haTerminado = ['FT', 'AET', 'PEN'].includes(fixture.status?.short);
            if (haTerminado) return false;
            
            const equipoLocal = (teams.home?.name || "").toLowerCase();
            const equipoVisitante = (teams.away?.name || "").toLowerCase();
            
            return equipoVisitante.includes("zaragoza") || (!equipoLocal.includes("zaragoza") && equipoLocal.length > 0);
        });

        contenedor.innerHTML = "";

        let htmlSection = `
            <div class="col-12 mb-3">
                <h3 class="fw-bold text-dark mb-0"><i class="fas fa-plane-departure text-primary me-2"></i>Próximos Desplazamientos</h3>
            </div>
        `;

        if (partidosFuera.length === 0) {
            htmlSection += `<div class="col-12 text-center py-4 bg-white rounded shadow-sm mb-4 border"><p class="text-muted mb-0">No hay próximos partidos fuera de casa programados.</p></div>`;
        } else {
            partidosFuera.slice(0, 3).forEach(p => {
                const fixture = p.fixture || {};
                const teams = p.teams || {};
                let rival = (teams.home?.name || "").toLowerCase().includes("zaragoza") ? teams.away?.name : teams.home?.name;
                
                rival = (rival || "").replace(/^vs\s+/i, '').trim();
                const fechaStr = fixture.date ? new Date(fixture.date).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' }) : "Fecha por confirmar";

                htmlSection += `
                    <div class="col-md-4 mb-4">
                        <div class="card h-100 border-0 shadow-sm">
                            <div class="card-body d-flex flex-column justify-content-between p-3">
                                <div>
                                    <span class="badge bg-warning text-dark mb-2">Fuera de Casa</span>
                                    <h5 class="fw-bold text-dark mb-1">${rival}</h5>
                                    <p class="text-secondary small mb-3"><i class="far fa-calendar-alt me-1"></i>${fechaStr}</p>
                                </div>
                                <a href="socio.html?partido=${fixture.id || p.id}#reservas" class="btn btn-sm btn-primary w-100 fw-bold">
                                    <i class="fas fa-car me-1"></i> Ofrecer Coche
                                </a>
                            </div>
                        </div>
                    </div>
                `;
            });
        }

        htmlSection += `
            <div class="col-12 mt-3 mb-3">
                <h4 class="fw-bold text-dark"><i class="fas fa-bus text-success me-2"></i>Plazas de Autobús / Coches Disponibles</h4>
            </div>
        `;

        if (!Array.isArray(viajes) || viajes.length === 0) {
            htmlSection += `
                <div class="col-12 text-center py-5 bg-white rounded shadow-sm border">
                    <i class="fas fa-bus-alt fa-3x text-muted mb-3 opacity-50"></i>
                    <p class="text-muted fw-bold mb-0">Aún no hay expediciones o coches registrados en el sistema.</p>
                </div>
            `;
        } else {
            // Ordenar cronológicamente
            viajes.sort((a, b) => {
                const fechaA = a.fecha_partido ? new Date(a.fecha_partido) : new Date('9999-12-31');
                const fechaB = b.fecha_partido ? new Date(b.fecha_partido) : new Date('9999-12-31');
                return fechaA - fechaB;
            });

            viajes.forEach(v => {
                const esCoche = (v.tipo_transporte && v.tipo_transporte.toLowerCase().includes("coche")) || 
                                (v.destino && v.destino.toLowerCase().includes("coche"));
                                
                const tipoIcono = esCoche ? "fa-car text-info" : "fa-bus text-success";
                
                let rivalLimpio = (v.rival || v.destino || "Desplazamiento")
                    .replace(/^vs\s+/i, '')
                    .replace(/^desplazamiento\s+/i, '')
                    .trim();

                let fechaFormateada = v.fecha_partido ? String(v.fecha_partido).split('T')[0] : (v.fecha || "Fecha pte.");
                let plazasTotales = v.plazas_totales !== undefined ? v.plazas_totales : 4;
                let plazasLibres = v.plazas_disponibles !== undefined ? v.plazas_disponibles : plazasTotales;

                // Extraemos el NOMBRE REAL del socio devuelto por el backend
                const nombreSocio = v.email_conductor || v.nombre_conductor || v.nombre_socio || v.conductor_nombre || "Socio de la Peña";

                htmlSection += `
                    <div class="col-md-6 col-lg-4 mb-4">
                        <div class="card h-100 shadow-sm border-0">
                            <div class="card-body d-flex flex-column justify-content-between">
                                <div>
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <h5 class="card-title fw-bold text-primary mb-0">${rivalLimpio}</h5>
                                        <i class="fas ${tipoIcono} fa-lg"></i>
                                    </div>
                                    <p class="card-text mb-1"><i class="far fa-calendar-alt me-2 text-muted"></i><strong>Fecha:</strong> ${fechaFormateada}</p>
                                    <p class="card-text mb-1"><i class="fas fa-users me-2 text-muted"></i><strong>Plazas libres:</strong> ${plazasLibres} de ${plazasTotales}</p>
                                    ${esCoche 
                                        ? `<p class="card-text small text-info fw-bold mt-2"><i class="fas fa-user-circle me-1"></i>Coche de: ${nombreSocio}</p>` 
                                        : `<p class="card-text small text-secondary mt-2"><i class="fas fa-bus me-1"></i>Autobús Oficial de la Peña</p>`}
                                </div>
                                <button class="btn btn-success w-100 mt-3 btn-reservar fw-bold" onclick="reservarPlazaViaje(${v.id})">
                                    <i class="fas fa-ticket-alt me-1"></i> Reservar Plaza
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });
        }

        contenedor.innerHTML = htmlSection;
    } catch (error) {
        console.error("Error crítico al renderizar viajes:", error);
        contenedor.innerHTML = `<div class="col-12 text-center text-danger py-4">⚠️ Error al cargar los datos de los viajes desde el servidor.</div>`;
    }
}

// Función para reservar una plaza en un viaje específico
async function reservarPlazaViaje(viajeId) {
    const usuarioId = parseInt(localStorage.getItem("usuario_id") || "2", 10);
    
    const payload = {
        usuario_id: usuarioId,
        viaje_id: viajeId,
        asientos_reservados: 1,
        tipo_reserva: "Viaje",
        motivo_evento: "Reserva de plaza en transporte",
        fecha_solicitada: new Date().toISOString().split('T')[0]
    };

    try {
        const response = await fetch("/reservas", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("¡Plaza reservada con éxito!");
            window.location.reload();
        } else {
            const errData = await response.json().catch(() => ({}));
            alert(`No se pudo reservar: ${errData.detail || "Error en el servidor"}`);
        }
    } catch (err) {
        console.error("Error al reservar plaza:", err);
        alert("Error de conexión al intentar reservar la plaza.");
    }
}

// Función para ordenar las solicitudes de viaje del socio según el criterio seleccionado
function ordenarSolicitudesSocio() {
    const selector = document.getElementById("filtro-orden");
    if (!selector || !Array.isArray(solicitudesGlobales)) return;
    
    const criterio = selector.value;
    
    solicitudesGlobales.sort((a, b) => {
        if (criterio === "fecha-asc") {
            return new Date(a.fecha_solicitada || '9999-12-31') - new Date(b.fecha_solicitada || '9999-12-31');
        } else if (criterio === "fecha-desc") {
            return new Date(b.fecha_solicitada || '0000-01-01') - new Date(a.fecha_solicitada || '0000-01-01');
        } else if (criterio === "estado") {
            return (a.estado_solicitud || "").localeCompare(b.estado_solicitud || "");
        } else if (criterio === "tipo") {
            return (a.tipo_reserva || "").localeCompare(b.tipo_reserva || "");
        }
        return 0;
    });

    if (typeof pintarTablaSolicitudesSocio === "function") {
        pintarTablaSolicitudesSocio(solicitudesGlobales);
    }
}