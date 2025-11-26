import docker
import os
import time

NETWORK_NAME = "proxy_net"
container_activity = {}

# 🔥 IGNORAR por completo variables heredadas que dañan docker-py
for var in ["DOCKER_HOST", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH"]:
    if var in os.environ:
        print(f"[WARN] Eliminando variable heredada: {var}={os.environ[var]}")
        del os.environ[var]

DOCKER_SOCKET = "/var/run/docker.sock"

if not os.path.exists(DOCKER_SOCKET):
    raise RuntimeError(
        f"NO EXISTE {DOCKER_SOCKET}. Docker Desktop no está compartiendo el socket."
    )

print("[INFO] Creando cliente Docker usando APIClient (bajo nivel)...")

# 🔥 ESTA ES LA LÍNEA CRÍTICA QUE SOLUCIONA ESTE INFIERNO:
client = docker.APIClient(
    base_url="unix:///var/run/docker.sock",
    version="auto"      # importante
)

# 🔥 docker.APIClient NO USA requests.request, así que NO usa http+docker://
#    Esto evita COMPLETAMENTE el bug de docker-py en Windows/WSL!


def build_image_and_run(path, image_tag, container_name):
    print(f"[BUILD] Building image '{image_tag}' from: {path}")

    try:
        response = [line for line in client.build(path=path, tag=image_tag, rm=True, decode=True)]
        print("[BUILD] Imagen construida correctamente.")
    except Exception as e:
        print("[ERROR] Error al construir imagen:", e)
        raise e

    # eliminar contenedor previo
    try:
        client.stop(container_name)
    except:
        pass
    try:
        client.remove_container(container_name)
    except:
        pass

    # verificar red
    networks = [n["Name"] for n in client.networks()]
    if NETWORK_NAME not in networks:
        print("[NETWORK] Creando red:", NETWORK_NAME)
        client.create_network(NETWORK_NAME, driver="bridge")

    # crear contenedor
    print(f"[RUN] Ejecutando contenedor '{container_name}'...")
    try:
        container = client.create_container(
            image=image_tag,
            name=container_name,
            host_config=client.create_host_config(
                network_mode=NETWORK_NAME,
                mem_limit="256m",
                nano_cpus=1_000_000_000,
                port_bindings={80: None}
            ),
            labels={"project": "user-project"}
        )
        client.start(container=container["Id"])
        container_activity[container["Id"]] = time.time()

        print("[SUCCESS] Contenedor levantado:", container_name)
        return container["Id"]

    except Exception as e:
        print("[ERROR] Error al iniciar contenedor:", e)
        raise e


def mark_activity(container_id):
    container_activity[container_id] = time.time()


def stop_inactive_containers(timeout_seconds=1800):
    now = time.time()
    for c in client.containers(all=True):
        labels = c.get("Labels", {})
        if labels.get("project") == "user-project":
            last = container_activity.get(c["Id"], now)
            if now - last > timeout_seconds:
                try:
                    print("[CLEANUP] Deteniendo contenedor inactivo:", c["Names"][0])
                    client.stop(c["Id"])
                except Exception as e:
                    print("[ERROR] No se pudo detener:", e)
