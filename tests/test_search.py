import os
import unittest

from flask import json

from app import create_app
from app.extensions import db
from app.models import Ingredient, Recipe, RecipeIngredient, User


class SearchAPITestCase(unittest.TestCase):
    """
    Test cases for the search API endpoints.
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
            # Create a test user
            user = User(username="testuser1", email="test1@example.com")
            user.set_password("Testsearch@1")
            db.session.add(user)
            db.session.commit()

            # Log in the test user
            response = self.client.post(
                "/auth/login",
                json={"email": "test1@example.com", "password": "Testsearch@1"},
            )
            self.assertEqual(response.status_code, 200)
            self.token = json.loads(response.data)["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}

            # Create a recipe
            recipe = Recipe(
                title="Your Recipe Title",
                description="Your Recipe Description",
                user_id=user.id,
            )
            db.session.add(recipe)
            db.session.commit()

    def tearDown(self):
        """
        Clean up the test environment after each test.
        """
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _create_sample_recipes(self):
        """
        Helper method to create sample recipes for testing.
        """
        # Create some sample recipes with different titles and ingredients
        sample_recipes = [
            {"title": "Spaghetti Carbonara", "ingredients": ["Spaghetti", "Pancetta"]},
            {"title": "Chicken Alfredo", "ingredients": ["Chicken", "Alfredo Sauce"]},
            {"title": "Vegetable Stir Fry", "ingredients": ["Broccoli", "Carrot"]},
        ]
        for recipe_data in sample_recipes:
            recipe = Recipe(title=recipe_data["title"], description="Test description")
            db.session.add(recipe)
            db.session.flush()

            for ingredient_name in recipe_data["ingredients"]:
                # Check if ingredient already exists
                ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
                if not ingredient:
                    # If not, create a new one
                    ingredient = Ingredient(name=ingredient_name)
                    db.session.add(ingredient)
                    db.session.flush()

                # Create association with recipe
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient.id,
                    quantity="Some quantity",
                )
                db.session.add(recipe_ingredient)

        db.session.commit()

    def test_search_recipes(self):
        """
        Test searching recipes by title or ingredient name.
        """
        with self.app.app_context():
            # Create some sample recipes for testing
            self._create_sample_recipes()

            # Perform search for existing title
            response = self.client.get(
                "/api/recipes?search=Spaghetti&page=1",
                headers=self.headers,
                # postman running - http://127.0.0.1:5000/api/recipes?search=pasta&page=1
            )
            self._check_search_response(response, 1)

            # Perform search for existing ingredient
            response = self.client.get(
                "/api/recipes?search=Pancetta", headers=self.headers
            )
            self._check_search_response(response, 1)

            # Perform search for non-existent term
            response = self.client.get(
                "/api/recipes?search=NonExistent", headers=self.headers
            )
            self._check_search_response(response, 0)

    def _check_search_response(self, response, expected_count):
        """
        Helper method to check search response.
        """
        if response.status_code == 308:
            # Follow the redirect
            redirected_response = self.client.get(
                response.headers["Location"], headers=self.headers
            )
            self.assertEqual(
                redirected_response.status_code, 200
            )  # Ensure successful redirection
            data = self._extracted_from__extracted_from_test_search_recipes_56_5(
                redirected_response, expected_count
            )
        else:
            # Normal response handling
            data = self._extracted_from__extracted_from_test_search_recipes_56_5(
                response, expected_count
            )

    def _extracted_from_test_search_recipes_10(self, arg0, arg1):
        # Perform search for existing title
        result = self.client.get(arg0, headers=self.headers)
        data = self._extracted_from_test_search_recipes_56(result, arg1)
        return result

    def _extracted_from_test_search_recipes_50(self):
        # Create some sample recipes for testing
        self._create_sample_recipes()

        # Perform search for existing title
        result = self.client.get("/api/recipes?search=Spaghetti", headers=self.headers)
        data = self._extracted_from_test_search_recipes_56(result, 1)
        # Perform search for existing ingredient
        result = self.client.get("/api/recipes?search=Pancetta", headers=self.headers)
        data = self._extracted_from_test_search_recipes_56(result, 1)
        # Perform search for non-existent term
        result = self.client.get(
            "/api/recipes?search=NonExistent", headers=self.headers
        )
        data = self._extracted_from_test_search_recipes_56(result, 0)
        return result

    def _extracted_from_test_search_recipes_56(self, response, arg1):
        return self._extracted_from__extracted_from_test_search_recipes_56_5(
            response, arg1
        )

    def _extracted_from__extracted_from_test_search_recipes_56_5(self, response, arg1):
        return self._extracted_from__extracted_from__extracted_from_test_search_recipes_56_5_11(
            response, arg1
        )

    def _extracted_from__extracted_from__extracted_from_test_search_recipes_56_5_11(
        self, arg0, arg1
    ):
        return self._extracted_from_test_search_recipes_no_results_4(arg0, arg1)

    def test_search_recipes_no_results(self):
        """
        Test searching recipes when no results are found.
        """
        with self.app.app_context():
            # Perform search for a term that doesn't exist
            response = self.client.get(
                "api/recipes?search=NonExistentTerm", headers=self.headers
            )
            data = self._extracted_from__extracted_from_test_search_recipes_no_results_4_11(
                response, 0
            )

    def _extracted_from_test_search_recipes_no_results_4(self, arg0, arg1):
        return self._extracted_from__extracted_from_test_search_recipes_no_results_4_11(
            arg0, arg1
        )

    def _extracted_from__extracted_from_test_search_recipes_no_results_4_11(
        self, arg0, arg1
    ):
        self.assertEqual(arg0.status_code, 200)
        result = json.loads(arg0.data)
        self.assertEqual(len(result["recipes"]), arg1)
        return result

    def test_search_redirect(self):
        response = self.client.get(
            "/api/recipes?search=NonExistentTerm",
            headers=self.headers,
        )
        if response.status_code == 308:
            redirected_response = self.client.get(
                response.headers["Location"], headers=self.headers
            )
            self.assertEqual(redirected_response.status_code, 200)
        else:
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
