from typing import List, Dict, Any
from database.connection import get_connection

def upsert_productos(productos: List[Dict[str, Any]]) -> None:
    """
    Inserta una lista de productos en la base de datos de PostgreSQL.
    Si el producto ya existe (identificado por su external_id),
    se actualizan sus datos y la fecha del scraper.
    """
    if not productos:
        return

    query = """
        INSERT INTO productos (
            external_id, title, handle, current_price, original_price,
            discount_percentage, stock_status, image_url, description,
            created_at, published_at, updated_at, last_scraped_at
        ) VALUES (
            %(external_id)s, %(title)s, %(handle)s, %(current_price)s, %(original_price)s,
            %(discount_percentage)s, %(stock_status)s, %(image_url)s, %(description)s,
            %(created_at)s, %(published_at)s, %(updated_at)s, CURRENT_TIMESTAMP
        )
        ON CONFLICT (external_id) DO UPDATE SET
            title = EXCLUDED.title,
            handle = EXCLUDED.handle,
            current_price = EXCLUDED.current_price,
            original_price = EXCLUDED.original_price,
            discount_percentage = EXCLUDED.discount_percentage,
            stock_status = EXCLUDED.stock_status,
            image_url = EXCLUDED.image_url,
            description = EXCLUDED.description,
            published_at = EXCLUDED.published_at,
            updated_at = EXCLUDED.updated_at,
            last_scraped_at = CURRENT_TIMESTAMP;
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.executemany(query, productos)
        conn.commit()
        print(f"Upsert exitoso: {len(productos)} productos sincronizados en la base de datos.")
    except Exception as e:
        conn.rollback()
        print(f"Error al guardar los productos en la base de datos: {e}")
        raise e
    finally:
        conn.close()

def get_productos_sin_insight(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Recupera una lista de productos de la base de datos que aún no
    tienen metadatos semánticos en insights_ia, listos para enviar al LLM.
    """
    query = """
        SELECT p.id, p.external_id, p.title, p.description
        FROM productos p
        LEFT JOIN insights_ia i ON p.external_id = i.external_id
        WHERE i.external_id IS NULL
        LIMIT %s;
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (limit,))
            return cur.fetchall()
    except Exception as e:
        print(f"Error al consultar productos sin insight: {e}")
        return []
    finally:
        conn.close()
