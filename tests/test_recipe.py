import os
import unittest

from flask import json

from app import create_app
from app.extensions import db
from app.models import Ingredient, Recipe, User


class RecipeAPITestCase(unittest.TestCase):
    """
    Test cases for the recipe API endpoints.
    """

    def setUp(self):
        """
        Set up the test environment before each test.
        """
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "TESTING_DATABASE_URL"
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create a test user
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()

            # Log in the test user
            response = self.client.post(
                "/auth/login",
                json={"email": "test@example.com", "password": "password"},
            )
            self.assertEqual(response.status_code, 200)
            self.token = json.loads(response.data)["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        """
        Clean up the test environment after each test.
        """
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_recipe(self):
        """
        Test creating a recipe.
        """
        response = self.client.post(
            "/api/recipes/",
            headers=self.headers,
            json={
                "title": "Test Recipe",
                "description": "Test Description",
                "ingredients": [
                    {"name": "Ingredient 1", "quantity": "1 cup"},
                    {"name": "Ingredient 2", "quantity": "2 tbsp"},
                ],
            },
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Recipe created successfully")

    def test_get_recipes(self):
        """
        Test retrieving all recipes.
        """
        # First, create a recipe
        self.client.post(
            "/api/recipes/",
            headers=self.headers,
            json={
                "title": "Test Recipe",
                "description": "Test Description",
                "ingredients": [
                    {"name": "Ingredient 1", "quantity": "1 cup"},
                    {"name": "Ingredient 2", "quantity": "2 tbsp"},
                ],
            },
        )

        # Then, get all recipes
        response = self.client.get("/api/recipes/", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(len(data["recipes"]) > 0)

    def test_get_recipe(self):
        """
        Test retrieving a specific recipe by its ID.
        """
        # First, create a recipe
        create_response = self.client.post(
            "/api/recipes/",
            headers=self.headers,
            json={
                "title": "Test Recipe",
                "description": "Test Description",
                "ingredients": [
                    {"name": "Ingredient 1", "quantity": "1 cup"},
                    {"name": "Ingredient 2", "quantity": "2 tbsp"},
                ],
            },
        )
        recipe_id = json.loads(create_response.data)["recipe"]["id"]

        # Then, get the recipe by ID
        response = self.client.get(f"/api/recipes/{recipe_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["title"], "Test Recipe")
        self.assertEqual(data["description"], "Test Description")

    def test_update_recipe(self):
        """
        Test updating a specific recipe by its ID.
        """
        # First, create a recipe
        create_response = self.client.post(
            "/api/recipes/",
            headers=self.headers,
            json={
                "title": "Test Recipe",
                "description": "Test Description",
                "ingredients": [
                    {"name": "Ingredient 1", "quantity": "1 cup"},
                    {"name": "Ingredient 2", "quantity": "2 tbsp"},
                ],
            },
        )
        recipe_id = json.loads(create_response.data)["recipe"]["id"]

        # Then, update the recipe by ID
        response = self.client.put(
            f"/api/recipes/{recipe_id}",
            headers=self.headers,
            json={
                "title": "Updated Recipe",
                "description": "Updated Description",
                "ingredients": [{"name": "Updated Ingredient", "quantity": "3 cups"}],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Recipe updated successfully")
        self.assertEqual(data["recipe"]["title"], "Updated Recipe")
        self.assertEqual(data["recipe"]["description"], "Updated Description")

    def test_delete_recipe(self):
        """
        Test deleting a specific recipe by its ID.
        """
        # First, create a recipe
        create_response = self.client.post(
            "/api/recipes/",
            headers=self.headers,
            json={
                "title": "Test Recipe",
                "description": "Test Description",
                "ingredients": [
                    {"name": "Ingredient 1", "quantity": "1 cup"},
                    {"name": "Ingredient 2", "quantity": "2 tbsp"},
                ],
            },
        )
        recipe_id = json.loads(create_response.data)["recipe"]["id"]

        # Then, delete the recipe by ID
        response = self.client.delete(f"/api/recipes/{recipe_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Recipe deleted successfully")

    def test_create_recipe_missing_fields(self):
        """
        Test creating a recipe with missing fields.
        """
        # Missing title
        response = self.client.post(
            "/api/recipes/",
            headers=self.headers,
            json={
                "description": "Test Description",
                "ingredients": [
                    {"name": "Ingredient 1", "quantity": "1 cup"},
                    {"name": "Ingredient 2", "quantity": "2 tbsp"},
                ],
            },
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Missing title")

        # Missing description
        response = self.client.post(
            "/api/recipes/",
            headers=self.headers,
            json={
                "title": "Test Recipe",
                "ingredients": [
                    {"name": "Ingredient 1", "quantity": "1 cup"},
                    {"name": "Ingredient 2", "quantity": "2 tbsp"},
                ],
            },
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Missing description")

        # Missing ingredients
        response = self.client.post(
            "/api/recipes/",
            headers=self.headers,
            json={
                "title": "Test Recipe",
                "description": "Test Description",
            },
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Missing ingredients")

    def test_create_recipe_invalid_data(self):
        """
        Test creating a recipe with invalid data.
        """
        response = self.client.post(
            "/api/recipes/",
            headers=self.headers,
            json={
                "title": "Test Recipe",
                "description": "Test Description",
                "ingredients": "Invalid ingredients format",
            },
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Invalid ingredients format")

    def test_get_recipe_not_found(self):
        """
        Test retrieving a non-existent recipe.
        """
        response = self.client.get("/api/recipes/999", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Recipe not found")

    def test_update_recipe_not_found(self):
        """
        Test updating a non-existent recipe.
        """
        response = self.client.put(
            "/api/recipes/999",
            headers=self.headers,
            json={
                "title": "Updated Recipe",
                "description": "Updated Description",
                "ingredients": [{"name": "Updated Ingredient", "quantity": "3 cups"}],
            },
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Recipe not found")

    def test_delete_recipe_not_found(self):
        """
        Test deleting a non-existent recipe.
        """
        response = self.client.delete("/api/recipes/999", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Recipe not found")


if __name__ == "__main__":
    unittest.main()
