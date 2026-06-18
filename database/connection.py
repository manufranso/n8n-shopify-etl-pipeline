import psycopg2
from psycopg2.extras import RealDictCursor
from config import settings

def get_connection():
    """Establece y retorna una conexión directa a la base de datos PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error crítico al conectar a PostgreSQL: {e}")
        raise e

def init_db():
    """Inicializa la base de datos ejecutando el script schema.sql."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Leer el archivo schema.sql
            with open("database/schema.sql", "r", encoding="utf-8") as f:
                schema_sql = f.read()
            # Ejecutar DDL
            cur.execute(schema_sql)
            conn.commit()
            print("Base de datos inicializada correctamente (tablas e índices creados).")
    except Exception as e:
        conn.rollback()
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Test de conexión e inicialización
    # Nota: Requiere que PostgreSQL esté levantado y con las credenciales correctas en el entorno.
    try:
        init_db()
    except Exception:
        pass
