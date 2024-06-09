import os
import unittest

from flask import json

from app import create_app
from app.extensions import db
from app.models import Ingredient, Recipe, User


class RecipeSearchTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "TESTING_DATABASE_URL"
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            user = User(username="testuser", email="test@example.com")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

            recipe1 = Recipe(
                title="Chocolate Cake",
                description="Delicious chocolate cake",
                user_id=self.user_id,
            )
            recipe2 = Recipe(
                title="Vanilla Cake",
                description="Delicious vanilla cake",
                user_id=self.user_id,
            )
            db.session.add(recipe1)
            db.session.add(recipe2)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get_auth_token(self):
        response = self.client.post(
            "/auth/login",
            data=json.dumps({"email": "test@example.com", "password": "testpassword"}),
            content_type="application/json",
        )
        return response.json["access_token"]

    def test_search_recipes_by_title(self):
        token = self.get_auth_token()
        response = self.client.get(
            "/api/recipes?search=Chocolate",
            headers={"Authorization": f"Bearer {token}"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["recipes"]), 1)
        self.assertEqual(response.json["recipes"][0]["title"], "Chocolate Cake")

    def test_search_recipes_by_ingredients(self):
        with self.app.app_context():
            recipe = Recipe.query.filter_by(title="Chocolate Cake").first()
            ingredient = Ingredient(
                name="Chocolate", quantity="200g", recipe_id=recipe.id
            )
            db.session.add(ingredient)
            db.session.commit()

        token = self.get_auth_token()
        response = self.client.get(
            "/api/recipes?search=Chocolate",
            headers={"Authorization": f"Bearer {token}"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["recipes"]), 1)
        self.assertEqual(response.json["recipes"][0]["title"], "Chocolate Cake")

    def test_search_with_no_matching_results(self):
        token = self.get_auth_token()
        response = self.client.get(
            "/api/recipes?search=Strawberry",
            headers={"Authorization": f"Bearer {token}"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["recipes"]), 0)


if __name__ == "__main__":
    unittest.main()
