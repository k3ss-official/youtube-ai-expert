"""
Updated Main Entry Point for YouTube Channel Conversational AI Expert

This script provides the main entry point for the YouTube Channel Conversational AI Expert
with enhanced refresh controls.
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
from src.interface.enhanced_cli import EnhancedCLI
from src.utils.refresh import RefreshManager

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
        os.path.join(base_dir, 'data', 'history'),
        os.path.join(base_dir, 'data', 'config')
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def main():
    """Main entry point for the YouTube Channel Conversational AI Expert."""
    parser = argparse.ArgumentParser(
        description="YouTube Channel Conversational AI Expert with Refresh Controls"
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
    
    parser.add_argument(
        "--refresh-mode", 
        type=str,
        choices=["auto", "manual"],
        help="Set refresh mode (auto or manual)"
    )
    
    args = parser.parse_args()
    
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Setup directories
    setup_directories(base_dir)
    
    # Extract channel name from handle
    channel_name = args.channel.replace('@', '')
    
    # Initialize refresh manager
    refresh_manager = RefreshManager(base_dir)
    
    # Set refresh mode if specified
    if args.refresh_mode:
        refresh_manager.set_refresh_mode(args.refresh_mode)
        print(f"Refresh mode set to: {args.refresh_mode.upper()}")
    
    try:
        # Determine which operations to perform
        if args.update:
            success = refresh_manager.refresh_channel(args.channel)
            if not success:
                return 1
        else:
            if args.crawl:
                crawler = YouTubeChannelCrawler(
                    channel_handle=args.channel,
                    output_dir=os.path.join(base_dir, 'data')
                )
                crawl_result = crawler.crawl_channel()
                print(f"\nCrawled {args.channel}, found {crawl_result['videos_count']} videos")
            
            if args.process:
                processor = VideoProcessor(
                    raw_data_dir=os.path.join(base_dir, 'data', 'raw'),
                    processed_data_dir=os.path.join(base_dir, 'data', 'processed')
                )
                process_result = processor.process_channel_videos(channel_name)
                print(f"\nProcessed {len(process_result)} videos for {channel_name}")
            
            if args.chunk:
                chunker = ContentChunker(
                    processed_data_dir=os.path.join(base_dir, 'data', 'processed'),
                    chunked_data_dir=os.path.join(base_dir, 'data', 'embeddings')
                )
                chunk_result = chunker.process_channel_videos(channel_name)
                print(f"\nChunked {len(chunk_result)} videos for {channel_name}")
            
            if args.embed:
                embedder = ContentEmbedder(
                    chunked_data_dir=os.path.join(base_dir, 'data', 'embeddings'),
                    embeddings_dir=os.path.join(base_dir, 'data', 'embeddings')
                )
                embed_result = embedder.process_channel_videos(channel_name)
                print(f"\nEmbedded {len(embed_result)} videos for {channel_name}")
            
            if args.index:
                vector_db = VectorDatabase(
                    embeddings_dir=os.path.join(base_dir, 'data', 'embeddings'),
                    index_dir=os.path.join(base_dir, 'data', 'index')
                )
                index_result = vector_db.build_index(channel_name)
                if index_result:
                    print(f"\nSuccessfully built index for {channel_name}")
                else:
                    print(f"\nFailed to build index for {channel_name}")
        
        # Run query or interactive mode
        if args.query:
            cli = EnhancedCLI(base_dir=base_dir, channel_name=channel_name)
            cli.run_single_query(args.query)
        elif args.interactive:
            cli = EnhancedCLI(base_dir=base_dir, channel_name=channel_name)
            cli.run_interactive()
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
