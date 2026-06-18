from typing import Any, Dict, List

def clean_html_tags(text: str) -> str:
    """Elimina etiquetas HTML simples que puedan venir en la descripción original."""
    if not text:
        return ""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def parse_product_json(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parsea un único producto del JSON de Shopify mapeando la estructura requerida:
    - Nombre del artículo
    - Precio actual
    - Descuento (porcentaje)
    - Estado de Stock (Disponible / Agotado)
    - URL de la imagen
    - Descripción original sin estructurar
    """
    # Identificar variantes para precios y disponibilidad de stock
    variants = product.get("variants", [])
    
    # Tomamos el precio de la primera variante como representativo o el menor
    prices = [float(v.get("price", 0)) for v in variants if v.get("price")]
    compare_prices = [float(v.get("compare_at_price", 0)) for v in variants if v.get("compare_at_price")]
    
    current_price = min(prices) if prices else 0.0
    original_price = min(compare_prices) if compare_prices else current_price
    
    # Calcular porcentaje de descuento
    discount_percentage = 0.0
    if original_price > current_price and original_price > 0:
        discount_percentage = round(((original_price - current_price) / original_price) * 100, 2)
        
    # Verificar disponibilidad (si alguna variante tiene inventario disponible)
    # Shopify API retorna 'available' como booleano en cada variante
    is_available = any(v.get("available", False) for v in variants)
    stock_status = "Disponible" if is_available else "Agotado"
    
    # URL de la imagen principal
    images = product.get("images", [])
    image_url = images[0].get("src", "") if images else ""
    
    # Descripción
    raw_body = product.get("body_html", "")
    description = clean_html_tags(raw_body)
    
    return {
        "external_id": str(product.get("id")),
        "title": product.get("title", ""),
        "handle": product.get("handle", ""),
        "current_price": current_price,
        "original_price": original_price,
        "discount_percentage": discount_percentage,
        "stock_status": stock_status,
        "image_url": image_url,
        "description": description,
        "created_at": product.get("created_at"),
        "published_at": product.get("published_at")
    }

def parse_products_batch(products_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parsea una lista de productos en formato JSON."""
    parsed_products = []
    for prod in products_list:
        try:
            parsed_products.append(parse_product_json(prod))
        except Exception as e:
            # Imprimir o registrar error de parsing sin detener el pipeline entero
            print(f"Error parsing product {prod.get('id', 'Unknown')}: {e}")
    return parsed_products
