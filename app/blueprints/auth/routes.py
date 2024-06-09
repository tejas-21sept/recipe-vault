from app.blueprints.auth import auth_bp
from app.blueprints.auth.views import (
    LoginAPI,
    LogoutAPI,
    ProtectedAPI,
    ProtectedRouteAPI,
    RegisterAPI,
)

# Register the view functions with their respective URL rules
register_view = RegisterAPI.as_view("register_api")
login_view = LoginAPI.as_view("login_api")
logout_view = LogoutAPI.as_view("logout_api")
protected_view = ProtectedAPI.as_view("protected_api")
protected_route_view = ProtectedRouteAPI.as_view("protected_route_api")

# Define URL routes for the authentication blueprint
auth_bp.add_url_rule("/register", view_func=register_view, methods=["POST"])
auth_bp.add_url_rule("/login", view_func=login_view, methods=["POST"])
auth_bp.add_url_rule("/logout", view_func=logout_view, methods=["POST"])
auth_bp.add_url_rule("/protected", view_func=protected_view, methods=["GET"])
auth_bp.add_url_rule(
    "/protected_route", view_func=protected_route_view, methods=["GET"]
)
