import json
import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dialogue_manager import DialogueManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Load configuration
config_path = os.environ.get('CONFIG_PATH', '../config.json')
dialogue_manager = DialogueManager(config_path)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "understander"}), 200

@app.route('/api/v1/understand', methods=['POST'])
def understand_message():
    """Process user messages and respond with next dialogue action"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        message = data.get('message', '')
        session_id = data.get('session_id', None)
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Process message through dialogue manager
        response = dialogue_manager.process_message(session_id, message)
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/dialogue/state', methods=['GET'])
def get_dialogue_state():
    """Get the current state of a dialogue session"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({"error": "No session_id provided"}), 400
        
        session = dialogue_manager.get_session(session_id)
        
        return jsonify(session.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Error getting dialogue state: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/dialogue/reset', methods=['POST'])
def reset_dialogue():
    """Reset a dialogue session"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"error": "No session_id provided"}), 400
        
        # Create new session with same ID
        new_session = dialogue_manager.get_session(None)
        dialogue_manager.sessions[session_id] = new_session
        
        return jsonify({"status": "success", "new_session_id": new_session.session_id}), 200
    
    except Exception as e:
        logger.error(f"Error resetting dialogue: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/user/profile', methods=['POST'])
def get_user_profile():
    """Generate a user profile from dialogue history"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"error": "No session_id provided"}), 400
        
        # Check if session exists
        if session_id not in dialogue_manager.sessions:
            return jsonify({"error": f"Session {session_id} not found"}), 404
        
        # Generate user profile
        user_profile = dialogue_manager.create_user_profile(session_id)
        
        return jsonify(user_profile), 200
    
    except Exception as e:
        logger.error(f"Error generating user profile: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/user/vector', methods=['POST'])
def get_user_vector():
    """Extract user vector from dialogue history"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"error": "No session_id provided"}), 400
        
        # Check if session exists
        if session_id not in dialogue_manager.sessions:
            return jsonify({"error": f"Session {session_id} not found"}), 404
        
        # Extract user vector
        user_vector = dialogue_manager.extract_user_vector(session_id)
        
        return jsonify({"vector": user_vector}), 200
    
    except Exception as e:
        logger.error(f"Error extracting user vector: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5052))
    
    # Run app
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')