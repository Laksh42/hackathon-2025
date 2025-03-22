from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from .models import db, User, UserPersona
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create auth blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize JWT
jwt = JWTManager()

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    # Validate email format
    if not EMAIL_REGEX.match(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password strength (min 8 chars, at least one number and letter)
    if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password):
        return jsonify({'error': 'Password must be at least 8 characters and contain both letters and numbers'}), 400
    
    # Check if user already exists
    existing_user = User.get_by_email(email)
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 409
    
    try:
        # Create new user
        user = User.create_user(email, password)
        
        # Generate access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
    
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return JWT token"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    # Find user by email
    user = User.get_by_email(email)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check password
    if not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    try:
        # Generate access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
    
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/check-persona', methods=['GET'])
@jwt_required()
def check_persona():
    """Check if the authenticated user has a persona vector"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user has persona
        persona = UserPersona.get_by_user_id(user_id)
        
        return jsonify({
            'has_persona': user.has_persona,
            'persona': persona.to_dict() if persona else None
        }), 200
    
    except Exception as e:
        logger.error(f"Error checking persona: {str(e)}")
        return jsonify({'error': 'Failed to check persona status'}), 500

@auth_bp.route('/save-persona', methods=['POST'])
@jwt_required()
def save_persona():
    """Save or update a user's financial persona vector"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get persona vector from request
        data = request.get_json()
        if not data or 'persona_vector' not in data:
            return jsonify({'error': 'Persona vector is required'}), 400
        
        persona_vector = data.get('persona_vector')
        
        # Save or update persona
        persona = UserPersona.create_or_update(user_id, persona_vector)
        
        return jsonify({
            'message': 'Persona saved successfully',
            'persona': persona.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error saving persona: {str(e)}")
        return jsonify({'error': 'Failed to save persona'}), 500

def init_app(app):
    """Initialize the auth module with the Flask app"""
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize JWT
    jwt.init_app(app)
    
    # Register blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Create db tables if they don't exist
    with app.app_context():
        db.create_all()