# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from auth import require_auth, users
from git_handler import clone_repo
from detectors import detect_project_type
from dockerfile_generator import ensure_dockerfile
from containers import build_image_and_run, stop_inactive_containers, mark_activity
from utils import generate_subdomain, container_name_from_subdomain
import threading, time, os, traceback

app = Flask(__name__)
CORS(app)

PROJECTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "projects"))
os.makedirs(PROJECTS_DIR, exist_ok=True)

projects = {}  # (user, project) -> info


# ------------------------
# AUTH ENDPOINTS
# ------------------------

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error":"username and password required"}), 400
        if username in users:
            return jsonify({"error":"Usuario ya existe"}), 400

        users[username] = password
        return jsonify({"success": True})

    except Exception as e:
        print("\n🔥 ERROR EN /register")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json or {}
        username = data.get("username")
        password = data.get("password")

        if users.get(username) != password:
            return jsonify({"error": "Credenciales inválidas"}), 401

        return jsonify({"success": True})

    except Exception as e:
        print("\n🔥 ERROR EN /login")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ------------------------
# PROJECT CREATION
# ------------------------

@app.route("/create-project", methods=["POST"])
@require_auth
def create_project(user):
    try:
        data = request.json or {}
        project_name = data.get("projectName")
        repo_url = data.get("repoUrl")
        template_id = data.get("templateId", "")

        if not project_name or not repo_url:
            return jsonify({"error":"projectName and repoUrl required"}), 400

        # Directorio destino
        target_dir = os.path.join(PROJECTS_DIR, f"{user}__{project_name}")

        # 1) Clonar repositorio
        try:
            clone_repo(repo_url, target_dir)
        except Exception as e:
            print("\n🔥 ERROR EN git clone:")
            traceback.print_exc()
            return jsonify({"error": f"git clone failed: {e}"}), 500

        # 2) Detectar tipo de proyecto
        try:
            ptype = detect_project_type(target_dir)
        except Exception as e:
            print("\n⚠️ WARNING detect_project_type falló, usando static.")
            traceback.print_exc()
            ptype = "static"

        # 3) Generar Dockerfile si falta
        try:
            ensure_dockerfile(target_dir, ptype)
        except Exception as e:
            print("\n🔥 ERROR EN ensure_dockerfile:")
            traceback.print_exc()
            return jsonify({"error": f"dockerfile generation failed: {e}"}), 500

        # 4) Construir imagen y ejecutar contenedor
        subdomain = generate_subdomain(project_name, user)
        container_name = container_name_from_subdomain(subdomain)
        image_tag = f"{user}_{project_name}_image".lower()

        try:
            container_id = build_image_and_run(
                path=target_dir,
                image_tag=image_tag,
                container_name=container_name
            )
        except Exception as e:
            print("\n🔥 ERROR EN docker build/run:")
            traceback.print_exc()
            return jsonify({"error": f"docker build/run failed: {e}"}), 500

        # Guardar info
        projects[(user, project_name)] = {
            "container_id": container_id,
            "container_name": container_name,
            "subdomain": subdomain,
            "created_at": time.time(),
            "repo": repo_url
        }

        return jsonify({
            "success": True,
            "url": f"http://{subdomain}.localhost",
            "container_name": container_name
        })

    except Exception as e:
        print("\n🔥 ERROR GENERAL EN /create-project:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ------------------------
# PING PROJECT
# ------------------------

@app.route("/ping-project", methods=["POST"])
@require_auth
def ping_project(user):
    try:
        data = request.json or {}
        project = data.get("projectName")
        key = (user, project)
        info = projects.get(key)

        if not info:
            return jsonify({"error":"project not found"}), 404

        mark_activity(info["container_id"])
        return jsonify({"success": True, "url": f"http://{info['subdomain']}.localhost"})

    except Exception as e:
        print("\n🔥 ERROR EN /ping-project:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ------------------------
# BACKGROUND CLEANER
# ------------------------

def cleaner():
    while True:
        try:
            stop_inactive_containers()
        except Exception as e:
            print("\n🔥 Cleaner error:")
            traceback.print_exc()
        time.sleep(60)

threading.Thread(target=cleaner, daemon=True).start()


# ------------------------
# MAIN
# ------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
