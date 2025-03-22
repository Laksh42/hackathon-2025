from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models
from models import db
import auth

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Enable CORS with permissive settings
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///auth.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    jwt = JWTManager(app)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    auth.init_app(app)
    
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "service": "auth_root"})
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5053))
    app.run(host='0.0.0.0', port=port, debug=True)