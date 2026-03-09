# BioAgent — Docker Space para Hugging Face
FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

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

# Copiar todo el código (las credenciales se inyectan via HF Secrets, no aquí)
COPY . .

# Puerto no requerido para bots de polling, pero HF lo espera
EXPOSE 7860

# Arrancar el bot
CMD ["python", "main.py"]
