from flask import current_app, jsonify, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Ingredient, Recipe


class RecipeAPI(MethodView):
    """
    Recipe API class to handle CRUD operations for recipes.
    """

    @jwt_required
    def post(self):
        """
        Create a new recipe.
        Expects JSON body with title, description, and ingredients.
        """
        data = request.get_json()
        recipe = Recipe(title=data["title"], description=data.get("description"))
        db.session.add(recipe)
        db.session.commit()

        for ingredient in data.get("ingredients", []):
            ing = Ingredient(
                name=ingredient["name"],
                quantity=ingredient["quantity"],
                recipe_id=recipe.id,
            )
            db.session.add(ing)
        db.session.commit()

        return jsonify({"message": "Recipe created successfully"}), 201

    @jwt_required
    def get(self, id=None):
        """
        Retrieve a recipe by ID or list recipes with pagination and search.
        If ID is provided, returns the recipe with that ID.
        Otherwise, returns a paginated list of recipes.
        """
        if id:
            recipe = Recipe.query.get_or_404(id)
            return jsonify(
                {
                    "id": recipe.id,
                    "title": recipe.title,
                    "description": recipe.description,
                    "ingredients": [
                        {"name": i.name, "quantity": i.quantity}
                        for i in recipe.ingredients
                    ],
                }
            )
        else:
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
                                {"name": i.name, "quantity": i.quantity}
                                for i in r.ingredients
                            ],
                        }
                        for r in recipes.items
                    ],
                    "total": recipes.total,
                    "pages": recipes.pages,
                    "current_page": recipes.page,
                }
            )

    @jwt_required
    def put(self, id):
        """
        Update an existing recipe by ID.
        Expects JSON body with updated title, description, and ingredients.
        """
        data = request.get_json()
        recipe = Recipe.query.get_or_404(id)
        recipe.title = data.get("title", recipe.title)
        recipe.description = data.get("description", recipe.description)
        db.session.commit()

        # Delete existing ingredients and add new ones
        Ingredient.query.filter_by(recipe_id=id).delete()
        for ingredient in data.get("ingredients", []):
            ing = Ingredient(
                name=ingredient["name"], quantity=ingredient["quantity"], recipe_id=id
            )
            db.session.add(ing)
        db.session.commit()

        return jsonify({"message": "Recipe updated successfully"})

    @jwt_required
    def delete(self, id):
        """
        Delete a recipe by ID if the current user is the owner.
        """
        recipe = Recipe.query.get_or_404(id)
        current_user = get_jwt_identity()

        if recipe.user_id != current_user:
            return (
                jsonify({"message": "You are not allowed to delete this recipe"}),
                403,
            )

        db.session.delete(recipe)
        db.session.commit()

        return jsonify({"message": "Recipe deleted successfully"})
