# 🦁 Plataforma Web Peña Zaragocista - Panel de Control del Proyecto

Este archivo actúa como el mapa de ruta definitivo del proyecto para asegurar la sincronización matemática entre el código real desarrollado y la memoria técnica que se entregará al tribunal.

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
- [x] *Estado Memoria:* Pendiente actualizar diagrama de clases/casos de uso (sección 3).

### 🟡 Módulo de Cuotas y Pasarela Stripe (⏳ EN PROCESO)
- [x] Modelo `Cuota` implementado en `models.py`.
- [ ] Definir esquemas Pydantic para `PaymentIntent`.
- [ ] Implementar `routers/cuotas.py` con integración (Sandbox).
- [ ] *Estado Memoria:* Pendiente volcar lógica final tras validación Sandbox.

---

## 🎨 2. ESTADO DEL FRONTEND (Pantallas de Usuario)

- [ ] Creación de Mockups visuales para la memoria (Figma/Diagramas).
- [ ] Implementación de estructura HTML5 + Bootstrap (index.html, login.html).
- [x] Núcleo de comunicación asíncrona (`app.js` con `fetch`).
- [ ] Ajuste de `app.js` para consumir los nuevos atributos del modelo (precio, pernocta, etc.).

---

## ⚠️ 3. ALERTA DE COHERENCIA (Revisión Obligatoria)
Cada vez que el código sufra una modificación, se debe verificar que:
1. **DDL (init.sql):** Las tablas reflejen exactamente los campos de `models.py`.
2. **Endpoints:** Las rutas definidas en `main.py` mantengan la estructura de los nuevos modelos.
3. **Memoria:** El apartado de "Diseño del Sistema" contemple los modelos `rivales_maestros` y `partidos` con su geolocalización.

---
**Última actualización:** 03/06/2026