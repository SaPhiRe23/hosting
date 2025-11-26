Plataforma de Hosting Autogestionado (Docker + Caddy + Flask + React)

Este repositorio implementa una plataforma de hosting local donde cualquier usuario puede:

- Registrar una cuenta  
- Seleccionar una plantilla (Static, React, Flask, etc.)  
- Proporcionar un repositorio Git  
- Generar automáticamente:
  - Dockerfile  
  - Imagen Docker  
  - Contenedor ejecutándose  
  - Subdominio accesible vía Caddy  

Todo desde una interfaz web.

---

## Tecnologías utilizadas

| Componente | Descripción |
|-----------|-------------|
| **Flask** | Backend API encargado de clonar repos, generar Dockerfiles, construir imágenes y ejecutar contenedores. |
| **Docker** | Para construir imágenes y crear contenedores desde el backend. |
| **Caddy** | Proxy reverso que asigna dinámicamente subdominios a cada proyecto. |
| **React + Vite** | Panel web donde el usuario registra datos y genera proyectos. |
| **Git** | Para clonar repositorios proporcionados por el usuario. |

---

## ▶️ Cómo ejecutar el proyecto

1. Clona el repositorio:

```
git clone <URL_DEL_REPO>
```
Te diriges a esta dirección en caso de no estar:
```
cd hosting
```

Construye todos los servicios:
```
docker-compose build
```

Inicia la plataforma:
```
docker-compose up
```
Abre el panel en el navegador:

http://localhost:8080

## 🖥 Uso del sistema
1. Registrarse / Iniciar sesión
   
Introduce:

   - Usuario y Contraseña

El backend registra automáticamente si no existe.

2. Elegir una plantilla
   
- El panel incluye templates como:

  - React
  - Static HTML
  - Python Flask
    
Cada plantilla incluye un repositorio de ejemplo.

3. Crear un proyecto
   
Debe llenarse:

- Usuario

- Contraseña

- Nombre del proyecto

- URL del repositorio Git (El cual se copia automaticamente al presionar el boton que dice "Usar plantilla" que se encuentra junto a cada plantilla disponible)

