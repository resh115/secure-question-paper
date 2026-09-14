import os
import firebase_admin
from firebase_admin import credentials, auth

_initialized = False

def _init():
    global _initialized
    if _initialized:
        return

    path = os.getenv("FIREBASE_SERVICE_ACCOUNT", "")
    if not path:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT is not configured.")

    if not os.path.exists(path):
        raise RuntimeError(f"Firebase service-account file not found: {path}")

    cred = credentials.Certificate(path)
    firebase_admin.initialize_app(cred)
    _initialized = True

def verify_id_token(id_token: str):
    _init()
    return auth.verify_id_token(id_token)
