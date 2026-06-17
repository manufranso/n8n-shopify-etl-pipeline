import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env si existiera
load_dotenv()

# Configuración de base de datos con valores por defecto (puerto 5434 configurado en Docker Compose)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5434")
DB_NAME = os.getenv("DB_NAME", "auditafin")
DB_USER = os.getenv("DB_USER", "admin_audit")
DB_PASSWORD = os.getenv("DB_PASSWORD", "super_secret_password_123")

def get_connection():
    """Establece conexión con la base de datos PostgreSQL local."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def bulk_insert_dimensions(df_prov, df_dept):
    """Inserta en lote las dimensiones estáticas de proveedores y departamentos."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Insertar departamentos (dim_departamentos)
        dept_values = [
            (row["id_departamento"], row["nombre_dept"], row["presupuesto_anual"])
            for _, row in df_dept.iterrows()
        ]
        insert_dept_query = """
            INSERT INTO dim_departamentos (id_departamento, nombre_dept, presupuesto_anual)
            VALUES %s
            ON CONFLICT (id_departamento) DO UPDATE 
            SET nombre_dept = EXCLUDED.nombre_dept, 
                presupuesto_anual = EXCLUDED.presupuesto_anual;
        """
        execute_values(cursor, insert_dept_query, dept_values)
        
        # 2. Insertar proveedores (dim_proveedores)
        prov_values = [
            (row["id_proveedor"], row["nombre"], row["sector"], row["pais"])
            for _, row in df_prov.iterrows()
        ]
        insert_prov_query = """
            INSERT INTO dim_proveedores (id_proveedor, nombre, sector, pais)
            VALUES %s
            ON CONFLICT (id_proveedor) DO UPDATE 
            SET nombre = EXCLUDED.nombre, 
                sector = EXCLUDED.sector, 
                pais = EXCLUDED.pais;
        """
        execute_values(cursor, insert_prov_query, prov_values)
        
        conn.commit()
        print(f"Dimensiones pobladas exitosamente ({len(dept_values)} departamentos, {len(prov_values)} proveedores).")
    except Exception as e:
        conn.rollback()
        print(f"Error al poblar dimensiones: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

def bulk_insert_gastos(df_gastos):
    """Inserta en lote los registros transaccionales en fact_gastos."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        gastos_values = [
            (row["id_factura"], row["fecha"], row["id_proveedor"], row["id_departamento"], row["importe"], row["concepto"])
            for _, row in df_gastos.iterrows()
        ]
        insert_gastos_query = """
            INSERT INTO fact_gastos (id_factura, fecha, id_proveedor, id_departamento, importe, concepto)
            VALUES %s
            ON CONFLICT (id_factura) DO NOTHING;
        """
        execute_values(cursor, insert_gastos_query, gastos_values)
        conn.commit()
        print(f"Hecho de gastos poblado exitosamente ({len(gastos_values)} facturas insertadas).")
    except Exception as e:
        conn.rollback()
        print(f"Error al poblar hecho de gastos: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()
        
def bulk_insert_alertas(alertas):
    """Inserta en lote las alertas de auditoría detectadas por el microservicio en fact_alertas."""
    if not alertas:
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Se asume que 'alertas' viene como una lista de diccionarios desde la Lambda
        alertas_values = [
            (a["id_alerta"], a["id_factura"], a["tipo_anomalia"], a["nivel_riesgo"])
            for a in alertas
        ]
        insert_alertas_query = """
            INSERT INTO fact_alertas (id_alerta, id_factura, tipo_anomalia, nivel_riesgo)
            VALUES %s
            ON CONFLICT (id_alerta) DO NOTHING;
        """
        execute_values(cursor, insert_alertas_query, alertas_values)
        conn.commit()
        print(f"Hecho de alertas poblado exitosamente ({len(alertas_values)} alertas insertadas).")
    except Exception as e:
        conn.rollback()
        print(f"Error al poblar alertas: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()
