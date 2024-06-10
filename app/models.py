from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    """
    User model for storing user-related data.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    recipes = db.relationship(
        "Recipe", backref="author", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """
        Set the user's password.

        Args:
            password (str): The password to set.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check the user's password.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """
        Get the user's ID.

        Returns:
            str: The user's ID as a string.
        """
        return str(self.id)

    def __repr__(self):
        """
        Get a string representation of the user.

        Returns:
            str: A string representation of the user.
        """
        return f"<User {self.username}>"


class Recipe(db.Model):
    """
    Recipe model for storing recipe-related data.
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    ingredients = db.relationship(
        "Ingredient",
        secondary="recipe_ingredient",
        backref=db.backref("recipes", lazy=True),
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        """
        Get a string representation of the recipe.

        Returns:
            str: A string representation of the recipe.
        """
        return f"<Recipe {self.title}>"


class Ingredient(db.Model):
    """
    Ingredient model for storing ingredient-related data.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        """
        Get a string representation of the ingredient.

        Returns:
            str: A string representation of the ingredient.
        """
        return f"<Ingredient {self.name}>"


class RecipeIngredient(db.Model):
    """
    Association table for many-to-many relationship between Recipe and Ingredient.
    """

    __tablename__ = "recipe_ingredient"
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), primary_key=True)
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredient.id"), primary_key=True
    )
    quantity = db.Column(db.String(64))
