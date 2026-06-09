/**
 * APP.JS - Módulo de Administración Integral
 * Proyecto: Peña Zaragocista (2026)
 * Gestión dinámica del DOM sin destrucción de elementos estáticos.
 */

// --- CONFIGURACIÓN GLOBAL ---
const API_BASE_URL = "http://localhost:8000";

// --- FUNCIONES AUXILIARES DE CREACIÓN DE NODOS (EVITA INNERHTML DESTRUCTIVO) ---

/**
 * Crea una celda con un badge de estado estilizado según las clases de Bootstrap
 */
function crearCeldaBadge(texto, clasesBootstrap) {
    const td = document.createElement("td");
    const span = document.createElement("span");
    span.className = `badge ${clasesBootstrap}`;
    span.innerText = texto;
    td.appendChild(span);
    return td;
}

/**
 * Crea el contenedor de acciones (botones) para la gestión de filas
 */
function crearCeldaAcciones(idRegistro, esSocio = true) {
    const td = document.createElement("td");
    td.className = "text-center";

    if (esSocio) {
        // Botón Editar
        const btnEdit = document.createElement("button");
        btnEdit.className = "btn btn-sm btn-outline-secondary me-1";
        btnEdit.title = "Editar";
        btnEdit.innerHTML = '<i class="fas fa-edit"></i>';
        
        // Botón Dar de Baja
        const btnBaja = document.createElement("button");
        btnBaja.className = "btn btn-sm btn-outline-danger";
        btnBaja.title = "Dar de baja";
        btnBaja.innerHTML = '<i class="fas fa-user-slash"></i>';

        td.appendChild(btnEdit);
        td.appendChild(btnBaja);
    } else {
        // Botones específicos para la aprobación de Reservas del Local
        const btnAprobar = document.createElement("button");
        btnAprobar.className = "btn btn-sm btn-success text-white fw-bold me-1";
        btnAprobar.innerHTML = '<i class="fas fa-thumbs-up me-1"></i> Approbar';
        btnAprobar.onclick = () => procesarResolucionReserva(idRegistro, 'Aprobada');

        const btnRechazar = document.createElement("button");
        btnRechazar.className = "btn btn-sm btn-danger fw-bold";
        btnRechazar.innerHTML = '<i class="fas fa-thumbs-down me-1"></i> Rechazar';
        btnRechazar.onclick = () => procesarResolucionReserva(idRegistro, 'Rechazada');

        td.appendChild(btnAprobar);
        td.appendChild(btnRechazar);
    }

    return td;
}

// --- CORE: RENDERIZADO DINÁMICO ---

function renderizarSociosDinamicos(socios) {
    // Sincronización exacta con el ID del contenedor del DOM provisto en admin.html
    const contenedorPane = document.getElementById("socios-pane");
    if (!contenedorPane) {
        console.warn("⚠️ [DOM] No se encontró el contenedor #socios-pane. Saltando renderizado.");
        return;
    }

    const tbody = contenedorPane.querySelector("table tbody");
    if (!tbody) return;

    // Validación defensiva: Si no hay datos reales en la base de datos, respetamos las filas estáticas del HTML
    if (!socios || socios.length === 0) {
        console.log("ℹ️ [Socios] No se recibieron socios de la API. Se mantienen los datos de prueba.");
        return;
    }

    // Si hay datos, limpiamos de forma segura e inyectamos los nuevos nodos elementales
    tbody.innerHTML = ""; 

    socios.forEach(socio => {
        const tr = document.createElement("tr");

        const tdId = document.createElement("td");
        tdId.className = "fw-bold";
        tdId.innerText = `#${String(socio.id).padStart(3, '0')}`;

        const tdNombre = document.createElement("td");
        tdNombre.innerText = socio.nombre_completo || socio.nombre || "Sin nombre";

        const tdEmail = document.createElement("td");
        tdEmail.innerText = socio.email;

        const tdTelefono = document.createElement("td");
        tdTelefono.innerText = socio.telefono || "600 000 000";

        // Mapeo dinámico del estado de la cuota anual
        const esPagada = socio.estado_cuota === "Pagada" || socio.cuota_pagada === true;
        const celdaBadge = crearCeldaBadge(
            esPagada ? "✅ Pagada 2026" : "⚠️ Pendiente",
            esPagada ? "bg-success" : "bg-warning text-dark"
        );

        const celdaAcciones = crearCeldaAcciones(socio.id, true);

        // Ensamblado del árbol de nodos de la fila
        tr.appendChild(tdId);
        tr.appendChild(tdNombre);
        tr.appendChild(tdEmail);
        tr.appendChild(tdTelefono);
        tr.appendChild(celdaBadge);
        tr.appendChild(celdaAcciones);

        tbody.appendChild(tr);
    });
    console.log(`✅ [Socios] ${socios.length} socios renderizados correctamente en el DOM.`);
}

function renderizarReservasLocalDinamicas(reservas) {
    const contenedorPane = document.getElementById("local-pane");
    if (!contenedorPane) {
        console.warn("⚠️ [DOM] No se encontró el contenedor #local-pane. Saltando renderizado.");
        return;
    }

    const tbody = contenedorPane.querySelector("table tbody");
    if (!tbody) return;

    if (!reservas || reservas.length === 0) {
        console.log("ℹ️ [Reservas] No hay solicitudes en la API. Se mantienen los datos de prueba.");
        return;
    }

    tbody.innerHTML = "";

    reservas.forEach(reserva => {
        const tr = document.createElement("tr");

        const tdSocio = document.createElement("td");
        tdSocio.className = "fw-bold";
        tdSocio.innerText = `Socio #${reserva.usuario_id}`;

        const tdFecha = document.createElement("td");
        tdFecha.innerText = reserva.fecha_solicitada || "Pendiente";

        const tdMotivo = document.createElement("td");
        tdMotivo.innerText = reserva.motivo_evento || "Uso General Sede";

        // Determinar estilo del badge según el estado de la solicitud
        let claseBadge = "bg-warning text-dark";
        if (reserva.estado_solicitud === "Aprobada") claseBadge = "bg-success";
        if (reserva.estado_solicitud === "Rechazada") claseBadge = "bg-danger";

        const celdaBadge = crearCeldaBadge(reserva.estado_solicitud || "⏳ Pendiente", claseBadge);
        const celdaAcciones = crearCeldaAcciones(reserva.id, false);

        tr.appendChild(tdSocio);
        tr.appendChild(tdFecha);
        tr.appendChild(tdMotivo);
        tr.appendChild(celdaBadge);
        tr.appendChild(celdaAcciones);

        tbody.appendChild(tr);
    });
    console.log(`✅ [Reservas] ${reservas.length} solicitudes mapeadas en el panel.`);
}

// --- GESTIÓN DE ESTADOS: ACCIONES FETCH (PATCH/POST) ---

async function procesarResolucionReserva(idReserva, nuevoEstado) {
    try {
        console.log(`📡 [API] Enviando resolución para reserva #${idReserva} -> Estado: ${nuevoEstado}`);
        
        const response = await fetch(`${API_BASE_URL}/reservas/${idReserva}/estado`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ estado: nuevoEstado })
        });

        if (response.ok) {
            console.log(`🔄 [API] Estado actualizado con éxito en servidor. Recargando datos globales.`);
            await cargarDatosGlobalesDashboard(); 
        } else {
            console.error(`❌ [API] Error al actualizar estado de reserva. Código: ${response.status}`);
        }
    } catch (error) {
        console.error("❌ [Fatal] Error de red al procesar resolución de reserva:", error);
    }
}

// --- CONTROLADOR DE INICIALIZACIÓN ORQUESTADA ---

async function cargarDatosGlobalesDashboard() {
    try {
        console.log("📡 [API] Solicitando datos globales al servidor...");
        const response = await fetch(`${API_BASE_URL}/panel/admin/global-data`);
        
        if (!response.ok) {
            throw new Error(`Error de servidor (HTTP ${response.status})`);
        }

        const data = await response.json();
        console.log("📦 [API] Datos decodificados recibidos para renderizar:", data);

        renderizarSociosDinamicos(data.socios);
        renderizarReservasLocalDinamicas(data.reservas_local);

    } catch (error) {
        console.error("❌ [Fatal] Error en la carga asíncrona del Dashboard. Manteniendo vista estática de seguridad:", error);
    }
}

// --- DISPARADOR DOM ---
document.addEventListener("DOMContentLoaded", () => {
    if (window.location.pathname.includes("admin.html")) {
        console.log("🛠️ [Admin] Inicializando Panel de Control de la Peña...");
        cargarDatosGlobalesDashboard();
    }
});

// --- ACCIÓN: CREAR NUEVO SOCIO DESDE EL PANEL ---

document.addEventListener("submit", async (e) => {
    if (e.target && e.target.id === "form-alta-socio") {
        e.preventDefault(); 

        // Capturamos los valores directamente de los dos nuevos campos de Bootstrap
        const nombre = document.getElementById("admin-nuevo-nombre").value.trim();
        const apellidos = document.getElementById("admin-nuevo-apellidos").value.trim();
        const email = document.getElementById("admin-nuevo-email").value.trim();

        // Construimos el envío con las claves exactas que tu PostgreSQL exige
        const nuevoSocioPayload = {
            nombre: nombre,
            apellidos: apellidos,
            email: email
        };

        try {
            console.log("📡 [API] Enviando nuevo socio al backend...", nuevoSocioPayload);
            
            const response = await fetch(`${API_BASE_URL}/usuarios/crear-socio`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(nuevoSocioPayload)
            });

            if (response.ok) {
                console.log("✅ [API] Socio creado con éxito. Actualizando tabla...");
                
                // Cerrar el modal de Bootstrap de forma limpia
                const modalElement = document.getElementById('modalNuevoSocio');
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) modal.hide();

                // Resetear el formulario de la pantalla
                e.target.reset();

                // Recargar la tabla llamando a tus datos globales de la peña
                await cargarDatosGlobalesDashboard();
            } else {
                const errorTexto = await response.text();
                console.error(`❌ [API] Error al crear socio. Estado HTTP: ${response.status}`, errorTexto);
                alert(`Error: El servidor rechazó los datos. Comprueba que el email no esté repetido.`);
            }
        } catch (error) {
            console.error("❌ [Fatal] Error de red al intentar crear el socio:", error);
            alert("Error de red: No se pudo conectar con el servidor de FastAPI.");
        }
    }
});