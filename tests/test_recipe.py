import os
import unittest

from flask import json

from app import create_app
from app.extensions import db
from app.models import Ingredient, Recipe, RecipeIngredient, User


class RecipeAPITestCase(unittest.TestCase):
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
            self._extracted_from_setUp_13()

    def _extracted_from_setUp_13(self):
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
        response = self.client.post(
            "/api/recipes/",
            json={
                "title": "Spaghetti Carbonara",
                "description": "A classic Italian pasta dish.",
                "ingredients": [
                    {"name": "Spaghetti", "quantity": "200g"},
                    {"name": "Pancetta", "quantity": "150g"},
                    {"name": "Eggs", "quantity": "2"},
                    {"name": "Grated Parmesan cheese", "quantity": "50g"},
                    {"name": "Black pepper", "quantity": "to taste"},
                ],
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["recipe"]["title"], "Spaghetti Carbonara")
        self.assertEqual(len(data["recipe"]["ingredients"]), 5)

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

    def test_get_recipe_by_id(self):
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
            json={
                "description": "A classic Italian pasta dish.",
                "ingredients": [
                    {"name": "Spaghetti", "quantity": "200g"},
                    {"name": "Pancetta", "quantity": "150g"},
                    {"name": "Eggs", "quantity": "2"},
                    {"name": "Grated Parmesan cheese", "quantity": "50g"},
                    {"name": "Black pepper", "quantity": "to taste"},
                ],
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self._check_invalid_field_response(response, "Invalid or missing title")

        # Missing description
        response = self.client.post(
            "/api/recipes/",
            json={
                "title": "Test Recipe",
                "ingredients": [
                    {"name": "Ingredient 1", "quantity": "1 cup"},
                    {"name": "Ingredient 2", "quantity": "2 tbsp"},
                ],
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self._check_invalid_field_response(response, "Invalid or missing description")

        # Missing ingredients
        response = self.client.post(
            "/api/recipes/",
            json={
                "title": "Test Recipe",
                "description": "Test Description",
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self._check_invalid_field_response(response, "Invalid or missing ingredients")

    def test_create_recipe_invalid_data(self):
        """
        Test creating a recipe with invalid data.
        """
        # Invalid title (empty string)
        response = self.client.post(
            "/api/recipes/",
            json={
                "title": "",
                "description": "A classic Italian pasta dish.",
                "ingredients": [
                    {"name": "Spaghetti", "quantity": "200g"},
                    {"name": "Pancetta", "quantity": "150g"},
                    {"name": "Eggs", "quantity": "2"},
                    {"name": "Grated Parmesan cheese", "quantity": "50g"},
                    {"name": "Black pepper", "quantity": "to taste"},
                ],
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self._check_invalid_field_response(response, "Invalid or missing title")

        # Invalid description (non-string type)
        response = self.client.post(
            "/api/recipes/",
            json={
                "title": "Spaghetti Carbonara",
                "description": 12345,
                "ingredients": [
                    {"name": "Spaghetti", "quantity": "200g"},
                    {"name": "Pancetta", "quantity": "150g"},
                    {"name": "Eggs", "quantity": "2"},
                    {"name": "Grated Parmesan cheese", "quantity": "50g"},
                    {"name": "Black pepper", "quantity": "to taste"},
                ],
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self._check_invalid_field_response(response, "Invalid or missing description")

        # Invalid ingredients (empty list)
        response = self.client.post(
            "/api/recipes/",
            json={
                "title": "Spaghetti Carbonara",
                "description": "A classic Italian pasta dish.",
                "ingredients": [],
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self._check_invalid_field_response(response, "Invalid or missing ingredients")

        # Invalid ingredient name (empty string)
        response = self.client.post(
            "/api/recipes/",
            json={
                "title": "Spaghetti Carbonara",
                "description": "A classic Italian pasta dish.",
                "ingredients": [
                    {"name": "", "quantity": "200g"},
                    {"name": "Pancetta", "quantity": "150g"},
                    {"name": "Eggs", "quantity": "2"},
                    {"name": "Grated Parmesan cheese", "quantity": "50g"},
                    {"name": "Black pepper", "quantity": "to taste"},
                ],
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self._check_invalid_field_response(response, "Invalid ingredient name")

        # Invalid ingredient quantity (non-string type)
        response = self.client.post(
            "/api/recipes/",
            json={
                "title": "Spaghetti Carbonara",
                "description": "A classic Italian pasta dish.",
                "ingredients": [
                    {"name": "Spaghetti", "quantity": 200},
                    {"name": "Pancetta", "quantity": "150g"},
                    {"name": "Eggs", "quantity": "2"},
                    {"name": "Grated Parmesan cheese", "quantity": "50g"},
                    {"name": "Black pepper", "quantity": "to taste"},
                ],
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self._check_invalid_field_response(response, "Invalid ingredient quantity")

    def _check_invalid_field_response(self, response, expected_message):
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertEqual(result["message"], expected_message)

    def test_get_recipe_not_found(self):
        """
        Test retrieving a recipe that does not exist.
        """
        non_existent_id = 9999  # An ID that does not exist in the database
        response = self.client.get(
            f"/api/recipes/{non_existent_id}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self._check_not_found_response(
            response, f"Recipe with id {non_existent_id} not found"
        )

    def test_update_recipe_not_found(self):
        """
        Test updating a recipe that does not exist.
        """
        non_existent_id = 9999  # An ID that does not exist in the database
        update_data = {
            "title": "Updated Recipe Title",
            "description": "Updated Description",
            "ingredients": [
                {"name": "Updated Ingredient 1", "quantity": "1 cup"},
                {"name": "Updated Ingredient 2", "quantity": "2 tbsp"},
            ],
        }
        response = self.client.put(
            f"/api/recipes/{non_existent_id}",
            headers={"Authorization": f"Bearer {self.token}"},
            json=update_data,
        )
        self._check_not_found_response(
            response, f"Recipe with id {non_existent_id} not found"
        )

    def test_delete_recipe_not_found(self):
        """
        Test deleting a recipe that does not exist.
        """
        non_existent_id = 9999  # An ID that does not exist in the database
        response = self.client.delete(
            f"/api/recipes/{non_existent_id}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self._check_not_found_response(
            response, f"Recipe with id {non_existent_id} not found"
        )

    def _check_not_found_response(self, response, expected_message):
        self.assertEqual(response.status_code, 404)
        result = json.loads(response.data)
        self.assertEqual(result["message"], expected_message)


if __name__ == "__main__":
    unittest.main()
