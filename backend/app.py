from flask import Flask
from flask_cors import CORS

from routes.question_papers import question_papers_bp
from routes.release import release_bp
from routes.auth import auth_bp


app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB


# -------------------------------------------------
# CORS configuration
# Allows the React/Vite frontend to communicate
# with the Flask backend during development.
# -------------------------------------------------
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173"
            ]
        }
    },
    supports_credentials=True
)


# -------------------------------------------------
# API Blueprints
# -------------------------------------------------
app.register_blueprint(
    auth_bp,
    url_prefix="/api/auth"
)

app.register_blueprint(
    question_papers_bp,
    url_prefix="/api/question-papers"
)

app.register_blueprint(
    release_bp,
    url_prefix="/api/release"
)


# -------------------------------------------------
# Health Check
# -------------------------------------------------
@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "Secure Question Paper Backend"
    }


# -------------------------------------------------
# Start Server
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)