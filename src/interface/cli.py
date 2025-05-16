"""
CLI Interface Module

This module provides a command-line interface for interacting with
the YouTube Channel Conversational AI Expert.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime

from src.interface.query import QueryProcessor
from src.interface.response import ResponseGenerator
from src.memory.vector_db import VectorDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConversationalCLI:
    """
    Command-line interface for the YouTube Channel Conversational AI Expert.
    """
    
    def __init__(self, base_dir: str, channel_name: str):
        """
        Initialize the conversational CLI.
        
        Args:
            base_dir: Base directory of the project
            channel_name: Name of the channel (without @ symbol)
        """
        self.base_dir = base_dir
        self.channel_name = channel_name
        
        # Initialize components
        self.query_processor = QueryProcessor()
        self.response_generator = ResponseGenerator()
        self.vector_db = VectorDatabase(
            embeddings_dir=os.path.join(base_dir, 'data', 'embeddings'),
            index_dir=os.path.join(base_dir, 'data', 'index')
        )
        
        # Create history directory
        self.history_dir = os.path.join(base_dir, 'data', 'history')
        os.makedirs(self.history_dir, exist_ok=True)
        
        logger.info(f"Initialized conversational CLI for channel {channel_name}")
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a query and generate a response.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary with query, response, and sources
        """
        logger.info(f"Processing query: {query}")
        
        # Process query
        processed_query = self.query_processor.process_query(query)
        
        # Search vector database
        search_results = self.vector_db.search(
            channel_name=self.channel_name,
            query_embedding=processed_query['embedding'],
            top_k=10
        )
        
        # Generate response
        response = self.response_generator.generate_response(
            query=query,
            search_results=search_results
        )
        
        # Save to history
        self.save_to_history(query, response)
        
        return response
    
    def save_to_history(self, query: str, response: Dict[str, Any]) -> None:
        """
        Save query and response to history.
        
        Args:
            query: Original query string
            response: Response dictionary
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = os.path.join(self.history_dir, f"query_{timestamp}.json")
        
        history_data = {
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'channel': self.channel_name
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved query and response to {history_file}")
    
    def run_interactive(self) -> None:
        """Run the CLI in interactive mode."""
        print(f"\n🎬 YouTube Channel Conversational AI Expert - {self.channel_name}")
        print("Ask questions about the channel's content or type 'exit' to quit.\n")
        
        while True:
            try:
                query = input("\n> ")
                
                if query.lower() in ['exit', 'quit', 'q']:
                    print("\nThank you for using the YouTube Channel Conversational AI Expert!")
                    break
                
                if not query.strip():
                    continue
                
                response = self.process_query(query)
                print("\n" + response['answer'])
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}", exc_info=True)
                print(f"\nError: {str(e)}")
    
    def run_single_query(self, query: str) -> None:
        """
        Run a single query and print the response.
        
        Args:
            query: Query string
        """
        try:
            response = self.process_query(query)
            print("\n" + response['answer'])
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            print(f"\nError: {str(e)}")
    
    def update_index(self) -> bool:
        """
        Update the vector index with new content.
        
        Returns:
            Boolean indicating success
        """
        try:
            success = self.vector_db.build_index(self.channel_name)
            if success:
                print(f"\nSuccessfully updated index for channel {self.channel_name}")
            else:
                print(f"\nFailed to update index for channel {self.channel_name}")
            return success
        except Exception as e:
            logger.error(f"Error updating index: {str(e)}", exc_info=True)
            print(f"\nError updating index: {str(e)}")
            return False
