from flask import Blueprint

# Initialize the Blueprint for authentication
auth_bp = Blueprint('auth', __name__, template_folder='templates')

# Import views to register routes with the Blueprint
from . import views
