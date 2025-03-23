import os
import json
import time
from typing import List, Dict, Any, Optional, Union, Callable
import requests
from langchain.llms import HuggingFaceHub, OpenAI
from langchain.schema import LLMResult

class LLMManager:
    """Manager for interacting with different LLM providers"""
    
    def __init__(self, config_path: str = "../config.json"):
        self.config = self._load_config(config_path)
        self.api_keys = self.config.get("api_keys", {})
        self.ai_models = self.config.get("ai_models", {})
        self.llm_config = self.ai_models.get("llm", {})
        
        # Set environment variables for API keys
        self._set_env_vars()
        
        # Initialize LLM instances
        self.primary_llm = self._init_primary_llm()
        self.fallback_llm = self._init_fallback_llm()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {
                "api_keys": {},
                "ai_models": {
                    "llm": {
                        "primary": {"provider": "openai", "model": "gpt-3.5-turbo"},
                        "fallback": {"provider": "huggingface", "model": "google/flan-t5-large"}
                    }
                }
            }
    
    def _set_env_vars(self):
        """Set environment variables for API keys"""
        if "huggingface" in self.api_keys:
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = self.api_keys["huggingface"]
        if "openai" in self.api_keys:
            os.environ["OPENAI_API_KEY"] = self.api_keys["openai"]
    
    def _init_primary_llm(self):
        """Initialize the primary LLM based on configuration"""
        primary_config = self.llm_config.get("primary", {})
        provider = primary_config.get("provider", "huggingface")
        model = primary_config.get("model", "google/flan-t5-large")
        
        if provider == "openai" and "openai" in self.api_keys:
            return self._create_openai_llm(model)
        elif provider == "huggingface" and "huggingface" in self.api_keys:
            return self._create_huggingface_llm(model)
        else:
            print(f"Primary LLM provider {provider} not configured. Using fallback.")
            return None
    
    def _init_fallback_llm(self):
        """Initialize the fallback LLM based on configuration"""
        fallback_config = self.llm_config.get("fallback", {})
        provider = fallback_config.get("provider", "huggingface")
        model = fallback_config.get("model", "google/flan-t5-large")
        
        if provider == "openai" and "openai" in self.api_keys:
            return self._create_openai_llm(model)
        elif provider == "huggingface" and "huggingface" in self.api_keys:
            return self._create_huggingface_llm(model)
        else:
            print(f"Fallback LLM provider {provider} not configured.")
            return None
    
    def _create_openai_llm(self, model: str):
        """Create an OpenAI LLM instance"""
        try:
            return OpenAI(
                model_name=model,
                temperature=0.7,
                max_tokens=1000
            )
        except Exception as e:
            print(f"Error creating OpenAI LLM: {e}")
            return None
    
    def _create_huggingface_llm(self, model: str):
        """Create a HuggingFace LLM instance"""
        try:
            return HuggingFaceHub(
                repo_id=model,
                model_kwargs={"temperature": 0.7, "max_length": 1000}
            )
        except Exception as e:
            print(f"Error creating HuggingFace LLM: {e}")
            return None
    
    def generate(self, prompt: str, retry_count: int = 1) -> str:
        """Generate a response from the LLM"""
        if not prompt:
            return ""
        
        # Try primary LLM first
        if self.primary_llm:
            try:
                return self.primary_llm(prompt)
            except Exception as e:
                print(f"Primary LLM error: {e}")
                
                # Retry with exponential backoff
                if retry_count > 0:
                    time.sleep(2)
                    return self.generate(prompt, retry_count - 1)
        
        # Fall back to secondary LLM
        if self.fallback_llm:
            try:
                return self.fallback_llm(prompt)
            except Exception as e:
                print(f"Fallback LLM error: {e}")
        
        # If all else fails, return a default message
        return "I'm unable to generate a response at the moment. Please try again later."
    
    def generate_with_context(self, prompt: str, context: List[str], retry_count: int = 1) -> str:
        """Generate a response from the LLM with context provided"""
        if not prompt:
            return ""
        
        # Format prompt with context
        formatted_prompt = self._format_prompt_with_context(prompt, context)
        
        return self.generate(formatted_prompt, retry_count)
    
    def _format_prompt_with_context(self, prompt: str, context: List[str]) -> str:
        """Format a prompt with context information"""
        formatted_context = "\n".join([f"- {item}" for item in context])
        
        return f"""Context information:
{formatted_context}

Based on the above context, {prompt}""" 