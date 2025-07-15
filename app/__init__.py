import os
from flask import Flask
from app.views import views
from app.models import DesignStatusDB
from datetime import datetime

def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    app.secret_key = os.environ.get('SECRET_KEY', '8455646587941315544641314463116496843116496846316541749645134864531645')

    # Initialize the database
    DesignStatusDB()

    # Register the views blueprint
    app.register_blueprint(views)

    # Make current year available in templates
    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow().year}

    return app
