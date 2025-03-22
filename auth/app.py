from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from auth import init_app

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'postgresql://postgres:postgres@db:5432/wells_fargo')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')  # Change in production!
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 60 * 60 * 24  # 24 hours
    
    # Initialize auth module
    init_app(app)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return {'status': 'healthy', 'service': 'auth'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5053))
    app.run(host='0.0.0.0', port=port, debug=True)