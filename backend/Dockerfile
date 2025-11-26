# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
# instalar git ya que clonamos repos dentro del contenedor
RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
