# routes/__init__.py

from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__)
chat_bp = Blueprint('chat', __name__)

# Import routes to register them with the blueprints
from .auth_routes import *
from .chat_routes import *
