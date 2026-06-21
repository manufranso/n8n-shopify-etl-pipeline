# E-Commerce Product Intelligence & Trend Detection Pipeline 🚀

Este proyecto implementa un pipeline automatizado de extracción de datos de catálogo (Web Scraping), almacenamiento estructurado (PostgreSQL) y enriquecimiento semántico mediante Inteligencia Artificial (Google Gemini) orquestado con n8n, culminando en un Dashboard analítico interactivo en Power BI.

El proyecto se encuentra **completamente operativo y finalizado**, sirviendo como un portfolio de nivel profesional para la toma de decisiones estratégicas de negocio y optimización SEO en el sector e-commerce.

El scraper está optimizado específicamente para extraer el catálogo completo del e-commerce **Oh Yeah Party** a través del endpoint interno estructurado de Shopify, garantizando estabilidad y rendimiento.

---

## 🛠️ Arquitectura del Proyecto

El sistema está completamente contenedorizado con **Docker** y consta de tres capas principales:

1. **Extracción y Carga (Python API - Flask)**:
   * Expone un endpoint `/trigger-scraping` para iniciar la extracción.
   * Consume de manera eficiente la API interna de colecciones de Shopify de Oh Yeah Party (`/products.json?limit=250&page=X`).
   * Almacena y sincroniza de forma idempotente (Insert or Update) los productos directamente en PostgreSQL, registrando las actualizaciones de stock, precios y metadatos (`updated_at`).
2. **Orquestación y Categorización Semántica (n8n & Google Gemini)**:
   * Un flujo orquestado recupera productos sin procesar en lotes controlados.
   * Utiliza el LLM **Gemini 3.1 Flash-Lite** para clasificar el producto en base a su título y descripción (extracción de Temática del Evento, Rango de Edad objetivo y optimización de título para SEO).
   * Almacena los insights resultantes en la tabla `insights_ia`.
   * Incluye un sistema de control de errores proactivo que notifica fallos de ejecución directamente por Email (SMTP).
3. **Capa Analítica (PostgreSQL Vistas)**:
   * Vistas SQL optimizadas preparadas en la base de datos para cruzar el catálogo con la categorización semántica, preparadas para alimentar de forma directa el Dashboard.

---

## 📂 Estructura del Repositorio

* `config/settings.py`: Parámetros globales de scraping, rate limits y cabeceras HTTP.
* `database/schema.sql`: Estructura DDL de las tablas, claves y sus índices analíticos.
* `database/clean_data.py`: Pipeline de limpieza y validación retroactiva de datos de catálogo.
* `dashboard/query_views.sql`: Vistas SQL analíticas (Análisis de catálogo, alertas de rotura de stock y optimizaciones SEO).
* `dashboard/OH_YEAH_DASHBOARD.pbix`: Archivo fuente del Dashboard interactivo en Power BI Desktop.
* `scraping/scraper.py`: Orquestador del scraper con lógica de paginación e intervalos seguros de rate-limit.
* `scraping/parser.py`: Limpieza de datos (descuentos, cálculo de stock y formateo).
* `scraping/app.py`: API Flask para el disparo HTTP desde n8n.
* `n8n/OH_YEAH_WORKFLOW.json`: Flujo de n8n listo para importar.
* `docker-compose.yml`: Definición del stack contenedorizado (Postgres 15 y API Python).

---

## 🚀 Instrucciones de Despliegue Local

### 1. Clonar el repositorio y levantar el entorno
En la raíz del proyecto, ejecuta el siguiente comando para levantar la base de datos PostgreSQL y la API Flask:
```bash
docker-compose up --build -d
```

### 2. Configurar el Orquestador n8n
1. Abre tu instancia local de n8n (ej: `http://localhost:5678`).
2. Haz clic en **Import from File** y selecciona el archivo `OH_YEAH_WORKFLOW.json` que se encuentra en la carpeta **`n8n/`** de este proyecto.
3. Configura tus credenciales en los nodos correspondientes:
   * **Google Gemini API**: Tu API key de Google AI Studio.
   * **Postgres**: Conexión al Host `catalog_intelligence_postgres` por el puerto `5432` con usuario `OH_YEAH_USER` y contraseña `OH_YEAH_PASSWORD`.
   * **Send Email (SMTP)**: Configura las credenciales SMTP de tu correo si deseas recibir alertas de fallos de ejecución.

---

## 📊 Explotación y Modelo Analítico en Power BI

El repositorio incluye un modelo analítico estructurado en **`dashboard/OH_YEAH_DASHBOARD.pbix`** que explota las siguientes vistas de la base de datos:
* `vista_analisis_catalogo`: Consolida los atributos del producto enriquecidos con temática, rango de edad, tipo de producto generado por la IA de Gemini, y el metadato `updated_at` que registra la fecha de última modificación del producto en la tienda de Shopify.
* `vista_alertas_roturas_stock`: Monitorea productos fuera de stock.
* `vista_optimizaciones_seo_ofertas`: Diseñada para optimizar las conversiones de búsqueda y las sugerencias de títulos optimizados generados por Gemini.

### Páginas del Dashboard y Storytelling Visual:
1. **Surtido y Mix de Producto**:
   * Análisis de volumen del catálogo con tarjetas dinámicas de total productos y precio promedio.
   * Gráficos interactivos de distribución de productos por Temática del Evento y Rango de Edad.
   * **KPI de Frescura de Catálogo (Última Sincronización)**: Mapeo dinámico mediante DAX del último cambio registrado en Shopify.
2. **Precios y Ofertas**:
   * KPIs dinámicos calculados por DAX para el control comercial: *Cantidad de Rebajados*, *Descuento Promedio* y *Descuento Máximo*.
   * Gráfico de barras interactivo de descuento medio por temática del evento que filtra la tabla central de productos en oferta.
3. **Stock**:
   * KPI de Tasa General de Rotura de Stock y Cantidad de Productos Agotados.
   * Detalle gráfico por temática para detectar huecos de catálogo críticos.
4. **SEO**:
   * Tabla interactiva de sugerencias de optimización semántica generadas por Gemini.
   * **Buscador de Productos integrado**: Filtro directo y rápido de términos clave de producto mediante segmentación integrada por texto.

---

## 📥 Cómo abrir el Dashboard en local (Para Reclutadores / Evaluadores)

El archivo del informe de Power BI está diseñado de forma no destructiva y es 100% interactivo. 

1. Asegúrate de tener instalado **Power BI Desktop** (aplicación gratuita disponible en la Microsoft Store).
2. Descarga y abre el archivo [dashboard/OH_YEAH_DASHBOARD.pbix](file:///c:/Users/manue/OneDrive/Escritorio/Proyectos/Web%20Scrapping/dashboard/OH_YEAH_DASHBOARD.pbix).
3. **Uso de Caché de Datos:** El archivo se comparte con una **caché de datos ya precargada**. Esto significa que podrás hacer clic en todos los gráficos, filtrar por temáticas, buscar productos e interactuar al 100% con el informe de forma inmediata sin necesidad de levantar los contenedores de Docker o conectarte a la base de datos de origen.
