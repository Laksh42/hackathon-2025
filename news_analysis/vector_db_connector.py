import numpy as np
import json
import os

class VectorDB:
    """
    Mock in-memory vector database for storing and retrieving news articles
    In a real implementation, this would connect to Elasticsearch, Faiss, or another vector DB
    """
    
    def __init__(self, db_file=None):
        """Initialize the vector database"""
        self.db_file = db_file or 'news_vectors.json'
        self.vectors = []
        
        # Load existing database if it exists
        self._load_db()
    
    def _load_db(self):
        """Load vector database from disk if it exists"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    self.vectors = json.load(f)
        except Exception as e:
            print(f"Error loading vector DB: {e}")
            self.vectors = []
    
    def _save_db(self):
        """Save vector database to disk"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.vectors, f, indent=2)
        except Exception as e:
            print(f"Error saving vector DB: {e}")
    
    def store_vector(self, article):
        """
        Store an article with its feature vector in the database
        
        Args:
            article (dict): Article with 'vector' field
        """
        if 'vector' not in article:
            raise ValueError("Article must have a 'vector' field")
        
        # Check if article already exists (by id)
        article_id = article.get('id')
        if article_id:
            # Update existing article
            for i, existing in enumerate(self.vectors):
                if existing.get('id') == article_id:
                    self.vectors[i] = article
                    self._save_db()
                    return
        
        # Add new article
        self.vectors.append(article)
        self._save_db()
    
    def cosine_similarity(self, v1, v2):
        """Calculate cosine similarity between two vectors"""
        v1 = np.array(v1)
        v2 = np.array(v2)
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        # Avoid division by zero
        if norm_v1 == 0 or norm_v2 == 0:
            return 0
            
        return dot_product / (norm_v1 * norm_v2)
    
    def query_similar_vectors(self, query_vector, top_n=3):
        """
        Find vectors similar to the query vector
        
        Args:
            query_vector (list): Query vector
            top_n (int): Number of results to return
            
        Returns:
            list: Top N most similar articles
        """
        if not self.vectors:
            return []
        
        # Calculate similarity for each vector
        similarities = []
        for article in self.vectors:
            article_vector = article.get('vector', [])
            if article_vector:
                similarity = self.cosine_similarity(query_vector, article_vector)
                similarities.append((article, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N articles
        return [article for article, _ in similarities[:top_n]] 