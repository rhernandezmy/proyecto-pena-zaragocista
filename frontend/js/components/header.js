const headerHTML = `
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom py-3">
        <div class="container">
            <a class="navbar-brand" href="index.html">
                <img src="logo.png" alt="Logo" style="height: 50px;">
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center">
                    <li class="nav-item"><a class="nav-link" href="index.html">Inicio</a></li>
                    <li class="nav-item"><a class="nav-link" href="noticias.html">Noticias</a></li>
                    <li class="nav-item"><a class="nav-link" href="partidos.html">Partidos</a></li>
                    <li class="nav-item"><a class="nav-link" href="pena.html">La Peña</a></li>
                    <li class="nav-item"><a class="nav-link" href="clasificacion.html">Clasificación</a></li>
                    <li class="nav-item"><a class="nav-link" href="partners.html">Partners</a></li>
                    <li class="nav-item ms-3">
                        <a class="btn btn-outline-primary" href="login.html">Acceso Socios</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
`;

document.getElementById('header-placeholder').innerHTML = headerHTML;