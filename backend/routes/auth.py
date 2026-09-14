from flask import Blueprint, jsonify
from security.rbac import require_roles

auth_bp = Blueprint("auth", __name__)

@auth_bp.get("/me")
@require_roles("admin", "setter", "examiner")
def me(user):
    return jsonify(user)
