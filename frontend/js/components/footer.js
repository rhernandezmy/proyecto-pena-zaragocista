const footerHTML = `
<footer class="bg-light py-5 mt-5 border-top">
    <div class="container">
        <div class="row">
            <div class="col-md-4">
                <img src="logo.png" alt="Logo" style="max-width: 120px;" class="mb-3">
                <p class="text-muted">Síguenos en Redes Sociales</p>
                <div class="d-flex gap-2">
                    <a href="#" class="btn btn-outline-dark btn-sm rounded-circle">f</a>
                    <a href="#" class="btn btn-outline-dark btn-sm rounded-circle">ig</a>
                    <a href="#" class="btn btn-outline-dark btn-sm rounded-circle">tw</a>
                    <a href="#" class="btn btn-outline-dark btn-sm rounded-circle">tk</a>
                </div>
            </div>

            <div class="col-md-4">
                <h5 class="mb-3">Menú</h5>
                <ul class="list-unstyled">
                    <li><a href="index.html" class="text-decoration-none text-dark">Inicio</a></li>
                    <li><a href="partidos.html" class="text-decoration-none text-dark">Partidos</a></li>
                    <li><a href="noticias.html" class="text-decoration-none text-dark">Noticias</a></li>
                    <li><a href="pena.html" class="text-decoration-none text-dark">La Peña</a></li>
                    <li><a href="clasificacion.html" class="text-decoration-none text-dark">Clasificación</a></li>
                    <li><a href="partners.html" class="text-decoration-none text-dark">Partners</a></li>
                </ul>
            </div>

            <div class="col-md-4">
                <h5 class="mb-3">Ayuda</h5>
                <ul class="list-unstyled">
                    <li><a href="#" class="text-decoration-none text-dark">Aviso Legal</a></li>
                    <li><a href="#" class="text-decoration-none text-dark">Política de Cookies</a></li>
                    <li><a href="#" class="text-decoration-none text-dark">Política de Privacidad</a></li>
                </ul>
            </div>
        </div>
        <div class="text-center mt-4">
            <p class="text-muted">&copy; 2026 Peña Zaragocista</p>
        </div>
    </div>
</footer>
`;

document.getElementById('footer-placeholder').innerHTML = footerHTML;