import os
import json
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingManager:
    """Handles text embeddings using various models"""
    
    def __init__(self, config_path: str = "../config.json"):
        self.config = self._load_config(config_path)
        self.model_name = self.config.get("ai_models", {}).get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        self.model = self._load_model()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"ai_models": {"embedding_model": "sentence-transformers/all-MiniLM-L6-v2"}}
            
    def _load_model(self) -> SentenceTransformer:
        """Load the embedding model"""
        try:
            return SentenceTransformer(self.model_name)
        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            # Fallback to a common model
            return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            
    def get_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for a list of texts"""
        if not texts:
            return []
        return self.model.encode(texts)
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        if not text:
            return np.zeros(384)  # Default dimension for the model
        return self.model.encode(text)
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return self._cosine_similarity(emb1, emb2)
    
    def similarities(self, query: str, texts: List[str]) -> List[float]:
        """Calculate cosine similarities between a query and multiple texts"""
        query_emb = self.get_embedding(query)
        text_embs = self.get_embeddings(texts)
        return [self._cosine_similarity(query_emb, text_emb) for text_emb in text_embs]
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def most_similar(self, query: str, texts: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find the most similar texts to a query"""
        if not texts or not query:
            return []
            
        similarities = self.similarities(query, texts)
        
        # Create pairs of (text, similarity)
        pairs = list(zip(texts, similarities))
        
        # Sort by similarity in descending order
        sorted_pairs = sorted(pairs, key=lambda x: x[1], reverse=True)
        
        # Return top_k results with text and score
        return [{"text": text, "score": float(score)} for text, score in sorted_pairs[:top_k]] 