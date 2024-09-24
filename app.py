# app.py

from flask import Flask
from extensions import db, jwt, cors, oauth
from config import load_config
from models import User, ChatSession, ChatMessage
from routes import auth_bp, chat_bp
from groq import Groq

def create_app():
    app = Flask(__name__)
    config = load_config()

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatgpt.db'
    app.config['JWT_SECRET_KEY'] = config.get("JWT_SECRET_KEY", 'your_jwt_secret_key')
    app.secret_key = config.get("APP_SECRET_KEY", 'your_app_secret_key')

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, supports_credentials=True)
    oauth.init_app(app)

    # Register OAuth clients
    google = oauth.register(
        name='google',
        client_id=config.get("GOOGLE_CLIENT_ID"),
        client_secret=config.get("GOOGLE_CLIENT_SECRET"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
        }
    )

    # Save 'google' into app config or extensions
    app.oauth_clients = {'google': google}

    # Initialize the Groq client with the API key
    api_key = config.get("API_KEY")
    client = Groq(api_key=api_key)
    app.groq_client = client

    with app.app_context():
        db.create_all()

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
