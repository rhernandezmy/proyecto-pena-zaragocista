-- SCRIPT DE CREACIÓN DE LA BASE DE DATOS - PEÑA PRESENTES POR EL ESCUDO

DROP TABLE IF EXISTS reservas CASCADE;
DROP TABLE IF EXISTS viajes CASCADE;
DROP TABLE IF EXISTS partidos CASCADE;
DROP TABLE IF EXISTS rivales_maestros CASCADE;
DROP TABLE IF EXISTS vehiculos CASCADE;
DROP TABLE IF EXISTS cuotas CASCADE;
DROP TABLE IF EXISTS socios CASCADE;
DROP TABLE IF EXISTS patrocinadores CASCADE;

-- 1. SOCIOS
CREATE TABLE socios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) DEFAULT 'Socio',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);
CREATE INDEX idx_socios_email ON socios (email);

-- 2. CUOTAS
CREATE TABLE cuotas (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL REFERENCES socios(id) ON DELETE RESTRICT,
    ano_ejercicio INT DEFAULT 2026,
    estado_pago VARCHAR(20) DEFAULT 'Pendiente',
    stripe_intent_id VARCHAR(100),
    fecha_pago TIMESTAMP,
    CONSTRAINT fk_cuotas_socio FOREIGN KEY (usuario_id) REFERENCES socios(id)
);

-- 3. VEHÍCULOS
CREATE TABLE vehiculos (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL REFERENCES socios(id) ON DELETE CASCADE,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    plazas_totales INT NOT NULL
);

-- 4. RIVALES MAESTROS
CREATE TABLE rivales_maestros (
    id SERIAL PRIMARY KEY,
    nombre_equipo VARCHAR(100) UNIQUE NOT NULL,
    estadio VARCHAR(100) NOT NULL,
    latitud DOUBLE PRECISION NOT NULL,
    longitud DOUBLE PRECISION NOT NULL
);

-- 5. PARTIDOS
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

-- 6. VIAJES
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

-- 7. RESERVAS
CREATE TABLE reservas (
    id SERIAL PRIMARY KEY,
    viaje_id INT NOT NULL REFERENCES viajes(id) ON DELETE CASCADE,
    nombre_socio VARCHAR(150) NOT NULL,
    asientos_reservados INT DEFAULT 1
);

-- 8. PATROCINADORES
CREATE TABLE patrocinadores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    tipo_negocio VARCHAR(50) DEFAULT 'Bar',
    logo_url VARCHAR(255),
    contribucion FLOAT DEFAULT 0.0
);