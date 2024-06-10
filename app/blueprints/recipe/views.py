from flask import current_app, jsonify, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Ingredient, Recipe, RecipeIngredient


class RecipeAPI(MethodView):
    """
    Recipe API class to handle CRUD operations for recipes.
    """

    @jwt_required()
    def post(self):
        """
        Create a new recipe.
        Expects JSON body with title, description, and ingredients.
        """
        data = request.get_json()

        # Validate input data
        if not data or not isinstance(data, dict):
            return jsonify({"message": "Invalid JSON data"}), 400

        if not isinstance(data.get("title"), str) or not data["title"].strip():
            return jsonify({"message": "Invalid or missing title"}), 400
        if (
            not isinstance(data.get("description"), str)
            or not data["description"].strip()
        ):
            return jsonify({"message": "Invalid or missing description"}), 400
        if not isinstance(data.get("ingredients"), list) or not data["ingredients"]:
            return jsonify({"message": "Invalid or missing ingredients"}), 400

        current_user_id = get_jwt_identity()

        # Create the recipe and associate it with the current user
        recipe = Recipe(
            title=data["title"],
            description=data.get("description"),
            user_id=current_user_id,
        )

        # Add recipe to session first
        db.session.add(recipe)
        db.session.flush()  # Get recipe.id before committing

        # Process ingredients
        ingredients_list = []
        for ingredient_data in data.get("ingredients", []):
            if (
                not isinstance(ingredient_data.get("name"), str)
                or not ingredient_data["name"].strip()
            ):
                return jsonify({"message": "Invalid ingredient name"}), 400
            if (
                not isinstance(ingredient_data.get("quantity"), str)
                or not ingredient_data["quantity"].strip()
            ):
                return jsonify({"message": "Invalid ingredient quantity"}), 400

            ingredient_name = ingredient_data["name"]
            quantity = ingredient_data["quantity"]

            # Check if ingredient already exists
            ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
            if not ingredient:
                ingredient = Ingredient(name=ingredient_name)
                db.session.add(ingredient)
                db.session.flush()  # Get ingredient.id before committing

            # Create association with quantity
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id, ingredient_id=ingredient.id, quantity=quantity
            )
            db.session.add(recipe_ingredient)
            ingredients_list.append({"name": ingredient_name, "quantity": quantity})

        db.session.commit()

        response_data = {
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "ingredients": ingredients_list,
        }

        return (
            jsonify(
                {"message": "Recipe created successfully", "recipe": response_data}
            ),
            201,
        )

    @jwt_required()
    def get(self, id=None):
        """
        Retrieve a recipe by ID or list recipes with pagination and search.
        If ID is provided, returns the recipe with that ID.
        Otherwise, returns a paginated list of recipes.
        """
        if id:
            return (
                jsonify(
                    {
                        "id": recipe.id,
                        "title": recipe.title,
                        "description": recipe.description,
                        "ingredients": [
                            {
                                "name": ingredient.name,
                                "quantity": ri.quantity,
                            }
                            for ingredient, ri in db.session.query(
                                Ingredient, RecipeIngredient
                            ).filter(
                                RecipeIngredient.recipe_id == recipe.id,
                                RecipeIngredient.ingredient_id == Ingredient.id,
                            )
                        ],
                    }
                )
                if (recipe := Recipe.query.get(id))
                else (jsonify({"message": f"Recipe with id {id} not found"}), 404)
            )
        page = request.args.get("page", 1, type=int)
        per_page = current_app.config["ITEMS_PER_PAGE"]
        query = Recipe.query
        if search := request.args.get("search"):
            query = query.filter(
                Recipe.title.ilike(f"%{search}%")
                | Recipe.ingredients.any(Ingredient.name.ilike(f"%{search}%"))
            )

        recipes = query.paginate(page=page, per_page=per_page)

        return jsonify(
            {
                "recipes": [
                    {
                        "id": r.id,
                        "title": r.title,
                        "description": r.description,
                        "ingredients": [
                            {
                                "name": ingredient.name,
                                "quantity": ri.quantity,
                            }
                            for ingredient, ri in db.session.query(
                                Ingredient, RecipeIngredient
                            ).filter(
                                RecipeIngredient.recipe_id == r.id,
                                RecipeIngredient.ingredient_id == Ingredient.id,
                            )
                        ],
                    }
                    for r in recipes.items
                ],
                "total": recipes.total,
                "pages": recipes.pages,
                "current_page": recipes.page,
            }
        )

    @jwt_required()
    def delete(self, recipe_id):
        # Disable foreign key checks
        db.session.execute("SET FOREIGN_KEY_CHECKS=0")

        if recipe := Recipe.query.get(recipe_id):
            db.session.delete(recipe)
            db.session.commit()
            message = {"message": "Recipe deleted successfully"}
        else:
            message = {"message": "Recipe not found"}

        # Re-enable foreign key checks
        db.session.execute("SET FOREIGN_KEY_CHECKS=1")

        return jsonify(message), 200
