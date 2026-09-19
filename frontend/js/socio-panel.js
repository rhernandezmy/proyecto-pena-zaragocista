// URL base unificada para conectar con tu servidor de FastAPI
const API_URL = "http://localhost:8000"; 

// =========================================================================
// 1. CARGAR LAS RESERVAS DEL SOCIO DESDE EL BACKEND
// =========================================================================
async function cargarSolicitudesDesdeBackend(socio) {
    const contenedorTabla = document.getElementById("tabla-mis-solicitudes");
    if (!contenedorTabla) return;

    try {
        const response = await fetch(`${API_URL}/reservas`);
        if (!response.ok) throw new Error("Error en la respuesta del servidor");
        
        const reservas = await response.json();
        contenedorTabla.innerHTML = "";
        
        // Filtramos para mostrar únicamente las reservas del socio logueado
        const misReservas = reservas.filter(r => r.usuario_id === socio.id);

        if (misReservas.length === 0) {
            contenedorTabla.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-3">No tienes solicitudes ni viajes activos actualmente.</td></tr>`;
            return;
        }

        misReservas.forEach(res => {
            const fila = document.createElement("tr");
            let badgeTipo = "";
            let detalle = "";
            let badgeEstado = "";

            if (res.tipo_reserva === "Viaje") {
                badgeTipo = '<span class="badge bg-info text-dark">🔹 Logística</span>';
                
                if (res.motivo_evento && res.motivo_evento.includes("vehículo")) {
                    detalle = `🚗 Coche Compartido: ${res.motivo_evento}`;
                } else {
                    detalle = `🚌 Autobús (Asientos reservados: ${res.asientos_reservados || 1})`;
                }
                
                const estadoTexto = res.estado_solicitud || res.estado || 'Aprobada';
                badgeEstado = `<span class="badge bg-success">✓ ${estadoTexto}</span>`;
            } else {
                badgeTipo = '<span class="badge bg-warning text-dark">🏠 Sede Social</span>';
                detalle = `Reserva de Local: ${res.motivo_evento || 'Evento común'}`;
                
                // Mapeo seguro de estados
                const estadoLocal = res.estado_solicitud || res.estado || "Pendiente";

                if (estadoLocal === "Pendiente") {
                    badgeEstado = '<span class="badge bg-warning text-dark">⏳ Pendiente</span>';
                } else if (estadoLocal === "Aprobada" || estadoLocal === "Aceptada") {
                    badgeEstado = '<span class="badge bg-success">✓ Aprobada</span>';
                } else {
                    badgeEstado = '<span class="badge bg-danger">✕ Rechazada</span>';
                }
            }

            // ⚠️ CORRECCIÓN CLAVE DE FECHA: Priorizamos la fecha SOLICITADA/ELEGIDA por el socio (día 20)
            let fechaRaw = res.fecha_solicitada || res.fecha_evento || res.fecha_reserva;
            let fechaFormateada = "Programada";

            if (fechaRaw) {
                fechaFormateada = fechaRaw.split("T")[0]; 
            }

            fila.innerHTML = `
                <td>${badgeTipo}</td>
                <td class="fw-bold">${detalle}</td>
                <td>${fechaFormateada}</td>
                <td>${badgeEstado}</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-danger" onclick="eliminarReservaBackend(${res.id})">
                        <i class="fas fa-trash-alt me-1"></i> Cancelar
                    </button>
                </td>
            `;
            contenedorTabla.appendChild(fila);
        });

    } catch (error) {
        console.error("Error al cargar la tabla:", error);
        contenedorTabla.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-3">⚠️ Error de comunicación con el servidor FastAPI.</td></tr>`;
    }
}

// =========================================================================
// 2. ENVIAR AL BACKEND EL COCHE COMPARTIDO
// =========================================================================
async function ofrecerCocheSocio(viajeId, plazasCoche) {
    // Obtenemos el ID del socio dinámicamente del almacenamiento del Login
    const socioId = parseInt(localStorage.getItem("usuario_id")) || parseInt(localStorage.getItem("socio_id")) || 2;

    const payload = {
        usuario_id: socioId,
        tipo_reserva: "Viaje",
        viaje_id: parseInt(viajeId),
        asientos_reservados: 1, // El conductor ocupa su asiento
        motivo_evento: `Ofrece vehículo con ${plazasCoche} plazas.`
    };

    try {
        const response = await fetch(`${API_URL}/reservas`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (response.status === 404) {
            alert("⚠️ Error 404: El ID del viaje proporcionado no existe en la base de datos.");
            return;
        }

        const data = await response.json();

        if (response.ok) {
            alert("🚗 ¡Vehículo registrado con éxito en el viaje!");
            window.location.reload(); 
        } else {
            alert(`⚠️ Error del servidor: ${data.detail || "Verifica las restricciones de plazas."}`);
        }
    } catch (error) {
        console.error("Error en la conexión POST:", error);
        alert("Error de red: No se pudo contactar con el backend.");
    }
}

// =========================================================================
// 3. ENVIAR SOLICITUD DE RESERVA DE LOCAL AL BACKEND
// =========================================================================
async function solicitarReservaLocal(fechaSeleccionada, motivoTexto) {
    const socioId = parseInt(localStorage.getItem("usuario_id")) || parseInt(localStorage.getItem("socio_id")) || 2;

    if (!fechaSeleccionada) {
        alert("⚠️ Por favor, selecciona una fecha para la reserva del local.");
        return;
    }

    const payload = {
        usuario_id: socioId,
        tipo_reserva: "Local",               // 👈 AQUÍ YA QUEDA CONFIGURADO COMO LOCAL
        fecha_solicitada: fechaSeleccionada, // 👈 ENVÍA LA FECHA ELEGIDA (Ej: "2026-09-27")
        motivo_evento: motivoTexto || "Uso de Sede Social",
        estado_solicitud: "Pendiente"
    };

    try {
        const response = await fetch(`${API_URL}/reservas`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("🏠 ¡Solicitud de reserva de local enviada con éxito!");
            window.location.reload();
        } else {
            const err = await response.json();
            alert(`⚠️ Error al enviar reserva: ${err.detail || "No se pudo completar."}`);
        }
    } catch (error) {
        console.error("Error al solicitar el local:", error);
        alert("Error de red: No se pudo contactar con el backend.");
    }
}

// =========================================================================
// 4. CANCELAR / ELIMINAR RESERVA (Conectado a tu @router.delete)
// =========================================================================
async function eliminarReservaBackend(reservaId) {
    if (!confirm("¿Seguro que deseas cancelar esta solicitud o retirar tu vehículo?")) return;

    try {
        const response = await fetch(`${API_URL}/reservas/${reservaId}`, {
            method: "DELETE"
        });

        if (response.ok) {
            alert("Solicitud cancelada y eliminada de PostgreSQL.");
            window.location.reload();
        } else {
            alert("No se pudo procesar la eliminación en el servidor.");
        }
    } catch (error) {
        console.error("Error al eliminar:", error);
        alert("Error de conexión al intentar borrar.");
    }
}

// =========================================================================
// 5. ACTUALIZAR LOS DATOS DEL SOCIO Y CARGARLOS AL INICIAR
// =========================================================================
document.addEventListener("DOMContentLoaded", async () => {
    // Obtenemos el ID del socio de forma consistente priorizando usuario_id (Admin es 2)
    const socioId = parseInt(localStorage.getItem("usuario_id")) || parseInt(localStorage.getItem("socio_id")) || 2;
    console.log("ID del socio detectado en LocalStorage:", socioId);

    // Mapeo directo y seguro mediante selectores por atributo 'placeholder' o tipo para evitar cruces
    let inputNombre = document.querySelector('input[placeholder*="Nombre"], #inputNombre');
    let inputEmail = document.querySelector('input[placeholder*="@"], input[type="email"], #inputEmail');
    let inputTelefono = document.querySelector('input[placeholder*="Teléfono"], input[placeholder*="600"], #inputTelefono');
    let inputDireccion = document.querySelector('input[placeholder*="Dirección"], input[placeholder*="Localidad"], #inputDireccion');

    // Fallback defensivo si los IDs explícitos no están presentes en el HTML
    if (!inputNombre || !inputTelefono) {
        const inputs = document.querySelectorAll(".form-control");
        if (inputs.length >= 4) {
            inputNombre = inputs[0];
            inputEmail = inputs[1];
            inputTelefono = inputs[2];
            inputDireccion = inputs[3];
        }
    }

    // =========================================================================
    // 🔄 PARTE A: LEER LOS DATOS REALES DE POSTGRESQL AL ENTRAR A LA WEB
    // =========================================================================
    try {
        const responseGet = await fetch(`${API_URL}/socios`);
        if (responseGet.ok) {
            const socios = await responseGet.json();
            console.log("Lista de socios recuperada del backend:", socios);
            
            // Búsqueda para localizar al usuario conectado
            const miFicha = socios.find(s => 
                Number(s.id) === socioId || 
                Number(s.usuario_id) === socioId || 
                Number(s.numero_socio) === socioId
            );
            
            if (miFicha) {
                console.log("¡Ficha de socio encontrada con éxito! Datos:", miFicha);
                
                // Rellenamos el campo de Nombre Completo
                if (inputNombre) {
                    const nombreFicha = miFicha.nombre || "";
                    const apellidosFicha = miFicha.apellidos || "";
                    
                    if (apellidosFicha && nombreFicha.includes(apellidosFicha)) {
                        inputNombre.value = nombreFicha.trim();
                    } else {
                        inputNombre.value = miFicha.nombre_completo || `${nombreFicha} ${apellidosFicha}`.trim();
                    }
                }
                
                // CORRECCIÓN CRÍTICA: Inyectamos el email real y prevenimos que se pinte el teléfono aquí
                if (inputEmail) {
                    inputEmail.value = miFicha.email || "presentexelescudo@gmail.com";
                }
                
                // Asignamos el teléfono de contacto de forma limpia
                if (inputTelefono) {
                    inputTelefono.value = (miFicha.telefono && miFicha.telefono !== "Sin Teléfono" && miFicha.telefono !== "no tiene") ? miFicha.telefono : "";
                }
                
                // Asignamos la dirección de residencia
                if (inputDireccion) {
                    inputDireccion.value = (miFicha.direccion && miFicha.direccion !== "Sin Dirección") ? miFicha.direccion : "";
                }

                // Cargamos las solicitudes del panel de reservas del socio
                if (typeof cargarSolicitudesDesdeBackend === "function") {
                    cargarSolicitudesDesdeBackend(miFicha);
                }
            } else {
                console.warn(`No se encontró ningún socio en el backend que coincida con el ID: ${socioId}`);
                if (inputNombre && localStorage.getItem("socio_nombre")) {
                    inputNombre.value = localStorage.getItem("socio_nombre");
                }
            }
        }
    } catch (error) {
        console.error("Error al pintar los datos guardados en el inicio:", error);
    }

    // =========================================================================
    // 💾 PARTE B: GUARDAR LOS DATOS CUANDO EL SOCIO MODIFICA ALGO
    // =========================================================================
    const botones = document.querySelectorAll("button");
    let botonGuardarReal = null;
    
    botones.forEach(btn => {
        if (btn.textContent.trim().includes("Guardar Cambios")) {
            botonGuardarReal = btn;
        }
    });

    if (botonGuardarReal) {
        botonGuardarReal.addEventListener("click", async (e) => {
            e.preventDefault();

            const nombreValor = inputNombre ? inputNombre.value.trim() : "";
            const telefonoValor = inputTelefono ? inputTelefono.value.trim() : "";
            const direccionValor = inputDireccion ? inputDireccion.value.trim() : "";

            if (!nombreValor) {
                alert("⚠️ El nombre completo no puede estar vacío.");
                return;
            }

            const payloadActualizar = {
                nombre: nombreValor,
                telefono: telefonoValor,
                direccion: direccionValor
            };

            try {
                const response = await fetch(`${API_URL}/usuarios/${socioId}`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payloadActualizar)
                });

                if (response.ok) {
                    localStorage.setItem("socio_nombre", nombreValor);
                    alert("✅ ¡Tus datos se han guardado correctamente en PostgreSQL!");
                    window.location.reload(); 
                } else {
                    const errorData = await response.json();
                    alert(`⚠️ Error del servidor (${response.status}): ${errorData.detail || "No se pudieron guardar los datos."}`);
                }
            } catch (error) {
                console.error("Error en la conexión PUT de usuario:", error);
                alert("⚠️ Error de red: No se pudo conectar con el servidor de FastAPI.");
            }
        });
    }
});