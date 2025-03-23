from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
import os
import requests
from datetime import datetime, timedelta
import time
import threading
from news_module import NewsAnalyzer
from vector_db_connector import VectorDB
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Initialize services
vector_db = VectorDB()
news_analyzer = NewsAnalyzer(vector_db)

# Load configuration
CONFIG_PATH = os.environ.get('CONFIG_PATH', '../config.json')
try:
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    logger.info(f"Loaded configuration from {CONFIG_PATH}")
except Exception as e:
    logger.error(f"Error loading configuration: {str(e)}")
    config = {}

# Import AI utilities
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from ai_utils.llm_utils import LLMManager
    llm_manager = LLMManager(config_path=CONFIG_PATH)
    logger.info("Loaded LLM Manager")
except ImportError as e:
    logger.warning(f"Error importing LLM Manager: {str(e)}")
    llm_manager = None

# News API configuration
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', 'demo-key')
NEWS_API_URL = os.environ.get('NEWS_API_URL', 'https://newsapi.org/v2/everything')
NEWS_SOURCES = os.environ.get('NEWS_SOURCES', 'financial-times,bloomberg,cnbc,the-wall-street-journal,business-insider')
NEWS_FETCH_INTERVAL = int(os.environ.get('NEWS_FETCH_INTERVAL', 3600))  # Default: fetch every hour

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "news_analysis"}), 200

@app.route('/api/v1/news/personalized', methods=['POST'])
def get_personalized_news():
    """Get news articles personalized to a user's financial profile vector"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_vector = data.get('user_vector')
        
        if not user_vector:
            return jsonify({"error": "No user_vector provided"}), 400
        
        # Get number of articles to return (default: 3)
        top_n = data.get('limit', 3)
        
        # Get keywords if provided (optional)
        keywords = data.get('keywords', [])
        
        logger.info(f"Getting personalized news with vector: {user_vector[:3]}... and {len(keywords)} keywords")
        
        if keywords and len(keywords) > 0:
            # If keywords provided, get news by both vector and keywords
            relevant_news = news_analyzer.get_relevant_news_for_vector_and_keywords(
                user_vector, keywords, top_n
            )
            logger.info(f"Found {len(relevant_news)} articles using vector and keywords")
        else:
            # Get relevant news for the user vector only
            relevant_news = news_analyzer.get_relevant_news_for_vector(user_vector, top_n)
            logger.info(f"Found {len(relevant_news)} articles using vector only")
        
        return jsonify({"relevant_news": relevant_news}), 200
    
    except Exception as e:
        logger.error(f"Error getting personalized news: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/news/keywords', methods=['POST'])
def get_news_by_keywords():
    """Get news articles containing specific keywords"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        keywords = data.get('keywords', [])
        
        if not keywords:
            return jsonify({"error": "No keywords provided"}), 400
        
        # Get number of articles to return (default: 3)
        top_n = data.get('limit', 3)
        
        # Get news articles by keywords
        articles = news_analyzer.get_news_by_keywords(keywords, top_n)
        
        return jsonify({"news": articles}), 200
    
    except Exception as e:
        logger.error(f"Error getting news by keywords: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/news/process', methods=['POST'])
def process_news_articles():
    """Process and index a batch of news articles"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        articles = data.get('articles', [])
        
        if not articles:
            return jsonify({"error": "No articles provided"}), 400
        
        # Process articles
        processed_articles = news_analyzer.batch_process_news(articles)
        
        return jsonify({
            "status": "success", 
            "processed": len(processed_articles),
            "message": f"Successfully processed {len(processed_articles)} articles"
        }), 200
    
    except Exception as e:
        logger.error(f"Error processing news articles: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/news/fetch', methods=['POST'])
def fetch_latest_news():
    """Fetch the latest financial news from external API"""
    try:
        # Get query parameters
        data = request.json or {}
        query = data.get('query', 'finance OR investing OR economy OR stocks OR bonds OR market')
        days = int(data.get('days', 1))
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        # Format dates for API
        to_date_str = to_date.strftime('%Y-%m-%d')
        from_date_str = from_date.strftime('%Y-%m-%d')
        
        # Make request to news API
        params = {
            'q': query,
            'sources': NEWS_SOURCES,
            'from': from_date_str,
            'to': to_date_str,
            'language': 'en',
            'sortBy': 'publishedAt',
            'apiKey': NEWS_API_KEY
        }
        
        # Don't actually make an external API call in this mock version
        # In a real implementation, we would do:
        # response = requests.get(NEWS_API_URL, params=params)
        
        # Instead, generate mock news data
        mock_articles = generate_mock_news(5)
        
        # Process and store the articles
        processed_articles = news_analyzer.batch_process_news(mock_articles)
        
        return jsonify({
            "status": "success",
            "fetched": len(mock_articles),
            "processed": len(processed_articles),
            "message": f"Successfully fetched and processed {len(processed_articles)} articles"
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v1/news/summarize', methods=['POST'])
def summarize_news():
    """Generate a summary of one or more news articles"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        articles = data.get('articles', [])
        
        if not articles:
            return jsonify({"error": "No articles provided"}), 400
        
        # Get summarization options
        options = {
            'max_length': data.get('max_length', 150),
            'focus_areas': data.get('focus_areas', []),
            'style': data.get('style', 'informative')  # informative, concise, detailed
        }
        
        # Use the NewsAnalyzer to generate the summary
        summary_results = news_analyzer.generate_article_summary(articles, options)
        logger.info(f"Generated summary for {len(articles)} articles with {options['style']} style")
        
        # Return the results with a timestamp
        summary_results['timestamp'] = datetime.now().isoformat()
        
        return jsonify(summary_results), 200
    
    except Exception as e:
        logger.error(f"Error summarizing news: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

def generate_summary_with_llm(articles, is_single_article, max_length, focus_areas, style):
    """Generate a summary using the LLM Manager"""
    # Prepare the articles for summarization
    article_texts = []
    for article in articles:
        title = article.get('title', '')
        content = article.get('content', '')
        text = f"Title: {title}\nContent: {content}"
        article_texts.append(text)
    
    # Combine all article texts
    combined_text = "\n\n".join(article_texts)
    
    # Configure style instructions
    style_instructions = {
        'concise': "Keep the summary very brief, focusing only on the most critical points.",
        'informative': "Create a balanced summary that captures the key information clearly.",
        'detailed': "Provide a comprehensive summary that includes important details and context."
    }
    
    # Create focus area instructions if specified
    focus_instructions = ""
    if focus_areas:
        focus_instructions = f"Focus particularly on aspects related to: {', '.join(focus_areas)}."
    
    # Create the prompt based on single or multiple articles
    if is_single_article:
        prompt = f"""
        Summarize the following news article in {max_length} words or less. 
        {style_instructions.get(style, style_instructions['informative'])}
        {focus_instructions}
        
        {combined_text}
        """
    else:
        prompt = f"""
        Synthesize a summary of the following {len(articles)} news articles in {max_length} words or less.
        Identify the common themes, key differences, and most important information across all articles.
        {style_instructions.get(style, style_instructions['informative'])}
        {focus_instructions}
        
        {combined_text}
        """
    
    # Generate the summary
    return llm_manager.generate(prompt)

def generate_fallback_summary(articles, is_single_article):
    """Generate a basic summary without using LLM"""
    if is_single_article:
        # For a single article, use the summary field or the first paragraph
        article = articles[0]
        if article.get('summary'):
            return article['summary']
        elif article.get('content'):
            # Get first paragraph (up to 200 chars)
            content = article['content']
            first_para = content.split('\n')[0]
            return first_para[:200] + ('...' if len(first_para) > 200 else '')
        else:
            return "No content available for summarization."
    else:
        # For multiple articles, combine the titles
        titles = [article.get('title', 'Untitled article') for article in articles]
        return f"A collection of {len(articles)} articles about: {'; '.join(titles[:3])}{'...' if len(titles) > 3 else ''}"

def extract_keywords_from_articles(articles):
    """Extract common keywords from the articles"""
    all_keywords = []
    
    # Collect all keywords/tags from the articles
    for article in articles:
        if article.get('keywords'):
            all_keywords.extend(article['keywords'])
        elif article.get('tags'):
            all_keywords.extend(article['tags'])
    
    # Count occurrences of each keyword
    keyword_counts = {}
    for keyword in all_keywords:
        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    # Sort by frequency and return top 10
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    top_keywords = [k for k, v in sorted_keywords[:10]]
    
    return top_keywords

def generate_mock_news(count=5):
    """Generate mock news articles for testing"""
    topics = [
        "Federal Reserve Rate Decision",
        "Stock Market Rally",
        "Housing Market Trends",
        "Inflation Report",
        "Tech Sector Performance",
        "Banking Industry Update",
        "Cryptocurrency Developments",
        "Small Business Lending",
        "Retirement Planning Strategies",
        "Consumer Spending Trends"
    ]
    
    articles = []
    for i in range(count):
        topic_index = i % len(topics)
        article_id = f"mock-{int(time.time())}-{i}"
        
        article = {
            "id": article_id,
            "title": f"Latest on {topics[topic_index]}: What Investors Need to Know",
            "summary": f"New developments in {topics[topic_index]} could impact your financial decisions. Read our analysis.",
            "content": f"Financial experts are closely watching {topics[topic_index]} as new data reveals important trends. "
                      f"This could affect investment strategies across multiple sectors including technology, real estate, "
                      f"and consumer goods. Analysts recommend considering these factors in your financial planning.",
            "date": datetime.now().isoformat(),
            "url": f"https://example.com/financial-news/{article_id}",
            "category": "finance",
            "tags": ["finance", "investing", topics[topic_index].lower().replace(" ", "-")]
        }
        
        articles.append(article)
    
    return articles

def start_periodic_news_fetch():
    """Start a background thread to periodically fetch news"""
    def news_fetch_job():
        while True:
            try:
                logger.info("Starting scheduled news fetch")
                mock_articles = generate_mock_news(5)
                processed_articles = news_analyzer.batch_process_news(mock_articles)
                logger.info(f"Scheduled job: processed {len(processed_articles)} news articles")
                
                # Sleep for the configured interval
                time.sleep(NEWS_FETCH_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in scheduled news fetch: {str(e)}")
                # Sleep for a shorter time if there was an error
                time.sleep(300)  # 5 minutes
    
    # Start the thread
    thread = threading.Thread(target=news_fetch_job, daemon=True)
    thread.start()
    logger.info(f"Started periodic news fetch thread (interval: {NEWS_FETCH_INTERVAL}s)")

if __name__ == '__main__':
    # Load sample news if vector DB is empty
    if not vector_db.vectors:
        try:
            sample_news_path = os.path.join(os.path.dirname(__file__), '../recommender/news.json')
            with open(sample_news_path, 'r') as f:
                sample_news = json.load(f)
                # Correctly process the news data - it's an array, not an object with a 'news' property
                news_analyzer.batch_process_news(sample_news)
                logger.info(f"Loaded and processed {len(sample_news)} sample news articles")
        except Exception as e:
            logger.error(f"Error loading sample news: {str(e)}")
    
    # Start periodic news fetch
    start_periodic_news_fetch()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5055, debug=True) 