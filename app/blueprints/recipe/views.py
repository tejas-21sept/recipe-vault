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
    def put(self, id):
        """
        Update an existing recipe by ID.
        Expects JSON body with updated title, description, and ingredients.
        """
        data = request.get_json()

        # Validate input data
        if not data or not isinstance(data, dict):
            return jsonify({"message": "Invalid JSON data"}), 400

        # Validate recipe existence
        recipe = Recipe.query.get(id)
        if not recipe:
            return jsonify({"message": f"Recipe with id {id} not found"}), 404

        # Validate and update title
        if "title" in data:
            if not isinstance(data["title"], str) or not data["title"].strip():
                return jsonify({"message": "Invalid or missing title"}), 400
            recipe.title = data["title"]

        # Validate and update description
        if "description" in data:
            if (
                not isinstance(data["description"], str)
                or not data["description"].strip()
            ):
                return jsonify({"message": "Invalid or missing description"}), 400
            recipe.description = data["description"]

        # Validate ingredients
        if "ingredients" in data:
            if not isinstance(data["ingredients"], list) or not data["ingredients"]:
                return jsonify({"message": "Invalid or missing ingredients"}), 400

            # Delete existing ingredients and add new ones
            RecipeIngredient.query.filter_by(recipe_id=id).delete()
            for ingredient_data in data["ingredients"]:
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

        db.session.commit()

        updated_data = {
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "ingredients": [
                {"name": ingredient.name, "quantity": ri.quantity}
                for ingredient, ri in db.session.query(Ingredient, RecipeIngredient)
                .filter(RecipeIngredient.recipe_id == recipe.id)
                .filter(RecipeIngredient.ingredient_id == Ingredient.id)
            ],
        }

        return (
            jsonify({"message": "Recipe updated successfully", "recipe": updated_data}),
            200,
        )

    @jwt_required()
    def delete(self, id):
        """
        Delete a recipe by ID.
        """
        # Query the recipe by ID
        recipe = Recipe.query.get(id)
        if not recipe:
            return jsonify({"message": f"Recipe with id {id} not found"}), 404

        try:
            # Delete associated records from RecipeIngredient table
            RecipeIngredient.query.filter_by(recipe_id=id).delete()

            # Then delete the recipe itself
            db.session.delete(recipe)
            db.session.commit()

            return jsonify({"message": "Recipe deleted successfully"}), 200
        except Exception as e:
            # Handle any exceptions that may occur during deletion
            db.session.rollback()
            return jsonify({"message": f"Failed to delete recipe: {str(e)}"}), 500
