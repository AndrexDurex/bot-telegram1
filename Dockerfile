# PokeBot — Docker para Render.com
FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PORT=10000

WORKDIR /app

# Dependencias del sistema (necesarias para sentence-transformers/torch)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código (las credenciales se inyectan via Render Environment Variables)
COPY . .

# Render usa el puerto 10000 por defecto para Web Services
EXPOSE 10000

# Arrancar el servidor web
CMD ["python", "app.py"]
