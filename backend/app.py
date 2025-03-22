import json
import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from functools import wraps
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load configuration
CONFIG_PATH = os.environ.get('CONFIG_PATH', '../config.json')
try:
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    logger.info(f"Loaded configuration from {CONFIG_PATH}")
except Exception as e:
    logger.error(f"Error loading configuration: {str(e)}")
    config = {}

# Service URLs from environment variables or default from config
UNDERSTANDER_SERVICE = os.environ.get('UNDERSTANDER_SERVICE', config.get('services', {}).get('understander', {}).get('url', 'http://localhost:5052'))
RECOMMENDER_SERVICE = os.environ.get('RECOMMENDER_SERVICE', config.get('services', {}).get('recommender', {}).get('url', 'http://localhost:5051'))
AUTH_SERVICE = os.environ.get('AUTH_SERVICE', config.get('services', {}).get('auth', {}).get('url', 'http://localhost:5053'))

# JWT secret key
JWT_SECRET = os.environ.get('JWT_SECRET', 'your_jwt_secret_key_change_in_production')

# Decorator for routes that require authentication
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        try:
            # Decode token
            jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            
            # Alternatively, verify with auth service
            # response = requests.get(
            #     f"{AUTH_SERVICE}/api/v1/auth/check-auth",
            #     headers={"Authorization": f"Bearer {token}"},
            #     timeout=5
            # )
            # if not response.json().get('authenticated', False):
            #     raise Exception("Invalid token")
            
        except Exception as e:
            return jsonify({'error': f'Invalid authentication token: {str(e)}'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "backend"}), 200

@app.route('/api/v1/chat', methods=['POST'])
@jwt_required
def process_chat():
    """Process chat messages by forwarding to the understander service"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        message = data.get('message', '')
        session_id = data.get('session_id', None)
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Forward request to understander service
        response = requests.post(
            f"{UNDERSTANDER_SERVICE}/api/v1/understand",
            json={"message": message, "session_id": session_id},
            timeout=10
        )
        
        # Return understander response
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with understander service: {str(e)}")
        return jsonify({"error": f"Service communication error: {str(e)}"}), 500
    
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/recommendations', methods=['GET'])
@jwt_required
def get_recommendations():
    """Get recommendations based on user profile"""
    try:
        # Get user token for profile
        token = request.headers['Authorization'].split(' ')[1]
        
        # Request user profile from auth service
        persona_response = requests.get(
            f"{AUTH_SERVICE}/api/v1/auth/persona",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        if persona_response.status_code != 200:
            return jsonify({"error": "Could not retrieve user profile"}), 400
        
        user_profile = persona_response.json().get('persona', {})
        
        # Request recommendations from recommender service
        response = requests.post(
            f"{RECOMMENDER_SERVICE}/api/v1/generate",
            json={"profile": user_profile, "vector": user_profile.get('vector', [])},
            timeout=10
        )
        
        # Return recommender response
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with service: {str(e)}")
        return jsonify({"error": f"Service communication error: {str(e)}"}), 500
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/news', methods=['GET'])
@jwt_required
def get_news():
    """Get financial news articles"""
    try:
        # Request news from recommender service
        response = requests.get(
            f"{RECOMMENDER_SERVICE}/api/v1/news",
            timeout=5
        )
        
        # Return recommender response
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with recommender service: {str(e)}")
        return jsonify({"error": f"Service communication error: {str(e)}"}), 500
    
    except Exception as e:
        logger.error(f"Error getting news: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/products', methods=['GET'])
@jwt_required
def get_products():
    """Get all available financial products"""
    try:
        # Request products from recommender service
        response = requests.get(
            f"{RECOMMENDER_SERVICE}/api/v1/products",
            timeout=5
        )
        
        # Return recommender response
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with recommender service: {str(e)}")
        return jsonify({"error": f"Service communication error: {str(e)}"}), 500
    
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Proxy route for authentication
@app.route('/api/v1/auth/<path:subpath>', methods=['GET', 'POST'])
def auth_proxy(subpath):
    """Proxy requests to auth service"""
    try:
        # Forward headers and request data
        headers = {key: value for key, value in request.headers if key != 'Host'}
        
        # Construct URL
        url = f"{AUTH_SERVICE}/api/v1/auth/{subpath}"
        
        if request.method == 'GET':
            response = requests.get(
                url,
                headers=headers,
                params=request.args,
                timeout=10
            )
        else:  # POST
            response = requests.post(
                url,
                headers=headers,
                json=request.json,
                timeout=10
            )
        
        # Return auth service response
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with auth service: {str(e)}")
        return jsonify({"error": f"Service communication error: {str(e)}"}), 500
    
    except Exception as e:
        logger.error(f"Error in auth proxy: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# User profile route
@app.route('/api/v1/user/profile', methods=['GET'])
@jwt_required
def get_user_profile():
    """Get user profile"""
    try:
        # Get user token
        token = request.headers['Authorization'].split(' ')[1]
        
        # Request user profile from auth service
        response = requests.get(
            f"{AUTH_SERVICE}/api/v1/auth/user",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        
        # Return auth service response
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with auth service: {str(e)}")
        return jsonify({"error": f"Service communication error: {str(e)}"}), 500
    
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5050))
    
    # Run app
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')