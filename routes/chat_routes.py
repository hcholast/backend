# routes/chat_routes.py

from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import ChatSession, ChatMessage
from routes import chat_bp
from utils import generate_session_title

# Start a new chat session
@chat_bp.route('/start_session', methods=['POST'])
@jwt_required()
def start_session():
    user_id = get_jwt_identity()
    new_session = ChatSession(user_id=user_id)
    db.session.add(new_session)
    db.session.commit()

    return jsonify({"session_id": new_session.id})

# Chat route within a specific session
@chat_bp.route('/chat/<int:session_id>', methods=['POST'])
@jwt_required()
def chat(session_id):
    data = request.json
    message = data.get('message')
    user_id = get_jwt_identity()

    session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"msg": "Session not found or unauthorized"}), 404

    client = current_app.groq_client

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "you are a helpful assistant."},
            {"role": "user", "content": message}
        ],
        model="mixtral-8x7b-32768"
    )

    response = chat_completion.choices[0].message.content

    new_message = ChatMessage(
        session_id=session_id,
        message=message,
        response=response
    )
    db.session.add(new_message)
    db.session.commit()

    message_count = ChatMessage.query.filter_by(session_id=session_id).count()

    if message_count == 2 or message_count == 3:
        messages = ChatMessage.query.filter_by(session_id=session_id).limit(3).all()
        message_list = [
            {"message": msg.message, "response": msg.response} for msg in messages
        ]
        new_title = generate_session_title(message_list, client)

        session.title = new_title
        db.session.commit()

    return jsonify({"message": message, "response": response})

# Get all sessions for the logged-in user
@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
def sessions():
    user_id = get_jwt_identity()
    sessions = ChatSession.query.filter_by(user_id=user_id).all()
    session_list = [
        {
            "session_id": session.id,
            "created_at": session.created_at,
            "title": session.title
        } for session in sessions
    ]

    return jsonify(session_list)

# Get messages for a specific session
@chat_bp.route('/session/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session_messages(session_id):
    user_id = get_jwt_identity()
    session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()

    if not session:
        return jsonify({"msg": "Session not found or unauthorized"}), 404

    messages = ChatMessage.query.filter_by(session_id=session.id).all()
    message_list = [
        {
            "message": msg.message,
            "response": msg.response,
            "timestamp": msg.timestamp
        } for msg in messages
    ]

    return jsonify(message_list)

# Route to delete a chat session
@chat_bp.route('/delete_session/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    user_id = get_jwt_identity()

    # Find the session that matches the session_id and belongs to the logged-in user
    session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()

    if not session:
        return jsonify({"msg": "Session not found or unauthorized"}), 404

    # Delete all associated chat messages first
    ChatMessage.query.filter_by(session_id=session.id).delete()

    # Delete the chat session
    db.session.delete(session)
    db.session.commit()

    return jsonify({"msg": "Chat session deleted successfully"})
