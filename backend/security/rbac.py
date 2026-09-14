from functools import wraps
from flask import request, jsonify
from services.firebase_auth import verify_id_token
from services.mongodb import users_collection

def current_user():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise PermissionError("Missing Firebase Bearer token.")

    token = header.split(" ", 1)[1].strip()
    decoded = verify_id_token(token)
    print("DEBUG Firebase UID:", decoded.get("uid"))
    print("DEBUG Firebase email:", decoded.get("email"))
    user = users_collection.find_one({"firebase_uid": decoded["uid"]})
    if not user:
        raise PermissionError("Authenticated Firebase user has no application role.")

    return {
        "uid": decoded["uid"],
        "email": decoded.get("email"),
        "role": user.get("role", "examiner")
    }

def require_roles(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                user = current_user()
                if user["role"] not in allowed_roles:
                    return jsonify({"error": "Insufficient permissions."}), 403
                return fn(user, *args, **kwargs)
            except PermissionError as exc:
                return jsonify({"error": str(exc)}), 403
            except Exception as exc:
                return jsonify({"error": str(exc)}), 401
        return wrapper
    return decorator
