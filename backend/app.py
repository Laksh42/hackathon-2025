from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs for local development
UNDERSTANDER_SERVICE_URL = "http://localhost:5051/process"
RECOMMENDER_SERVICE_URL = "http://localhost:5052/recommend"

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "backend-api"})

@app.route('/api/chat', methods=['POST'])
def process_chat():
    try:
        # Get chat data from request
        chat_data = request.json
        logger.info(f"Received chat data: {chat_data}")
        
        if not chat_data or 'conversation' not in chat_data:
            return jsonify({"error": "Invalid request format. 'conversation' field is required."}), 400
        
        # Pass the conversation to the understander service
        logger.info(f"Sending request to understander service at: {UNDERSTANDER_SERVICE_URL}")
        understander_response = requests.post(
            UNDERSTANDER_SERVICE_URL,
            json={"conversation": chat_data['conversation']}
        )
        
        if understander_response.status_code != 200:
            logger.error(f"Understander service error: {understander_response.text}")
            return jsonify({"error": f"Understander service error: {understander_response.text}"}), 500
        
        # Extract user vector from understander response
        user_data = understander_response.json()
        logger.info(f"Received user vector from understander: {user_data}")
        
        # Pass the user vector to the recommender service
        logger.info(f"Sending request to recommender service at: {RECOMMENDER_SERVICE_URL}")
        recommender_response = requests.post(
            RECOMMENDER_SERVICE_URL,
            json={"user_data": user_data}
        )
        
        if recommender_response.status_code != 200:
            logger.error(f"Recommender service error: {recommender_response.text}")
            return jsonify({"error": f"Recommender service error: {recommender_response.text}"}), 500
        
        # Return the recommendations
        recommendations = recommender_response.json()
        logger.info(f"Received recommendations: {recommendations}")
        return jsonify(recommendations)
    
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Connection error: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 503
    except Exception as e:
        error_msg = f"Error processing chat: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)