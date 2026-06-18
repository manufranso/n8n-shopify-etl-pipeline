from flask import Flask, jsonify
from scraping.scraper import ShopifyScraper
from database.crud import upsert_productos

app = Flask(__name__)

@app.route("/trigger-scraping", methods=["GET", "POST"])
def trigger_scraping():
    """
    Endpoint HTTP que activa la extracción del catálogo de Shopify
    y realiza el Upsert automático de los productos en PostgreSQL.
    n8n llamará a este endpoint para iniciar el flujo de datos.
    """
    try:
        print("[API] Recibida petición para iniciar Web Scraping...")
        scraper = ShopifyScraper()
        
        # Ejecutar la extracción del catálogo (máximo 12 páginas, unos 3.000 productos)
        productos_extraidos = scraper.run(max_pages=12)
        
        if not productos_extraidos:
            return jsonify({
                "status": "warning",
                "message": "La extracción finalizó pero no se recuperó ningún producto.",
                "total_productos": 0
            }), 200
            
        # Sincronizar en base de datos
        upsert_productos(productos_extraidos)
        
        return jsonify({
            "status": "success",
            "message": "Web Scraping y sincronización completados con éxito.",
            "total_productos": len(productos_extraidos)
        }), 200
        
    except Exception as e:
        print(f"[API ERROR] Error en la ejecución del pipeline: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error interno en el servidor: {str(e)}"
        }), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    # Escucha en todas las interfaces en el puerto 5000
    app.run(host="0.0.0.0", port=5000)
