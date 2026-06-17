-- Creación del modelo dimensional en estrella para AuditaFin

-- 1. Dimensión Proveedores
CREATE TABLE IF NOT EXISTS dim_proveedores (
    id_proveedor VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    sector VARCHAR(100),
    pais VARCHAR(100)
);

-- 2. Dimensión Departamentos
CREATE TABLE IF NOT EXISTS dim_departamentos (
    id_departamento VARCHAR(50) PRIMARY KEY,
    nombre_dept VARCHAR(100) NOT NULL,
    presupuesto_anual NUMERIC(15, 2) NOT NULL
);

-- 3. Tabla de Hechos de Gastos (Fact Gastos)
CREATE TABLE IF NOT EXISTS fact_gastos (
    id_factura VARCHAR(100) PRIMARY KEY,
    fecha DATE NOT NULL,
    id_proveedor VARCHAR(50) REFERENCES dim_proveedores(id_proveedor),
    id_departamento VARCHAR(50) REFERENCES dim_departamentos(id_departamento),
    importe NUMERIC(12, 2) NOT NULL,
    concepto TEXT
);

-- 4. Tabla de Hechos de Alertas de Auditoría (Fact Alertas)
CREATE TABLE IF NOT EXISTS fact_alertas (
    id_alerta VARCHAR(100) PRIMARY KEY,
    id_factura VARCHAR(100) REFERENCES fact_gastos(id_factura) ON DELETE CASCADE,
    tipo_anomalia VARCHAR(100) NOT NULL,
    nivel_riesgo VARCHAR(20) NOT NULL, -- BAJO, MEDIO, ALTO, CRÍTICO
    fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices recomendados para optimizar el rendimiento analítico (CTEs/Joins en consultas complejas)
CREATE INDEX IF NOT EXISTS idx_fact_gastos_fecha ON fact_gastos(fecha);
CREATE INDEX IF NOT EXISTS idx_fact_gastos_proveedor ON fact_gastos(id_proveedor);
CREATE INDEX IF NOT EXISTS idx_fact_gastos_depto ON fact_gastos(id_departamento);
CREATE INDEX IF NOT EXISTS idx_fact_alertas_factura ON fact_alertas(id_factura);
