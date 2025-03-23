import os
import json
from typing import List, Dict, Any, Optional, Union
import numpy as np

from .embedding_utils import EmbeddingManager
from .vector_store import VectorStore
from .llm_utils import LLMManager

class RAGManager:
    """Manager for Retrieval Augmented Generation"""
    
    def __init__(self, 
                 collection_name: str = "default", 
                 config_path: str = "../config.json"):
        
        self.config = self._load_config(config_path)
        self.rag_config = self.config.get("ai_models", {}).get("rag", {})
        
        # Initialize components
        self.embedding_manager = EmbeddingManager(config_path)
        self.vector_store = VectorStore(collection_name, self.embedding_manager, config_path)
        self.llm_manager = LLMManager(config_path)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {
                "ai_models": {
                    "rag": {
                        "top_k": 5,
                        "min_score": 0.65
                    }
                }
            }
    
    def add_documents(self, 
                      texts: List[str], 
                      metadatas: Optional[List[Dict[str, Any]]] = None,
                      ids: Optional[List[str]] = None) -> None:
        """Add documents to the vector store"""
        self.vector_store.add(texts, metadatas, ids)
    
    def get_relevant_context(self, 
                             query: str, 
                             top_k: Optional[int] = None,
                             min_score: Optional[float] = None,
                             where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant context for a query"""
        if not query:
            return []
        
        top_k = top_k or self.rag_config.get("top_k", 5)
        min_score = min_score or self.rag_config.get("min_score", 0.65)
        
        # Query the vector store
        results = self.vector_store.search(query, n_results=top_k, where=where)
        
        # No results
        if not results or "documents" not in results or not results["documents"]:
            return []
        
        # Extract documents, metadatas, and distances
        documents = results["documents"][0]
        metadatas = results["metadatas"][0] if "metadatas" in results else [{} for _ in documents]
        distances = results["distances"][0] if "distances" in results else [1.0 for _ in documents]
        ids = results["ids"][0] if "ids" in results else [f"doc_{i}" for i in range(len(documents))]
        
        # Convert distances to similarity scores (1 - distance for cosine distance)
        scores = [1 - dist for dist in distances]
        
        # Filter by minimum score
        filtered_results = []
        for doc, meta, score, doc_id in zip(documents, metadatas, scores, ids):
            if score >= min_score:
                filtered_results.append({
                    "text": doc,
                    "metadata": meta,
                    "score": score,
                    "id": doc_id
                })
        
        return filtered_results
    
    def generate_with_rag(self, 
                          query: str, 
                          top_k: Optional[int] = None,
                          min_score: Optional[float] = None,
                          where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a response using RAG"""
        if not query:
            return {"answer": "", "context": [], "query": query}
        
        # Get relevant context
        context_docs = self.get_relevant_context(query, top_k, min_score, where)
        
        # Extract text from context documents
        context_texts = [doc["text"] for doc in context_docs]
        
        # Generate response with context
        answer = self.llm_manager.generate_with_context(query, context_texts)
        
        return {
            "answer": answer,
            "context": context_docs,
            "query": query
        }
    
    def reset(self) -> None:
        """Reset the vector store"""
        self.vector_store.reset() 