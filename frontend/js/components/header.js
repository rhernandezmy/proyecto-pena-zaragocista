// Verificamos si hay un socio logado para decidir qué mostrar
const socioLogado = localStorage.getItem("socio_nombre");

let menuViajesHTML = "";
let botonAuthHTML = `<a class="btn btn-outline-primary" href="login.html">Acceso Socios</a>`;

// Si el socio está logado, modificamos el menú
if (socioLogado) {
    menuViajesHTML = `<a class="nav-link text-success fw-bold" href="viajes.html">🚗 Viajes Peña</a>`;
    botonAuthHTML = `
        <div class="d-flex align-items-center gap-3">
            <span class="text-muted small">Hola, <strong>${socioLogado}</strong></span>
            <button class="btn btn-sm btn-outline-danger" id="btn-logout">Cerrar Sesión</button>
        </div>
    `;
}

const headerHTML = `
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom py-3">
        <div class="container">
            <a class="navbar-brand" href="index.html">
                <img src="assets/logo.png" alt="Logo Peña" style="height: 100px;">
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <div class="navbar-nav ms-auto align-items-center">
                    <a class="nav-link" href="noticias.html">Noticias</a>
                    <a class="nav-link" href="partidos.html">Partidos</a>
                    <a class="nav-link" href="pena.html">La Peña</a>
                    <a class="nav-link" href="clasificacion.html">Clasificación</a>
                    <a class="nav-link" href="partners.html">Partners</a>
                    
                    ${menuViajesHTML}
                    
                    <div class="ms-3">
                        ${botonAuthHTML}
                    </div>
                </div>
            </div>
        </div>
    </nav>
`;

document.getElementById('header-placeholder').innerHTML = headerHTML;

// Si está logado, añadimos la lógica para que el botón de Cerrar Sesión funcione
if (socioLogado) {
    document.getElementById("btn-logout").addEventListener("click", () => {
        localStorage.removeItem("socio_nombre"); // Borramos el rastro del socio
        alert("Sesión cerrada. ¡Hasta la próxima, zaragocista!");
        window.location.href = "index.html"; // Lo mandamos a la home pública
    });
}