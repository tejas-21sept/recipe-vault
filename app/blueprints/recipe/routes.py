from app.blueprints.recipe import recipe_bp
from app.blueprints.recipe.views import RecipeAPI

# Register the RecipeAPI view with its URL routes
recipe_view = RecipeAPI.as_view("recipe_api")

# Define URL routes for the recipe blueprint
recipe_bp.add_url_rule(
    "/", defaults={"id": None}, view_func=recipe_view, methods=["GET"]
)
recipe_bp.add_url_rule("/", view_func=recipe_view, methods=["POST"])
recipe_bp.add_url_rule(
    "/<int:id>", view_func=recipe_view, methods=["GET", "PUT", "DELETE"]
)
