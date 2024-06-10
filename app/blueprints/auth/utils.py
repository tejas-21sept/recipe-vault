import datetime
from functools import wraps

import jwt
from flask import current_app, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity
from flask_jwt_extended import jwt_required as flask_jwt_required
from flask_jwt_extended import verify_jwt_in_request
from flask_login import current_user, login_user, logout_user

from app.extensions import db, login_manager
from app.models import User

def generate_jwt(user_id):
    """
    Generate a JWT for the given user ID with a 1-day expiration.
    
    Args:
        user_id (int): The ID of the user for whom to generate the token.
        
    Returns:
        str: The generated JWT.
    """
    expires = datetime.timedelta(days=1)
    return create_access_token(identity=user_id, expires_delta=expires)

def jwt_required(fn):
    """
    Custom decorator to ensure a valid JWT is present and retrieve the current user.
    
    Args:
        fn (function): The function to wrap with the JWT check.
        
    Returns:
        function: The wrapped function.
    """
    @wraps(fn)
    @flask_jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        return fn(current_user, *args, **kwargs)

    return wrapper

@login_manager.user_loader
def load_user(user_id):
    """
    Load a user from the database by their user ID.
    
    Args:
        user_id (int): The ID of the user to load.
        
    Returns:
        User: The loaded user instance or None if not found.
    """
    return User.query.get(int(user_id))

def get_user_by_id(user_id):
    """
    Retrieve a user from the database by their user ID.
    
    Args:
        user_id (int): The ID of the user to retrieve.
        
    Returns:
        User: The retrieved user instance or None if not found.
    """
    return db.session.get(User, int(user_id))

def get_current_user():
    """
    Retrieve the current user based on the JWT token.
    
    Returns:
        User: The current user instance or None if not found.
    """
    current_user_id = get_jwt_identity()
    return db.session.get(User, current_user_id)
