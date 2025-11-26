# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from auth import require_auth, users
from git_handler import clone_repo
from detectors import detect_project_type
from dockerfile_generator import ensure_dockerfile
from containers import build_image_and_run, stop_inactive_containers, mark_activity
from utils import generate_subdomain, container_name_from_subdomain
import threading, time, os

app = Flask(__name__)
CORS(app)

PROJECTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "projects"))
os.makedirs(PROJECTS_DIR, exist_ok=True)

# store currently active projects: key (user,project) -> info
projects = {}

@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error":"username and password required"}), 400
    if username in users:
        return jsonify({"error":"Usuario ya existe"}), 400
    users[username] = password
    return jsonify({"success": True})

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if users.get(username) != password:
        return jsonify({"error": "Credenciales inválidas"}), 401
    return jsonify({"success": True})

@app.route("/create-project", methods=["POST"])
@require_auth
def create_project(user):
    data = request.json or {}
    project_name = data.get("projectName")
    repo_url = data.get("repoUrl")
    template_id = data.get("templateId", "")  # optional id from frontend for UI
    if not project_name or not repo_url:
        return jsonify({"error":"projectName and repoUrl required"}), 400

    # prepare directories
    target_dir = os.path.join(PROJECTS_DIR, f"{user}__{project_name}")
    # clone
    try:
        clone_repo(repo_url, target_dir)
    except Exception as e:
        return jsonify({"error": f"git clone failed: {e}"}), 500

    # detect type
    try:
        ptype = detect_project_type(target_dir)
    except Exception as e:
        ptype = "static"

    # ensure Dockerfile exists (generate if missing)
    try:
        ensure_dockerfile(target_dir, ptype)
    except Exception as e:
        return jsonify({"error": f"dockerfile generation failed: {e}"}), 500

    # build image and run container
    subdomain = generate_subdomain(project_name, user)
    container_name = container_name_from_subdomain(subdomain)
    image_tag = f"{user}_{project_name}_image".lower()

    try:
        container_id = build_image_and_run(path=target_dir, image_tag=image_tag, container_name=container_name)
    except Exception as e:
        return jsonify({"error": f"docker build/run failed: {e}"}), 500

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

@app.route("/ping-project", methods=["POST"])
@require_auth
def ping_project(user):
    data = request.json or {}
    project = data.get("projectName")
    key = (user, project)
    info = projects.get(key)
    if not info:
        return jsonify({"error":"project not found"}), 404
    mark_activity(info["container_id"])
    return jsonify({"success": True, "url": f"http://{info['subdomain']}.localhost"})

# background cleaner
def cleaner():
    while True:
        try:
            stop_inactive_containers()
        except Exception as e:
            print("Cleaner error:", e)
        time.sleep(60)

threading.Thread(target=cleaner, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
