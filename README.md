# AuditaFin - Pipeline de Auditoría Financiera y Spend Analytics

Este repositorio contiene la arquitectura, código y configuración del proyecto **AuditaFin**, una solución End-to-End (E2E) para la ingesta, detección de anomalías contables y visualización de gastos corporativos.

## 📊 Arquitectura del Flujo de Datos

1. **Ingesta:** Script en Python (`ingestion/generator.py`) parametrizado para cargas históricas o incrementales simuladas con la librería `Faker`.
2. **Orquestación:** n8n en Docker ejecuta peticiones REST dirigidas a un microservicio local en Flask, eliminando la necesidad de scripts directos en n8n.
3. **Validación:** AWS Lambda (simulada localmente y desplegable de forma serverless) audita cada transacción detectando duplicados o anomalías según la Ley de Benford.
4. **Persistencia:** Base de datos PostgreSQL en contenedor Docker local estructurada con un modelo dimensional en estrella (Star Schema) en el puerto `5434`.
5. **Visualización:** Conexión directa y local de Power BI Desktop a vistas analíticas optimizadas de PostgreSQL (`v_tableau_master_spend`, etc.) para refrescos instantáneos.

## 📁 Estructura del Proyecto

* `data/`: Almacenamiento local de los CSVs históricos y de control de proveedores, departamentos y transacciones.
* `docker/`: Configuración del Docker Compose para levantar la base de datos PostgreSQL y el microservicio API de Flask de forma orquestada, junto con el script de inicialización del esquema `init_db.sql`.
* `ingestion/`: Módulos generadores de transacciones en Python, API de Flask (`app_api.py`), conector a base de datos (`db_loader.py`) y script de control de auditoría (`audit_process.py`).
* `lambda/`: Código del servicio serverless de auditoría y reglas de riesgo (`lambda_handler.py`).
* `n8n/`: Flujos de automatización exportados para su importación rápida en n8n.
* `.gemini/`: Configuración interna del IDE Antigravity (excluido en `.gitignore`).
