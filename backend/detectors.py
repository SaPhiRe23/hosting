# backend/detectors.py
import os

def detect_project_type(path):
    """
    Detecta el tipo del proyecto basándose en archivos presentes:
    - si package.json -> node/react
    - si requirements.txt or app.py with flask import -> flask
    - if index.html en raíz -> static
    Devuelve: 'node', 'flask', 'static'
    """
    # package.json -> node/react
    if os.path.exists(os.path.join(path, "package.json")):
        return "node"
    # requirements.txt -> likely python/flask
    if os.path.exists(os.path.join(path, "requirements.txt")):
        # inspect requirements for flask
        try:
            with open(os.path.join(path, "requirements.txt"), "r", encoding="utf-8", errors="ignore") as f:
                r = f.read().lower()
                if "flask" in r:
                    return "flask"
        except:
            pass
        return "python"
    # app.py examine for flask import
    app_py = os.path.join(path, "app.py")
    if os.path.exists(app_py):
        try:
            with open(app_py, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()
                if "from flask" in content or "flask" in content:
                    return "flask"
        except:
            pass
    # html files in root
    for fname in ["index.html", "index.htm"]:
        if os.path.exists(os.path.join(path, fname)):
            return "static"
    # fallback node if there's src and package-lock.json
    if os.path.exists(os.path.join(path, "src")) and os.path.exists(os.path.join(path, "package-lock.json")):
        return "node"
    return "static"
