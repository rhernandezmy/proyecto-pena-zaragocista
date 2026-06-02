-- SCRIPT DE CREACIÓN DE LA BASE DE DATOS - PEÑA PRESENTES POR EL ESCUDO
-- Coherente con los modelos SQLAlchemy del backend

DROP TABLE IF EXISTS reservas_viajes CASCADE;
DROP TABLE IF EXISTS viajes_compartidos CASCADE;
DROP TABLE IF EXISTS vehiculos CASCADE;
DROP TABLE IF EXISTS cuotas CASCADE;
DROP TABLE IF EXISTS socios CASCADE;
DROP TABLE IF EXISTS patrocinadores CASCADE;

-- ========================================================
-- TABLA: SOCIOS (Antes 'socios')
-- ========================================================
CREATE TABLE socios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    fecha_alta DATE DEFAULT CURRENT_DATE,
    es_administrador BOOLEAN DEFAULT FALSE
);
CREATE INDEX idx_socios_email ON socios (email);

-- ========================================================
-- TABLA: CUOTAS
-- ========================================================
CREATE TABLE cuotas (
    id SERIAL PRIMARY KEY,
    socio_id INT NOT NULL,
    ejercicio_fiscal INT DEFAULT 2026,
    importe NUMERIC(10, 2) DEFAULT 120.00,
    estado VARCHAR(20) DEFAULT 'PENDIENTE',
    fecha_limite DATE NOT NULL,
    stripe_payment_intent_id VARCHAR(100),
    CONSTRAINT fk_cuotas_socio FOREIGN KEY (socio_id) 
        REFERENCES socios(id) ON DELETE CASCADE
);

-- ========================================================
-- TABLA: VEHÍCULOS
-- ========================================================
CREATE TABLE vehiculos (
    id SERIAL PRIMARY KEY,
    socio_id INT NOT NULL,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    plazas_totales INT NOT NULL,
    CONSTRAINT fk_vehiculos_socio FOREIGN KEY (socio_id) 
        REFERENCES socios(id) ON DELETE CASCADE
);

-- ========================================================
-- TABLA: VIAJES COMPARTIDOS
-- ========================================================
CREATE TABLE viajes_compartidos (
    id SERIAL PRIMARY KEY,
    vehiculo_id INT NOT NULL,
    origen VARCHAR(100) DEFAULT 'Zaragoza',
    destino VARCHAR(100) NOT NULL,
    fecha_salida TIMESTAMP NOT NULL,
    plazas_disponibles INT NOT NULL,
    CONSTRAINT fk_viajes_vehiculo FOREIGN KEY (vehiculo_id)
        REFERENCES vehiculos(id) ON DELETE CASCADE
);

-- ========================================================
-- TABLA: RESERVAS VIAJES
-- ========================================================
CREATE TABLE reservas_viajes (
    id SERIAL PRIMARY KEY,
    socio_id INT NOT NULL,
    viaje_id INT NOT NULL,
    plazas_reservadas INT DEFAULT 1,
    fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reserva_socio FOREIGN KEY (socio_id) REFERENCES socios(id) ON DELETE CASCADE,
    CONSTRAINT fk_reserva_viaje FOREIGN KEY (viaje_id) REFERENCES viajes_compartidos(id) ON DELETE CASCADE
);

-- ========================================================
-- TABLA: PATROCINADORES
-- ========================================================
CREATE TABLE patrocinadores (
    id SERIAL PRIMARY KEY,
    nombre_comercial VARCHAR(150) NOT NULL,
    sector VARCHAR(50) DEFAULT 'Bar',
    logo_url VARCHAR(255),
    contribucion NUMERIC(10, 2) DEFAULT 0.0
);