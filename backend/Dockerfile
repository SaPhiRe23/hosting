FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para pip y git
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
 && apt-get clean

# Copiar requirements primero
COPY requirements.txt .

# Instalar dependencias de Python sin actualizar pip
RUN pip install --no-cache-dir --upgrade setuptools wheel \
 && pip uninstall -y docker docker-py || true \
 && pip install --no-cache-dir docker requests requests-unixsocket

# Instalar el resto (sin versiones problemáticas)
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
