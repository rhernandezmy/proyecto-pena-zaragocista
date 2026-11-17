// =========================================================================
// 🤝 CARGAR PARTNERS EN EL INDEX
// =========================================================================
document.addEventListener("DOMContentLoaded", () => {
    cargarPartner();
});

async function cargarPartner() {
    const contenedor = document.getElementById("contenedor-partners-index");
    if (!contenedor) return;

    try {
        const response = await fetch("/patrocinadores");
        
        if (!response.ok) {
            throw new Error(`Error en el servidor: ${response.status}`);
        }

        const partners = await response.json();

        // Si no hay patrocinadores registrados en la BD
        if (!Array.isArray(partners) || partners.length === 0) {
            contenedor.innerHTML = `<span class="text-muted small py-1" style="font-size: 0.75rem;">No hay partners disponibles.</span>`;
            return;
        }

        // Limpiamos el texto de "Cargando..."
        contenedor.innerHTML = "";

        // Pintamos los primeros 3 o 4 patrocinadores de forma compacta para la barra lateral
        partners.slice(0, 4).forEach(p => {
            const logo = p.logo_url || 'https://via.placeholder.com/80x40?text=Partner';
            const enlace = p.enlace_web || '#';
            
            contenedor.innerHTML += `
                <a href="${enlace}" target="_blank" rel="noopener noreferrer" class="d-block text-decoration-none w-100 hover-shadow transition-all">
                    <div class="p-1 border rounded bg-light d-flex align-items-center justify-content-center" style="min-height: 45px;">
                        <img src="${logo}" alt="${p.nombre}" class="img-fluid" style="max-height: 35px; object-fit: contain;">
                    </div>
                </a>
            `;
        });

    } catch (error) {
        console.error("Error al cargar partners en el index:", error);
        contenedor.innerHTML = `<span class="text-muted small py-1" style="font-size: 0.75rem;">Sin conexión con partners</span>`;
    }
}