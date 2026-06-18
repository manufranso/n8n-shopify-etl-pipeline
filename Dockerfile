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
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente necesario del proyecto al contenedor
COPY config/ ./config/
COPY database/ ./database/
COPY scraping/ ./scraping/

# Configurar variables de entorno por defecto para apuntar al PostgreSQL interno del Docker Compose
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_NAME=OH_YEAH_DB
ENV DB_USER=OH_YEAH_USER
ENV DB_PASSWORD=OH_YEAH_PASSWORD
ENV PYTHONPATH=/app

# Exponer el puerto de la API de Flask
EXPOSE 5000

# Comando para ejecutar (levanta la API Flask)
CMD ["python", "scraping/app.py"]
