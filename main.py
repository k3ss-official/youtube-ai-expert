"""
Main Entry Point for YouTube Channel Conversational AI Expert

This script provides the main entry point for the YouTube Channel Conversational AI Expert.
It orchestrates the crawling, processing, indexing, and conversational interface.
"""

import os
import sys
import logging
import argparse
from datetime import datetime

from src.ingestion.crawler import YouTubeChannelCrawler
from src.processing.processor import VideoProcessor
from src.semantic.chunker import ContentChunker
from src.semantic.embedder import ContentEmbedder
from src.memory.vector_db import VectorDatabase
from src.interface.cli import ConversationalCLI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("youtube_ai_expert.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_directories(base_dir):
    """Create necessary directories if they don't exist."""
    dirs = [
        os.path.join(base_dir, 'data', 'raw'),
        os.path.join(base_dir, 'data', 'processed'),
        os.path.join(base_dir, 'data', 'embeddings'),
        os.path.join(base_dir, 'data', 'index'),
        os.path.join(base_dir, 'data', 'history')
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def crawl_channel(channel_handle, base_dir):
    """
    Crawl a YouTube channel using crawl4ai.
    
    Args:
        channel_handle: YouTube channel handle (e.g., @ManusAGI)
        base_dir: Base directory of the project
    """
    logger.info(f"Starting crawl for channel: {channel_handle}")
    
    # Initialize crawler
    crawler = YouTubeChannelCrawler(
        channel_handle=channel_handle,
        output_dir=os.path.join(base_dir, 'data')
    )
    
    # Perform full channel crawl
    result = crawler.crawl_channel()
    
    logger.info(f"Crawl completed for {channel_handle}. Found {result['videos_count']} videos.")
    return result

def process_videos(channel_name, base_dir):
    """
    Process videos for a channel.
    
    Args:
        channel_name: Name of the channel (without @ symbol)
        base_dir: Base directory of the project
    """
    logger.info(f"Starting video processing for channel: {channel_name}")
    
    # Initialize processor
    processor = VideoProcessor(
        raw_data_dir=os.path.join(base_dir, 'data', 'raw'),
        processed_data_dir=os.path.join(base_dir, 'data', 'processed')
    )
    
    # Process videos
    result = processor.process_channel_videos(channel_name)
    
    logger.info(f"Processing completed for {channel_name}. Processed {len(result)} videos.")
    return result

def chunk_content(channel_name, base_dir):
    """
    Chunk content for a channel.
    
    Args:
        channel_name: Name of the channel (without @ symbol)
        base_dir: Base directory of the project
    """
    logger.info(f"Starting content chunking for channel: {channel_name}")
    
    # Initialize chunker
    chunker = ContentChunker(
        processed_data_dir=os.path.join(base_dir, 'data', 'processed'),
        chunked_data_dir=os.path.join(base_dir, 'data', 'embeddings')
    )
    
    # Chunk content
    result = chunker.process_channel_videos(channel_name)
    
    logger.info(f"Chunking completed for {channel_name}. Chunked {len(result)} videos.")
    return result

def embed_content(channel_name, base_dir):
    """
    Generate embeddings for a channel.
    
    Args:
        channel_name: Name of the channel (without @ symbol)
        base_dir: Base directory of the project
    """
    logger.info(f"Starting embedding generation for channel: {channel_name}")
    
    # Initialize embedder
    embedder = ContentEmbedder(
        chunked_data_dir=os.path.join(base_dir, 'data', 'embeddings'),
        embeddings_dir=os.path.join(base_dir, 'data', 'embeddings')
    )
    
    # Generate embeddings
    result = embedder.process_channel_videos(channel_name)
    
    logger.info(f"Embedding completed for {channel_name}. Embedded {len(result)} videos.")
    return result

def build_index(channel_name, base_dir):
    """
    Build vector index for a channel.
    
    Args:
        channel_name: Name of the channel (without @ symbol)
        base_dir: Base directory of the project
    """
    logger.info(f"Starting index building for channel: {channel_name}")
    
    # Initialize vector database
    vector_db = VectorDatabase(
        embeddings_dir=os.path.join(base_dir, 'data', 'embeddings'),
        index_dir=os.path.join(base_dir, 'data', 'index')
    )
    
    # Build index
    result = vector_db.build_index(channel_name)
    
    if result:
        logger.info(f"Index building completed successfully for {channel_name}.")
    else:
        logger.error(f"Index building failed for {channel_name}.")
    
    return result

def run_interactive_cli(channel_name, base_dir):
    """
    Run interactive CLI for a channel.
    
    Args:
        channel_name: Name of the channel (without @ symbol)
        base_dir: Base directory of the project
    """
    logger.info(f"Starting interactive CLI for channel: {channel_name}")
    
    # Initialize CLI
    cli = ConversationalCLI(
        base_dir=base_dir,
        channel_name=channel_name
    )
    
    # Run interactive mode
    cli.run_interactive()

def run_query(channel_name, base_dir, query):
    """
    Run a single query for a channel.
    
    Args:
        channel_name: Name of the channel (without @ symbol)
        base_dir: Base directory of the project
        query: Query string
    """
    logger.info(f"Running query for channel {channel_name}: {query}")
    
    # Initialize CLI
    cli = ConversationalCLI(
        base_dir=base_dir,
        channel_name=channel_name
    )
    
    # Run query
    cli.run_single_query(query)

def update_channel(channel_handle, base_dir):
    """
    Update a channel with new content.
    
    Args:
        channel_handle: YouTube channel handle (e.g., @ManusAGI)
        base_dir: Base directory of the project
    """
    logger.info(f"Starting update for channel: {channel_handle}")
    
    # Extract channel name from handle
    channel_name = channel_handle.replace('@', '')
    
    # Crawl channel
    crawl_result = crawl_channel(channel_handle, base_dir)
    
    # Process videos
    process_result = process_videos(channel_name, base_dir)
    
    # Chunk content
    chunk_result = chunk_content(channel_name, base_dir)
    
    # Generate embeddings
    embed_result = embed_content(channel_name, base_dir)
    
    # Build index
    index_result = build_index(channel_name, base_dir)
    
    if index_result:
        logger.info(f"Update completed successfully for {channel_handle}.")
        return True
    else:
        logger.error(f"Update failed for {channel_handle}.")
        return False

def main():
    """Main entry point for the YouTube Channel Conversational AI Expert."""
    parser = argparse.ArgumentParser(
        description="YouTube Channel Conversational AI Expert"
    )
    
    parser.add_argument(
        "--channel", 
        type=str, 
        default="@ManusAGI",
        help="YouTube channel handle to process (default: @ManusAGI)"
    )
    
    parser.add_argument(
        "--crawl", 
        action="store_true",
        help="Crawl the channel using crawl4ai"
    )
    
    parser.add_argument(
        "--process", 
        action="store_true",
        help="Process videos and transcripts"
    )
    
    parser.add_argument(
        "--chunk", 
        action="store_true",
        help="Chunk content into semantic units"
    )
    
    parser.add_argument(
        "--embed", 
        action="store_true",
        help="Generate embeddings for chunked content"
    )
    
    parser.add_argument(
        "--index", 
        action="store_true",
        help="Build vector index for embeddings"
    )
    
    parser.add_argument(
        "--update", 
        action="store_true",
        help="Update channel with new content (performs all steps)"
    )
    
    parser.add_argument(
        "--query", 
        type=str,
        help="Run a single query and exit"
    )
    
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Setup directories
    setup_directories(base_dir)
    
    # Extract channel name from handle
    channel_name = args.channel.replace('@', '')
    
    try:
        # Determine which operations to perform
        if args.update:
            success = update_channel(args.channel, base_dir)
            if not success:
                return 1
        else:
            if args.crawl:
                crawl_result = crawl_channel(args.channel, base_dir)
                print(f"\nCrawled {args.channel}, found {crawl_result['videos_count']} videos")
            
            if args.process:
                process_result = process_videos(channel_name, base_dir)
                print(f"\nProcessed {len(process_result)} videos for {channel_name}")
            
            if args.chunk:
                chunk_result = chunk_content(channel_name, base_dir)
                print(f"\nChunked {len(chunk_result)} videos for {channel_name}")
            
            if args.embed:
                embed_result = embed_content(channel_name, base_dir)
                print(f"\nEmbedded {len(embed_result)} videos for {channel_name}")
            
            if args.index:
                index_result = build_index(channel_name, base_dir)
                if index_result:
                    print(f"\nSuccessfully built index for {channel_name}")
                else:
                    print(f"\nFailed to build index for {channel_name}")
        
        # Run query or interactive mode
        if args.query:
            run_query(channel_name, base_dir, args.query)
        elif args.interactive:
            run_interactive_cli(channel_name, base_dir)
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
