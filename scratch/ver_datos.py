import json
import pandas as pd
from scraping.scraper import ShopifyScraper

def ver_datos_consola():
    """
    Ejecuta una extracción de prueba de 1 página (250 productos)
    y visualiza la estructura tabular usando un DataFrame de pandas.
    """
    print("Iniciando extracción de prueba en memoria...")
    scraper = ShopifyScraper()
    
    # Extraemos solo la primera página para la demostración
    productos_brutos = scraper.run(max_pages=1)
    
    if not productos_brutos:
        print("No se pudieron extraer datos.")
        return
        
    # Convertir a DataFrame de Pandas para formatear como tabla analítica
    df = pd.DataFrame(productos_brutos)
    
    print("\n" + "="*80)
    print(" ANÁLISIS DE DATOS EXTRAÍDOS (Muestra de los primeros 5 productos)")
    print("="*80)
    # Seleccionamos columnas clave para mostrar de forma limpia en consola
    columnas_vista = ["external_id", "title", "current_price", "discount_percentage", "stock_status"]
    print(df[columnas_vista].head(5).to_markdown(index=False))
    
    print("\n" + "="*80)
    print(" ESTRUCTURA COMPLETA DEL PRIMER REGISTRO EN FORMATO JSON")
    print("="*80)
    print(json.dumps(productos_brutos[0], indent=4, ensure_ascii=False))
    
    # Opcional: Guardar una muestra local para inspección visual
    archivo_salida = "scratch/muestra_productos.json"
    import os
    os.makedirs("scratch", exist_ok=True)
    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(productos_brutos, f, indent=4, ensure_ascii=False)
    print(f"\n[INFO] Archivo de muestra exportado correctamente a: {archivo_salida}")

if __name__ == "__main__":
    ver_datos_consola()
