from app.blueprints.recipe import recipe_bp
from app.blueprints.recipe.views import RecipeAPI

recipe_view = RecipeAPI.as_view("recipe_api")

recipe_bp.add_url_rule(
    "/", defaults={"id": None}, view_func=recipe_view, methods=["GET"]
)
recipe_bp.add_url_rule("/", view_func=recipe_view, methods=["POST"])
recipe_bp.add_url_rule(
    "/<int:id>", view_func=recipe_view, methods=["GET", "PUT", "DELETE"]
)
