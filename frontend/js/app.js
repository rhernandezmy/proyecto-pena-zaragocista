// --- FUNCIONES DE RENDERIZADO (ADMIN) ---

function renderizarSocios(socios) {
    const tbody = document.querySelector("#socios-pane tbody");
    if (!tbody) return;
    
    // Si llegan socios del servidor, inyectamos los reales. 
    // Si no, dejamos los de ejemplo del HTML.
    if (socios && socios.length > 0) {
        tbody.innerHTML = socios.map(s => `
            <tr>
                <td class="fw-bold">#${s.id}</td>
                <td>${s.nombre_completo}</td>
                <td>${s.email}</td>
                <td>${s.telefono || 'N/A'}</td>
                <td><span class="badge ${s.estado_cuota === 'Pagada' ? 'bg-success' : 'bg-warning'}">${s.estado_cuota}</span></td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-secondary me-1"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-outline-danger"><i class="fas fa-user-slash"></i></button>
                </td>
            </tr>
        `).join('');
    }
}

function renderizarReservasLocal(reservas) {
    const tbody = document.querySelector("#local-pane tbody");
    if (!tbody) return;

    if (reservas && reservas.length > 0) {
        tbody.innerHTML = reservas.map(r => `
            <tr>
                <td class="fw-bold">Socio #${r.usuario_id}</td>
                <td>${r.fecha_solicitada || 'N/A'}</td>
                <td>${r.motivo_evento}</td>
                <td><span class="badge bg-warning">${r.estado_solicitud}</span></td>
                <td class="text-center">
                    <button class="btn btn-sm btn-success text-white fw-bold me-1"><i class="fas fa-thumbs-up me-1"></i></button>
                    <button class="btn btn-sm btn-danger fw-bold"><i class="fas fa-thumbs-down me-1"></i></button>
                </td>
            </tr>
        `).join('');
    }
}

// --- LÓGICA DE CARGA ---

async function inicializarAdmin() {
    try {
        const response = await fetch("http://localhost:8000/panel/admin/global-data");
        if (!response.ok) return; // Si falla, dejamos el HTML intacto
        
        const data = await response.json();
        console.log("Datos recibidos:", data);

        // Renderizamos solo si hay datos reales
        renderizarSocios(data.socios);
        renderizarReservasLocal(data.reservas_local);

    } catch (error) {
        console.error("Error en carga dinámica:", error);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    if (window.location.pathname.includes("admin.html")) {
        inicializarAdmin();
    }
});