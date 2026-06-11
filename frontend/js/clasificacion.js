document.addEventListener("DOMContentLoaded", async () => {
    const tbody = document.getElementById("body-clasificacion");
    
    // Indicador visual de carga
    tbody.innerHTML = `
        <tr>
            <td colspan="4" class="text-center py-4">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2 text-muted">Consultando datos del Mundial...</p>
            </td>
        </tr>`;
    
    try {
        // Llamada a tu backend con el prefijo correcto definido en main.py
        const response = await fetch("http://127.0.0.1:8000/mundial/clasificacion-mundial");
        
        if (!response.ok) {
            throw new Error(`Error en el servidor: ${response.status}`);
        }
        
        const datos = await response.json();
        
        // Limpiamos el indicador de carga
        tbody.innerHTML = ""; 

        // Verificamos si hay datos
        if (!datos.clasificacion || datos.clasificacion.length === 0) {
            tbody.innerHTML = "<tr><td colspan='4' class='text-center'>No hay datos de clasificación disponibles actualmente.</td></tr>";
            return;
        }

        // Recorremos los grupos de la API
        datos.clasificacion.forEach(grupo => {
            const nombreGrupo = grupo.group ? grupo.group.replace('_', ' ') : "Fase de Grupos";
            
            // Fila de cabecera del grupo
            tbody.innerHTML += `
                <tr>
                    <td colspan="4" class="bg-light text-primary fw-bold text-center border-bottom-2">
                        ${nombreGrupo}
                    </td>
                </tr>`;
            
            // Recorremos los equipos dentro del grupo
            grupo.table.forEach(equipo => {
                tbody.innerHTML += `
                    <tr>
                        <td class="text-center">${equipo.position}</td>
                        <td>
                            <img src="${equipo.team.crest || ''}" width="25" class="me-2" onerror="this.style.display='none'"> 
                            ${equipo.team.name}
                        </td>
                        <td class="text-center">${equipo.playedGames}</td>
                        <td class="text-center fw-bold text-dark">${equipo.points}</td>
                    </tr>
                `;
            });
        });
        
    } catch (error) {
        console.error("Error al cargar la clasificación:", error);
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle"></i> No se pudieron cargar los datos. 
                    Verifica que el servidor esté encendido.
                </td>
            </tr>`;
    }
});