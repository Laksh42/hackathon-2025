import os
import json
import shutil
from typing import List, Dict, Any, Optional, Union
import numpy as np
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from .embedding_utils import EmbeddingManager

class VectorStore:
    """Vector database for storing and retrieving embeddings"""
    
    def __init__(self, 
                 collection_name: str = "default", 
                 embedding_manager: Optional[EmbeddingManager] = None,
                 config_path: str = "../config.json"):
        
        self.config = self._load_config(config_path)
        self.db_path = self.config.get("vector_db", {}).get("path", "./vector_db")
        self.collection_name = collection_name or self.config.get("vector_db", {}).get(
            "collection_names", {}).get("default", "default")
        
        # Create embedding manager if not provided
        self.embedding_manager = embedding_manager or EmbeddingManager(config_path)
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"vector_db": {"path": "./vector_db", "collection_names": {"default": "default"}}}
    
    def _get_or_create_collection(self):
        """Get or create a collection in the vector database"""
        try:
            return self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self._embedding_function()
            )
        except Exception as e:
            print(f"Error creating collection: {e}")
            # Try to recreate with default settings
            return self.client.get_or_create_collection(
                name=self.collection_name
            )
    
    def _embedding_function(self):
        """Create a custom embedding function that uses our embedding manager"""
        return embedding_functions.PythonEmbeddingFunction(
            lambda texts: [self.embedding_manager.get_embedding(text).tolist() for text in texts]
        )
    
    def add(self, 
            texts: List[str], 
            metadatas: Optional[List[Dict[str, Any]]] = None,
            ids: Optional[List[str]] = None) -> None:
        """Add texts to the vector store"""
        if not texts:
            return
            
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}_{hash(text) % 10000000}" for i, text in enumerate(texts)]
        
        # Ensure metadatas exists for each text
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        # Add to collection
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, 
               query: str, 
               n_results: int = 5, 
               where: Optional[Dict[str, Any]] = None,
               where_document: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search for similar texts in the vector store"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
            where_document=where_document
        )
        
        return results
    
    def get(self, 
            ids: Optional[List[str]] = None, 
            where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get documents by ID or filter"""
        return self.collection.get(
            ids=ids,
            where=where
        )
    
    def delete(self, 
               ids: Optional[List[str]] = None, 
               where: Optional[Dict[str, Any]] = None) -> None:
        """Delete documents by ID or filter"""
        self.collection.delete(
            ids=ids,
            where=where
        )
    
    def count(self) -> int:
        """Count documents in the collection"""
        return self.collection.count()
    
    def reset(self) -> None:
        """Delete and recreate the collection"""
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
        self.collection = self._get_or_create_collection()
    
    def reset_db(self) -> None:
        """Delete and recreate the entire database"""
        try:
            if os.path.exists(self.db_path):
                shutil.rmtree(self.db_path)
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self._get_or_create_collection()
        except Exception as e:
            print(f"Error resetting database: {e}") 