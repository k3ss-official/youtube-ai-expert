"""
Enhanced CLI Interface Module

This module provides a command-line interface for interacting with
the YouTube Channel Conversational AI Expert, including refresh controls.
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
from src.utils.config import ConfigManager
from src.utils.refresh import RefreshManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedCLI:
    """
    Enhanced command-line interface for the YouTube Channel Conversational AI Expert.
    """
    
    def __init__(self, base_dir: str, channel_name: str):
        """
        Initialize the enhanced CLI.
        
        Args:
            base_dir: Base directory of the project
            channel_name: Name of the channel (without @ symbol)
        """
        self.base_dir = base_dir
        self.channel_name = channel_name
        self.channel_handle = f"@{channel_name}"
        
        # Initialize components
        self.query_processor = QueryProcessor()
        self.response_generator = ResponseGenerator()
        self.vector_db = VectorDatabase(
            embeddings_dir=os.path.join(base_dir, 'data', 'embeddings'),
            index_dir=os.path.join(base_dir, 'data', 'index')
        )
        
        # Initialize refresh manager
        self.refresh_manager = RefreshManager(base_dir)
        
        # Create history directory
        self.history_dir = os.path.join(base_dir, 'data', 'history')
        os.makedirs(self.history_dir, exist_ok=True)
        
        logger.info(f"Initialized enhanced CLI for channel {channel_name}")
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a query and generate a response.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary with query, response, and sources
        """
        logger.info(f"Processing query: {query}")
        
        # Check for auto refresh
        self.refresh_manager.check_auto_refresh(self.channel_handle)
        
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
    
    def toggle_refresh_mode(self) -> str:
        """
        Toggle between auto and manual refresh modes.
        
        Returns:
            New refresh mode
        """
        return self.refresh_manager.toggle_refresh_mode()
    
    def get_refresh_status(self) -> Dict[str, Any]:
        """
        Get current refresh status.
        
        Returns:
            Dictionary with refresh status information
        """
        return self.refresh_manager.get_refresh_status()
    
    def refresh_channel(self) -> bool:
        """
        Refresh channel data.
        
        Returns:
            Boolean indicating success
        """
        return self.refresh_manager.refresh_channel(self.channel_handle)
    
    def print_refresh_status(self) -> None:
        """Print current refresh status."""
        status = self.get_refresh_status()
        mode = status['mode']
        last_refresh = status['last_refresh'].split('T')[0]  # Just the date part
        
        print(f"\nRefresh Mode: {mode.upper()}")
        print(f"Last Refresh: {last_refresh}")
        
        if mode == 'auto':
            next_refresh = status['next_refresh'].split('T')[0] if status['next_refresh'] else 'Unknown'
            print(f"Auto Refresh Interval: {status['auto_refresh_interval_days']} days")
            print(f"Next Scheduled Refresh: {next_refresh}")
    
    def run_interactive(self) -> None:
        """Run the CLI in interactive mode."""
        print(f"\n🎬 YouTube Channel Conversational AI Expert - {self.channel_name}")
        print("Ask questions about the channel's content or use special commands.")
        print("\nSpecial Commands:")
        print("  !mode     - Toggle between auto and manual refresh modes")
        print("  !status   - Show current refresh status")
        print("  !refresh  - Manually refresh channel (only in manual mode)")
        print("  !exit     - Exit the program")
        
        # Check for auto refresh on startup
        self.refresh_manager.check_auto_refresh(self.channel_handle)
        
        while True:
            try:
                # Show refresh mode in prompt
                mode = self.refresh_manager.get_refresh_mode()
                prompt = f"\n[{mode.upper()}] > "
                
                # Get user input
                user_input = input(prompt)
                
                # Handle special commands
                if user_input.lower() in ['!exit', 'exit', 'quit', 'q']:
                    print("\nThank you for using the YouTube Channel Conversational AI Expert!")
                    break
                
                elif user_input.lower() == '!mode':
                    new_mode = self.toggle_refresh_mode()
                    print(f"\nRefresh mode switched to: {new_mode.upper()}")
                    continue
                
                elif user_input.lower() == '!status':
                    self.print_refresh_status()
                    continue
                
                elif user_input.lower() == '!refresh':
                    # Only allow manual refresh in manual mode
                    if mode == 'manual':
                        print("\nRefreshing channel data... This may take a while.")
                        success = self.refresh_channel()
                        if success:
                            print("\nChannel refresh completed successfully!")
                        else:
                            print("\nChannel refresh failed. Please check the logs.")
                    else:
                        print("\nManual refresh is only available in MANUAL mode.")
                        print("Use '!mode' to switch to MANUAL mode first.")
                    continue
                
                # Skip empty input
                if not user_input.strip():
                    continue
                
                # Process regular query
                response = self.process_query(user_input)
                print("\n" + response['answer'])
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error processing input: {str(e)}", exc_info=True)
                print(f"\nError: {str(e)}")
    
    def run_single_query(self, query: str) -> None:
        """
        Run a single query and print the response.
        
        Args:
            query: Query string
        """
        try:
            # Check for auto refresh
            self.refresh_manager.check_auto_refresh(self.channel_handle)
            
            # Process query
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
            success = self.refresh_channel()
            return success
        except Exception as e:
            logger.error(f"Error updating index: {str(e)}", exc_info=True)
            print(f"\nError updating index: {str(e)}")
            return False
