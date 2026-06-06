const socioLogado = localStorage.getItem("socio_nombre");

let menuViajesHTML = "";
let botonAuthHTML = `<a class="btn btn-outline-primary" href="login.html">Acceso Socios</a>`;

if (socioLogado) {
    menuViajesHTML = `<a class="nav-link text-success fw-bold" href="viajes.html">🚗 Viajes</a>`;
    botonAuthHTML = `
        <div class="d-flex align-items-center gap-3">
            <span class="text-muted">Hola, <strong>${socioLogado}</strong></span>
            <button class="btn btn-sm btn-outline-danger" id="btn-logout">Salir</button>
        </div>
    `;
}

const headerHTML = `
    <nav class="navbar navbar-expand-lg">
        <div class="container">
            <a class="navbar-brand" href="index.html">
                <img src="assets/logo.png" alt="Logo" style="height: 60px;">
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <div class="navbar-nav ms-auto align-items-center">
                    <a class="nav-link" href="noticias.html">Noticias</a>
                    <a class="nav-link" href="partidos.html">Partidos</a>
                    <a class="nav-link" href="pena.html">La Peña</a>
                    ${menuViajesHTML}
                    <div class="ms-lg-3">${botonAuthHTML}</div>
                </div>
            </div>
        </div>
    </nav>
`;

document.getElementById('header-placeholder').innerHTML = headerHTML;

if (socioLogado) {
    document.getElementById("btn-logout").addEventListener("click", () => {
        localStorage.removeItem("socio_nombre");
        window.location.href = "index.html";
    });
}