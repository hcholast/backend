# extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
oauth = OAuth()
