# E-Commerce Product Intelligence & Trend Detection Pipeline 🚀 (En Progreso)

Este proyecto implementa un pipeline automatizado de extracción de datos de catálogo (Web Scraping), almacenamiento estructurado (PostgreSQL) y enriquecimiento semántico mediante Inteligencia Artificial (Google Gemini) orquestado con n8n.

Actualmente, el backend y el pipeline de automatización de datos se encuentran completamente operativos, y el proyecto está **en fase de desarrollo activo**, siendo la siguiente etapa la construcción del dashboard visual final.

El scraper está optimizado específicamente para extraer el catálogo completo del e-commerce **Oh Yeah Party** a través del endpoint interno estructurado de Shopify, garantizando estabilidad y rendimiento.

---

## 🛠️ Arquitectura del Proyecto

El sistema está completamente contenedorizado con **Docker** y consta de tres capas principales:

1. **Extracción y Carga (Python API - Flask)**:
   * Expone un endpoint `/trigger-scraping` para iniciar la extracción.
   * Consume de manera eficiente la API interna de colecciones de Shopify de Oh Yeah Party (`/products.json?limit=250&page=X`).
   * Almacena y sincroniza de forma idempotente (Insert or Update) los productos directamente en PostgreSQL.
2. **Orquestación y Categorización Semántica (n8n & Google Gemini)**:
   * Un flujo orquestado recupera productos sin procesar en lotes controlados.
   * Utiliza el LLM **Gemini 2.5 Flash** para clasificar el producto en base a su título y descripción (extracción de Temática del Evento, Rango de Edad objetivo y optimización de título para SEO).
   * Almacena los insights resultantes en la tabla `insights_ia`.
   * Incluye un sistema de control de errores proactivo que notifica fallos de ejecución directamente por Email (SMTP).
3. **Capa Analítica (PostgreSQL Vistas)**:
   * Vistas SQL optimizadas preparadas en la base de datos para cruzar el catálogo con la categorización semántica, listas para conectar en la siguiente fase con Power BI o Tableau.

---

## 📂 Estructura del Repositorio

* `config/settings.py`: Parámetros globales de scraping, rate limits y cabeceras HTTP.
* `database/schema.sql`: Estructura DDL de las tablas, claves y sus índices analíticos.
* `dashboard/query_views.sql`: Vistas SQL analíticas (Análisis de catálogo, alertas de rotura de stock y optimizaciones SEO).
* `scraping/scraper.py`: Orquestador del scraper con lógica de paginación e intervalos seguros de rate-limit.
* `scraping/parser.py`: Limpieza de datos (descuentos, cálculo de stock y formateo).
* `scraping/app.py`: API Flask para el disparo HTTP desde n8n.
* `OH_YEAH_WORKFLOW.json`: Flujo de n8n listo para importar.
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

### 3. Explotación de Datos (Fase de Modelado en Progreso)
Puedes conectar tu herramienta BI directamente a la base de datos local usando las siguientes credenciales para iniciar la construcción de reportes:
* **Motor**: PostgreSQL
* **Host**: `localhost` (o la IP del servidor)
* **Puerto**: `5434`
* **Base de Datos**: `OH_YEAH_DB`
* **Usuario**: `OH_YEAH_USER`
* **Contraseña**: `OH_YEAH_PASSWORD`

Vistas SQL preparadas para el consumo BI:
* `vista_analisis_catalogo`
* `vista_alertas_roturas_stock`
* `vista_optimizaciones_seo_ofertas`
