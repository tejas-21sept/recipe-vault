# # tests/test_search.py
# import os
# import unittest

# from flask import json

# from app import create_app
# from app.extensions import db
# from app.models import Ingredient, Recipe, User


# class SearchAPITestCase(unittest.TestCase):
#     """
#     Test cases for the search API endpoints.
#     """

#     def setUp(self):
#         """
#         Set up the test environment before each test.
#         """
#         self.app = create_app()
#         self.app.config["TESTING"] = True
#         self.app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
#             "TESTING_DATABASE_URL"
#         )
#         self.client = self.app.test_client()

#         with self.app.app_context():
#             self._extracted_from_setUp_13()

#     def _extracted_from_setUp_13(self):
#         db.create_all()

#         # Create a test user
#         user = User(username="testuser", email="test@example.com")
#         user.set_password("password")
#         db.session.add(user)
#         db.session.commit()

#         # Log in the test user
#         response = self.client.post(
#             "/auth/login",
#             json={"email": "test@example.com", "password": "password"},
#         )
#         self.assertEqual(response.status_code, 200)
#         self.token = json.loads(response.data)["access_token"]
#         self.headers = {"Authorization": f"Bearer {self.token}"}

#         # Create test recipes
#         recipe1 = Recipe(
#             title="Pancakes", description="Delicious pancakes", user_id=user.id
#         )
#         recipe2 = Recipe(
#             title="Salad", description="Healthy salad", user_id=user.id
#         )

#         ingredient1 = Ingredient(name="Flour", quantity="2 cups", recipe=recipe1)
#         ingredient2 = Ingredient(name="Lettuce", quantity="1 head", recipe=recipe2)

#         db.session.add_all([recipe1, recipe2, ingredient1, ingredient2])
#         db.session.commit()

#     def tearDown(self):
#         """
#         Clean up the test environment after each test.
#         """
#         with self.app.app_context():
#             db.session.remove()
#             db.drop_all()

#     def test_search_recipes(self):
#         """
#         Test searching for recipes by title.
#         """
#         response = self.client.get(
#             "/api/search/recipes?q=Pancakes", headers=self.headers
#         )
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertTrue(len(data["recipes"]) > 0)
#         self.assertEqual(data["recipes"][0]["title"], "Pancakes")

#     def test_search_recipes_no_results(self):
#         """
#         Test searching for recipes with no matching results.
#         """
#         response = self.client.get(
#             "/api/search/recipes?q=NonExistentRecipe", headers=self.headers
#         )
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertEqual(len(data["recipes"]), 0)

#     def test_search_ingredients(self):
#         """
#         Test searching for recipes by ingredient name.
#         """
#         response = self.client.get(
#             "/api/search/ingredients?q=Flour", headers=self.headers
#         )
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertTrue(len(data["recipes"]) > 0)
#         self.assertEqual(data["recipes"][0]["title"], "Pancakes")

#     def test_search_ingredients_no_results(self):
#         """
#         Test searching for recipes with no matching ingredients.
#         """
#         response = self.client.get(
#             "/api/search/ingredients?q=NonExistentIngredient", headers=self.headers
#         )
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertEqual(len(data["recipes"]), 0)


# if __name__ == "__main__":
#     unittest.main()
