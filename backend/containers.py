# backend/containers.py
import docker, time, os
client = docker.from_env()

# map container_id -> last_activity_timestamp
container_activity = {}
NETWORK_NAME = "proxy_net"

def build_image_and_run(path, image_tag, container_name):
    """
    Construye la imagen desde la carpeta path con tag image_tag y lanza un contenedor con name container_name.
    Si existe un contenedor con el mismo name, lo para y borra antes de crear uno nuevo.
    Devuelve container.id
    """
    # build image
    # client.images.build can accept path
    print(f"Building image {image_tag} from {path} ...")
    image, logs = client.images.build(path=path, tag=image_tag, rm=True)
    # stop/remove existing container if exists
    try:
        old = client.containers.get(container_name)
        try:
            old.stop()
        except:
            pass
        try:
            old.remove()
        except:
            pass
    except docker.errors.NotFound:
        pass

    # run container, attach to network
    container = client.containers.run(
        image=image.tags[0] if image.tags else image.id,
        name=container_name,
        detach=True,
        network=NETWORK_NAME,
        labels={"project":"user-project"},
        ports={"80/tcp": None},
        mem_limit="256m",
        nano_cpus=1_000_000_000
    )
    container_activity[container.id] = time.time()
    return container.id

def mark_activity(container_id):
    container_activity[container_id] = time.time()

def stop_inactive_containers(timeout_seconds=1800):
    now = time.time()
    for c in client.containers.list(all=True):
        labels = c.labels or {}
        # only check containers we started (we labeled project)
        if labels.get("project") == "user-project":
            last = container_activity.get(c.id, now)
            if now - last > timeout_seconds:
                try:
                    if c.status == "running":
                        print("Stopping inactive container:", c.name)
                        c.stop()
                except Exception as e:
                    print("Error stopping container", c.name, e)
