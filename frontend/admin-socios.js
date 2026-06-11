const API_URL = "http://127.0.0.1:8000"; // Puerto de tu FastAPI

document.addEventListener("DOMContentLoaded", () => {
    const formSocio = document.getElementById("form-nuevo-socio"); // Formulario en admin.html
    const btnExportar = document.getElementById("btn-exportar-csv"); // Busca si tienes este ID para el CSV

    // 1. Cargar la lista de socios en la tabla nada más entrar
    cargarSociosBackend();

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
                    cargarSociosBackend(); // Recargamos la tabla
                } else {
                    alert(`⚠️ Error: ${data.detail}`);
                }
            } catch (error) {
                console.error("Error al conectar:", error);
                alert("Hubo un error de conexión con el servidor FastAPI.");
            }
        });
    }

    // 3. ENLACE EXPORTAR CSV (Arreglado)
    if (btnExportar) {
        btnExportar.addEventListener("click", exportarSociosCSV);
    }
});

// 4. Función para pintar la tabla llamando a tu GET /socios
async function cargarSociosBackend() {
    const tablaSocios = document.querySelector("#socios-pane tbody"); 
    if (!tablaSocios) return;

    try {
        const response = await fetch(`${API_URL}/socios`);
        if (!response.ok) throw new Error("Error al obtener socios");
        
        const socios = await response.json();
        tablaSocios.innerHTML = ""; // Limpiamos filas antiguas

        socios.forEach(socio => {
            // Si el socio está inactivo, le ponemos un estilo visual de "archivado"
            const claseFila = socio.activo ? "" : "table-danger text-muted";
            const textoActivo = socio.activo ? "" : " (DE BAJA)";

            const fila = document.createElement("tr");
            if (!socio.activo) fila.className = claseFila; // Aplica el fondo rojo claro si está de baja
            
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

// 5. NUEVA FUNCIÓN PARA MODIFICAR SOCIOS (PUT)
async function editarSocio(id, nombreActual, apellidosActual, emailActual) {
    const nuevoNombre = prompt("Modificar Nombre:", nombreActual);
    if (nuevoNombre === null) return; // Si cancela, salimos
    
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
            cargarSociosBackend(); // Refrescar vista
        } else {
            alert(`⚠️ Error al actualizar: ${data.detail}`);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Fallo de red al intentar actualizar al socio.");
    }
}

// 6. NUEVA FUNCIÓN PARA ELIMINAR / DAR DE BAJA (DELETE)
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
            cargarSociosBackend(); // Refrescar la tabla
        } else {
            alert(`⚠️ No se pudo procesar la baja: ${data.detail}`);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Error de conexión al procesar la baja.");
    }
}

// 7. NUEVA FUNCIÓN PARA EXPORTAR A CSV CLIENT-SIDE
async function exportarSociosCSV() {
    try {
        const response = await fetch(`${API_URL}/socios`);
        if (!response.ok) throw new Error("No se pueden obtener datos para exportar");
        const socios = await response.json();

        // Construimos las líneas del archivo CSV
        let csvContent = "data:text/csv;charset=utf-8,ID,Nombre Completo,Email,Telefono,Estado Cuota\n";
        
        socios.forEach(s => {
            csvContent += `${s.id},"${s.nombre_completo}",${s.email},${s.telefono},${s.estado_cuota}\n`;
        });

        // Truco del navegador para forzar la descarga del archivo listo
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