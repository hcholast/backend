# routes/auth_routes.py

from flask import request, jsonify, redirect, url_for, session, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models import User
from routes import auth_bp
import bcrypt
from authlib.common.security import generate_token

# OAuth routes
@auth_bp.route('/auth/google')
def auth_google():
    google = current_app.oauth_clients['google']
    
    # Generate a nonce and store it in the session
    nonce = generate_token()  # Corrected import
    session['nonce'] = nonce

    redirect_uri = url_for('auth.auth_google_callback', _external=True)
    return google.authorize_redirect(redirect_uri, nonce=nonce)

@auth_bp.route('/auth/google/callback')
def auth_google_callback():
    google = current_app.oauth_clients['google']
    
    try:
        # Get the token
        token = google.authorize_access_token()
        print(f"Token received: {token}")
        
        # Retrieve the nonce from session for verification
        nonce = session.get('nonce')
        if not nonce:
            return jsonify({"msg": "Nonce not found in session"}), 400
        
        # Parse the ID token and log it for debugging
        user_info = google.parse_id_token(token, nonce=nonce)
        print(f"User info: {user_info}")
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return jsonify({"msg": "Failed to authenticate."}), 400

    # Get user details
    email = user_info['email']
    name = user_info.get('name', '')
    google_id = user_info['sub']
    print(f"Google user details - Email: {email}, Name: {name}, Google ID: {google_id}")

    # Check if user exists in the database
    user = User.query.filter_by(email=email).first()

    if user:
        if not user.is_oauth_user:
            return jsonify({
                "msg": "Email already registered. Please log in using your username and password."
            }), 400
    else:
        user = User(
            email=email,
            username=name,
            google_id=google_id,
            is_oauth_user=True
        )
        db.session.add(user)
        db.session.commit()

    # Create JWT token
    access_token = create_access_token(identity=user.id)
    print(f"Access token created: {access_token}")

    # Store the token in the session (optional)
    session['access_token'] = access_token

    # Redirect to the frontend with the token as a query parameter
    return redirect(f'http://localhost:3000/oauth-success?token={access_token}')


# Register route
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({"msg": "Missing username, email, or password"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(
        username=username,
        email=email,
        password=hashed.decode('utf-8'),
        is_oauth_user=False
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201

# Login route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    if user:
        if user.is_oauth_user:
            return jsonify({"msg": "Please log in using Google OAuth."}), 400

        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            access_token = create_access_token(identity=user.id)
            return jsonify({"msg": f"Welcome back {username}", "access_token": access_token})
        else:
            return jsonify({"msg": "Invalid username or password"}), 401
    else:
        return jsonify({"msg": "User not found"}), 404

# Logout route
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Since JWTs are stateless, instruct the client to delete the token
    return jsonify({"msg": "Logged out successfully"}), 200
