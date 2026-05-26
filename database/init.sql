-- SCRIPT DE CREACIÓN DE LA BASE DE DATOS - PEÑA PRESENTES POR EL ESCUDO

-- 1. Tabla de Usuarios (Socios y Administradores)
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol VARCHAR(20) DEFAULT 'Socio', -- 'Socio' o 'Administrador'
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Cuotas Anuales (Historial de pagos vinculados a Stripe)
CREATE TABLE IF NOT EXISTS cuotas (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    ano_ejercicio INT NOT NULL,
    estado_pago VARCHAR(20) DEFAULT 'Pendiente', -- 'Pagado' o 'Pendiente'
    stripe_intent_id VARCHAR(100), -- ID de la transacción simulada en Stripe
    fecha_pago TIMESTAMP,
    CONSTRAINT fk_usuario_cuota FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- 3. Tabla de Partidos (Calendario de desplazamientos)
CREATE TABLE IF NOT EXISTS partidos (
    id SERIAL PRIMARY KEY,
    rival VARCHAR(100) NOT NULL,
    estadio VARCHAR(100) NOT NULL,
    fecha_hora TIMESTAMP NOT NULL
);

-- 4. Tabla de Tablón de Viajes (Coordinación de desplazamientos entre socios)
CREATE TABLE IF NOT EXISTS viajes (
    id SERIAL PRIMARY KEY,
    partido_id INT NOT NULL,
    usuario_id INT NOT NULL,
    modalidad VARCHAR(30) NOT NULL, -- 'Autobús Federación' o 'Vehículo Propio'
    plazas_ofertadas INT DEFAULT 0, -- Solo aplica si es vehículo propio
    hora_salida VARCHAR(10), -- Por ejemplo: '08:30'
    CONSTRAINT fk_partido_viaje FOREIGN KEY (partido_id) REFERENCES partidos(id) ON DELETE CASCADE,
    CONSTRAINT fk_usuario_viaje FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);