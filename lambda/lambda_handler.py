import json
import math
import uuid
from datetime import datetime

def get_first_digit(num):
    """Devuelve el primer dígito significativo de un número."""
    try:
        val = str(abs(num)).replace('.', '').lstrip('0')
        if val:
            return int(val[0])
    except (ValueError, TypeError):
        pass
    return None

def analyze_benford(importe):
    """
    Evalúa si un importe viola la Ley de Benford de forma sospechosa.
    En la Ley de Benford, los dígitos 1, 2 y 3 representan el ~60% de los casos.
    Los dígitos 7, 8 y 9 ocurren con mucha menor frecuencia (~4.6% a ~5.8% cada uno).
    Además, los importes redondos elevados (ej. que terminen en .00 o 99.00) incrementan el riesgo.
    """
    first_digit = get_first_digit(importe)
    if not first_digit:
        return None, "BAJO"

    # Si el primer dígito es alto (7, 8, 9) e importe > 1000, hay mayor probabilidad de revisión.
    # Si encima termina en .00 o 99.00 de forma redonda, incrementamos sospecha a alto.
    es_redondo = (importe % 100 == 0) or (str(importe).endswith('.00') or str(importe).endswith('99'))
    
    if first_digit in [7, 8, 9] and importe >= 5000:
        if es_redondo:
            return "Benford - Primer dígito alto y redondo", "ALTO"
        return "Benford - Primer dígito alto", "MEDIO"
    
    return None, "BAJO"

def analyze_duplicates(gastos):
    """
    Detecta facturas potencialmente duplicadas dentro de un mismo lote.
    Criterio: Mismo proveedor, mismo importe y misma fecha, pero con IDs de factura diferentes.
    """
    alertas = []
    # Usamos un diccionario agrupando por clave única: (fecha, id_proveedor, importe)
    vistos = {}
    
    for i, g in enumerate(gastos):
        key = (g.get("fecha"), g.get("id_proveedor"), float(g.get("importe", 0)))
        if key in vistos:
            # Marcamos tanto el actual como el que vimos antes (si no ha sido marcado antes)
            original_idx = vistos[key]
            orig_g = gastos[original_idx]
            
            # Crear alerta para el duplicado actual
            alertas.append({
                "id_alerta": f"ALE_{uuid.uuid4().hex[:8].upper()}",
                "id_factura": g["id_factura"],
                "tipo_anomalia": "Integridad - Factura Duplicada",
                "nivel_riesgo": "CRÍTICO"
            })
            
            # Si el original no tiene alerta de duplicado ya creada, se podría reportar,
            # pero reportar el duplicado actual ya es suficiente para el analista.
        else:
            vistos[key] = i
            
    return alertas

def lambda_handler(event, context):
    """
    AWS Lambda Handler para auditoría financiera ySpend Analytics.
    Recibe un lote de facturas (event) por HTTP API Gateway, analiza duplicados, 
    evalúa la Ley de Benford por registro y devuelve una estructura enriquecida.
    """
    # Manejar si el payload viene en string (API Gateway)
    if isinstance(event, str):
        try:
            body = json.loads(event)
        except Exception:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Formato de payload no válido (JSON string esperado)"})
            }
    elif isinstance(event, dict) and "body" in event:
        # Petición HTTP desde API Gateway (Proxy Integration)
        try:
            body = json.loads(event["body"])
        except Exception:
            body = event["body"]
    else:
        body = event

    # Extraer la lista de facturas
    gastos = body.get("gastos", [])
    if not gastos:
        return {
            "statusCode": 200,
            "body": json.dumps({"gastos_procesados": 0, "alertas": []}, ensure_ascii=False)
        }

    alertas_generadas = []
    
    # 1. Detección de duplicados en el lote
    alertas_duplicados = analyze_duplicates(gastos)
    alertas_generadas.extend(alertas_duplicados)
    
    # IDs de facturas que ya tienen alerta de duplicado para evitar solapar alertas de menor nivel
    facturas_con_duplicado = {a["id_factura"] for a in alertas_duplicados}

    # 2. Análisis individual por factura (Benford y límites presupuestarios)
    for g in gastos:
        id_factura = g.get("id_factura")
        importe = float(g.get("importe", 0))
        
        # Omitir Benford si ya es crítico por duplicado
        if id_factura in facturas_con_duplicado:
            continue
            
        tipo_anomalia, nivel_riesgo = analyze_benford(importe)
        
        if tipo_anomalia:
            alertas_generadas.append({
                "id_alerta": f"ALE_{uuid.uuid4().hex[:8].upper()}",
                "id_factura": id_factura,
                "tipo_anomalia": tipo_anomalia,
                "nivel_riesgo": nivel_riesgo
            })

    # Respuesta estructurada de vuelta al orquestador n8n
    response_body = {
        "status": "success",
        "timestamp_auditoria": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "total_procesado": len(gastos),
        "total_alertas": len(alertas_generadas),
        "alertas": alertas_generadas
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(response_body, ensure_ascii=False)
    }
