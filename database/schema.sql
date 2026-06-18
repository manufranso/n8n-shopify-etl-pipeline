-- Definición de Tablas para E-Commerce Product Intelligence & Trend Detection

-- 1. Tabla de Productos: Almacena los atributos extraídos en el scraping
CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(50) UNIQUE NOT NULL,    -- ID único de Shopify
    title VARCHAR(255) NOT NULL,
    handle VARCHAR(255),
    current_price NUMERIC(10, 2) NOT NULL,
    original_price NUMERIC(10, 2) NOT NULL,
    discount_percentage NUMERIC(5, 2) DEFAULT 0.00,
    stock_status VARCHAR(50) NOT NULL,           -- 'Disponible' / 'Agotado'
    image_url TEXT,
    description TEXT,
    created_at TIMESTAMP,                        -- Fecha creación en Shopify
    published_at TIMESTAMP,                      -- Fecha publicación en Shopify
    last_scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Insights IA: Datos enriquecidos mediante LLM / n8n
CREATE TABLE IF NOT EXISTS insights_ia (
    id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES productos(id) ON DELETE CASCADE,
    external_id VARCHAR(50) UNIQUE NOT NULL,    -- ID único de Shopify para emparejamiento rápido
    tematica VARCHAR(100),                      -- Ej: Disney, Cumpleaños Infantil, Halloween
    rango_edad VARCHAR(50),                     -- Ej: Bebés, Niños, Adultos, Universal
    seo_title_opt VARCHAR(255),                 -- Título optimizado sugerido por la IA
    analizado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar las consultas del Dashboard de Power BI / Tableau
CREATE INDEX IF NOT EXISTS idx_productos_stock_status ON productos(stock_status);
CREATE INDEX IF NOT EXISTS idx_productos_discount ON productos(discount_percentage);
CREATE INDEX IF NOT EXISTS idx_insights_tematica ON insights_ia(tematica);
CREATE INDEX IF NOT EXISTS idx_insights_rango_edad ON insights_ia(rango_edad);
