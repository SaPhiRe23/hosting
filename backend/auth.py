# backend/auth.py
from flask import request, jsonify

# in-memory simple user store
users = {}

def require_auth(f):
    def wrapper(*args, **kwargs):
        data = request.json or {}
        username = data.get("username")
        if not username:
            return jsonify({"error":"Auth requerida: enviar 'username' en JSON"}), 403
        if username not in users:
            return jsonify({"error":"Usuario no existe"}), 403
        return f(username, *args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper
