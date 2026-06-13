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
                    <li class="mb-1"><a href="#" data-bs-toggle="modal" data-bs-target="#modalAvisoLegalFijo" class="text-decoration-none text-muted">⚖️ Aviso Legal</a></li>
                    <li class="mb-1"><a href="#" data-bs-toggle="modal" data-bs-target="#modalCookiesFijo" class="text-decoration-none text-muted">🍪 Política de Cookies</a></li>
                    <li class="mb-1"><a href="#" data-bs-toggle="modal" data-bs-target="#modalPrivacidadFijo" class="text-decoration-none text-muted">🛡️ Política de Privacidad (RGPD)</a></li>
                </ul>
            </div>
        </div>
        
        <hr class="my-4 text-muted opacity-25">
        
        <div class="text-center">
            <p class="text-muted small mb-0">&copy; 2026 Peña Zaragocista Oficial. Todos los derechos reservados.</p>
            <p class="mt-1 small">
                <a href="#" data-bs-toggle="modal" data-bs-target="#modalAvisoLegalFijo" class="text-decoration-none mx-2 text-secondary">Aviso Legal</a> | 
                <a href="#" data-bs-toggle="modal" data-bs-target="#modalPrivacidadFijo" class="text-decoration-none mx-2 text-secondary">Privacidad</a> | 
                <a href="#" data-bs-toggle="modal" data-bs-target="#modalCookiesFijo" class="text-decoration-none mx-2 text-secondary">Cookies</a>
            </p>
        </div>
    </div>
</footer>

<div class="modal fade" id="modalAvisoLegalFijo" tabindex="-1" aria-labelledby="modalAvisoLegalFijoLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
            <div class="modal-header bg-dark text-white">
                <h5 class="modal-title fw-bold" id="modalAvisoLegalFijoLabel">⚖️ Aviso Legal</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body text-dark" style="text-align: justify; line-height: 1.6; font-size: 0.95rem;">
                <h6 class="fw-bold mb-2">1. Datos Identificativos</h6>
                <p>En cumplimiento con el deber de información recogido en el artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios de la Sociedad de la Información y del Comercio Electrónico (LSSI-CE), se hace constar que este sitio web es gestionado de forma oficial por la administración de la Peña Zaragocista Oficial, encargada de la coordinación y difusión de contenidos para la afición.</p>
                
                <h6 class="fw-bold mb-2 mt-3">2. Condiciones de Uso</h6>
                <p>El acceso y uso de este portal web atribuye la condición de usuario, el cual acepta desde dicho acceso las condiciones generales aquí reflejadas. Los contenidos mostrados tienen un carácter meramente informativo y divulgativo sobre las actividades, eventos, noticias y partidos correspondientes a la agrupación.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Entendido</button>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="modalCookiesFijo" tabindex="-1" aria-labelledby="modalCookiesFijoLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
            <div class="modal-header bg-dark text-white">
                <h5 class="modal-title fw-bold" id="modalCookiesFijoLabel">🍪 Política de Cookies</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body text-dark" style="text-align: justify; line-height: 1.6; font-size: 0.95rem;">
                <p>Este sitio web utiliza únicamente cookies técnicas esenciales para su correcto funcionamiento, optimización de la interfaz y seguridad global del portal web.</p>
                <p>Estas herramientas permiten cargar correctamente los datos de partidos en tiempo real a través de la API externa y mantener las preferencias básicas de la sesión de navegación. Al continuar navegando por este sitio web, usted acepta de manera consciente el almacenamiento local de estos elementos indispensables.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Entendido y Aceptar Cookies</button>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="modalPrivacidadFijo" tabindex="-1" aria-labelledby="modalPrivacidadFijoLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
            <div class="modal-header bg-dark text-white">
                <h5 class="modal-title fw-bold" id="modalPrivacidadFijoLabel">🛡️ Política de Privacidad y Protección de Datos (RGPD)</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body text-dark" style="text-align: justify; line-height: 1.6; font-size: 0.95rem;">
                <h6 class="fw-bold mb-2">Responsable del Tratamiento</h6>
                <p>La Peña Zaragocista Oficial, conforme al Reglamento General de Protección de Datos (RGPD) y la legislación vigente, le garantiza que todos los datos recopilados de forma interna para la gestión de socios, viajes o consultas administrativas serán tratados bajo las más estrictas medidas de seguridad confidencial.</p>
                
                <h6 class="fw-bold mb-2 mt-3">Finalidad e Intercambio</h6>
                <p>La información recopilada tiene como único fin la correcta organización de cuotas, eventos y desplazamientos de la peña. Ningún dato personal de los usuarios o peñistas será vendido, cedido o intercambiado con terceras empresas u organismos bajo ningún concepto sin su previo consentimiento explícito.</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Aceptar y Continuar</button>
            </div>
        </div>
    </div>
</div>
`;

if (document.getElementById('footer-placeholder')) {
    document.getElementById('footer-placeholder').innerHTML = footerHTML;
}