"""
WealthSutra Backend — Flask + SQLite
Entry point: run with `python app.py` or `flask run`
"""
from flask import send_from_directory
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask import render_template
from models.models import db
from routes.profile_routes import profile_bp
from routes.score_routes import score_bp
from routes.fire_routes import fire_bp
from routes.chat_routes import chat_bp

load_dotenv()


def create_app():
    app = Flask(__name__)
    @app.route("/")
    def home():
     return render_template("fire_advisor.html")
    
    @app.route("/ui")
    def serve_ui():
     return send_from_directory(".", "fire_advisor.html")

    # ── Config ──────────────────────────────────────────
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wealthsutra.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ── Extensions ──────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    # ── Blueprints (all under /api) ──────────────────────
    app.register_blueprint(profile_bp, url_prefix="/api")
    app.register_blueprint(score_bp, url_prefix="/api")
    app.register_blueprint(fire_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")

    # ── Create DB tables ────────────────────────────────
    with app.app_context():
        db.create_all()

    # ── Health check ────────────────────────────────────
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "WealthSutra API"}), 200

    # ── 404 / 405 handlers ──────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=os.getenv("FLASK_ENV") == "development", port=5000)
