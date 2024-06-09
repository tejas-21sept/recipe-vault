import datetime
from functools import wraps

import jwt
from flask import current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity
from flask_jwt_extended import jwt_required as flask_jwt_required
from flask_jwt_extended import verify_jwt_in_request
from flask_login import current_user, login_user, logout_user

from app.extensions import login_manager
from app.models import User


def generate_jwt(user_id):
    expires = datetime.timedelta(days=1)
    access_token = create_access_token(identity=user_id, expires_delta=expires)
    return access_token


def jwt_required(fn):
    @wraps(fn)
    @flask_jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        return fn(current_user, *args, **kwargs)

    return wrapper


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from flask_jwt_extended import JWTManager, get_jwt_identity

from app.extensions import db
from app.models import User


def get_user_by_id(user_id):
    return db.session.get(User, int(user_id))


def get_current_user():
    current_user_id = get_jwt_identity()
    return db.session.get(User, current_user_id)
