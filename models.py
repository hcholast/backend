# models.py

from datetime import datetime
from extensions import db

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)
    google_id = db.Column(db.String(200), unique=True, nullable=True)
    is_oauth_user = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if not self.password and not self.google_id:
            raise ValueError('User must have either a password or a google_id.')

# Define ChatSession model
class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    title = db.Column(
        db.String(100),
        default=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    )  # Initial title as date
    messages = db.relationship('ChatMessage', backref='session', lazy=True)

# Define ChatMessage model
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    message = db.Column(db.String, nullable=False)
    response = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
