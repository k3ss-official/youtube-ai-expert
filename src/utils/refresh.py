"""
Refresh Manager Module

This module manages the channel refresh process, including auto and manual modes.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from src.utils.config import ConfigManager
from src.ingestion.crawler import YouTubeChannelCrawler
from src.processing.processor import VideoProcessor
from src.semantic.chunker import ContentChunker
from src.semantic.embedder import ContentEmbedder
from src.memory.vector_db import VectorDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RefreshManager:
    """
    Manager for channel refresh operations.
    """
    
    def __init__(self, base_dir: str):
        """
        Initialize the refresh manager.
        
        Args:
            base_dir: Base directory of the project
        """
        self.base_dir = base_dir
        self.config_manager = ConfigManager(base_dir)
        
        logger.info(f"Initialized refresh manager")
    
    def toggle_refresh_mode(self) -> str:
        """
        Toggle between auto and manual refresh modes.
        
        Returns:
            New refresh mode
        """
        current_mode = self.config_manager.get_refresh_mode()
        new_mode = 'manual' if current_mode == 'auto' else 'auto'
        
        self.config_manager.set_refresh_mode(new_mode)
        logger.info(f"Toggled refresh mode from {current_mode} to {new_mode}")
        
        return new_mode
    
    def set_refresh_mode(self, mode: str) -> None:
        """
        Set refresh mode explicitly.
        
        Args:
            mode: Refresh mode ('auto' or 'manual')
        """
        self.config_manager.set_refresh_mode(mode)
        logger.info(f"Set refresh mode to {mode}")
    
    def get_refresh_mode(self) -> str:
        """
        Get current refresh mode.
        
        Returns:
            Current refresh mode
        """
        return self.config_manager.get_refresh_mode()
    
    def check_auto_refresh(self, channel_handle: str) -> bool:
        """
        Check if auto refresh is needed and perform if necessary.
        
        Args:
            channel_handle: YouTube channel handle (e.g., @ManusAGI)
            
        Returns:
            Boolean indicating whether refresh was performed
        """
        # Check if auto refresh is needed
        if not self.config_manager.should_refresh():
            logger.info("Auto refresh not needed")
            return False
        
        # Perform refresh
        logger.info(f"Auto refresh triggered for channel {channel_handle}")
        success = self.refresh_channel(channel_handle)
        
        if success:
            # Update last refresh timestamp
            self.config_manager.set_last_refresh()
            logger.info("Auto refresh completed successfully")
        else:
            logger.error("Auto refresh failed")
        
        return success
    
    def refresh_channel(self, channel_handle: str) -> bool:
        """
        Refresh channel data by crawling, processing, and indexing.
        
        Args:
            channel_handle: YouTube channel handle (e.g., @ManusAGI)
            
        Returns:
            Boolean indicating success
        """
        try:
            logger.info(f"Starting refresh for channel {channel_handle}")
            
            # Extract channel name from handle
            channel_name = channel_handle.replace('@', '')
            
            # Initialize components
            crawler = YouTubeChannelCrawler(
                channel_handle=channel_handle,
                output_dir=os.path.join(self.base_dir, 'data')
            )
            
            processor = VideoProcessor(
                raw_data_dir=os.path.join(self.base_dir, 'data', 'raw'),
                processed_data_dir=os.path.join(self.base_dir, 'data', 'processed')
            )
            
            chunker = ContentChunker(
                processed_data_dir=os.path.join(self.base_dir, 'data', 'processed'),
                chunked_data_dir=os.path.join(self.base_dir, 'data', 'embeddings')
            )
            
            embedder = ContentEmbedder(
                chunked_data_dir=os.path.join(self.base_dir, 'data', 'embeddings'),
                embeddings_dir=os.path.join(self.base_dir, 'data', 'embeddings')
            )
            
            vector_db = VectorDatabase(
                embeddings_dir=os.path.join(self.base_dir, 'data', 'embeddings'),
                index_dir=os.path.join(self.base_dir, 'data', 'index')
            )
            
            # Crawl channel
            logger.info(f"Crawling channel {channel_handle}")
            crawl_result = crawler.crawl_channel()
            
            # Process videos
            logger.info(f"Processing videos for channel {channel_name}")
            process_result = processor.process_channel_videos(channel_name)
            
            # Chunk content
            logger.info(f"Chunking content for channel {channel_name}")
            chunk_result = chunker.process_channel_videos(channel_name)
            
            # Generate embeddings
            logger.info(f"Generating embeddings for channel {channel_name}")
            embed_result = embedder.process_channel_videos(channel_name)
            
            # Build index
            logger.info(f"Building index for channel {channel_name}")
            index_result = vector_db.build_index(channel_name)
            
            # Update last refresh timestamp
            self.config_manager.set_last_refresh()
            
            logger.info(f"Refresh completed for channel {channel_handle}")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing channel {channel_handle}: {str(e)}", exc_info=True)
            return False
    
    def get_refresh_status(self) -> Dict[str, Any]:
        """
        Get current refresh status.
        
        Returns:
            Dictionary with refresh status information
        """
        mode = self.config_manager.get_refresh_mode()
        last_refresh = self.config_manager.get_last_refresh()
        interval = self.config_manager.get_auto_refresh_interval()
        
        # Calculate next refresh if in auto mode
        next_refresh = None
        if mode == 'auto':
            from datetime import timedelta
            next_refresh = last_refresh + timedelta(days=interval)
        
        return {
            'mode': mode,
            'last_refresh': last_refresh.isoformat(),
            'auto_refresh_interval_days': interval,
            'next_refresh': next_refresh.isoformat() if next_refresh else None
        }
