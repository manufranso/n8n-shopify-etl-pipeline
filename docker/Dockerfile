# Usar una imagen oficial y ligera de Python
FROM python:3.11-slim

# Definir directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias necesarias del sistema (para psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependencias
COPY ingestion/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente necesario del proyecto al contenedor
COPY ingestion/ ./ingestion/
COPY lambda/ ./lambda/

# Configurar variables de entorno por defecto para apuntar al PostgreSQL interno del Docker Compose
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_NAME=auditafin
ENV DB_USER=admin_audit
ENV DB_PASSWORD=super_secret_password_123

# Exponer el puerto de la API de Flask
EXPOSE 5000

# Comando para ejecutar la API
CMD ["python", "ingestion/app_api.py"]
