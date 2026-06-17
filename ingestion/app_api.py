import os
import sys
from flask import Flask, jsonify, request

# Asegurar importaciones relativas añadiendo la raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.generator import generate_static_dimensions, generate_facturas
from ingestion.db_loader import bulk_insert_dimensions, bulk_insert_gastos
from ingestion.audit_process import audit_and_save

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    """Ruta para comprobación de estado de la API."""
    return jsonify({"status": "healthy", "service": "AuditaFin Local API Gateway"}), 200

@app.route("/generate", methods=["POST"])
def generate():
    """
    Ruta para la generación diaria incremental de facturas.
    Inserta las facturas resultantes en PostgreSQL de forma automática.
    """
    try:
        # Generar las dimensiones de forma determinista para consistencia
        df_prov, df_dept = generate_static_dimensions(num_proveedores=35)
        
        # Generar lote incremental del día
        df_gastos = generate_facturas(df_prov, mode="incremental")
        total_generado = len(df_gastos)
        
        # Insertar en base de datos
        bulk_insert_dimensions(df_prov, df_dept)
        bulk_insert_gastos(df_gastos)
        
        # Devolver las facturas generadas a n8n en el JSON de respuesta
        return jsonify({
            "status": "success",
            "message": f"Se han generado e insertado {total_generado} facturas exitosamente.",
            "total_generado": total_generado,
            "gastos": df_gastos.to_dict(orient="records")
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/audit", methods=["POST"])
def audit():
    """
    Ruta para ejecutar el proceso completo de auditoría y detección de alertas.
    Conecta con la AWS Lambda local e inyecta las alertas de riesgo en PostgreSQL.
    """
    try:
        # Ejecuta la lógica de integración de auditoría
        audit_and_save()
        return jsonify({
            "status": "success",
            "message": "Auditoría ejecutada con éxito. Nuevas alertas registradas en fact_alertas."
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Escucha en todas las interfaces en el puerto 5000 para permitir peticiones desde el Docker de n8n
    app.run(host="0.0.0.0", port=5000, debug=False)
