const API_URL = "http://127.0.0.1:8000"; // Asegúrate de que este es el puerto de tu FastAPI

document.addEventListener("DOMContentLoaded", () => {
    const formSocio = document.getElementById("form-nuevo-socio"); // Tu formulario en admin.html
    
    // 1. Cargar la lista de socios en la tabla nada más entrar
    cargarSociosBackend();

    // 2. Escuchar cuando el administrador crea un nuevo socio
    if (formSocio) {
        formSocio.addEventListener("submit", async (e) => {
            e.preventDefault();

            // Capturamos los datos de los inputs del formulario
            const nombre = document.getElementById("socio-nombre").value;
            const apellidos = document.getElementById("socio-apellidos").value;
            const email = document.getElementById("socio-email").value;

            // Construimos el JSON exactamente como lo espera tu Python payload.get()
            const payload = {
                nombre: nombre,
                apellidos: apellidos,
                email: email
            };

            try {
                const response = await fetch(`${API_URL}/crear-socio`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.status === 201) {
                    alert("🚀 ¡Socio guardado correctamente en PostgreSQL!");
                    formSocio.reset();
                    cargarSociosBackend(); // Recargamos la tabla para ver al nuevo socio
                } else {
                    // Si el email está duplicado o la BD falla, capturamos el HTTPException de tu Python
                    alert(`⚠️ Error: ${data.detail}`);
                }

            } catch (error) {
                console.error("Error al conectar:", error);
                alert("Hubo un error de conexión con el servidor FastAPI.");
            }
        });
    }
});

// 3. Función para pintar la tabla llamando a tu GET /socios
async function cargarSociosBackend() {
    const tablaSocios = document.querySelector("#socios-pane tbody"); // El contenedor de la pestaña de socios
    if (!tablaSocios) return;

    try {
        const response = await fetch(`${API_URL}/socios`);
        if (!response.ok) throw new Error("Error al obtener socios");
        
        const socios = await response.json();
        tablaSocios.innerHTML = ""; // Limpiamos filas estáticas del HTML

        socios.forEach(socio => {
            const fila = document.createElement("tr");
            
            // Estilo para el estado de la cuota
            let badgeCuota = socio.estado_cuota === "Al día" 
                ? '<span class="badge bg-success">Al día</span>' 
                : '<span class="badge bg-warning text-dark">Pendiente</span>';

            fila.innerHTML = `
                <td>#${socio.id}</td>
                <td class="fw-bold">${socio.nombre_completo}</td>
                <td>${socio.email}</td>
                <td>${socio.telefono}</td>
                <td>${badgeCuota}</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></button>
                </td>
            `;
            tablaSocios.appendChild(fila);
        });

    } catch (error) {
        console.error("Error:", error);
        tablaSocios.innerHTML = `<tr><td colspan="6" class="text-center text-danger">No se pudo cargar el listado de socios.</td></tr>`;
    }
}