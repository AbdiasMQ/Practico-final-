FROM python:3.11-slim

# Ver logs en tiempo real
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /systemventas

# Instalar dependencias del sistema necesarias para pycairo, psycopg2 y pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY systemventas/ .

# Puerto que expondrá Django
EXPOSE 8000

# Comando por defecto para correr el proyecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
