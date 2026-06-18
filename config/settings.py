import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env si existe
load_dotenv()

# Configuración del Scraper
BASE_URL = "https://www.ohyeahparty.com/collections/all/products.json"
REQUEST_LIMIT = 250  # Límite máximo de productos por página permitido por Shopify
REQUEST_DELAY = 1.5   # Delay en segundos entre peticiones para evitar bloqueos/rate-limits

# Headers de navegación para simular una petición legítima de navegador
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
}

# Configuración de Base de Datos PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5434")
DB_NAME = os.getenv("DB_NAME", "OH_YEAH_DB")
DB_USER = os.getenv("DB_USER", "OH_YEAH_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD", "OH_YEAH_PASSWORD")
