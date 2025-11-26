# backend/dockerfile_generator.py
import os, textwrap

def ensure_dockerfile(path, ptype):
    """
    Si repo no trae Dockerfile, genera uno apropiado según tipo.
    """
    dockerfile_path = os.path.join(path, "Dockerfile")
    if os.path.exists(dockerfile_path):
        return False  # ya existe
    if ptype == "node":
        content = textwrap.dedent("""\
            FROM node:18 AS build
            WORKDIR /app
            COPY package*.json ./
            RUN npm install --legacy-peer-deps
            COPY . .
            RUN npm run build || true
            FROM nginx:alpine
            COPY --from=build /app/dist /usr/share/nginx/html
            EXPOSE 80
            CMD ["nginx", "-g", "daemon off;"]
        """)
    elif ptype == "flask" or ptype == "python":
        content = textwrap.dedent("""\
            FROM python:3.11-slim
            WORKDIR /app
            COPY requirements.txt .
            RUN pip install --no-cache-dir -r requirements.txt
            COPY . .
            EXPOSE 80
            CMD ["python", "app.py"]
        """)
    else:  # static
        content = textwrap.dedent("""\
            FROM nginx:alpine
            COPY . /usr/share/nginx/html
            EXPOSE 80
            CMD ["nginx", "-g", "daemon off;"]
        """)
    with open(dockerfile_path, "w", encoding="utf-8") as f:
        f.write(content)
    return True
