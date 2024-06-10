import re

from flask import current_app, jsonify, request
from flask.views import MethodView
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import DataError, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.blueprints.auth import auth_bp
from app.blueprints.auth.utils import generate_jwt, jwt_required
from app.extensions import db
from app.models import User
from app.utils import api_response


class RegisterAPI(MethodView):
    """
    API endpoint for user registration.
    """

    def post(self):
        """
        Handle POST requests for user registration.
        """
        if not request.is_json:
            return (
                jsonify(api_response(415, "Content-Type must be application/json")),
                415,
            )

        try:
            return self._process_registration()
        except Exception as e:
            current_app.logger.error(f"Registration error: {str(e)}")
            return jsonify(api_response(500, "Internal server error")), 500

    def _process_registration(self):
        """
        Process the registration data and register the user.
        """
        data = request.get_json()
        if data is None:
            return jsonify(api_response(400, "Request body must not be empty")), 400

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username:
            return jsonify(api_response(400, "Missing username")), 400
        if not email:
            return jsonify(api_response(400, "Missing email")), 400
        if not password:
            return jsonify(api_response(400, "Missing password")), 400

        if User.query.filter_by(username=username).first():
            return jsonify(api_response(400, "Username already exists")), 400
        if User.query.filter_by(email=email).first():
            return jsonify(api_response(400, "Email already exists")), 400

        # Validate password strength
        if not self.is_strong_password(password):
            return (
                jsonify(
                    api_response(
                        400,
                        "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character.",
                    )
                ),
                400,
            )

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return (
            jsonify(
                api_response(201, "User registered successfully", data=user.to_dict())
            ),
            201,
        )

    def is_strong_password(self, password):
        """
        Validate the strength of the given password.
        """
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        return bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))


class LoginAPI(MethodView):
    """
    API endpoint for user login.
    """

    def post(self):
        """
        Handle POST requests for user login.
        """
        if not request.is_json:
            return (
                jsonify(api_response(415, "Content-Type must be application/json")),
                415,
            )

        try:
            return self._process_login()
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            return jsonify(api_response(500, "Internal server error")), 500

    def _process_login(self):
        """
        Process the login data and authenticate the user.
        """
        data = request.get_json()
        if data is None:
            return jsonify(api_response(400, "Request body must not be empty")), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify(api_response(400, "Missing email or password")), 400

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            return jsonify(api_response(401, "Invalid email or password")), 401

        login_user(user)
        access_token = generate_jwt(user.id)
        return (
            jsonify(
                api_response(
                    200, "Login successful", data={"access_token": access_token}
                )
            ),
            200,
        )


class LogoutAPI(MethodView):
    """
    API endpoint for user logout.
    """

    @login_required
    def post(self):
        """
        Handle POST requests for user logout.
        """
        try:
            logout_user()
            return jsonify(api_response(200, "Logged out successfully")), 200
        except Exception as e:
            return jsonify(api_response(500, str(e))), 500


class ProtectedRouteAPI(MethodView):
    """
    API endpoint for accessing a protected route.
    """

    @jwt_required
    def get(self):
        """
        Handle GET requests for the protected route.
        """
        try:
            current_user_id = get_jwt_identity()
            if current_user_id is None:
                return (
                    jsonify(api_response(401, "Token has expired or is invalid")),
                    401,
                )
            return (
                jsonify(
                    api_response(
                        200, f"User {current_user_id} accessed a protected route"
                    )
                ),
                200,
            )
        except Exception as e:
            return jsonify(api_response(500, str(e))), 500


class ProtectedAPI(MethodView):
    """
    API endpoint for accessing a protected resource.
    """

    @jwt_required
    def get(self, current_user):
        """
        Handle GET requests for the protected resource.
        """
        try:
            return jsonify(api_response(200, f"Hello, {current_user.username}!")), 200
        except Exception as e:
            return jsonify(api_response(500, str(e))), 500
