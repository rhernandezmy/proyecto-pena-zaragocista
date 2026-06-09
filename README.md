# 🦁 Plataforma Web Peña Zaragocista - Panel de Control del Proyecto

Este archivo actúa como el mapa de ruta definitivo del proyecto para asegurar la sincronización matemática entre el código real desarrollado y la memoria técnica que se entregará al tribunal.

## 📌 ÍNDICE DE CONTENIDOS

* [⚙️ 1. Estado del Backend (FastAPI + PostgreSQL)](#️-1-estado-del-backend-fastapi--postgresql)
  * [Módulo de Socios y Autenticación](#-módulo-de-socios-y-autenticación-listo)
  * [Módulo de Partidos y Rivales](#-módulo-de-partidos-y-rivales-listo)
  * [Módulo de Viajes y Logística](#-módulo-de-viajes-y-logística-listo)
  * [Módulo de Reservas y Notificaciones](#-módulo-de-reservas-y-notificaciones-listo)
  * [Módulo de Cuotas y Pasarela Stripe](#-módulo-de-cuotas-y-pasarela-stripe--en-proceso)
* [🎨 2. Estado del Frontend (Pantallas de Usuario e Integración)](#-2-estado-del-frontend-pantallas-de-usuario-e-integración)
* [🚀 3. Infraestructura y Repositorio (¡Al Día!)](#-3-infraestructura-y-repositorio-al-día)
* [⚠️ 4. Alerta de Coherencia (Revisión Obligatoria)](#️-4-alerta-de-coherencia-revisión-obligatoria)

## ⚙️ 1. ESTADO DEL BACKEND (FastAPI + PostgreSQL)

### 🟢 Módulo de Socios y Autenticación (¡LISTO!)
- [x] Modelo de base de datos `Usuario` en `models.py`.
- [x] Rutas de registro y login con hashing seguro (Bcrypt).
- [x] Control de sesiones mediante tokens JWT.
- [x] *Estado Memoria:* Sincronizado.

### 🟢 Módulo de Partidos y Rivales (¡LISTO!)
- [x] Modelos `Partido` y `RivalMaestro` con geolocalización (lat/long).
- [x] Rutas CRUD completas.
- [x] Lógica de negocio defensiva (bloqueo de viajes locales).
- [x] *Estado Memoria:* Sincronizado.

### 🟢 Módulo de Viajes y Logística (¡LISTO!)
- [x] Modelo `Viaje` con precio, detalles, pernocta y plazas dinámicas.
- [x] Integración de `email_conductor` para coordinación.
- [x] *Estado Memoria:* Scripts DDL sincronizados con los modelos de SQLAlchemy.

### 🟢 Módulo de Reservas y Notificaciones (¡LISTO!)
- [x] Integridad referencial (`CASCADE`) validada en SQL y ORM.
- [x] Lógica transaccional de plazas.
- [x] Protocolo SMTP configurado para alertas de viaje.
- [x] Endpoint unificado de administración /panel/admin/global-data para servir socios, viajes y reservas_local de un solo golpe de forma asíncrona.
- [x] *Estado Memoria:* Pendiente actualizar diagrama de clases/casos de uso (sección 3).

### 🟡 Módulo de Cuotas y Pasarela Stripe (⏳ EN PROCESO)
- [x] Modelo `Cuota` implementado en `models.py`.
- [ ] Definir esquemas Pydantic para `PaymentIntent`.
- [ ] Implementar `routers/cuotas.py` con integración (Sandbox).
- [ ] *Estado Memoria:* Pendiente volcar lógica final tras validación Sandbox.

---

## 🎨 2. ESTADO DEL FRONTEND (Pantallas de Usuario e Integración)

- [ ] Creación de Mockups visuales para la memoria (Figma/Diagramas).
- [x] Estructura semántica HTML5 + Bootstrap unificada bajo una identidad visual corporativa fija (azul y oro) para todas las vistas (index.html, viajes.html, partidos.html, noticias.html).
- [x] Implementación de estructura HTML5 + Bootstrap (index.html, login.html).
- [x] Arquitectura de componentes globales dinámicos (header.js y footer.js) para evitar duplicidad de código.
- [x] Diseño modular y responsivo del Panel de Control del Administrador (admin.html) dividido por pestañas interactivas de control nativo de Bootstrap.
- [x] Núcleo de comunicación asíncrona (app.js con fetch) configurado y libre de bloqueos de seguridad de origen gracias a la implementación de CORS en el Backend.
- [🟡] Ajuste crítico en desarrollo: Sincronización fina del DOM en app.js para consumir los campos exactos del JSON global (teléfonos, cuotas, motivos de eventos) utilizando lógica no destructiva de nodos para asegurar la persistencia visual.

---

## 🚀 3. INFRAESTRUCTURA Y REPOSITORIO (¡AL DÍA!)
- [x] Repositorio de GitHub inicializado bajo protocolo HTTPS seguro.
- [x] Sincronización completa y fusión (merge) de la rama de desarrollo feature/frontend-development hacia la rama principal main.
- [x] Historial de Git limpio, documentado con commits semánticos funcionales y respaldado en la nube.
- [x] Enlace institucional al repositorio integrado como punto de partida en el primer bloque de la Memoria Técnica.

---

## ⚠️ 4. ALERTA DE COHERENCIA (Revisión Obligatoria)

Cada vez que el código sufra una modificación, se debe verificar que:
1. **DDL (init.sql):** Las tablas reflejen exactamente los campos de `models.py`.
2. **Endpoints:** Las rutas definidas en `main.py` mantengan la estructura de los nuevos modelos.
3. **Manejo del DOM:** Las funciones de renderizado dinámico en JavaScript apunten a los selectores exactos del HTML actual sin romper el flujo de Bootstrap.
4. **Memoria:** El apartado de "Diseño del Sistema" contemple los modelos `rivales_maestros` y `partidos` con su geolocalización.

---
**Última actualización:** 09/06/2026 (Tras merge exitoso de Frontend a Main)