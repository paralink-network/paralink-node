from sanic import Blueprint, response

auth_blueprint = Blueprint("auth_blueprint", url_prefix="/api/auth")
