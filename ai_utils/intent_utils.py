import os
import json
import re
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np

from .embedding_utils import EmbeddingManager
from .llm_utils import LLMManager

class IntentClassifier:
    """Classifier for identifying user intents from messages"""
    
    def __init__(self, config_path: str = "../config.json"):
        self.config = self._load_config(config_path)
        self.intent_config = self.config.get("ai_models", {}).get("intent", {})
        
        # Initialize components
        self.embedding_manager = EmbeddingManager(config_path)
        self.llm_manager = LLMManager(config_path)
        
        # Load or initialize intents
        self.intents = self.intent_config.get("classes", DEFAULT_INTENTS)
        self.intent_examples = self.intent_config.get("examples", DEFAULT_INTENT_EXAMPLES)
        
        # Pre-compute embeddings for intent examples
        self._precompute_embeddings()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {
                "ai_models": {
                    "intent": {
                        "classes": DEFAULT_INTENTS,
                        "examples": DEFAULT_INTENT_EXAMPLES,
                        "threshold": 0.7
                    }
                }
            }
    
    def _precompute_embeddings(self):
        """Precompute embeddings for all intent examples"""
        self.example_embeddings = {}
        
        for intent, examples in self.intent_examples.items():
            if examples:
                self.example_embeddings[intent] = self.embedding_manager.get_embeddings(examples)
    
    def classify_intent_rule_based(self, text: str) -> str:
        """Classify intent using simple rule-based approach"""
        text = text.lower()
        
        if any(word in text for word in ["news", "article", "headline", "update"]):
            return "news_inquiry"
        
        if any(word in text for word in ["recommend", "suggestion", "advice", "what should"]):
            return "recommendation_request"
            
        if any(word in text for word in ["explain", "how", "what is", "tell me about"]):
            return "information_request"
            
        if any(word in text for word in ["hello", "hi", "hey", "greetings"]):
            return "greeting"
            
        if any(word in text for word in ["bye", "goodbye", "see you", "talk later"]):
            return "farewell"
            
        if any(word in text for word in ["thanks", "thank you", "appreciate"]):
            return "gratitude"
            
        if any(phrase in text for phrase in ["help me", "i need help", "can you help", "assist me"]):
            return "help_request"
            
        return "general_query"
    
    def classify_intent_embedding(self, text: str) -> Tuple[str, float]:
        """Classify intent using embedding similarity"""
        if not text:
            return "general_query", 0.0
            
        # Get embedding for input text
        text_embedding = self.embedding_manager.get_embedding(text)
        
        best_intent = "general_query"
        best_score = 0.0
        
        # Compare with each intent's examples
        for intent, embeddings in self.example_embeddings.items():
            for emb in embeddings:
                # Calculate cosine similarity
                similarity = np.dot(text_embedding, emb) / (np.linalg.norm(text_embedding) * np.linalg.norm(emb))
                
                if similarity > best_score:
                    best_score = similarity
                    best_intent = intent
        
        # If score below threshold, return general_query
        threshold = self.intent_config.get("threshold", 0.7)
        if best_score < threshold:
            return "general_query", best_score
            
        return best_intent, best_score
    
    def classify_intent_llm(self, text: str) -> str:
        """Classify intent using LLM"""
        if not text:
            return "general_query"
            
        # Create a prompt for intent classification
        intents_str = ", ".join(self.intents)
        prompt = f"""Classify the following user message into one of these intents: {intents_str}.
        
User message: "{text}"

Intent: """
        
        # Generate classification
        response = self.llm_manager.generate(prompt)
        
        # Extract the intent from the response
        if response:
            # Clean up response
            response = response.strip()
            
            # Check if response matches any intent
            for intent in self.intents:
                if intent.lower() in response.lower():
                    return intent
        
        # Default fallback
        return "general_query"
    
    def classify_intent(self, text: str, method: str = "hybrid") -> Dict[str, Any]:
        """Classify intent using the specified method"""
        if not text:
            return {"intent": "general_query", "confidence": 0.0, "method": method}
            
        if method == "rule":
            intent = self.classify_intent_rule_based(text)
            return {"intent": intent, "confidence": 1.0, "method": "rule"}
            
        elif method == "embedding":
            intent, confidence = self.classify_intent_embedding(text)
            return {"intent": intent, "confidence": float(confidence), "method": "embedding"}
            
        elif method == "llm":
            intent = self.classify_intent_llm(text)
            return {"intent": intent, "confidence": 0.9, "method": "llm"}
            
        elif method == "hybrid":
            # First try rule-based for efficiency
            rule_intent = self.classify_intent_rule_based(text)
            if rule_intent != "general_query":
                return {"intent": rule_intent, "confidence": 0.85, "method": "hybrid_rule"}
                
            # If rule-based didn't find a specific intent, try embedding
            intent, confidence = self.classify_intent_embedding(text)
            if intent != "general_query" and confidence > self.intent_config.get("threshold", 0.7):
                return {"intent": intent, "confidence": float(confidence), "method": "hybrid_embedding"}
                
            # If still not confident, use LLM for more complex cases
            llm_intent = self.classify_intent_llm(text)
            return {"intent": llm_intent, "confidence": 0.8, "method": "hybrid_llm"}
        
        # Default fallback
        return {"intent": "general_query", "confidence": 0.0, "method": "fallback"}
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using a simple approach"""
        # Use LLM for keyword extraction
        prompt = f"""Extract the 3-5 most important keywords from the following text. Return only the keywords separated by commas, with no additional text or explanation:

Text: "{text}"

Keywords:"""
        
        response = self.llm_manager.generate(prompt)
        
        if response:
            # Clean up response 
            keywords = [kw.strip() for kw in response.split(',')]
            return [kw for kw in keywords if kw]
        
        # Fallback to simple extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        words = [w for w in words if w not in STOPWORDS]
        return words[:5]  # Return top 5 words

# Default intents
DEFAULT_INTENTS = [
    "greeting", 
    "farewell", 
    "information_request", 
    "recommendation_request", 
    "news_inquiry", 
    "help_request", 
    "gratitude", 
    "general_query"
]

# Default examples for each intent
DEFAULT_INTENT_EXAMPLES = {
    "greeting": [
        "Hello there",
        "Hi, how are you?",
        "Good morning",
        "Hey, what's up?",
        "Greetings"
    ],
    "farewell": [
        "Goodbye",
        "See you later",
        "Have a nice day",
        "Bye bye",
        "Talk to you soon"
    ],
    "information_request": [
        "Can you tell me about retirement planning?",
        "What is a Roth IRA?",
        "How do mutual funds work?",
        "Explain stock market basics",
        "What's the difference between stocks and bonds?"
    ],
    "recommendation_request": [
        "What investments do you recommend?",
        "Should I invest in tech stocks?",
        "Give me some financial advice",
        "What's the best retirement plan for me?",
        "How should I allocate my portfolio?"
    ],
    "news_inquiry": [
        "What's the latest financial news?",
        "Tell me about recent market developments",
        "Any updates on the stock market?",
        "What's happening with interest rates?",
        "Are there any important financial headlines today?"
    ],
    "help_request": [
        "I need help with my investments",
        "Can you assist me with financial planning?",
        "Help me understand my options",
        "I'm struggling with budgeting",
        "I need guidance on saving money"
    ],
    "gratitude": [
        "Thank you so much",
        "Thanks for your help",
        "I appreciate your assistance",
        "That was helpful, thanks",
        "Thanks a lot"
    ],
    "general_query": [
        "What can you do?",
        "Tell me something",
        "I have a question",
        "Let's talk",
        "I'm just browsing"
    ]
}

# Stopwords for keyword extraction
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
    "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
    "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves", "tell", "get", "give", "see", "want", "look", "come", "take"
} 