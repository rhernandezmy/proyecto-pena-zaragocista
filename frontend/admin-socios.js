const API_URL = "http://127.0.0.1:8000"; // Puerto de tu FastAPI

document.addEventListener("DOMContentLoaded", () => {
    const formSocio = document.getElementById("form-nuevo-socio");
    const btnExportar = document.getElementById("btn-exportar-csv");

    // 1. Cargar las tablas al iniciar la página
    cargarSociosBackend();
    cargarReservasAdmin(); // 👈 Carga las reservas del local

    // 2. Escuchar cuando el administrador crea un nuevo socio (POST)
    if (formSocio) {
        formSocio.addEventListener("submit", async (e) => {
            e.preventDefault();

            const nombre = document.getElementById("socio-nombre").value;
            const apellidos = document.getElementById("socio-apellidos").value;
            const email = document.getElementById("socio-email").value;

            const payload = {
                nombre: nombre,
                apellidos: apellidos,
                email: email
            };

            try {
                const response = await fetch(`${API_URL}/crear-socio`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.status === 201) {
                    alert("🚀 ¡Socio guardado correctamente en la Base de Datos!");
                    formSocio.reset();
                    cargarSociosBackend();
                } else {
                    alert(`⚠️ Error: ${data.detail}`);
                }
            } catch (error) {
                console.error("Error al conectar:", error);
                alert("Hubo un error de conexión con el servidor FastAPI.");
            }
        });
    }

    // 3. ENLACE EXPORTAR CSV
    if (btnExportar) {
        btnExportar.addEventListener("click", exportarSociosCSV);
    }
});

// =========================================================================
// 4. Cargar y pintar la tabla de socios (GET /socios)
// =========================================================================
async function cargarSociosBackend() {
    const tablaSocios = document.querySelector("#socios-pane tbody"); 
    if (!tablaSocios) return;

    try {
        const response = await fetch(`${API_URL}/socios`);
        if (!response.ok) throw new Error("Error al obtener socios");
        
        const socios = await response.json();
        tablaSocios.innerHTML = "";

        socios.forEach(socio => {
            const claseFila = socio.activo ? "" : "table-danger text-muted";
            const textoActivo = socio.activo ? "" : " (DE BAJA)";

            const fila = document.createElement("tr");
            if (!socio.activo) fila.className = claseFila;
            
            let badgeCuota = socio.estado_cuota === "Al día" 
                ? '<span class="badge bg-success">Al día</span>' 
                : '<span class="badge bg-warning text-dark">Pendiente</span>';

            fila.innerHTML = `
                <td>#${socio.id}</td>
                <td class="fw-bold" id="name-${socio.id}">${socio.nombre} ${socio.apellidos}${textoActivo}</td>
                <td>${socio.email}</td>
                <td>${socio.telefono}</td>
                <td>${badgeCuota}</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editarSocio(${socio.id}, '${socio.nombre}', '${socio.apellidos}', '${socio.email}')" title="Editar Socio" ${!socio.activo ? 'disabled' : ''}>
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="eliminarSocio(${socio.id})" title="Dar de Baja" ${!socio.activo ? 'disabled' : ''}>
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            `;
            tablaSocios.appendChild(fila);
        });

    } catch (error) {
        console.error("Error:", error);
        tablaSocios.innerHTML = `<tr><td colspan="6" class="text-center text-danger">No se pudo cargar el listado de socios.</td></tr>`;
    }
}

// =========================================================================
// 5. Cargar solicitudes del Local (GET /reservas)
// =========================================================================
async function cargarReservasAdmin() {
    // 🎯 Apuntamos directamente al ID de tu HTML: "tabla-reservas-admin"
    const tablaReservas = document.getElementById("tabla-reservas-admin"); 
    if (!tablaReservas) return;

    try {
        const response = await fetch(`${API_URL}/reservas`);
        if (!response.ok) throw new Error("Error al obtener reservas");

        const reservas = await response.json();
        const reservasLocal = reservas.filter(r => r.tipo_reserva === "Local");

        tablaReservas.innerHTML = "";

        if (reservasLocal.length === 0) {
            tablaReservas.innerHTML = `<tr><td colspan="5" class="text-center py-3">No hay solicitudes de reserva registradas.</td></tr>`;
            return;
        }

        reservasLocal.forEach(r => {
            const socio = r.socio_nombre || `Usuario #${r.usuario_id}`;
            const fecha = r.fecha_solicitada ? r.fecha_solicitada.split("T")[0] : "Sin fecha";
            const motivo = r.motivo_evento || "Uso de Sede";
            const estado = r.estado_solicitud || "Pendiente";

            let badgeClass = "bg-warning text-dark";
            if (estado === "Aprobada") badgeClass = "bg-success";
            if (estado === "Rechazada") badgeClass = "bg-danger";

            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td class="fw-bold">${socio}</td>
                <td>${fecha}</td>
                <td>${motivo}</td>
                <td><span class="badge ${badgeClass}">${estado}</span></td>
                <td class="text-center">
                    <button class="btn btn-sm btn-success me-1" onclick="resolverReserva(${r.id}, 'Aprobada')" title="Aprobar">
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="resolverReserva(${r.id}, 'Rechazada')" title="Rechazar">
                        <i class="fas fa-times"></i>
                    </button>
                </td>
            `;
            tablaReservas.appendChild(fila);
        });

    } catch (error) {
        console.error("Error al cargar reservas:", error);
        tablaReservas.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-3">Error al conectar con el servidor.</td></tr>`;
    }
}

// =========================================================================
// 6. Resolver Reserva del Local (PATCH /reservas/{id}/resolucion?estado=...)
// =========================================================================
async function resolverReserva(reservaId, nuevoEstado) {
    try {
        // 🔧 CORRECCIÓN: Se añade '/resolucion' a la URL para coincidir con FastAPI
        const response = await fetch(`${API_URL}/reservas/${reservaId}/resolucion?estado=${encodeURIComponent(nuevoEstado)}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" }
        });

        if (response.ok) {
            alert(`✅ Reserva marcada como: ${nuevoEstado}`);
            cargarReservasAdmin(); // Recargar la tabla tras actualizar
        } else {
            const data = await response.json();
            alert(`⚠️ Error al actualizar la reserva: ${data.detail || 'Operación no permitida.'}`);
        }
    } catch (error) {
        console.error("Error al resolver reserva:", error);
        alert("Error de conexión al intentar actualizar la reserva.");
    }
}

// =========================================================================
// 7. Modificar Socios (PUT /socios/{id})
// =========================================================================
async function editarSocio(id, nombreActual, apellidosActual, emailActual) {
    const nuevoNombre = prompt("Modificar Nombre:", nombreActual);
    if (nuevoNombre === null) return;
    
    const nuevosApellidos = prompt("Modificar Apellidos:", apellidosActual);
    if (nuevosApellidos === null) return;

    const nuevoEmail = prompt("Modificar Correo Electrónico:", emailActual);
    if (nuevoEmail === null) return;

    const payload = {
        nombre: nuevoNombre,
        apellidos: nuevosApellidos,
        email: nuevoEmail
    };

    try {
        const response = await fetch(`${API_URL}/socios/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            alert("✅ Socio modificado y guardado con éxito en la base de datos.");
            cargarSociosBackend();
        } else {
            alert(`⚠️ Error al actualizar: ${data.detail}`);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Fallo de red al intentar actualizar al socio.");
    }
}

// =========================================================================
// 8. Eliminar / Dar de Baja Socio (DELETE /socios/{id})
// =========================================================================
async function eliminarSocio(id) {
    if (!confirm("⚠️ ¿Estás completamente seguro de que deseas dar de baja y eliminar a este socio del sistema?")) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/socios/${id}`, {
            method: "DELETE"
        });

        const data = await response.json();

        if (response.ok) {
            alert("🗑️ El socio ha sido eliminado correctamente del registro.");
            cargarSociosBackend();
        } else {
            alert(`⚠️ No se pudo procesar la baja: ${data.detail}`);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Error de conexión al procesar la baja.");
    }
}

// =========================================================================
// 9. Exportar Socios a CSV
// =========================================================================
async function exportarSociosCSV() {
    try {
        const response = await fetch(`${API_URL}/socios`);
        if (!response.ok) throw new Error("No se pueden obtener datos para exportar");
        const socios = await response.json();

        let csvContent = "data:text/csv;charset=utf-8,ID,Nombre Completo,Email,Telefono,Estado Cuota\n";
        
        socios.forEach(s => {
            csvContent += `${s.id},"${s.nombre_completo}",${s.email},${s.telefono},${s.estado_cuota}\n`;
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "Listado_Socios_Peña.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        alert("Error al generar el documento CSV.");
    }
}