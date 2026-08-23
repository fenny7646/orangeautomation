import logging
from flask import Blueprint, render_template, current_app

main_bp = Blueprint("main", __name__)
logger = logging.getLogger("automation_hub.main")

@main_bp.route("/")
def index():
    try:
        return render_template("index.html", title="Automation Hub")
    except Exception as e:
        logger.exception(f"Error rendering index template: {e}")
        return render_template("base.html", title="Error", content_override=f"Failed to load dashboard: {str(e)}"), 500

@main_bp.route("/about")
def about():
    try:
        return render_template("about.html", title="About Project")
    except Exception as e:
        logger.exception(f"Error rendering about template: {e}")
        return render_template("base.html", title="Error", content_override=f"Failed to load about page: {str(e)}"), 500
