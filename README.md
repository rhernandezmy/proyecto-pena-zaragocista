# 🦁 Plataforma Web Peña Zaragocista - Panel de Control del Proyecto

Este archivo actúa como el mapa de ruta definitivo del proyecto para asegurar la sincronización matemática entre el código real desarrollado y la memoria técnica (Puntos 3 y 4) que se entregará al tribunal.

## ⚙️ 1. ESTADO DEL BACKEND (FastAPI + PostgreSQL)

### 🟢 Módulo de Usuarios y Autenticación (¡LISTO!)
- [x] Modelo de base de datos `Usuario` en `models.py`.
- [x] Rutas de registro y login con hashing seguro de contraseñas.
- [x] Emisión de tokens JWT para controlar las sesiones de socios.
- [x] *Anotación Memoria:* Sincronizado en el listado de tablas.

### 🟢 Módulo de Partidos y Rivales (¡LISTO!)
- [x] Modelo `Partido` y tabla maestra `RivalMaestro` con coordenadas de geolocalización.
- [x] Rutas GET y POST para la cartelera deportiva.
- [x] Validación para impedir viajes si el partido es local ("Ibercaja estadio").
- [x] *Anotación Memoria:* Añadidos campos de latitud/longitud en la sección 3.1.

### 🟢 Módulo de Viajes y Logística (¡LISTO!)
- [x] Modelo `Viaje` con precio, detalles y flag de pernocta (`hace_noche`).
- [x] Gestión de plazas dinámicas (`plazas_totales` y `plazas_disponibles`).
- [x] Vinculación del trayecto a un `email_conductor` real.
- [x] *Anotación Memoria:* Actualizados los scripts DDL en la documentación.

### 🟢 Módulo de Reservas y Notificaciones (¡LISTO!)
- [x] Modelo `Reserva` enlazado con integridad referencial en cascada (`CASCADE`).
- [x] Lógica transaccional: restar asientos en el POST y devolver plazas en el DELETE.
- [x] Integración segura del protocolo SMTP con Google (`python-dotenv` + `.env`).
- [x] Envío dinámico de emails reales de alerta al conductor ante cancelaciones.
- [x] *Anotación Memoria:* **FALTA ACTUALIZAR CASOS DE USO Y DIAGRAMA DE CLASES EN EL PUNTO 3.**

### 🟡 Módulo de Cuotas y Pasarela Stripe (⏳ EN PROCESO)
- [ ] Implementar el modelo `Cuota` en `models.py` (id, usuario_id, ano_ejercicio, estado_pago, stripe_intent_id, fecha_pago).
- [ ] Crear el esquema de validación en `schemas.py` para tramitar intenciones de pago.
- [ ] Crear el enrutador `routers/cuotas.py` e instalar la librería oficial de Stripe (`pip install stripe`).
- [ ] Desarrollar la lógica del endpoint para generar un `PaymentIntent` simulado en modo Sandbox.
- [ ] *Anotación Memoria:* **FALTA INTEGRAR SCRIPTS SQL Y LÓGICA DE NEGOCIO AL FINALIZAR EL CÓDIGO.**

---

## 🎨 2. ESTADO DEL FRONTEND (Pantallas de Usuario)

- [ ] Bocetar los Mockups visuales oficiales para la memoria (Cartelera, Coches/Formulario, Zona de Cancelación, Pasarela de Pago).
- [ ] Crear la estructura base en HTML5 y diseño responsive con Bootstrap.
- [ ] Conectar los endpoints mediante peticiones asíncronas de JavaScript (`fetch`).

---

## ⚠️ 3. ALERTA DE COHERENCIA (Revisión Obligatoria antes de Entregar)
Cada vez que el código sufra una modificación técnica, se debe verificar que los siguientes puntos de la memoria reflejen exactamente el cambio:
1. **Apartado 3.1.1:** Descripción de datos elementales (¿coinciden los campos?).
2. **Apartado 3.1.3:** Sentencias SQL del DDL de creación de tablas.
3. **Apartado 4.1.1:** Índice jerárquico de ficheros del proyecto.
4. **Archivos de Código (4.1.2 - 4.1.7):** Los bloques de texto plano deben ser idénticos a los del editor de código.