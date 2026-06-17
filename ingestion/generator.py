import random
import uuid
import argparse
from datetime import datetime, timedelta
import json
from faker import Faker
import pandas as pd

# Inicialización de Faker en español de España
fake = Faker('es_ES')

# Estructura fija de Departamentos y Presupuestos
DEPARTAMENTOS = [
    {"id_departamento": "DEP_IT", "nombre_dept": "Tecnología de la Información", "presupuesto_anual": 750000.00},
    {"id_departamento": "DEP_HR", "nombre_dept": "Recursos Humanos", "presupuesto_anual": 200000.00},
    {"id_departamento": "DEP_MKT", "nombre_dept": "Marketing y Ventas", "presupuesto_anual": 450000.00},
    {"id_departamento": "DEP_OPS", "nombre_dept": "Operaciones y Logística", "presupuesto_anual": 1200000.00},
    {"id_departamento": "DEP_LEG", "nombre_dept": "Legal y Cumplimiento", "presupuesto_anual": 150000.00},
    {"id_departamento": "DEP_FIN", "nombre_dept": "Finanzas y Administración", "presupuesto_anual": 100000.00}
]

# Sectores y países de proveedores
SECTORES = ["Tecnología", "Consultoría", "Logística", "Suministros Oficina", "Marketing", "Servicios Legales", "Seguridad", "Mantenimiento"]
PAISES = ["España", "Portugal", "Francia", "Alemania", "Italia", "Reino Unido", "Estados Unidos"]

def generate_static_dimensions(num_proveedores=30):
    """
    Genera dimensiones estáticas: Proveedores y Departamentos.
    Útil para poblar la base de datos inicialmente.
    """
    # 1. Departamentos
    df_dept = pd.DataFrame(DEPARTAMENTOS)
    
    # 2. Proveedores
    proveedores = []
    # Fijar semilla para reproducibilidad de dimensiones básicas
    Faker.seed(42)
    random.seed(42)
    
    for i in range(1, num_proveedores + 1):
        proveedores.append({
            "id_proveedor": f"PROV_{i:04d}",
            "nombre": fake.company(),
            "sector": random.choice(SECTORES),
            "pais": random.choice(PAISES)
        })
    df_prov = pd.DataFrame(proveedores)
    
    # Restaurar semillas aleatorias para ejecuciones dinámicas posteriores
    Faker.seed(None)
    random.seed(None)
    
    return df_prov, df_dept

def generate_concept(sector, importe):
    """Genera un concepto de factura coherente con el sector y el importe."""
    conceptos = {
        "Tecnología": ["Licencias de Software Cloud", "Mantenimiento Servidores", "Soporte de Sistemas E2E", "Hardware Portátiles", "Hosting Web mensual"],
        "Consultoría": ["Auditoría de Procesos", "Consultoría Estratégica Trimestral", "Asesoría Financiera", "Servicio Formación Ejecutiva"],
        "Logística": ["Servicios de Transporte Nacional", "Almacenamiento y Picking", "Distribución Última Milla", "Fletes Internacionales"],
        "Suministros Oficina": ["Material de Oficina general", "Mobiliario ergonómico", "Consumibles y Papelería", "Cafetería y Catering"],
        "Marketing": ["Campaña Publicidad Digital", "Gestión RRSS mensual", "Diseño Marca Corporativa", "Patrocinio Evento Anual"],
        "Servicios Legales": ["Asesoría Legal laboral", "Tasas de Registro y Patentes", "Defensa Jurídica mensual", "Servicio Notaría"],
        "Seguridad": ["Servicio de Vigilancia mensual", "Sistemas Alarma Instalación", "Control Acceso Biométrico"],
        "Mantenimiento": ["Limpieza Oficinas Centrales", "Reparación Climatización", "Mantenimiento Ascensores", "Consumo Eléctrico Centralizado"]
    }
    temas = conceptos.get(sector, ["Servicio General", "Gastos Operativos", "Factura de Compra"])
    tema = random.choice(temas)
    return f"{tema} - Ref {random.randint(1000, 9999)}"

def inject_benford_anomaly():
    """
    Genera un importe anómalo que rompe la Ley de Benford de forma intencionada.
    Por ejemplo, forzando que empiece por los dígitos 9 o 8 con importes altos y muy específicos
    o números redondos artificiales (ej. 9900.00, 8900.00).
    """
    digitos_sospechosos = [7, 8, 9]
    primer_digito = random.choice(digitos_sospechosos)
    restante = random.choice([0, 50, 90, 99])
    millares = random.randint(1, 9)
    importe = (primer_digito * 1000) + (millares * 100) + restante
    return float(importe)

def generate_facturas(df_prov, mode="incremental", date_str=None, pct_anomalas=0.08):
    """
    Genera facturas de transacciones (fact_gastos) con inyección controlada de anomalías.
    Modos:
      - 'historical': Genera el histórico homogéneo de los últimos 2.5 años (aprox. 1500-2500 facturas).
      - 'incremental': Genera de 20 a 50 facturas estrictamente del día en curso (o de la fecha proporcionada).
    """
    facturas = []
    
    if mode == "historical":
        # Generar rango de fechas desde hace 900 días hasta ayer
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=900)
        num_facturas = random.randint(1500, 2200)
        
        fechas = [fake.date_between_dates(date_start=start_date, date_end=end_date) for _ in range(num_facturas)]
    else:
        # Modo incremental (Lote diario)
        if date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            target_date = datetime.now().date()
        
        num_facturas = random.randint(20, 50)
        fechas = [target_date] * num_facturas
    
    # Lista de proveedores válidos
    lista_provs = df_prov.to_dict('records')
    
    for fecha in fechas:
        # Selección de departamento y proveedor aleatorios
        prov = random.choice(lista_provs)
        dept = random.choice(DEPARTAMENTOS)
        
        # Simulación de importes coherentes por sector del proveedor
        if prov["sector"] in ["Tecnología", "Consultoría", "Logística"]:
            importe = round(random.uniform(2500.00, 15000.00), 2)
        elif prov["sector"] in ["Suministros Oficina", "Mantenimiento"]:
            importe = round(random.uniform(50.00, 950.00), 2)
        else:
            importe = round(random.uniform(500.00, 5000.00), 2)
        
        # Decisión de inyección de anomalías
        es_anomala_benford = random.random() < pct_anomalas
        if es_anomala_benford:
            importe = inject_benford_anomaly()
            
        concepto = generate_concept(prov["sector"], importe)
        
        facturas.append({
            "id_factura": f"FAC_{uuid.uuid4().hex[:8].upper()}",
            "fecha": fecha.strftime("%Y-%m-%d") if isinstance(fecha, datetime) or hasattr(fecha, 'strftime') else str(fecha),
            "id_proveedor": prov["id_proveedor"],
            "id_departamento": dept["id_departamento"],
            "importe": importe,
            "concepto": concepto
        })
        
    # Inyección de Facturas Duplicadas (Anomalía de integridad contable)
    # Selecciona un subconjunto del lote actual y lo duplica exactamente, cambiando únicamente el ID de Factura (o manteniéndolo en base a la validación que queramos hacer)
    num_duplicados = int(len(facturas) * (pct_anomalas / 2))
    if num_duplicados > 0:
        duplicados = random.sample(facturas, num_duplicados)
        for original in duplicados:
            duplicada = original.copy()
            # Anomalía tipo 1: Mismo importe, mismo proveedor, misma fecha, distinto ID factura
            duplicada["id_factura"] = f"FAC_{uuid.uuid4().hex[:8].upper()}"
            duplicada["concepto"] = f"[DPL] {original['concepto']}" # Prefijo interno para control visual rápido
            facturas.append(duplicada)
            
    df_facturas = pd.DataFrame(facturas)
    return df_facturas

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de Datos de Facturación Corporativa (Faker)")
    parser.add_argument("--mode", type=str, choices=["historical", "incremental"], default="incremental",
                        help="Modo de generación: 'historical' (histórico masivo) o 'incremental' (lote diario)")
    parser.add_argument("--date", type=str, default=None,
                        help="Fecha específica para el modo incremental (YYYY-MM-DD). Por defecto usa hoy.")
    parser.add_argument("--output", type=str, choices=["json", "csv"], default="json",
                        help="Formato de salida de los datos generados")
    parser.add_argument("--db", action="store_true",
                        help="Persistir directamente los datos generados en la base de datos local de PostgreSQL")
    args = parser.parse_args()
    
    # Generar dimensiones básicas
    df_prov, df_dept = generate_static_dimensions(num_proveedores=35)
    
    # Generar transacciones de gastos
    df_gastos = generate_facturas(df_prov, mode=args.mode, date_str=args.date)
    
    # Persistencia directa opcional (Ej: Setup inicial del histórico)
    if args.db:
        from db_loader import bulk_insert_dimensions, bulk_insert_gastos
        print("Iniciando persistencia directa en PostgreSQL local (puerto 5434)...")
        try:
            bulk_insert_dimensions(df_prov, df_dept)
            bulk_insert_gastos(df_gastos)
            print("Persistencia finalizada con éxito.")
        except Exception as e:
            print(f"Error crítico en persistencia: {e}")
    
    # Exportación
    if args.output == "json":
        # Formatear la salida como JSON estructurado para el orquestador n8n
        salida = {
            "proveedores": df_prov.to_dict(orient="records"),
            "departamentos": df_dept.to_dict(orient="records"),
            "gastos": df_gastos.to_dict(orient="records")
        }
        print(json.dumps(salida, ensure_ascii=False, indent=2))
    else:
        # Guardar en CSV local en la carpeta dedicada 'data' para inspección o debugging
        os.makedirs("data", exist_ok=True)
        df_prov.to_csv("data/dim_proveedores.csv", index=False)
        df_dept.to_csv("data/dim_departamentos.csv", index=False)
        df_gastos.to_csv("data/fact_gastos.csv", index=False)
        print(f"Archivos exportados exitosamente en CSV en la carpeta 'data/' en modo: {args.mode}")
