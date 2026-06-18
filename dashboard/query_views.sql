-- Vistas SQL optimizadas para el Dashboard de Power BI / Tableau

-- 1. Vista de Análisis de Catálogo: Cruza productos con su categorización semántica por IA
CREATE OR REPLACE VIEW vista_analisis_catalogo AS
SELECT 
    p.id AS producto_id,
    p.external_id,
    p.title AS producto_titulo,
    p.handle,
    p.current_price,
    p.original_price,
    p.discount_percentage,
    p.stock_status,
    p.image_url,
    p.created_at,
    p.published_at,
    p.last_scraped_at,
    COALESCE(i.tematica, 'Sin Categorizar') AS tematica,
    COALESCE(i.rango_edad, 'Sin Clasificar') AS rango_edad,
    COALESCE(i.seo_title_opt, p.title) AS seo_title_opt,
    i.analizado_at AS ia_analizado_at
FROM productos p
LEFT JOIN insights_ia i ON p.external_id = i.external_id;

-- 2. Vista de Alertas de Roturas de Stock: Identifica productos agotados agrupados por temática y rango de edad
CREATE OR REPLACE VIEW vista_alertas_roturas_stock AS
SELECT 
    COALESCE(i.tematica, 'Sin Categorizar') AS tematica,
    COALESCE(i.rango_edad, 'Sin Clasificar') AS rango_edad,
    COUNT(*) AS total_productos,
    SUM(CASE WHEN p.stock_status = 'Agotado' THEN 1 ELSE 0 END) AS productos_agotados,
    ROUND(
        (SUM(CASE WHEN p.stock_status = 'Agotado' THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)) * 100, 
        2
    ) AS tasa_rotura_stock
FROM productos p
LEFT JOIN insights_ia i ON p.external_id = i.external_id
GROUP BY COALESCE(i.tematica, 'Sin Categorizar'), COALESCE(i.rango_edad, 'Sin Clasificar');

-- 3. Vista de Oportunidades SEO y Descuentos: Para identificar discrepancias de títulos y análisis de margen/oferta
CREATE OR REPLACE VIEW vista_optimizaciones_seo_ofertas AS
SELECT 
    p.id AS producto_id,
    p.external_id,
    p.title AS titulo_original,
    i.seo_title_opt AS titulo_optimizado,
    CASE 
        WHEN i.seo_title_opt IS NOT NULL AND i.seo_title_opt <> p.title THEN TRUE
        ELSE FALSE
    END AS requiere_actualizacion_seo,
    p.current_price,
    p.original_price,
    p.discount_percentage,
    COALESCE(i.tematica, 'Sin Categorizar') AS tematica
FROM productos p
LEFT JOIN insights_ia i ON p.external_id = i.external_id;
