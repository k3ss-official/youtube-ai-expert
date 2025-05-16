"""
Query Processor Module

This module processes natural language queries and transforms them
into semantic search queries for the vector database.
"""

import os
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QueryProcessor:
    """
    Processor for transforming natural language queries into semantic search queries.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the query processor.
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.model_name = model_name
        
        # Load embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        logger.info(f"Initialized query processor with model {model_name}")
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary with processed query information
        """
        # Clean query
        clean_query = query.strip()
        
        # Generate embedding
        embedding = self.model.encode(clean_query)
        
        # Extract potential entities or keywords
        # This is a simple implementation; could be enhanced with NLP techniques
        keywords = [word for word in clean_query.split() if len(word) > 3]
        
        return {
            'original_query': query,
            'clean_query': clean_query,
            'embedding': embedding,
            'keywords': keywords,
            'embedding_model': self.model_name
        }
