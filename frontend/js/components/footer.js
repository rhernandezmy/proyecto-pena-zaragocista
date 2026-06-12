const footerHTML = `
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<footer class="bg-light py-5 mt-5 border-top">
    <div class="container">
        <div class="row">
            <div class="col-md-4 text-center d-flex flex-column align-items-center mb-4 mb-md-0">
                <img src="assets/logo.png" alt="Logo Peña" style="height: 50px;" class="mb-2">
                <p class="text-muted small mb-2">Síguenos en Redes Sociales</p>
                <div class="d-flex gap-2">
                    <a href="https://www.facebook.com/share/1AqBw3hvb2/" target="_blank" class="btn btn-outline-dark btn-sm rounded-circle" style="width: 32px; height: 32px; padding: 5px;">
                        <i class="fab fa-facebook-f"></i>
                    </a>
                    <a href="https://www.instagram.com/pz_presentes/" target="_blank" class="btn btn-outline-dark btn-sm rounded-circle" style="width: 32px; height: 32px; padding: 5px;">
                        <i class="fab fa-instagram"></i>
                    </a>
                    <a href="https://twitter.com/PZgzPresentesxE" target="_blank" class="btn btn-outline-dark btn-sm rounded-circle" style="width: 32px; height: 32px; padding: 5px;">
                        <i class="fab fa-x-twitter"></i>
                    </a>
                </div>
            </div>

            <div class="col-md-4 mb-4 mb-md-0">
                <h5 class="mb-3 fw-bold small text-uppercase" style="color: #0033A0;">Menú</h5>
                <ul class="list-unstyled shm-list small">
                    <li class="mb-1"><a href="index.html" class="text-decoration-none text-muted">🏠 Inicio</a></li>
                    <li class="mb-1"><a href="partidos.html" class="text-decoration-none text-muted">⚽ Partidos</a></li>
                    <li class="mb-1"><a href="noticias.html" class="text-decoration-none text-muted">📰 Noticias</a></li>
                    <li class="mb-1"><a href="pena.html" class="text-decoration-none text-muted">🦁 La Peña</a></li>
                    <li class="mb-1"><a href="clasificacion.html" class="text-decoration-none text-muted">📊 Clasificación</a></li>
                    <li class="mb-1"><a href="partners.html" class="text-decoration-none text-muted">🤝 Partners</a></li>
                </ul>
            </div>

            <div class="col-md-4">
                <h5 class="mb-3 fw-bold small text-uppercase" style="color: #0033A0;">Ayuda y Legal</h5>
                <ul class="list-unstyled small">
                    <li class="mb-1"><a href="#" data-bs-toggle="modal" data-bs-target="#modalAvisoLegal" class="text-decoration-none text-muted">⚖️ Aviso Legal</a></li>
                    <li class="mb-1"><a href="#" data-bs-toggle="modal" data-bs-target="#modalCookies" class="text-decoration-none text-muted">🍪 Política de Cookies</a></li>
                    <li class="mb-1"><a href="#" data-bs-toggle="modal" data-bs-target="#modalPrivacidad" class="text-decoration-none text-muted">🛡️ Política de Privacidad (RGPD)</a></li>
                </ul>
            </div>
        </div>
        
        <hr class="my-4 text-muted opacity-25">
        
        <div class="text-center">
            <p class="text-muted small mb-0">&copy; 2026 Peña Zaragocista Oficial. Todos los derechos reservados.</p>
            <p class="mt-1 small">
                <a href="#" data-bs-toggle="modal" data-bs-target="#modalAvisoLegal" class="text-decoration-none mx-2 text-secondary">Aviso Legal</a> | 
                <a href="#" data-bs-toggle="modal" data-bs-target="#modalPrivacidad" class="text-decoration-none mx-2 text-secondary">Privacidad</a> | 
                <a href="#" data-bs-toggle="modal" data-bs-target="#modalCookies" class="text-decoration-none mx-2 text-secondary">Cookies</a>
            </p>
        </div>
    </div>
</footer>

<div class="modal fade" id="modalAvisoLegal" tabindex="-1" aria-labelledby="modalAvisoLegalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title fw-bold" id="modalAvisoLegalLabel" style="color: #0033A0;">⚖️ Aviso Legal</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" style="text-align: justify; line-height: 1.6;">
                <p>En cumplimiento del artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios de la Sociedad de la Información y Comercio Electrónico (LSSI-CE), se informa que este sitio web es gestionado por la Peña Zaragocista Oficial. El acceso y uso de este portal atribuye la condición de usuario e implica la aceptación de los términos aquí contenidos.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="modalCookies" tabindex="-1" aria-labelledby="modalCookiesLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title fw-bold" id="modalCookiesLabel" style="color: #0033A0;">🍪 Política de Cookies</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" style="text-align: justify; line-height: 1.6;">
                <p>Este sitio web utiliza cookies propias y de terceros para optimizar la experiencia de usuario, analizar el tráfico web y facilitar las sesiones de inicio en la plataforma de socios web. Al continuar navegando, consideramos que acepta de forma consciente nuestra política de gestión de almacenamiento local.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="modalPrivacidad" tabindex="-1" aria-labelledby="modalPrivacidadLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title fw-bold" id="modalPrivacidadLabel" style="color: #0033A0;">🛡️ Política de Privacidad (RGPD)</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" style="text-align: justify; line-height: 1.6;">
                <p>De acuerdo con el Reglamento General de Protección de Datos (RGPD) y la LOPDGDD, le informamos que los datos recogidos a través de los formularios de alta de socios físicos e inicios de sesión web serán tratados bajo estricta seguridad con el único fin de gestionar administrativamente los viajes, eventos y cuotas de la Peña Zaragocista.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            </div>
        </div>
    </div>
</div>
`;

if (document.getElementById('footer-placeholder')) {
    document.getElementById('footer-placeholder').innerHTML = footerHTML;
}