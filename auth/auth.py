from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# Import models directly
from models import db, User, UserPersona
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create auth blueprint
auth_bp = Blueprint('auth', __name__)

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def init_app(app):
    """Initialize the auth module with the Flask app"""
    # Register blueprint
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    
    # Create db tables if they don't exist
    with app.app_context():
        db.create_all()

@auth_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "auth"}), 200

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """Register a new user"""
    # Handle OPTIONS request (preflight)
    if request.method == 'OPTIONS':
        response = jsonify({})
        return response, 200
    
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        response = jsonify({"error": "Missing email or password"})
        return response, 400
        
    email = data.get('email')
    password = data.get('password')
    username = data.get('username', email.split('@')[0])
    
    if User.query.filter_by(email=email).first():
        response = jsonify({"error": "User already exists"})
        return response, 409
        
    if User.query.filter_by(username=username).first():
        response = jsonify({"error": "Username already taken"})
        return response, 409
    
    try:
        # Create new user with required parameters
        new_user = User(email=email, password=password)
        new_user.username = username  # Set username after initialization

        db.session.add(new_user)
        db.session.commit()
        
        access_token = create_access_token(identity=new_user.id)
        response = jsonify({
            "message": "User registered successfully",
            "access_token": access_token,
            "user": new_user.to_dict(),
            "has_persona": False  # New users don't have a persona yet
        })
        return response, 201
    except Exception as e:
        db.session.rollback()
        response = jsonify({"error": str(e)})
        return response, 500

@auth_bp.route('/check-auth', methods=['GET'])
@jwt_required()
def check_auth():
    """Validate the JWT token and return user data"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get user from database
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                "authenticated": False,
                "error": "User not found"
            }), 404
        
        # Check if user has persona
        has_persona = bool(UserPersona.query.filter_by(user_id=user_id).first())
        
        return jsonify({
            "authenticated": True,
            "user": user.to_dict(),
            "has_persona": has_persona
        }), 200
    except Exception as e:
        return jsonify({
            "authenticated": False,
            "error": str(e)
        }), 401

@auth_bp.route('/persona', methods=['GET'])
@jwt_required()
def get_user_persona():
    """Get user persona data"""
    user_id = get_jwt_identity()
    
    # Get user persona
    persona = UserPersona.query.filter_by(user_id=user_id).first()
    
    if not persona:
        return jsonify({
            "error": "Persona not found"
        }), 404
    
    return jsonify({
        "persona": persona.to_dict()
    }), 200

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """Authenticate a user and return JWT token"""
    # Handle OPTIONS request (preflight)
    if request.method == 'OPTIONS':
        response = jsonify({})
        return response, 200
        
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        response = jsonify({"error": "Missing email or password"})
        return response, 400
        
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        response = jsonify({"error": "Invalid email or password"})
        return response, 401
        
    # Update last login time
    user.last_login = datetime.utcnow()
    
    # Check if user has a persona
    has_persona = bool(UserPersona.query.filter_by(user_id=user.id).first())
    
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    response = jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict(),
        "has_persona": has_persona
    })
    return response, 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    # Get user persona if exists
    persona = UserPersona.query.filter_by(user_id=user_id).first()
    
    return jsonify({
        "user": user.to_dict(),
        "persona": persona.to_dict() if persona else None
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    # Update user fields
    if 'username' in data and data['username'] != user.username:
        # Check if username is already taken
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already taken"}), 409
        user.username = data['username']
        
    # Save changes
    db.session.commit()
    
    return jsonify({
        "message": "Profile updated successfully",
        "user": user.to_dict()
    }), 200