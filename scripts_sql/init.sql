-- SCRIPT DE CREACIÓN DE LA BASE DE DATOS - PEÑA PRESENTES POR EL ESCUDO
-- (Estructura corregida: Separación de Socios y Usuarios Web)

DROP TABLE IF EXISTS reservas CASCADE;
DROP TABLE IF EXISTS viajes CASCADE;
DROP TABLE IF EXISTS partidos CASCADE;
DROP TABLE IF EXISTS rivales_maestros CASCADE;
DROP TABLE IF EXISTS vehiculos CASCADE;
DROP TABLE IF EXISTS cuotas CASCADE;
DROP TABLE IF EXISTS usuarios_web CASCADE;
DROP TABLE IF EXISTS socios_pena CASCADE;
DROP TABLE IF EXISTS patrocinadores CASCADE;

-- 1. SOCIOS DE LA PEÑA (Gestión interna/Administrativa)
-- Aquí se gestionan los socios reales de la peña desde la Pestaña 1.
CREATE TABLE socios_pena (
    id SERIAL PRIMARY KEY,
    numero_socio INT UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(150) NOT NULL,
    dni VARCHAR(20) UNIQUE,
    telefono VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE,
    fecha_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. USUARIOS WEB (Cuentas de acceso a la plataforma)
-- Aquí se gestionan los accesos a la web desde la Pestaña 2.
CREATE TABLE usuarios_web (
    id SERIAL PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) DEFAULT 'Socio',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    socio_pena_id INT REFERENCES socios_pena(id) ON DELETE SET NULL
);
CREATE INDEX idx_usuarios_web_email ON usuarios_web (email);

-- 3. CUOTAS
CREATE TABLE cuotas (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL REFERENCES usuarios_web(id) ON DELETE RESTRICT,
    ano_ejercicio INT DEFAULT 2026,
    estado_pago VARCHAR(20) DEFAULT 'Pendiente',
    stripe_intent_id VARCHAR(100),
    fecha_pago TIMESTAMP,
    CONSTRAINT fk_cuotas_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios_web(id)
);

-- 4. VEHÍCULOS
CREATE TABLE vehiculos (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL REFERENCES usuarios_web(id) ON DELETE CASCADE,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    plazas_totales INT NOT NULL
);

-- 5. RIVALES MAESTROS
CREATE TABLE rivales_maestros (
    id SERIAL PRIMARY KEY,
    nombre_equipo VARCHAR(100) UNIQUE NOT NULL,
    estadio VARCHAR(100) NOT NULL,
    latitud DOUBLE PRECISION NOT NULL,
    longitud DOUBLE PRECISION NOT NULL
);

-- 6. PARTIDOS
CREATE TABLE partidos (
    id SERIAL PRIMARY KEY,
    rival VARCHAR(100) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    lugar VARCHAR(100) DEFAULT 'La Romareda',
    estado VARCHAR(20) DEFAULT 'Programado',
    latitud DOUBLE PRECISION,
    longitud DOUBLE PRECISION,
    rival_maestro_id INT REFERENCES rivales_maestros(id) ON DELETE SET NULL
);

-- 7. VIAJES
CREATE TABLE viajes (
    id SERIAL PRIMARY KEY,
    destino VARCHAR(100) NOT NULL,
    email_conductor VARCHAR(100) DEFAULT 'presentesxelescudo@gmail.com',
    partido_id INT NOT NULL REFERENCES partidos(id) ON DELETE CASCADE,
    tipo_transporte VARCHAR(30) DEFAULT 'Coche',
    plazas_totales INT NOT NULL,
    plazas_disponibles INT NOT NULL,
    precio FLOAT DEFAULT 0.0,
    detalles_precio VARCHAR(255),
    hace_noche BOOLEAN DEFAULT FALSE,
    latitud DOUBLE PRECISION,
    longitud DOUBLE PRECISION
);

-- 8. RESERVAS
CREATE TABLE reservas (
    id SERIAL PRIMARY KEY,
    viaje_id INT NOT NULL REFERENCES viajes(id) ON DELETE CASCADE,
    nombre_socio VARCHAR(150) NOT NULL,
    asientos_reservados INT DEFAULT 1
);

-- 9. PATROCINADORES
CREATE TABLE patrocinadores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    tipo_negocio VARCHAR(50) DEFAULT 'Bar',
    logo_url VARCHAR(255),
    contribucion FLOAT DEFAULT 0.0
);