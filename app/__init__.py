import logging
import os
import sys
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("automation_hub")


def create_app(config_name=None):
    try:
        if config_name is None:
            config_name = os.getenv("FLASK_ENV", "development")

        app = Flask(__name__)

        selected_config = config.get(config_name, config.get("default"))
        if selected_config:
            app.config.from_object(selected_config)
        else:
            logger.warning(f"Configuration '{config_name}' not found. Falling back to default.")

        try:
            CORS(app)
        except Exception as cors_err:
            logger.error(f"Error initializing CORS: {cors_err}")

        try:
            from app.routes.main import main_bp
            from app.routes.api import api_bp

            app.register_blueprint(main_bp)
            app.register_blueprint(api_bp, url_prefix="/api")
        except ImportError as import_err:
            logger.critical(f"Failed to import application blueprints: {import_err}")
            raise

        @app.errorhandler(400)
        def handle_bad_request(error):
            logger.warning(f"400 Bad Request: {error} - Path: {request.path}")
            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "status": "Failed",
                    "error": "Bad Request",
                    "message": str(error.description) if hasattr(error, "description") else "The request was invalid or malformed."
                }), 400
            return render_template("base.html", title="400 - Bad Request", content_override="Bad Request: The request could not be processed."), 400

        @app.errorhandler(404)
        def handle_not_found(error):
            logger.warning(f"404 Not Found: {request.path}")
            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "status": "Failed",
                    "error": "Not Found",
                    "message": f"Endpoint '{request.path}' was not found on this server."
                }), 404
            return render_template("base.html", title="404 - Page Not Found", content_override="404 - The requested page could not be found."), 404

        @app.errorhandler(405)
        def handle_method_not_allowed(error):
            logger.warning(f"405 Method Not Allowed: {request.method} on {request.path}")
            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "status": "Failed",
                    "error": "Method Not Allowed",
                    "message": f"HTTP method '{request.method}' is not allowed on '{request.path}'."
                }), 405
            return render_template("base.html", title="405 - Method Not Allowed", content_override="405 - Method Not Allowed."), 405

        @app.errorhandler(500)
        def handle_internal_server_error(error):
            logger.error(f"500 Internal Server Error on {request.path}: {error}")
            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "status": "Failed",
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred on the server. Please check server logs."
                }), 500
            return render_template("base.html", title="500 - Server Error", content_override="500 - Internal Server Error. Please check server logs."), 500

        @app.errorhandler(Exception)
        def handle_unhandled_exception(exception):
            logger.exception(f"Unhandled Exception on {request.path}: {exception}")
            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "status": "Failed",
                    "error": "Unhandled Server Exception",
                    "message": str(exception) or "An unhandled server exception occurred."
                }), 500
            return render_template("base.html", title="500 - Internal Error", content_override=f"An unexpected error occurred: {str(exception)}"), 500

        return app

    except Exception as factory_err:
        logger.critical(f"Critical error during Flask app creation: {factory_err}")
        raise
