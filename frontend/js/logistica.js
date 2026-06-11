// URL base de tu servidor backend de FastAPI
const API_URL = "http://localhost:8000"; 

// Ejecutar automáticamente al cargar la página para dar vida a los formularios y tablas
document.addEventListener("DOMContentLoaded", () => {
    // Verificamos si estamos en la interfaz que contiene los elementos de logística
    if (document.getElementById("tabla-viajes-admin") || document.getElementById("viaje-partido-select")) {
        cargarViajesAdmin();
        cargarPartidosEnDesplegable();
        configurarFormularioViajeAdmin();
    }
});

// =========================================================================
// 1. CARGAR PARTIDOS EN EL SELECT DESPLEGABLE
// =========================================================================
async function cargarPartidosEnDesplegable() {
    const selectPartido = document.getElementById("viaje-partido-select");
    if (!selectPartido) return;

    try {
        // Petición al GET /partidos de tu FastAPI para listar los encuentros disponibles
        const response = await fetch(`${API_URL}/partidos`);
        if (!response.ok) throw new Error("No se pudieron cargar los partidos");

        const partidos = await response.json();
        
        // Limpiamos el indicador de carga inicial
        selectPartido.innerHTML = '<option value="">-- Selecciona un Partido / Destino --</option>';

        if (partidos.length === 0) {
            selectPartido.innerHTML = '<option value="">⚠️ Crea primero un partido en la sección de Partidos</option>';
            return;
        }

        // Rellenamos el select. El "value" es el ID numérico que exige viajes.py
        partidos.forEach(p => {
            // Se evalúa p.rival o p.lugar según tus nombres de columnas en la tabla Partido
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
        // Llamada al GET /viajes de tu FastAPI
        const response = await fetch(`${API_URL}/viajes`);
        if (!response.ok) throw new Error("Error al obtener los viajes");
        
        const viajes = await response.json();
        tablaViajes.innerHTML = "";

        if (viajes.length === 0) {
            tablaViajes.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-3">No hay viajes reales en la base de datos. ¡Crea el primero!</td></tr>`;
            return;
        }

        // Pintamos cada viaje de la base de datos en la tabla
        viajes.forEach(v => {
            const fila = document.createElement("tr");
            
            // Renderizado estético del tipo de transporte
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
// 3. CONFIGURAR EL FORMULARIO DE CREACIÓN (POST /viajes)
// =========================================================================
function configurarFormularioViajeAdmin() {
    const formViaje = document.getElementById("form-nuevo-viaje");
    if (!formViaje) return;

    // Removemos eventos duplicados clonando el nodo para mayor seguridad de ejecución
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

        // Obtenemos el texto limpio del partido para rellenar el campo 'destino' en la base de datos
        const textoCompletoPartido = selectPartido.options[selectPartido.selectedIndex].text;
        const destinoTextoLimpio = textoCompletoPartido.split("-")[0].trim();

        // Construimos el objeto JSON exacto que tu schemas.ViajeCrear y viajes.py necesitan
        const payload = {
            partido_id: parseInt(selectPartido.value), // ID numérico que requiere la verificación de FastAPI
            destino: destinoTextoLimpio,
            fecha: fechaInput.value,
            tipo_transporte: transporteSelect.value,
            plazas_totales: parseInt(plazasInput.value) || 0
        };

        try {
            const response = await fetch(`${API_URL}/viajes`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert("🚀 ¡Viaje publicado On Tour con éxito en la base de datos!");
                nuevoForm.reset();
                cargarViajesAdmin(); // Recarga la tabla de viajes automáticamente
            } else if (response.status === 422) {
                const errData = await response.json();
                const mensajes = errData.detail.map(err => `• Campo [${err.loc[1] || err.loc[0]}]: ${err.msg}`).join("\n");
                alert(`⚠️ Error de validación en los esquemas (422):\n\n${mensajes}`);
            } else {
                const errData = await response.json();
                alert(`⚠️ Error del servidor (${response.status}): ${errData.detail || "No se pudo guardar."}`);
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