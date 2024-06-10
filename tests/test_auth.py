# tests/test_auth.py
import os
import unittest

from flask import json

from app import create_app
from app.extensions import db
from app.models import User


class AuthTestCase(unittest.TestCase):
    """
    Test cases for the authentication functionalities.
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

    def tearDown(self):
        """
        Clean up the test environment after each test.
        """
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_user(self):
        """
        Test user registration with valid data.
        """
        response = self.client.post(
            "/auth/register",
            data=json.dumps(
                {
                    "username": "newuser",
                    "email": "newuser@example.com",
                    "password": "NewPassword@12345",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "User registered successfully")

    def test_register_user_missing_fields(self):
        """
        Test user registration with missing fields.
        """
        # Missing email
        response = self.client.post(
            "/auth/register",
            data=json.dumps({"username": "newuser", "password": "newpassword"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "Missing email")

        # Missing username
        response = self.client.post(
            "/auth/register",
            data=json.dumps(
                {"email": "newuser@example.com", "password": "newpassword"}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "Missing username")

        # Missing password
        response = self.client.post(
            "/auth/register",
            data=json.dumps({"username": "newuser", "email": "newuser@example.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "Missing password")

    def test_login_user(self):
        """
        Test user login with valid credentials.
        """
        response = self._extracted_from_test_login_user_wrong_username_5(
            "test@example.com", "testpassword", 200
        )
        self.assertIn("access_token", response.json['data'])


    def test_login_user_invalid(self):
        """
        Test user login with invalid credentials.
        """
        response = self._extracted_from_test_login_user_wrong_username_5(
            "test@example.com", "wrongpassword", 401
        )
        self.assertEqual(response.json["message"], "Invalid email or password")

    def test_logout_user(self):
        """
        Test user logout.
        """
        with self.app.app_context():
            self._extracted_from_test_login_user_wrong_username_6()
        response = self.client.post(
            "/auth/login",
            data=json.dumps({"email": "test@example.com", "password": "testpassword"}),
            content_type="application/json",
        )
        access_token = response.json["data"]["access_token"]

        response = self.client.post(
            "/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Logged out successfully")

    def test_register_user_existing_username(self):
        """
        Test registering a user with an existing username.
        """
        # Register the first user
        response = self.client.post(
            "/auth/register",
            data=json.dumps(
                {
                    "username": "existinguser",
                    "email": "existinguser1@example.com",
                    "password": "NewPassword@12345",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "User registered successfully")

        # Attempt to register another user with the same username
        response = self.client.post(
            "/auth/register",
            data=json.dumps(
                {
                    "username": "existinguser",
                    "email": "existinguser2@example.com",
                    "password": "password123",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "Username already exists")

    def test_login_user_missing_credentials(self):
        """
        Test user login with missing credentials.
        """
        # Missing email
        response = self.client.post(
            "/auth/login",
            data=json.dumps({"password": "testpassword"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "Missing email or password")

        # Missing password
        response = self.client.post(
            "/auth/login",
            data=json.dumps({"email": "test@example.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "Missing email or password")

    def test_register_user_weak_password(self):
        """
        Test registering a user with a weak password.
        """
        response = self.client.post(
            "/auth/register",
            data=json.dumps(
                {
                    "username": "newuser",
                    "email": "newuser@example.com",
                    "password": "123",  # Example of a weak password
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["message"],
            "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character.",
        )

    def test_login_user_wrong_username(self):
        """
        Test user login with wrong username.
        """
        response = self._extracted_from_test_login_user_wrong_username_5(
            "wrong@example.com", "testpassword", 401
        )
        self.assertEqual(response.json["message"], "Invalid email or password")

    # TODO Rename this here and in `test_login_user`, `test_login_user_invalid`, `test_logout_user` and `test_login_user_wrong_username`
    def _extracted_from_test_login_user_wrong_username_5(self, arg0, arg1, arg2):
        with self.app.app_context():
            self._extracted_from_test_login_user_wrong_username_6()
        result = self.client.post(
            "/auth/login",
            data=json.dumps({"email": arg0, "password": arg1}),
            content_type="application/json",
        )
        self.assertEqual(result.status_code, arg2)
        return result

    # TODO Rename this here and in `test_login_user`, `test_login_user_invalid`, `test_logout_user` and `test_login_user_wrong_username`
    def _extracted_from_test_login_user_wrong_username_6(self):
        user = User(username="testuser", email="test@example.com")
        user.set_password("testpassword")
        db.session.add(user)
        db.session.commit()


if __name__ == "__main__":
    unittest.main()
