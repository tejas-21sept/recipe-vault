from flask import Blueprint

# Create the recipe blueprint
recipe_bp = Blueprint("recipe", __name__)

# Import the routes to register them with the blueprint
from . import routes
