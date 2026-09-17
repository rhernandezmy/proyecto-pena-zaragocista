const socioLogado = localStorage.getItem("socio_nombre");

// Configuración de los elementos del menú
let menuViajesHTML = "";
let botonAuthHTML = `<a class="btn btn-outline-primary btn-sm fw-bold" href="registro.html">📝 Registrarse</a>`;

// Si el usuario está logado, activamos el menú privado
if (socioLogado) {
    menuViajesHTML = `<a class="nav-link fw-bold px-2" href="viajes.html" style="color: #198754;">🚗 Viajes</a>`;

    botonAuthHTML = `
        <div class="d-flex align-items-center gap-2">
            <!-- Nombre que actúa directamente como botón hacia Mi Perfil -->
            <a href="socio.html" class="btn btn-sm btn-outline-primary fw-bold text-truncate" style="max-width: 170px;" title="Ir a Mi Perfil">
                👤 ${socioLogado}
            </a>

            <!-- Botón Salir compacto -->
            <button class="btn btn-sm btn-outline-danger" id="btn-logout" title="Cerrar sesión">Salir</button>
        </div>
    `;
}

const headerHTML = `
    <nav class="navbar navbar-expand-lg bg-white shadow-sm py-1">
        <div class="container-fluid px-lg-4">
            <!-- 1. BLOQUE IZQUIERDA: LOGO / INICIO -->
            <a class="navbar-brand d-flex flex-column align-items-center me-0" href="index.html" title="Volver al Inicio" style="text-decoration: none;">
                <img src="assets/logo.png" alt="Logo Peña Zaragocista" style="height: 48px;">
                <span style="font-size: 10px; color: #0033A0; font-weight: bold; text-transform: uppercase; margin-top: 1px; letter-spacing: 1px;">Inicio</span>
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <!-- 2. BLOQUE CENTRO: MENÚ DE NAVEGACIÓN PRINCIPAL -->
                <div class="navbar-nav mx-auto align-items-center gap-1 small">
                    <a class="nav-link fw-bold px-2" href="noticias.html" style="color: #0033A0;">📰 Noticias</a>
                    <a class="nav-link fw-bold px-2" href="partidos.html" style="color: #0033A0;">⚽ Partidos</a>
                    <a class="nav-link fw-bold px-2" href="clasificacion.html" style="color: #0033A0;">📊 Clasificación</a>
                    <a class="nav-link fw-bold px-2" href="reservas.html" style="color: #0033A0;">🏠 Local</a>
                    <a class="nav-link fw-bold px-2" href="pena.html" style="color: #0033A0;">🦁 La Peña</a>
                    <a class="nav-link fw-bold px-2" href="partners.html" style="color: #0033A0;">🤝 Partners</a>
                    ${menuViajesHTML}
                </div>

                <!-- 3. BLOQUE DERECHA: BOTONES DE USUARIO Y SESIÓN -->
                <div class="d-flex align-items-center ms-auto">
                    ${botonAuthHTML}
                </div>
            </div>
        </div>
    </nav>
`;

document.getElementById('header-placeholder').innerHTML = headerHTML;

// Lógica para cerrar sesión
if (socioLogado) {
    const btnLogout = document.getElementById("btn-logout");
    if (btnLogout) {
        btnLogout.addEventListener("click", () => {
            localStorage.clear();
            window.location.href = "index.html";
        });
    }
}