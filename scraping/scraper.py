import time
import requests
from typing import List, Dict, Any

from config import settings
from scraping.parser import parse_products_batch

class ShopifyScraper:
    def __init__(self):
        self.base_url = settings.BASE_URL
        self.limit = settings.REQUEST_LIMIT
        self.delay = settings.REQUEST_DELAY
        self.headers = settings.DEFAULT_HEADERS

    def fetch_page(self, page: int) -> List[Dict[str, Any]]:
        """Realiza la petición HTTP GET a una página específica del endpoint JSON."""
        params = {
            "limit": self.limit,
            "page": page
        }
        try:
            print(f"Solicitando página {page} a Shopify...")
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get("products", [])
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión en página {page}: {e}")
            return []

    def run(self, max_pages: int = None) -> List[Dict[str, Any]]:
        """
        Ejecuta el ciclo de paginación del scraper de forma secuencial
        respetando el delay para evitar rate limiting.
        """
        all_parsed_products = []
        page = 1
        
        while True:
            products = self.fetch_page(page)
            if not products:
                print("No se encontraron más productos o se produjo un error. Finalizando extracción.")
                break
                
            parsed = parse_products_batch(products)
            all_parsed_products.extend(parsed)
            print(f"Página {page} parseada. {len(parsed)} productos extraídos.")
            
            # Condición de parada si se alcanza el máximo de páginas de prueba
            if max_pages and page >= max_pages:
                print(f"Se alcanzó el límite máximo de páginas configurado ({max_pages}). Parando.")
                break
                
            page += 1
            time.sleep(self.delay)
            
        print(f"Extracción finalizada. Total de productos extraídos: {len(all_parsed_products)}")
        return all_parsed_products

if __name__ == "__main__":
    # Test rápido de extracción de 1 página
    scraper = ShopifyScraper()
    resultados = scraper.run(max_pages=1)
    if resultados:
        print("\nMuestra del primer producto extraído:")
        print(resultados[0])
