from flask import Flask

from app.blueprints.auth import auth_bp
from app.blueprints.recipe.routes import recipe_bp  # Corrected the import path
from app.config import Config
from app.extensions import db, jwt, login_manager, migrate


def create_app(config_class=Config):
    """
    Factory function to create and configure the Flask application.

    Args:
        config_class (class): The configuration class to use for the application.

    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(recipe_bp, url_prefix="/api/recipes")

    return app
