"""
Test Script for YouTube Channel Conversational AI Expert

This script tests the functionality of the YouTube Channel Conversational AI Expert
by running a series of demo queries against the system.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interface.cli import ConversationalCLI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_queries.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_demo_queries(base_dir, channel_name):
    """
    Run a series of demo queries to validate the system.
    
    Args:
        base_dir: Base directory of the project
        channel_name: Name of the channel (without @ symbol)
    """
    logger.info(f"Starting demo query validation for channel {channel_name}")
    
    # Initialize CLI
    cli = ConversationalCLI(base_dir=base_dir, channel_name=channel_name)
    
    # Define demo queries
    demo_queries = [
        "What are the main topics covered in this channel?",
        "What tools or software have been reviewed recently?",
        "Can you summarize the latest video about AI?",
        "What's the channel's opinion on large language models?",
        "How has the channel's content evolved over time?"
    ]
    
    # Create results directory
    results_dir = os.path.join(base_dir, 'tests', 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Run queries and save results
    results = []
    for i, query in enumerate(demo_queries):
        logger.info(f"Running demo query {i+1}/{len(demo_queries)}: {query}")
        
        try:
            # Process query
            response = cli.process_query(query)
            
            # Add to results
            result = {
                'query': query,
                'response': response,
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)
            
            # Print response
            print(f"\nQuery: {query}")
            print(f"Response: {response['answer'][:200]}...\n")
            
        except Exception as e:
            logger.error(f"Error processing query '{query}': {str(e)}", exc_info=True)
            print(f"Error: {str(e)}")
    
    # Save all results
    results_path = os.path.join(results_dir, f"demo_queries_{channel_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Demo query validation completed, results saved to {results_path}")
    return results

if __name__ == "__main__":
    # Get base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Get channel name from command line or use default
    channel_name = sys.argv[1] if len(sys.argv) > 1 else "ManusAGI"
    
    # Run demo queries
    run_demo_queries(base_dir, channel_name)
