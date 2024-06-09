import os
import unittest

from flask import json

from app import create_app
from app.extensions import db
from app.models import Ingredient, Recipe, User


class RecipeAPITestCase(unittest.TestCase):
    def setUp(self):
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
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_recipe(self):
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
        # First, create a recipe
        self.test_create_recipe()

        response = self.client.get("/api/recipes/", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(len(data["recipes"]) > 0)

    def test_get_recipe_by_id(self):
        # First, create a recipe
        self.test_create_recipe()

        with self.app.app_context():
            recipe = Recipe.query.first()

        response = self.client.get(f"/api/recipes/{recipe.id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["title"], "Test Recipe")

    # def test_update_recipe(self):
    #     # First, create a recipe
    #     self.test_create_recipe()
    #     recipe = Recipe.query.first()

    #     response = self.client.put(
    #         f"/api/recipes/{recipe.id}",
    #         headers=self.headers,
    #         json={
    #             "title": "Updated Recipe",
    #             "description": "Updated Description",
    #             "ingredients": [{"name": "Updated Ingredient 1", "quantity": "1 cup"}],
    #         },
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["message"], "Recipe updated successfully")

    #     # Verify the update
    #     updated_recipe = Recipe.query.get(recipe.id)
    #     self.assertEqual(updated_recipe.title, "Updated Recipe")

    def test_update_recipe(self):
        # First, create a recipe
        self.test_create_recipe()

        with self.app.app_context():
            recipe = Recipe.query.first()

        response = self.client.put(
            f"/api/recipes/{recipe.id}",
            headers=self.headers,
            json={
                "title": "Updated Recipe",
                "description": "Updated Description",
                "ingredients": [{"name": "Updated Ingredient 1", "quantity": "1 cup"}],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Recipe updated successfully")

        # Verify the update
        with self.app.app_context():
            updated_recipe = Recipe.query.get(recipe.id)
            self.assertEqual(updated_recipe.title, "Updated Recipe")

    # def test_delete_recipe(self):
    #     # First, create a recipe
    #     self.test_create_recipe()
    #     recipe = Recipe.query.first()

    #     response = self.client.delete(f"/api/recipes/{recipe.id}", headers=self.headers)
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["message"], "Recipe deleted successfully")

    #     # Verify deletion
    #     deleted_recipe = Recipe.query.get(recipe.id)
    #     self.assertIsNone(deleted_recipe)

    # def test_delete_recipe(self):
    #     # First, create a recipe
    #     self.test_create_recipe()

    #     with self.app.app_context():
    #         recipe = Recipe.query.first()

    #     response = self.client.delete(f"/api/recipes/{recipe.id}", headers=self.headers)
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["message"], "Recipe deleted successfully")

    #     # Verify deletion
    #     with self.app.app_context():
    #         deleted_recipe = Recipe.query.get(recipe.id)
    #         self.assertIsNone(deleted_recipe)

    def test_delete_recipe_not_owner(self):
        # First, create a recipe with the initial user
        self.test_create_recipe()

        with self.app.app_context():
            recipe = Recipe.query.first()
            self.assertIsNotNone(recipe)  # Ensure the recipe was created

        # Create a second test user
        with self.app.app_context():
            user2 = User(username="seconduser", email="second@example.com")
            user2.set_password("password")
            db.session.add(user2)
            db.session.commit()

        # Log in as the second user
        response = self.client.post(
            "/auth/login",
            json={"email": "second@example.com", "password": "password"},
        )
        self.assertEqual(response.status_code, 200)
        token2 = json.loads(response.data)["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Attempt to delete the recipe as the second user
        response = self.client.delete(f"/api/recipes/{recipe.id}", headers=headers2)
        self.assertEqual(response.status_code, 403)  # Forbidden
        data = json.loads(response.data)
        self.assertEqual(data["message"], "You are not allowed to delete this recipe")

        # Verify the recipe still exists
        with self.app.app_context():
            existing_recipe = Recipe.query.get(recipe.id)
            self.assertIsNotNone(existing_recipe)

    def test_delete_recipe_without_login(self):
        # First, create a recipe
        self.test_create_recipe()

        with self.app.app_context():
            recipe = Recipe.query.first()

        response = self.client.delete(f"/api/recipes/{recipe.id}")
        self.assertEqual(response.status_code, 401)

    def test_delete_non_existent_recipe(self):
        response = self.client.delete("/api/recipes/9999", headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_delete_recipe_not_owned(self):
        # Create another user
        with self.app.app_context():
            another_user = User(username="anotheruser", email="another@example.com")
            another_user.set_password("NewPassword@12345")
            db.session.add(another_user)
            db.session.commit()

            # Create a recipe for the new user
            recipe = Recipe(title="Another User Recipe", description="Description")
            db.session.add(recipe)
            db.session.commit()

            another_user_id = another_user.id
            recipe_id = recipe.id

        # Log in as the original test user
        response = self.client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "password"},
        )
        self.assertEqual(response.status_code, 200)
        self.token = json.loads(response.data)["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Try to delete the recipe owned by another user
        response = self.client.delete(f"/api/recipes/{recipe_id}", headers=self.headers)
        self.assertEqual(
            response.status_code, 403
        )  # Assuming 403 is returned for forbidden


if __name__ == "__main__":
    unittest.main()
