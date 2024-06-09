import os
import unittest

from flask import json

from app import create_app
from app.extensions import db
from app.models import User


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "TESTING_DATABASE_URL"
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_user(self):
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
        with self.app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

        response = self.client.post(
            "/auth/login",
            data=json.dumps({"email": "test@example.com", "password": "testpassword"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json)

    def test_login_user_invalid(self):
        with self.app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

        response = self.client.post(
            "/auth/login",
            data=json.dumps({"email": "test@example.com", "password": "wrongpassword"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Invalid email or password")

    def test_logout_user(self):
        with self.app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

        response = self.client.post(
            "/auth/login",
            data=json.dumps({"email": "test@example.com", "password": "testpassword"}),
            content_type="application/json",
        )
        access_token = response.json["access_token"]

        response = self.client.post(
            "/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Logged out successfully")

    def test_register_user_existing_username(self):
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
        with self.app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

        response = self.client.post(
            "/auth/login",
            data=json.dumps({"email": "wrong@example.com", "password": "testpassword"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Invalid email or password")

    # def test_access_protected_route_after_logout(self):
    #     with self.app.app_context():
    #         user = User(username="testuser", email="test@example.com")
    #         user.set_password("testpassword")
    #         db.session.add(user)
    #         db.session.commit()

    #     response = self.client.post(
    #         "/auth/login",
    #         data=json.dumps({"email": "test@example.com", "password": "testpassword"}),
    #         content_type="application/json",
    #     )
    #     access_token = response.json["access_token"]

    #     response = self.client.post(
    #         "/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json["message"], "Logged out successfully")

    #     # Attempt to access a protected route after logout
    #     response = self.client.get(
    #         "/auth/protected_route", headers={"Authorization": f"Bearer {access_token}"}
    #     )
    #     self.assertEqual(response.status_code, 401)
    #     self.assertEqual(response.json["message"], "Token has expired or is invalid")

    # def test_access_protected_route_after_logout(self):
    #     with self.app.app_context():
    #         user = User(username="testuser", email="test@example.com")
    #         user.set_password("testpassword")
    #         db.session.add(user)
    #         db.session.commit()

    #     # Log in the user
    #     response = self.client.post(
    #         "/auth/login",
    #         data=json.dumps({"email": "test@example.com", "password": "testpassword"}),
    #         content_type="application/json",
    #     )
    #     access_token = response.json["access_token"]

    #     # Log out the user
    #     response = self.client.post(
    #         "/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json["message"], "Logged out successfully")

    #     # Attempt to access a protected route after logout
    #     response = self.client.get(
    #         "/auth/protected_route", headers={"Authorization": f"Bearer {access_token}"}
    #     )
    #     self.assertEqual(response.status_code, 401)
    #     self.assertEqual(response.json["message"], "Token has expired or is invalid")


if __name__ == "__main__":
    unittest.main()
