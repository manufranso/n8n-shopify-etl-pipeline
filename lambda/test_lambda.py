import unittest
import json
from lambda_handler import lambda_handler

class TestAuditLambda(unittest.TestCase):

    def test_benford_detection(self):
        """Prueba que un importe con primer dígito alto y redondo sea detectado como anomalía Benford."""
        # FAC_1 con 9900.00 (Anomalía Benford - Alta sospecha)
        # FAC_2 con 250.00 (Normal - Baja sospecha)
        payload = {
            "gastos": [
                {"id_factura": "FAC_1", "fecha": "2026-06-17", "id_proveedor": "PROV_1", "id_departamento": "DEP_IT", "importe": 9900.00, "concepto": "Software"},
                {"id_factura": "FAC_2", "fecha": "2026-06-17", "id_proveedor": "PROV_2", "id_departamento": "DEP_HR", "importe": 250.00, "concepto": "Papel"}
            ]
        }
        
        response = lambda_handler(payload, None)
        self.assertEqual(response["statusCode"], 200)
        
        body = json.loads(response["body"])
        self.assertEqual(body["total_alertas"], 1)
        self.assertEqual(body["alertas"][0]["id_factura"], "FAC_1")
        self.assertEqual(body["alertas"][0]["nivel_riesgo"], "ALTO")

    def test_duplicate_detection(self):
        """Prueba que dos facturas idénticas en fecha, proveedor e importe se marquen como duplicadas."""
        payload = {
            "gastos": [
                {"id_factura": "FAC_A", "fecha": "2026-06-17", "id_proveedor": "PROV_1", "id_departamento": "DEP_IT", "importe": 500.00, "concepto": "Consultoría"},
                {"id_factura": "FAC_B", "fecha": "2026-06-17", "id_proveedor": "PROV_1", "id_departamento": "DEP_OPS", "importe": 500.00, "concepto": "Consultoría duplicada"}
            ]
        }
        
        response = lambda_handler(payload, None)
        body = json.loads(response["body"])
        
        # Debe marcar al menos una como duplicado crítico
        self.assertEqual(body["total_alertas"], 1)
        self.assertEqual(body["alertas"][0]["nivel_riesgo"], "CRÍTICO")
        self.assertIn("Factura Duplicada", body["alertas"][0]["tipo_anomalia"])

if __name__ == "__main__":
    unittest.main()
