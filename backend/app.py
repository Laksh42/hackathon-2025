import json
import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from functools import wraps
import jwt
import uuid
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True, origins="*")

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
NEWS_ANALYSIS_SERVICE = os.environ.get('NEWS_ANALYSIS_SERVICE', config.get('services', {}).get('news_analysis', {}).get('url', 'http://localhost:5055'))

# JWT secret key
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'VnbRyn2dIcom20/8Y0o9fQrg00Ew2RRPxA9Gj0CoGK0=')

# Add ai_utils to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try to import our AI utilities
try:
    from ai_utils.embedding_utils import EmbeddingManager
    from ai_utils.llm_utils import LLMManager
    
    # Initialize AI utilities
    EMBEDDING_MANAGER = EmbeddingManager(config_path=CONFIG_PATH)
    LLM_MANAGER = LLMManager(config_path=CONFIG_PATH)
    
    AI_UTILS_AVAILABLE = True
    logger.info("AI utilities loaded successfully")
except ImportError as e:
    logger.warning(f"AI utilities not available: {str(e)}. Using fallback methods.")
    AI_UTILS_AVAILABLE = False

# API Models
class Message(BaseModel):
    session_id: str
    message: str

class FinancialProfileRequest(BaseModel):
    session_id: str

class RecommendationRequest(BaseModel):
    session_id: str
    query: Optional[str] = None

class NewsRequest(BaseModel):
    keywords: Optional[List[str]] = None
    query: Optional[str] = None
    session_id: Optional[str] = None

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
def chat():
    """
    Handle chat messages and return AI responses along with relevant news
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.json
        
        if 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        message = data.get('message')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Get user from token
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({"error": "Authorization token is missing"}), 401
        
        try:
            # Verify token with auth service
            auth_response = requests.get(
                f"{AUTH_SERVICE}/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            
            if not auth_response.ok:
                return jsonify({"error": "Invalid or expired token"}), 401
            
            user_data = auth_response.json().get('user', {})
            user_id = user_data.get('id')
            
            if not user_id:
                return jsonify({"error": "User ID not found in token"}), 401
                
            # Get user persona if available
            persona_response = requests.get(
                f"{AUTH_SERVICE}/api/v1/auth/persona/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            
            user_persona = {}
            if persona_response.ok:
                user_persona = persona_response.json().get('persona', {})
                logger.info(f"Retrieved user persona for chat: {user_persona}")
            else:
                logger.warning(f"Failed to get user persona: {persona_response.status_code}")
            
            # Send message to understander service
            understander_response = requests.post(
                f"{UNDERSTANDER_SERVICE}/api/v1/understander/chat",
                json={
                    "message": message,
                    "session_id": session_id,
                    "user_id": user_id,
                    "user_persona": user_persona
                },
                timeout=10
            )
            
            if not understander_response.ok:
                logger.error(f"Understander error: {understander_response.status_code} - {understander_response.text}")
                return jsonify({"error": "Error processing message"}), 500
            
            response_data = understander_response.json()
            logger.info(f"Got understander response: {response_data}")
            
            # Check if we should include news or recommendations
            should_include_news = False
            should_include_recommendations = False
            news_keywords = []
            
            # Extract metadata and intent from understander response
            metadata = response_data.get('metadata', {})
            intent = metadata.get('intent', '')
            
            # Check if the response directly indicates news or recommendations
            is_news_query = metadata.get('is_news_query', False)
            is_recommendation_query = metadata.get('is_recommendation_query', False)
            
            # Get news keywords if available
            if 'news_keywords' in metadata:
                news_keywords = metadata.get('news_keywords', [])
                logger.info(f"Extracted news keywords: {news_keywords}")
            
            # Additional check based on intent
            news_intents = ['inquiry_news', 'market_update', 'investment_advice', 'economic_outlook']
            recommendation_intents = ['inquiry_recommendations', 'investment_advice', 'financial_planning']
            
            if is_news_query or any(intent_key in intent.lower() for intent_key in news_intents):
                should_include_news = True
                logger.info("This is a news-related query")
            
            if is_recommendation_query or any(intent_key in intent.lower() for intent_key in recommendation_intents):
                should_include_recommendations = True
                logger.info("This is a recommendation-related query")
            
            # Prepare response
            result = {
                "response_text": response_data.get('response_text', ''),
                "session_id": session_id
            }
            
            # Add news if relevant
            if should_include_news:
                try:
                    # Prepare request with user vector and keywords
                    news_request = {
                        "limit": 3
                    }
                    
                    # Add user vector if available
                    if user_persona and 'vector' in user_persona:
                        news_request["user_vector"] = user_persona.get('vector')
                    
                    # Add keywords if available
                    if news_keywords:
                        news_request["keywords"] = news_keywords
                    
                    logger.info(f"Fetching news with: {news_request}")
                    
                    # Get relevant news
                    news_response = requests.post(
                        f"{NEWS_ANALYSIS_SERVICE}/api/v1/news/personalized",
                        json=news_request,
                        timeout=5
                    )
                    
                    if news_response.ok:
                        news_data = news_response.json()
                        if 'relevant_news' in news_data and news_data['relevant_news']:
                            result['news'] = news_data['relevant_news']
                            logger.info(f"Added {len(news_data['relevant_news'])} news items to response")
                    else:
                        logger.error(f"News service error: {news_response.status_code} - {news_response.text}")
                except Exception as e:
                    logger.error(f"Error fetching news: {str(e)}")
            
            # Add recommendations if relevant
            if should_include_recommendations and user_persona:
                try:
                    # Get personalized recommendations
                    rec_request = {
                        "profile": user_persona,
                        "vector": user_persona.get('vector', []),
                        "limit": 3
                    }
                    
                    logger.info(f"Fetching recommendations with profile")
                    
                    rec_response = requests.post(
                        f"{RECOMMENDER_SERVICE}/api/v1/generate",
                        json=rec_request,
                        timeout=5
                    )
                    
                    if rec_response.ok:
                        rec_data = rec_response.json()
                        if 'recommendations' in rec_data and rec_data['recommendations']:
                            result['recommendations'] = rec_data['recommendations']
                            logger.info(f"Added {len(rec_data['recommendations'])} recommendations to response")
                    else:
                        logger.error(f"Recommender service error: {rec_response.status_code} - {rec_response.text}")
                except Exception as e:
                    logger.error(f"Error fetching recommendations: {str(e)}")
            
            return jsonify(result), 200
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Service communication error: {str(e)}")
            return jsonify({"error": "Error communicating with services"}), 500
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/recommendations', methods=['GET'])
@jwt_required
def get_recommendations():
    """Get recommendations based on user profile"""
    try:
        # Get user token for profile
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            logger.error("No token provided in Authorization header")
            return jsonify({"error": "Authentication token is missing"}), 401
        
        logger.info(f"Getting recommendations for token: {token[:10]}...")
        
        # Request user profile from auth service
        try:
            persona_response = requests.get(
                f"{AUTH_SERVICE}/api/v1/auth/persona",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            
            if persona_response.status_code != 200:
                logger.error(f"Failed to get persona: {persona_response.status_code} - {persona_response.text}")
                return jsonify({"error": f"Could not retrieve user profile: {persona_response.text}"}), 400
            
            logger.info(f"Got persona response: {persona_response.status_code}")
            user_profile = persona_response.json().get('persona', {})
            logger.info(f"User profile: {user_profile}")
            
            if not user_profile:
                logger.error("Empty profile returned from auth service")
                return jsonify({"error": "User profile is empty"}), 400
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with auth service: {str(e)}")
            return jsonify({"error": f"Failed to retrieve profile: {str(e)}"}), 500
        
        # Request recommendations from recommender service
        try:
            request_data = {
                "profile": user_profile,
                "vector": user_profile.get('vector', [])
            }
            logger.info(f"Sending to recommender: {request_data}")
            
            response = requests.post(
                f"{RECOMMENDER_SERVICE}/api/v1/generate",
                json=request_data,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Recommender error: {response.status_code} - {response.text}")
                return jsonify({"error": f"Failed to generate recommendations: {response.text}"}), response.status_code
            
            logger.info(f"Got recommender response with status: {response.status_code}")
            
            # Parse response
            try:
                recommender_data = response.json()
                logger.info(f"Recommendation data contains {len(recommender_data.get('recommendations', []))} items")
                return jsonify(recommender_data), 200
            except ValueError:
                logger.error(f"Invalid JSON from recommender: {response.text[:100]}")
                return jsonify({"error": "Invalid response from recommendation service"}), 500
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to recommender: {str(e)}")
            return jsonify({"error": f"Failed to generate recommendations: {str(e)}"}), 500
        
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

@app.route('/api/v1/personalized-news', methods=['GET'])
@jwt_required
def get_personalized_news():
    """Get news articles personalized to the user's financial profile"""
    try:
        # Get user token
        token = request.headers['Authorization'].split(' ')[1]
        
        # 1. Get user vector from auth service
        try:
            # First, get the user's profile from auth service
            profile_response = requests.get(
                f"{AUTH_SERVICE}/api/v1/auth/persona",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            
            if profile_response.status_code != 200:
                logger.error(f"Failed to get persona: {profile_response.status_code} - {profile_response.text}")
                return jsonify({"error": f"Could not retrieve user profile: {profile_response.text}"}), 400
            
            persona = profile_response.json().get('persona', {})
            logger.info(f"Got persona for news personalization: {persona}")
            
            # Extract user vector or use default if not available
            user_vector = persona.get('vector', [0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with auth service: {str(e)}")
            return jsonify({"error": f"Failed to retrieve profile: {str(e)}"}), 500
        
        # 2. Get personalized news from news analysis service
        try:
            response = requests.post(
                f"{NEWS_ANALYSIS_SERVICE}/api/v1/news/personalized",
                json={"user_vector": user_vector, "limit": 5},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"News analysis error: {response.status_code} - {response.text}")
                return jsonify({"error": f"Failed to get personalized news: {response.text}"}), response.status_code
            
            # Return the personalized news
            return jsonify(response.json()), 200
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with news analysis service: {str(e)}")
            return jsonify({"error": f"Service communication error: {str(e)}"}), 500
        
    except Exception as e:
        logger.error(f"Error getting personalized news: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/news/fetch', methods=['POST'])
@jwt_required
def fetch_latest_news():
    """Fetch the latest financial news from external APIs"""
    try:
        # Forward the request to the news analysis service
        response = requests.post(
            f"{NEWS_ANALYSIS_SERVICE}/api/v1/news/fetch",
            json=request.json,
            timeout=30  # Longer timeout for external API calls
        )
        
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with news analysis service: {str(e)}")
        return jsonify({"error": f"Service communication error: {str(e)}"}), 500
        
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/news/summarize', methods=['POST'])
@jwt_required
def summarize_news():
    """Generate a summary of news articles"""
    try:
        # Get request data
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Validate request data
        if 'articles' not in data or not data['articles']:
            return jsonify({"error": "No articles provided for summarization"}), 400
        
        # Get user token for personalization options if needed
        token = request.headers['Authorization'].split(' ')[1]
        
        # Prepare summarization options
        summarization_params = {
            'articles': data['articles'],
            'max_length': data.get('max_length', 150),
            'focus_areas': data.get('focus_areas', []),
            'style': data.get('style', 'informative')
        }
        
        # Add user profile to request if available and requested
        if data.get('personalize', False):
            try:
                # Get user profile from auth service
                profile_response = requests.get(
                    f"{AUTH_SERVICE}/api/v1/auth/persona",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                )
                
                if profile_response.status_code == 200:
                    persona = profile_response.json().get('persona', {})
                    
                    # Extract financial interests for focus areas
                    financial_interests = persona.get('financial_interests', {})
                    if financial_interests:
                        # Use top financial interests as focus areas if not specified
                        if not summarization_params['focus_areas']:
                            # Get areas with interest score > 0.6
                            high_interest_areas = [area for area, score in financial_interests.items() 
                                               if float(score) > 0.6]
                            summarization_params['focus_areas'] = high_interest_areas[:3]  # Top 3 areas
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Could not get user profile for personalized summarization: {str(e)}")
                # Continue without personalization
        
        # Forward the request to the news analysis service
        logger.info(f"Requesting news summary with params: {summarization_params}")
        response = requests.post(
            f"{NEWS_ANALYSIS_SERVICE}/api/v1/news/summarize",
            json=summarization_params,
            timeout=15
        )
        
        if response.status_code != 200:
            logger.error(f"News summarization error: {response.status_code} - {response.text}")
            return jsonify({"error": f"Failed to summarize news: {response.text}"}), response.status_code
        
        # Return the summary results
        return jsonify(response.json()), 200
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with news analysis service: {str(e)}")
        return jsonify({"error": f"Service communication error: {str(e)}"}), 500
        
    except Exception as e:
        logger.error(f"Error summarizing news: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/news/summarize-collection', methods=['POST'])
@jwt_required
def summarize_news_collection():
    """Generate a summary of a collection of news articles using their IDs"""
    try:
        # Get request data
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Validate request data
        if 'news_ids' not in data or not data['news_ids']:
            return jsonify({"error": "No news IDs provided for summarization"}), 400
        
        # Get user token for authentication
        token = request.headers['Authorization'].split(' ')[1]
        
        # First, get the news articles from the recommender service
        try:
            # Get all news articles
            news_response = requests.get(
                f"{RECOMMENDER_SERVICE}/api/v1/news",
                timeout=5
            )
            
            if news_response.status_code != 200:
                logger.error(f"Failed to get news: {news_response.status_code} - {news_response.text}")
                return jsonify({"error": f"Could not retrieve news articles: {news_response.text}"}), 400
            
            all_news = news_response.json().get('news', [])
            
            # Filter news by the requested IDs
            selected_news = []
            for news_id in data['news_ids']:
                for article in all_news:
                    if article.get('id') == news_id:
                        selected_news.append(article)
                        break
            
            if not selected_news:
                return jsonify({"error": "No articles found with the provided IDs"}), 404
            
            logger.info(f"Found {len(selected_news)} articles for summarization")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with recommender service: {str(e)}")
            return jsonify({"error": f"Failed to retrieve news articles: {str(e)}"}), 500
        
        # Prepare summarization options
        summarization_params = {
            'articles': selected_news,
            'max_length': data.get('max_length', 200),  # Slightly longer for collections
            'focus_areas': data.get('focus_areas', []),
            'style': data.get('style', 'informative')
        }
        
        # Add user profile to request if available and requested
        if data.get('personalize', True):  # Default to true for collections
            try:
                # Get user profile from auth service
                profile_response = requests.get(
                    f"{AUTH_SERVICE}/api/v1/auth/persona",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                )
                
                if profile_response.status_code == 200:
                    persona = profile_response.json().get('persona', {})
                    
                    # Extract financial interests for focus areas
                    financial_interests = persona.get('financial_interests', {})
                    if financial_interests:
                        # Use top financial interests as focus areas if not specified
                        if not summarization_params['focus_areas']:
                            # Get areas with interest score > 0.6
                            high_interest_areas = [area for area, score in financial_interests.items() 
                                               if float(score) > 0.6]
                            summarization_params['focus_areas'] = high_interest_areas[:3]  # Top 3 areas
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Could not get user profile for personalized summarization: {str(e)}")
                # Continue without personalization
        
        # Forward the request to the news analysis service
        logger.info(f"Requesting news collection summary with {len(selected_news)} articles")
        response = requests.post(
            f"{NEWS_ANALYSIS_SERVICE}/api/v1/news/summarize",
            json=summarization_params,
            timeout=15
        )
        
        if response.status_code != 200:
            logger.error(f"News summarization error: {response.status_code} - {response.text}")
            return jsonify({"error": f"Failed to summarize news collection: {response.text}"}), response.status_code
        
        # Add article IDs to the response
        summary_response = response.json()
        summary_response['article_ids'] = data['news_ids']
        
        # Return the summary results
        return jsonify(summary_response), 200
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with services: {str(e)}")
        return jsonify({"error": f"Service communication error: {str(e)}"}), 500
        
    except Exception as e:
        logger.error(f"Error summarizing news collection: {str(e)}")
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

@app.get("/")
async def root():
    """Service health check"""
    return {"status": "ok", "service": "backend"}

@app.get("/ping_services")
async def ping_services():
    """Ping all connected services to check their status"""
    results = {}
    
    services = config.get("services", {})
    
    for service_name, service_config in services.items():
        try:
            url = service_config.get("url", f"http://localhost:8000") + "/"
            timeout = service_config.get("timeout", 5)
            
            response = requests.get(url, timeout=timeout)
            results[service_name] = {
                "status": "ok" if response.status_code == 200 else "error",
                "code": response.status_code
            }
        except Exception as e:
            results[service_name] = {
                "status": "error",
                "message": str(e)
            }
    
    return {"services": results}

@app.post("/process_message")
async def process_message(message: Message):
    """
    Process a user message and return a response
    """
    try:
        session_id = message.session_id
        user_message = message.message
        
        # Call understander service to process the message
        understander_url = config["services"]["understander"]["url"] + "/process_message"
        timeout = config["services"]["understander"]["timeout"]
        
        understander_payload = {
            "session_id": session_id,
            "message": user_message
        }
        
        response = requests.post(
            understander_url, 
            json=understander_payload,
            timeout=timeout
        )
        
        if response.status_code != 200:
            logger.error(f"Error from understander service: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Error processing message with understander service")
        
        understander_response = response.json()
        
        # If the AI enhances the response, add it here
        if AI_UTILS_AVAILABLE and "response" in understander_response:
            try:
                # Check if we can enrich the response with AI insights
                user_intent = understander_response.get("intent", {}).get("primary_intent", "")
                
                # For general information requests, we can add more context
                if user_intent in ["inquiry_personal_finance", "general_query"]:
                    enriched_response = await enrich_response_with_ai(
                        user_message=user_message,
                        original_response=understander_response["response"],
                        session_id=session_id
                    )
                    understander_response["response"] = enriched_response
                    understander_response["ai_enhanced"] = True
            except Exception as e:
                logger.error(f"Error enhancing response with AI: {str(e)}")
        
        return understander_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_session")
async def create_session():
    """
    Create a new session
    """
    try:
        # Call understander service to create a session
        understander_url = config["services"]["understander"]["url"] + "/create_session"
        timeout = config["services"]["understander"]["timeout"]
        
        response = requests.post(understander_url, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"Error from understander service: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Error creating session with understander service")
        
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_session/{session_id}")
async def get_session(session_id: str):
    """
    Get a specific session by ID
    """
    try:
        # Call understander service to get the session
        understander_url = f"{config['services']['understander']['url']}/get_session/{session_id}"
        timeout = config["services"]["understander"]["timeout"]
        
        response = requests.get(understander_url, timeout=timeout)
        
        if response.status_code != 200:
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Session not found")
            logger.error(f"Error from understander service: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Error getting session from understander service")
        
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/end_session/{session_id}")
async def end_session(session_id: str):
    """
    End a specific session
    """
    try:
        # Call understander service to end the session
        understander_url = f"{config['services']['understander']['url']}/end_session/{session_id}"
        timeout = config["services"]["understander"]["timeout"]
        
        response = requests.delete(understander_url, timeout=timeout)
        
        if response.status_code != 200:
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Session not found")
            logger.error(f"Error from understander service: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Error ending session with understander service")
        
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/financial_profile")
async def get_financial_profile(request: FinancialProfileRequest):
    """
    Get financial profile for a session
    """
    try:
        session_id = request.session_id
        
        # Call understander service to get the user profile
        understander_url = f"{config['services']['understander']['url']}/user_profile/{session_id}"
        timeout = config["services"]["understander"]["timeout"]
        
        response = requests.get(understander_url, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"Error from understander service: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Error getting user profile from understander service")
        
        profile_data = response.json()
        
        # If AI is available, enrich the profile with additional insights
        if AI_UTILS_AVAILABLE and "profile" in profile_data:
            try:
                profile_data["profile"] = await enrich_profile_with_ai(profile_data["profile"], session_id)
            except Exception as e:
                logger.error(f"Error enriching profile with AI: {str(e)}")
        
        return profile_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting financial profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized recommendations based on user profile
    """
    try:
        session_id = request.session_id
        user_query = request.query
        
        # First get user profile from understander service
        understander_url = f"{config['services']['understander']['url']}/user_profile/{session_id}"
        timeout = config["services"]["understander"]["timeout"]
        
        profile_response = requests.get(understander_url, timeout=timeout)
        
        if profile_response.status_code != 200:
            logger.error(f"Error from understander service: {profile_response.text}")
            raise HTTPException(status_code=profile_response.status_code, detail="Error getting user profile from understander service")
        
        profile_data = profile_response.json()
        
        # Now call recommender service to get recommendations
        recommender_url = f"{config['services']['recommender']['url']}/recommend"
        timeout = config["services"]["recommender"]["timeout"]
        
        recommender_payload = {
            "session_id": session_id,
            "user_profile": profile_data.get("profile", {}),
            "max_items": 5
        }
        
        # Add user query if available for AI-powered recommendations
        if user_query:
            recommender_payload["user_query"] = user_query
        
        recommender_response = requests.post(
            recommender_url, 
            json=recommender_payload,
            timeout=timeout
        )
        
        if recommender_response.status_code != 200:
            logger.error(f"Error from recommender service: {recommender_response.text}")
            raise HTTPException(status_code=recommender_response.status_code, detail="Error getting recommendations from recommender service")
        
        return recommender_response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/news")
async def get_news(request: NewsRequest):
    """
    Get relevant news articles
    """
    try:
        keywords = request.keywords
        query_text = request.query
        session_id = request.session_id
        
        # Prepare user profile if session_id is provided
        user_profile = None
        if session_id:
            try:
                # Get user profile from understander service
                understander_url = f"{config['services']['understander']['url']}/user_profile/{session_id}"
                timeout = config["services"]["understander"]["timeout"]
                
                profile_response = requests.get(understander_url, timeout=timeout)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    user_profile = profile_data.get("profile", {})
            except Exception as e:
                logger.warning(f"Error getting user profile for news: {str(e)}")
        
        # Call news service to get news articles
        news_url = f"{config['services']['news']['url']}/search"
        timeout = config["services"]["news"]["timeout"]
        
        news_payload = {
            "keywords": keywords,
            "limit": 10
        }
        
        # Add user profile if available for personalization
        if user_profile:
            news_payload["user_profile"] = user_profile
        
        # Add query text for AI-powered search if available
        if query_text:
            news_payload["query_text"] = query_text
        
        news_response = requests.post(
            news_url, 
            json=news_payload,
            timeout=timeout
        )
        
        if news_response.status_code != 200:
            logger.error(f"Error from news service: {news_response.text}")
            raise HTTPException(status_code=news_response.status_code, detail="Error getting news from news service")
        
        return news_response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_news")
async def analyze_news(request: Request):
    """
    Analyze news articles and provide insights
    """
    try:
        data = await request.json()
        news_ids = data.get("news_ids", [])
        session_id = data.get("session_id")
        query = data.get("query")
        
        # Validate input
        if not news_ids:
            raise HTTPException(status_code=400, detail="No news IDs provided")
        
        # Prepare user profile if session_id is provided
        user_profile = None
        if session_id:
            try:
                # Get user profile from understander service
                understander_url = f"{config['services']['understander']['url']}/user_profile/{session_id}"
                timeout = config["services"]["understander"]["timeout"]
                
                profile_response = requests.get(understander_url, timeout=timeout)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    user_profile = profile_data.get("profile", {})
            except Exception as e:
                logger.warning(f"Error getting user profile for news analysis: {str(e)}")
        
        # Call news service to analyze news articles
        news_url = f"{config['services']['news']['url']}/analyze"
        timeout = config["services"]["news"]["timeout"]
        
        analyze_payload = {
            "news_ids": news_ids
        }
        
        # Add user profile if available for personalization
        if user_profile:
            analyze_payload["user_profile"] = user_profile
        
        # Add query if available for context
        if query:
            analyze_payload["query"] = query
        
        news_response = requests.post(
            news_url, 
            json=analyze_payload,
            timeout=timeout
        )
        
        if news_response.status_code != 200:
            logger.error(f"Error from news service: {news_response.text}")
            raise HTTPException(status_code=news_response.status_code, detail="Error analyzing news from news service")
        
        return news_response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def enrich_response_with_ai(user_message: str, original_response: str, session_id: str):
    """
    Enrich a response with AI-generated content
    """
    try:
        # Get user profile for context
        understander_url = f"{config['services']['understander']['url']}/user_profile/{session_id}"
        timeout = config["services"]["understander"]["timeout"]
        
        profile_response = requests.get(understander_url, timeout=timeout)
        user_profile = {}
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            user_profile = profile_data.get("profile", {})
        
        # Get session history for context
        history_url = f"{config['services']['understander']['url']}/get_session/{session_id}"
        history_response = requests.get(history_url, timeout=timeout)
        
        conversation_context = ""
        if history_response.status_code == 200:
            session_data = history_response.json()
            messages = session_data.get("messages", [])
            # Format last few messages as context
            conversation_messages = messages[-5:] if len(messages) > 5 else messages
            conversation_context = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in conversation_messages
            ])
        
        # Generate prompt for response enhancement
        prompt = f"""
        Enhance the following response to make it more personalized, informative, and helpful.
        Include relevant financial insights or tips if appropriate, but keep the response concise.
        
        User message: {user_message}
        
        Original response: {original_response}
        
        Recent conversation:
        {conversation_context}
        
        User profile: {json.dumps(user_profile) if user_profile else "Not available"}
        
        Enhanced response:
        """
        
        # Generate enhanced response
        enhanced_response = LLM_MANAGER.generate(prompt)
        
        return enhanced_response.strip()
    except Exception as e:
        logger.error(f"Error enriching response: {str(e)}")
        return original_response  # Fallback to original response on error

async def enrich_profile_with_ai(profile: Dict, session_id: str):
    """
    Enrich a user profile with AI-generated insights
    """
    try:
        # Get session history for context
        understander_url = f"{config['services']['understander']['url']}/get_session/{session_id}"
        timeout = config["services"]["understander"]["timeout"]
        
        history_response = requests.get(understander_url, timeout=timeout)
        
        conversation_context = ""
        if history_response.status_code == 200:
            session_data = history_response.json()
            messages = session_data.get("messages", [])
            # Extract user messages for context
            user_messages = [msg['content'] for msg in messages if msg['role'] == 'user']
            conversation_context = "\n".join(user_messages)
        
        # Generate prompt for profile enhancement
        prompt = f"""
        Based on the user profile and conversation history, provide additional financial insights 
        and recommendations for this user. Return the results as JSON with these fields:
        
        1. financial_summary: A brief summary of the user's financial situation
        2. strengths: Array of financial strengths
        3. improvement_areas: Array of areas that need improvement
        4. next_steps: Array of recommended next steps
        
        User profile: {json.dumps(profile)}
        
        Conversation history:
        {conversation_context}
        
        Enhanced profile insights (JSON only):
        """
        
        # Generate enhanced profile insights
        insights_json = LLM_MANAGER.generate(prompt)
        
        try:
            # Parse insights JSON
            insights = json.loads(insights_json)
            
            # Add insights to profile
            profile["ai_insights"] = insights
        except json.JSONDecodeError:
            logger.error("Failed to parse AI insights JSON")
            # Create a simple format if JSON parsing fails
            profile["ai_insights"] = {
                "financial_summary": "Based on the available information, we've analyzed your financial profile.",
                "strengths": [],
                "improvement_areas": [],
                "next_steps": ["Speak with a financial advisor for personalized guidance."]
            }
        
        return profile
    except Exception as e:
        logger.error(f"Error enriching profile: {str(e)}")
        return profile  # Return original profile on error

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5050))
    
    # Run app
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')