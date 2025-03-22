import json
import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

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
    config = {
        "confidence_threshold": 0.65
    }

# Load product data
try:
    with open('products.json', 'r') as f:
        products = json.load(f)
    logger.info(f"Loaded products data")
except Exception as e:
    logger.error(f"Error loading products: {str(e)}")
    products = []

# Load news data
try:
    with open('news.json', 'r') as f:
        news = json.load(f)
    logger.info(f"Loaded news data")
except Exception as e:
    logger.error(f"Error loading news: {str(e)}")
    news = []

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "recommender"}), 200

@app.route('/api/v1/generate', methods=['POST'])
def generate_recommendations():
    """Generate recommendations based on user profile"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get user profile and vector
        user_profile = data.get('profile', {})
        user_vector = data.get('vector', None)
        
        if not user_vector:
            return jsonify({"error": "No user vector provided"}), 400
        
        # Convert user vector to numpy array
        user_vector_np = np.array(user_vector).reshape(1, -1)
        
        # Calculate similarity scores with each product
        recommendations = []
        for product in products:
            if 'vector' in product:
                product_vector = np.array(product['vector']).reshape(1, -1)
                
                # Calculate cosine similarity
                similarity = cosine_similarity(user_vector_np, product_vector)[0][0]
                
                # Add to recommendations if above threshold
                if similarity >= config.get('confidence_threshold', 0.65):
                    recommendations.append({
                        'product': {
                            'id': product.get('id'),
                            'name': product.get('name'),
                            'description': product.get('description'),
                            'features': product.get('features', []),
                            'vector': product.get('vector')
                        },
                        'confidence': float(similarity),
                        'explanation': generate_explanation(user_profile, product, similarity)
                    })
        
        # Sort recommendations by confidence
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Get relevant news
        relevant_news = get_relevant_news(user_profile)
        
        return jsonify({
            "recommendations": recommendations,
            "news": relevant_news
        }), 200
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

def generate_explanation(user_profile, product, confidence):
    """Generate explanation for why a product was recommended"""
    explanation = f"Based on your financial profile, this {product.get('name')} seems like a good fit for you."
    
    # Add details based on financial info
    financial_info = user_profile.get('financial_info', {})
    risk_profile = user_profile.get('risk_profile', 'moderate')
    goals = user_profile.get('financial_goals', [])
    
    # Add goal-specific explanation
    if 'retirement' in product.get('tags', []) and 'retirement' in goals:
        explanation += f" It aligns with your retirement planning goals."
    
    if 'investment' in product.get('tags', []) and 'investment' in goals:
        explanation += f" It matches your investment objectives."
    
    if 'home_purchase' in product.get('tags', []) and 'home_purchase' in goals:
        explanation += f" It can help with your home purchase plans."
    
    # Add risk profile explanation
    if 'conservative' in product.get('tags', []) and risk_profile == 'conservative':
        explanation += f" The conservative nature of this product matches your risk tolerance."
    
    if 'moderate' in product.get('tags', []) and risk_profile == 'moderate':
        explanation += f" This product's balanced risk profile is suitable for your moderate risk tolerance."
    
    if 'aggressive' in product.get('tags', []) and risk_profile == 'aggressive':
        explanation += f" This product's growth potential aligns with your higher risk tolerance."
    
    # Add confidence score context
    if confidence > 0.9:
        explanation += f" This recommendation has a very high confidence score of {confidence:.0%}."
    elif confidence > 0.8:
        explanation += f" This recommendation has a high confidence score of {confidence:.0%}."
    else:
        explanation += f" This recommendation has a confidence score of {confidence:.0%}."
    
    return explanation

def get_relevant_news(user_profile):
    """Get relevant news based on user profile"""
    # In a real implementation, this would filter news based on user interests
    # For now, just return all news
    return news

@app.route('/api/v1/products', methods=['GET'])
def get_products():
    """Get all available products"""
    return jsonify({"products": products}), 200

@app.route('/api/v1/news', methods=['GET'])
def get_news():
    """Get all available news"""
    return jsonify({"news": news}), 200

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5051))
    
    # Run app
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')