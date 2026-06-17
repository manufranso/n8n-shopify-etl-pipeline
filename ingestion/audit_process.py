import sys
import os
import json
import pandas as pd

# Añadir directorios de ingestion y lambda al path del sistema para importaciones relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lambda"))

from ingestion.db_loader import get_connection, bulk_insert_alertas
# Importación dinámica del módulo 'lambda' para evitar el conflicto con la palabra clave reservada de Python
lambda_module = __import__("lambda.lambda_handler", fromlist=["lambda_handler"])
lambda_handler = lambda_module.lambda_handler

def fetch_unaudited_expenses():
    """
    Obtiene todas las facturas de fact_gastos que aún no han sido auditadas.
    Criterio: Aquellas cuyo id_factura no existe en la tabla fact_alertas
    ni se han procesado anteriormente como exentas.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Consulta SQL para traer gastos sin alertas asociadas
    query = """
        SELECT g.id_factura, g.fecha, g.id_proveedor, g.id_departamento, g.importe, g.concepto
        FROM fact_gastos g
        LEFT JOIN fact_alertas a ON g.id_factura = a.id_factura
        WHERE a.id_factura IS NULL;
    """
    
    try:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # Convertir a una lista de diccionarios para que sea compatible con el handler de la Lambda
        expenses = []
        for row in rows:
            # PostgreSQL devuelve decimal.Decimal para tipos NUMERIC, lo convertimos a float para JSON
            item = dict(zip(columns, row))
            item["importe"] = float(item["importe"])
            item["fecha"] = str(item["fecha"])
            expenses.append(item)
            
        return expenses
    except Exception as e:
        print(f"Error al extraer gastos sin auditar: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

def audit_and_save():
    """
    Punto de entrada para el pipeline de auditoría:
      1. Extrae facturas no auditadas de PostgreSQL.
      2. Invoca localmente a la lógica de validación de AWS Lambda.
      3. Persiste las alertas analizadas de vuelta en fact_alertas en PostgreSQL.
    """
    print("Iniciando proceso de auditoría de gastos...")
    
    # 1. Obtener gastos pendientes
    expenses = fetch_unaudited_expenses()
    total_pendientes = len(expenses)
    
    if total_pendientes == 0:
        print("No hay nuevas facturas pendientes de auditar en PostgreSQL.")
        return
        
    print(f"Detectadas {total_pendientes} facturas sin auditar en la base de datos.")
    
    # 2. Invocar la Lambda localmente pasándole el lote de facturas
    payload = {"gastos": expenses}
    
    try:
        # Ejecutar auditoría serverless
        response = lambda_handler(payload, None)
        
        if response["statusCode"] != 200:
            print(f"Error en la ejecución de la Lambda: {response['body']}")
            return
            
        result = json.loads(response["body"])
        alertas = result.get("alertas", [])
        total_alertas = result.get("total_alertas", 0)
        
        print(f"Auditoría finalizada. Se detectaron {total_alertas} anomalías en este lote.")
        
        # 3. Guardar las alertas resultantes en PostgreSQL
        if total_alertas > 0:
            bulk_insert_alertas(alertas)
            print("Alertas registradas exitosamente en la tabla fact_alertas.")
        else:
            print("Lote limpio. No se inyectaron alertas de riesgo.")
            
    except Exception as e:
        print(f"Error crítico en el proceso de integración de auditoría: {e}")

if __name__ == "__main__":
    audit_and_save()
