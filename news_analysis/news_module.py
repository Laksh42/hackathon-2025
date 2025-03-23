import numpy as np
import json
import os
import re
from collections import Counter
import math
from vector_db_connector import VectorDB

class NewsAnalyzer:
    """
    News analyzer class that processes financial news and extracts feature vectors using
    text processing techniques like TF-IDF and keyword matching.
    This is a simplified version that would typically use more sophisticated NLP.
    """
    def __init__(self, vector_db=None):
        """Initialize with a vector database connector"""
        self.vector_db = vector_db or VectorDB()
        
        # Financial keyword categories for vector representation
        self.keyword_categories = {
            'income': ['salary', 'income', 'earn', 'revenue', 'wage', 'paycheck', 'compensation', 'bonus', 'profit'],
            'spending': ['spend', 'purchase', 'buy', 'cost', 'expense', 'payment', 'fee', 'price', 'consumption'],
            'risk': ['risk', 'volatile', 'uncertainty', 'fluctuation', 'variability', 'danger', 'threat', 'exposure', 'stability'],
            'goals': ['goal', 'plan', 'future', 'aspiration', 'target', 'objective', 'aim', 'ambition', 'vision'],
            'savings': ['save', 'savings', 'invest', 'deposit', 'fund', 'reserve', 'accumulate', 'nest egg', 'portfolio'],
            'debt': ['debt', 'loan', 'borrow', 'credit', 'mortgage', 'obligation', 'liability', 'financing', 'interest rate']
        }
        
        # Sentiment lexicon - positive and negative financial terms
        self.sentiment_lexicon = {
            'positive': ['growth', 'increase', 'gain', 'profit', 'rally', 'recovery', 'upward', 'bullish', 'opportunity', 
                        'improvement', 'positive', 'strong', 'success', 'advance', 'advantage', 'benefit'],
            'negative': ['decline', 'decrease', 'loss', 'drop', 'bearish', 'recession', 'downward', 'crisis', 'risk', 
                        'downturn', 'negative', 'weak', 'failure', 'crash', 'default', 'deficit', 'problem']
        }
        
        # Financial entity types to track
        self.entity_types = ['company', 'market', 'sector', 'economic_indicator', 'financial_product']
        
        # Document corpus (for TF-IDF calculation)
        self.document_corpus = []
        
        # Import LLM utilities if available
        try:
            import sys
            import os
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
            from ai_utils.llm_utils import LLMManager
            self.llm_manager = LLMManager()
        except ImportError:
            self.llm_manager = None
        
    def preprocess_text(self, text):
        """
        Preprocesses text by lowercasing, removing punctuation, and tokenizing
        
        Args:
            text (str): Raw text
            
        Returns:
            list: Tokenized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split into tokens
        tokens = text.split()
        
        return tokens
        
    def calculate_tfidf(self, document, category_keywords):
        """
        Calculate TF-IDF scores for category keywords in the document
        
        Args:
            document (list): Tokenized document
            category_keywords (list): Keywords to calculate TF-IDF for
            
        Returns:
            float: TF-IDF score for the category
        """
        # Term frequency in document
        document_length = len(document)
        if document_length == 0:
            return 0.0
            
        # Count occurrences of category keywords
        keyword_count = sum(1 for token in document if token in category_keywords)
        
        # Calculate term frequency
        tf = keyword_count / document_length
        
        # Calculate inverse document frequency (simplified)
        # In a real implementation, this would use the full corpus
        matches_in_corpus = 0
        corpus_size = max(1, len(self.document_corpus))
        
        for doc in self.document_corpus:
            if any(keyword in doc for keyword in category_keywords):
                matches_in_corpus += 1
        
        # Add smoothing to avoid division by zero
        idf = math.log((corpus_size + 1) / (matches_in_corpus + 1)) + 1
        
        return tf * idf
    
    def extract_sentiment(self, tokens):
        """
        Extract sentiment score from tokens
        
        Args:
            tokens (list): Tokenized text
            
        Returns:
            float: Sentiment score (-1 to 1)
        """
        positive_count = sum(1 for token in tokens if token in self.sentiment_lexicon['positive'])
        negative_count = sum(1 for token in tokens if token in self.sentiment_lexicon['negative'])
        
        total_count = positive_count + negative_count
        
        if total_count == 0:
            return 0.0
            
        return (positive_count - negative_count) / total_count
    
    def process_news_article(self, article):
        """
        Process a news article and extract a feature vector
        
        Args:
            article (dict): News article with title, content, date, etc.
            
        Returns:
            dict: Processed article with feature vector
        """
        # Extract text from article
        title = article.get('title', '')
        content = article.get('content', '')
        summary = article.get('summary', '')
        
        # Create full text for analysis
        full_text = f"{title} {summary} {content}"
        
        # Preprocess text
        tokens = self.preprocess_text(full_text)
        
        # Update document corpus for future TF-IDF calculations
        self.document_corpus.append(tokens)
        
        # Initialize feature vector
        # [income_relevance, spending_relevance, risk_relevance, 
        #  goals_relevance, savings_relevance, debt_relevance]
        vector = [0.0] * 6
        
        # Calculate TF-IDF scores for each category
        for i, (category, keywords) in enumerate(self.keyword_categories.items()):
            vector[i] = self.calculate_tfidf(tokens, keywords)
        
        # Extract sentiment score
        sentiment = self.extract_sentiment(tokens)
        
        # Normalize vector values to 0-1 range
        max_value = max(vector) if max(vector) > 0 else 1.0
        vector = [min(1.0, v / max_value) for v in vector]
        
        # Create processed article
        processed_article = article.copy()
        processed_article['vector'] = vector
        processed_article['sentiment'] = sentiment
        processed_article['processed_date'] = os.environ.get('CURRENT_DATE', '2025-03-23')
        
        # Extract keywords for searchability
        all_keywords = []
        for category, keywords in self.keyword_categories.items():
            for keyword in keywords:
                if keyword in tokens:
                    all_keywords.append(keyword)
        
        # Store top keywords (unique)
        processed_article['keywords'] = list(set(all_keywords))
        
        # Store in vector DB
        self.vector_db.store_vector(processed_article)
        
        return processed_article
    
    def batch_process_news(self, articles):
        """Process a batch of news articles"""
        processed = []
        for article in articles:
            processed.append(self.process_news_article(article))
        return processed
    
    def get_relevant_news_for_vector(self, user_vector, top_n=3):
        """
        Get news articles relevant to a user vector
        
        Args:
            user_vector (list): User financial persona vector
            top_n (int): Number of articles to return
            
        Returns:
            list: Top N most relevant articles
        """
        return self.vector_db.query_similar_vectors(user_vector, top_n)
        
    def get_news_by_keywords(self, keywords, top_n=3):
        """
        Get news articles containing specific keywords
        
        Args:
            keywords (list): List of keywords to search for
            top_n (int): Number of articles to return
            
        Returns:
            list: Articles containing the keywords
        """
        matching_articles = []
        
        for article in self.vector_db.vectors:
            article_keywords = article.get('keywords', [])
            
            # Check if any of the search keywords match article keywords
            if any(keyword in article_keywords for keyword in keywords):
                matching_articles.append(article)
        
        # Return top N matching articles
        return matching_articles[:top_n]
        
    def get_relevant_news_for_vector_and_keywords(self, user_vector, keywords, top_n=3):
        """
        Get news articles relevant to both a user vector and containing specific keywords
        
        Args:
            user_vector (list): User financial persona vector
            keywords (list): List of keywords to search for
            top_n (int): Number of articles to return
            
        Returns:
            list: Top N most relevant articles that also match keywords
        """
        # Get articles by vector similarity
        vector_matches = self.vector_db.query_similar_vectors(user_vector, top_n * 2)  # Get more to filter
        
        # If no keywords provided, just return vector matches
        if not keywords or len(keywords) == 0:
            return vector_matches[:top_n]
            
        # Process keywords to lowercase for case-insensitive matching
        keywords_lower = [k.lower() for k in keywords]
        
        # Filter vector matches by keywords
        keyword_filtered = []
        
        for article in vector_matches:
            # Get article text
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            summary = article.get('summary', '').lower()
            article_keywords = [k.lower() for k in article.get('keywords', [])]
            
            # Check if any keyword matches in article text or keywords
            full_text = f"{title} {summary} {content}"
            if any(keyword in full_text for keyword in keywords_lower) or \
               any(keyword in article_keywords for keyword in keywords_lower):
                keyword_filtered.append(article)
        
        # If we don't have enough keyword matches, supplement with top vector matches
        if len(keyword_filtered) < top_n:
            # Get IDs of articles already in keyword_filtered
            filtered_ids = {article.get('id') for article in keyword_filtered}
            
            # Add vector matches that aren't already in keyword_filtered
            for article in vector_matches:
                if article.get('id') not in filtered_ids and len(keyword_filtered) < top_n:
                    keyword_filtered.append(article)
        
        return keyword_filtered[:top_n]
    
    def generate_article_summary(self, articles, options=None):
        """
        Generate a summary of one or more news articles
        
        Args:
            articles (list): List of news articles to summarize
            options (dict): Summarization options including:
                - max_length (int): Maximum length of summary in words
                - focus_areas (list): Areas to focus on in the summary
                - style (str): Summarization style (concise, informative, detailed)
                
        Returns:
            dict: Summary results including the summary text and metadata
        """
        if not articles:
            return {"summary": "", "error": "No articles provided"}
        
        # Set default options
        options = options or {}
        max_length = options.get('max_length', 150)
        focus_areas = options.get('focus_areas', [])
        style = options.get('style', 'informative')  # informative, concise, detailed
        
        # Check if we're summarizing a single article or multiple articles
        is_single_article = len(articles) == 1
        
        # Generate the summary using LLM if available
        if self.llm_manager:
            summary = self._generate_summary_with_llm(articles, is_single_article, max_length, focus_areas, style)
        else:
            # Fallback summary if LLM is not available
            summary = self._generate_fallback_summary(articles, is_single_article)
        
        # Extract common themes (using a simplified approach)
        themes = self._extract_themes_from_articles(articles)
        
        # Extract common keywords
        keywords = self._extract_keywords_from_articles(articles)
        
        # Determine overall sentiment
        sentiment = self._calculate_aggregate_sentiment(articles)
        
        return {
            "summary": summary,
            "article_count": len(articles),
            "themes": themes,
            "keywords": keywords,
            "sentiment": sentiment,
            "generated_at": os.environ.get('CURRENT_DATE', '2025-03-23')
        }
    
    def _generate_summary_with_llm(self, articles, is_single_article, max_length, focus_areas, style):
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
            Summarize the following financial news article in {max_length} words or less. 
            {style_instructions.get(style, style_instructions['informative'])}
            {focus_instructions}
            
            {combined_text}
            """
        else:
            prompt = f"""
            Synthesize a summary of the following {len(articles)} financial news articles in {max_length} words or less.
            Identify the common themes, key developments, and implications for financial markets or personal finance.
            {style_instructions.get(style, style_instructions['informative'])}
            {focus_instructions}
            
            {combined_text}
            """
        
        # Generate the summary
        return self.llm_manager.generate(prompt)
    
    def _generate_fallback_summary(self, articles, is_single_article):
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
    
    def _extract_themes_from_articles(self, articles):
        """Extract common themes from the articles"""
        # In a real implementation, this would use topic modeling or clustering
        # Here we use a simplified approach based on keywords and categories
        
        categories = {}
        for article in articles:
            category = article.get('category', 'general')
            categories[category] = categories.get(category, 0) + 1
        
        # Get the most common categories
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        # Map categories to themes
        theme_mapping = {
            'economy': 'Economic Developments',
            'markets': 'Market Trends',
            'stocks': 'Stock Market Performance',
            'real estate': 'Real Estate Market',
            'banking': 'Banking Sector News',
            'technology': 'Technology Sector Updates',
            'policy': 'Financial Policy Changes',
            'personal finance': 'Personal Finance Tips',
            'global markets': 'Global Market Trends',
            'finance': 'Financial Industry News'
        }
        
        themes = []
        for category, _ in sorted_categories[:3]:  # Get top 3 categories
            theme = theme_mapping.get(category, f"{category.title()} News")
            themes.append(theme)
        
        return themes
    
    def _extract_keywords_from_articles(self, articles):
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
    
    def _calculate_aggregate_sentiment(self, articles):
        """Calculate the aggregate sentiment across all articles"""
        sentiment_scores = []
        
        for article in articles:
            if 'sentiment' in article:
                if isinstance(article['sentiment'], (int, float)):
                    sentiment_scores.append(article['sentiment'])
                elif article['sentiment'] in ['positive', 'neutral', 'negative']:
                    # Convert text sentiment to numeric
                    sentiment_map = {'positive': 1.0, 'neutral': 0.0, 'negative': -1.0}
                    sentiment_scores.append(sentiment_map[article['sentiment']])
        
        # Calculate average sentiment
        if sentiment_scores:
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            
            # Convert to text category
            if avg_sentiment > 0.3:
                return 'positive'
            elif avg_sentiment < -0.3:
                return 'negative'
            else:
                return 'neutral'
        else:
            return 'neutral'  # Default if no sentiment scores available 