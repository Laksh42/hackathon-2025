import os
import json
import logging
import random
import sys
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Financial Assistant News Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
CONFIG_PATH = os.environ.get("CONFIG_PATH", "../config.json")
try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    logger.info(f"Loaded configuration from {CONFIG_PATH}")
except Exception as e:
    logger.error(f"Error loading configuration: {str(e)}")
    config = {}

# Load news data
NEWS_DATA_PATH = os.path.join(os.path.dirname(__file__), "news.json")
try:
    with open(NEWS_DATA_PATH, "r") as f:
        news_data = json.load(f)
    logger.info(f"Loaded news data from {NEWS_DATA_PATH}")
except Exception as e:
    logger.warning(f"Error loading news data: {str(e)}. Creating sample data.")
    # Create sample data
    news_data = [
        {
            "id": "news_1",
            "title": "Fed Raises Interest Rates by 0.25%",
            "summary": "The Federal Reserve announced a quarter-point interest rate hike on Wednesday, its 10th increase since March 2022.",
            "content": "The Federal Reserve raised interest rates by 0.25% on Wednesday, bringing the target range for the federal funds rate to 5.25%-5.50%. The decision came as inflation has shown signs of moderating but remains above the central bank's 2% target. Fed Chair Jerome Powell indicated that future decisions would be data-dependent, with a focus on inflation and employment figures. Market reaction was mixed, with stocks initially falling before recovering later in the session.",
            "source": "Financial Times",
            "published_at": "2023-09-20T14:30:00Z",
            "url": "https://example.com/news/fed-raises-rates",
            "category": "economy",
            "sentiment": "neutral",
            "tags": ["federal reserve", "interest rates", "monetary policy", "inflation"],
            "relevance_score": 0.85
        },
        {
            "id": "news_2",
            "title": "Apple Unveils New iPhone with AI Features",
            "summary": "Apple's latest iPhone includes advanced AI capabilities aimed at improving user experience and battery life.",
            "content": "Apple introduced its latest iPhone lineup on Tuesday, highlighting new artificial intelligence features that promise to enhance user experience while improving battery efficiency. The new models include a more powerful chip dedicated to AI processing, enabling features like improved photography, real-time language translation, and predictive text that adapts to the user's writing style. Analysts noted that these AI features represent Apple's strategy to differentiate its products in an increasingly competitive smartphone market. The new iPhones will be available starting next month, with prices ranging from $799 to $1,299.",
            "source": "Tech Review",
            "published_at": "2023-09-19T18:15:00Z",
            "url": "https://example.com/news/apple-ai-iphone",
            "category": "technology",
            "sentiment": "positive",
            "tags": ["apple", "iphone", "artificial intelligence", "technology"],
            "relevance_score": 0.72
        },
        {
            "id": "news_3",
            "title": "Housing Market Shows Signs of Cooling",
            "summary": "After months of record-breaking prices, the housing market is showing signs of normalization with inventory increasing.",
            "content": "The U.S. housing market is showing signs of cooling after nearly two years of record-breaking price increases. According to the latest data, home inventory has increased by 15% compared to last year, while the rate of price growth has slowed significantly. Analysts attribute this shift to higher mortgage rates, which have risen to their highest level in 15 years, reducing affordability for many potential buyers. Regional variations remain significant, with some markets experiencing more pronounced cooling than others. Economists suggest this represents a normalization rather than a crash, with prices expected to stabilize rather than decline sharply in most regions.",
            "source": "Housing Wire",
            "published_at": "2023-09-18T10:45:00Z",
            "url": "https://example.com/news/housing-market-cooling",
            "category": "real estate",
            "sentiment": "neutral",
            "tags": ["housing market", "real estate", "mortgage rates", "home prices"],
            "relevance_score": 0.91
        },
        {
            "id": "news_4",
            "title": "Major Bank Announces Fee-Free Checking for Students",
            "summary": "A leading national bank has introduced a new checking account with no fees for college students.",
            "content": "One of the nation's largest banks announced yesterday a new checking account program specifically designed for college students, featuring no monthly maintenance fees, free overdraft protection, and reimbursement for up to five ATM fees per month from non-network ATMs. The program also includes a mobile banking app with special budgeting features tailored to student needs. Financial education experts praised the move, noting that it could help students build healthy financial habits while avoiding common banking pitfalls that often affect young adults. To qualify, customers must provide proof of enrollment in a qualifying educational institution.",
            "source": "Banking Daily",
            "published_at": "2023-09-17T09:30:00Z",
            "url": "https://example.com/news/bank-student-accounts",
            "category": "banking",
            "sentiment": "positive",
            "tags": ["banking", "student finance", "checking accounts", "financial services"],
            "relevance_score": 0.88
        },
        {
            "id": "news_5",
            "title": "Global Markets React to Economic Data from China",
            "summary": "International markets showed mixed reactions to weaker-than-expected economic indicators from China.",
            "content": "Global financial markets displayed mixed reactions today following the release of economic data from China that fell short of analyst expectations. China's industrial output grew by 4.5% year-over-year in August, below the forecasted 5.2%, while retail sales increased by 2.5%, missing the projected 3.0% growth. Asian markets closed mostly lower, with the Shanghai Composite Index falling 1.2% and the Hang Seng dropping 0.8%. European markets showed resilience, with modest gains across major indices, while U.S. futures indicated a slightly lower open. Commodities were notably affected, with oil prices declining more than 2% on concerns about Chinese demand. Economists are closely watching for any policy responses from Chinese authorities, including potential stimulus measures.",
            "source": "Global Markets Today",
            "published_at": "2023-09-16T16:00:00Z",
            "url": "https://example.com/news/markets-china-data",
            "category": "global markets",
            "sentiment": "negative",
            "tags": ["china", "global economy", "markets", "economic indicators"],
            "relevance_score": 0.78
        }
    ]
    # Save sample data
    try:
        with open(NEWS_DATA_PATH, "w") as f:
            json.dump(news_data, f, indent=2)
        logger.info(f"Created and saved sample news data to {NEWS_DATA_PATH}")
    except Exception as e:
        logger.error(f"Error saving sample news data: {str(e)}")

# Add ai_utils to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try to import our AI utilities
try:
    from ai_utils.embedding_utils import EmbeddingManager
    from ai_utils.llm_utils import LLMManager
    from ai_utils.rag_utils import RAGManager
    from ai_utils.vector_store import VectorStore
    
    # Initialize AI utilities
    EMBEDDING_MANAGER = EmbeddingManager(config_path=CONFIG_PATH)
    LLM_MANAGER = LLMManager(config_path=CONFIG_PATH)
    
    # Initialize vector store for news
    VECTOR_STORE = VectorStore(
        collection_name="financial_news",
        embedding_manager=EMBEDDING_MANAGER,
        config_path=CONFIG_PATH
    )
    
    # Index news data if not already indexed
    if VECTOR_STORE.count() == 0:
        # Index news articles
        texts = []
        metadatas = []
        ids = []
        
        for article in news_data:
            # Combine title and content for better embedding
            text = f"{article['title']}. {article['content']}"
            texts.append(text)
            
            # Store metadata
            metadata = {
                "id": article["id"],
                "title": article["title"],
                "summary": article["summary"],
                "source": article["source"],
                "published_at": article["published_at"],
                "category": article["category"],
                "sentiment": article["sentiment"],
                "tags": ",".join(article["tags"]),
                "url": article["url"]
            }
            metadatas.append(metadata)
            ids.append(article["id"])
        
        # Add to vector store
        VECTOR_STORE.add(texts=texts, metadatas=metadatas, ids=ids)
        logger.info(f"Indexed {len(texts)} news articles in vector store")
    
    AI_UTILS_AVAILABLE = True
    logger.info("AI utilities loaded successfully")
except ImportError as e:
    logger.warning(f"AI utilities not available: {str(e)}. Using fallback methods.")
    AI_UTILS_AVAILABLE = False
    EMBEDDING_MANAGER = None
    LLM_MANAGER = None
    VECTOR_STORE = None

# API Models
class NewsQuery(BaseModel):
    keywords: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    sentiment: Optional[str] = None
    limit: Optional[int] = 10
    query_text: Optional[str] = None
    user_profile: Optional[Dict[str, Any]] = None

class NewsAnalysisRequest(BaseModel):
    news_ids: List[str]
    user_profile: Optional[Dict[str, Any]] = None
    query: Optional[str] = None

@app.get("/")
def root():
    """Service health check"""
    return {"status": "ok", "service": "news"}

@app.get("/news")
def get_news():
    """Get all available news articles"""
    return {"news": news_data, "count": len(news_data)}

@app.post("/search")
def search_news(query: NewsQuery):
    """
    Search for news articles
    """
    # If AI is available and we have query text, use semantic search
    if AI_UTILS_AVAILABLE and query.query_text and VECTOR_STORE:
        try:
            return search_news_with_ai(query)
        except Exception as e:
            logger.error(f"Error searching news with AI: {str(e)}")
            # Fall back to rule-based search
            
    # Use rule-based search
    return search_news_rule_based(query)

@app.post("/analyze")
def analyze_news(request: NewsAnalysisRequest):
    """
    Analyze news articles and provide insights
    """
    # Validate input
    if not request.news_ids:
        raise HTTPException(status_code=400, detail="No news IDs provided")
    
    # Find the news articles
    articles = []
    for article_id in request.news_ids:
        for article in news_data:
            if article["id"] == article_id:
                articles.append(article)
                break
    
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found for the provided IDs")
    
    # If AI is available, use it for analysis
    if AI_UTILS_AVAILABLE and LLM_MANAGER:
        try:
            return analyze_news_with_ai(articles, request.user_profile, request.query)
        except Exception as e:
            logger.error(f"Error analyzing news with AI: {str(e)}")
            # Fall back to basic analysis
    
    # Basic analysis without AI
    categories = {}
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    tags = {}
    
    for article in articles:
        # Count categories
        category = article.get("category", "uncategorized")
        categories[category] = categories.get(category, 0) + 1
        
        # Count sentiments
        sentiment = article.get("sentiment", "neutral")
        sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        
        # Count tags
        for tag in article.get("tags", []):
            tags[tag] = tags.get(tag, 0) + 1
    
    return {
        "articles_count": len(articles),
        "categories": categories,
        "sentiments": sentiments,
        "common_tags": sorted(tags.items(), key=lambda x: x[1], reverse=True)[:5],
        "summary": f"Analysis of {len(articles)} articles shows the most common category is {max(categories, key=categories.get)} and the dominant sentiment is {max(sentiments, key=sentiments.get)}."
    }

def search_news_with_ai(query: NewsQuery):
    """
    Search for news using AI-powered semantic search
    """
    search_query = query.query_text
    
    # Enhance with user profile if available
    if query.user_profile:
        # Extract financial interests from user profile
        interests = []
        for category, score in query.user_profile.get("financial_interests", {}).items():
            if score > 0.6:  # Only include high-interest categories
                interests.append(category)
        
        if interests:
            search_query = f"{search_query} related to {', '.join(interests)}"
    
    # Use vector store for semantic search
    search_results = VECTOR_STORE.search(
        query_texts=[search_query],
        n_results=query.limit or 10,
        where=get_search_filters(query)
    )
    
    if not search_results or not search_results.get("ids"):
        return {"news": [], "count": 0}
    
    # Process results
    results = []
    for i, doc_id in enumerate(search_results["ids"][0]):
        # Find the original article
        for article in news_data:
            if article["id"] == doc_id:
                # Add relevance score from search results
                article_copy = article.copy()
                article_copy["relevance_score"] = float(search_results["distances"][0][i])
                results.append(article_copy)
                break
    
    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    return {"news": results, "count": len(results)}

def search_news_rule_based(query: NewsQuery):
    """
    Search for news using rule-based approach
    """
    results = []
    
    # Apply filters
    for article in news_data:
        # Filter by keywords
        if query.keywords and not any(keyword.lower() in article["title"].lower() or 
                                     keyword.lower() in article["content"].lower()
                                     for keyword in query.keywords):
            continue
        
        # Filter by categories
        if query.categories and article.get("category") not in query.categories:
            continue
        
        # Filter by sentiment
        if query.sentiment and article.get("sentiment") != query.sentiment:
            continue
        
        # Add to results
        results.append(article)
    
    # Sort by published date (newest first)
    results.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    
    # Apply limit
    limit = query.limit or 10
    results = results[:limit]
    
    return {"news": results, "count": len(results)}

def get_search_filters(query: NewsQuery):
    """
    Construct filters for vector store search
    """
    filters = {}
    
    if query.categories:
        filters["category"] = {"$in": query.categories}
    
    if query.sentiment:
        filters["sentiment"] = query.sentiment
    
    return filters if filters else None

def analyze_news_with_ai(articles, user_profile=None, query=None):
    """
    Analyze news articles using AI
    """
    # Combine article content
    combined_content = "\n\n".join([
        f"Title: {article['title']}\nSummary: {article['summary']}\nCategory: {article['category']}\n"
        f"Source: {article['source']}\nDate: {article['published_at']}\n"
        f"Content: {article['content']}"
        for article in articles
    ])
    
    # Create prompt for analysis
    prompt = f"""
    Analyze the following financial news articles and provide insights:
    
    {combined_content}
    
    {f"User query: {query}" if query else ""}
    
    {f"User profile: {json.dumps(user_profile)}" if user_profile else ""}
    
    Please provide:
    1. A concise summary (2-3 sentences) of the key themes across these articles
    2. The potential impact on financial markets or personal finance
    3. Important trends identified in these news items
    4. Recommended actions for investors or financial consumers
    5. Any notable contrasts or contradictions between the articles
    
    Format your response as JSON with these keys: summary, market_impact, trends, recommendations, contradictions
    """
    
    # Generate analysis
    analysis_response = LLM_MANAGER.generate(prompt)
    
    try:
        # Parse JSON response
        analysis = json.loads(analysis_response)
    except json.JSONDecodeError:
        logger.error("Failed to parse AI analysis as JSON")
        # Create a simple format
        analysis = {
            "summary": "Analysis of the provided news articles shows several key financial trends.",
            "market_impact": "These events may impact various market segments differently.",
            "trends": ["Economic policy changes", "Technology advancements", "Market fluctuations"],
            "recommendations": ["Monitor market developments", "Consider diversification strategies"],
            "contradictions": "Some sources present conflicting outlooks on economic growth."
        }
    
    # Add metadata
    result = {
        "articles_count": len(articles),
        "analysis": analysis,
        "categories": list(set(article.get("category", "uncategorized") for article in articles)),
        "sources": list(set(article.get("source", "unknown") for article in articles)),
        "date_range": {
            "oldest": min((article.get("published_at", "2023-01-01") for article in articles), default="2023-01-01"),
            "newest": max((article.get("published_at", "2023-01-01") for article in articles), default="2023-01-01")
        }
    }
    
    return result

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5054))
    uvicorn.run(app, host="0.0.0.0", port=port) 