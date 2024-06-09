import re

from flask import jsonify, request
from flask.views import MethodView
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import DataError, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.blueprints.auth import auth_bp
from app.blueprints.auth.utils import generate_jwt, jwt_required
from app.extensions import db
from app.models import User

# class RegisterAPI(MethodView):
#     def post(self):
#         try:
#             data = request.get_json()
#             if data is None:
#                 return jsonify({"message": "Request body must not be empty"}), 400

#             username = data.get("username")
#             email = data.get("email")
#             password = data.get("password")

#             if not username or not email or not password:
#                 return jsonify({"message": "Missing fields"}), 400

#             # Check if username or email already exists
#             if (
#                 User.query.filter_by(username=username).first()
#                 or User.query.filter_by(email=email).first()
#             ):
#                 return jsonify({"message": "Username or email already exists"}), 400

#             new_user = User(username=username, email=email)
#             new_user.set_password(password)
#             db.session.add(new_user)
#             db.session.commit()

#             return jsonify({"message": "User registered successfully"}), 201

#         except IntegrityError as e:
#             db.session.rollback()
#             if "UNIQUE constraint failed" in str(e.orig):
#                 return jsonify({"message": "Username or email already exists"}), 400
#             return jsonify({"message": "Database integrity error"}), 500
#         except DataError:
#             db.session.rollback()
#             return (
#                 jsonify({"message": "Data error, possibly data too long for a column"}),
#                 400,
#             )
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({"message": f"An error occurred: {str(e)}"}), 500


class RegisterAPI(MethodView):
    def post(self):
        if not request.is_json:
            return jsonify({"message": "Content-Type must be application/json"}), 415

        try:
            data = request.get_json()
            if data is None:
                return jsonify({"message": "Request body must not be empty"}), 400

            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            if not username:
                return jsonify({"message": "Missing username"}), 400
            if not email:
                return jsonify({"message": "Missing email"}), 400
            if not password:
                return jsonify({"message": "Missing password"}), 400

            if User.query.filter_by(username=username).first():
                return jsonify({"message": "Username already exists"}), 400
            if User.query.filter_by(email=email).first():
                return jsonify({"message": "Email already exists"}), 400

            # Validate password strength
            if not self.is_strong_password(password):
                return (
                    jsonify(
                        {
                            "message": "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character."
                        }
                    ),
                    400,
                )

            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            return jsonify({"message": "User registered successfully"}), 201

        except Exception as e:
            current_app.logger.error(f"Registration error: {str(e)}")
            return jsonify({"message": "Internal server error"}), 500

    def is_strong_password(self, password):
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True


class LoginAPI(MethodView):
    def post(self):
        if not request.is_json:
            return jsonify({"message": "Content-Type must be application/json"}), 415

        try:
            data = request.get_json()
            if data is None:
                return jsonify({"message": "Request body must not be empty"}), 400

            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return jsonify({"message": "Missing email or password"}), 400

            user = User.query.filter_by(email=email).first()
            if user is None or not user.check_password(password):
                return jsonify({"message": "Invalid email or password"}), 401

            login_user(user)
            access_token = generate_jwt(user.id)
            return jsonify({"access_token": access_token}), 200

        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            return jsonify({"message": "Internal server error"}), 500


class LogoutAPI(MethodView):
    @login_required
    def post(self):
        try:
            logout_user()
            return jsonify({"message": "Logged out successfully"}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500


from flask import jsonify
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required


class ProtectedRouteAPI(MethodView):
    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            if current_user_id is None:
                return jsonify({"message": "Token has expired or is invalid"}), 401
            return (
                jsonify(
                    {"message": f"User {current_user_id} accessed a protected route"}
                ),
                200,
            )
        except Exception as e:
            return jsonify({"message": str(e)}), 500


class ProtectedAPI(MethodView):
    @jwt_required
    def get(self, current_user):
        try:
            return jsonify({"message": f"Hello, {current_user.username}!"}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500
