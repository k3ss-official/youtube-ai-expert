"""
YouTube Channel Crawler using crawl4ai

This module implements the YouTube channel crawler using crawl4ai as the core engine.
It extracts video metadata, descriptions, and transcripts from a specified YouTube channel.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from crawl4ai import Crawler
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YouTubeChannelCrawler:
    """
    Crawler for extracting content from YouTube channels using crawl4ai.
    """
    
    def __init__(self, channel_handle: str, output_dir: str):
        """
        Initialize the YouTube channel crawler.
        
        Args:
            channel_handle: YouTube channel handle (e.g., @ManusAGI)
            output_dir: Directory to save crawled data
        """
        self.channel_handle = channel_handle
        self.output_dir = output_dir
        self.raw_dir = os.path.join(output_dir, 'raw')
        self.channel_dir = os.path.join(self.raw_dir, channel_handle.replace('@', ''))
        
        # Create directories if they don't exist
        os.makedirs(self.channel_dir, exist_ok=True)
        os.makedirs(os.path.join(self.channel_dir, 'videos'), exist_ok=True)
        
        # Initialize crawl4ai crawler
        self.crawler = Crawler()
        
        logger.info(f"Initialized YouTube channel crawler for {channel_handle}")
    
    def get_channel_url(self) -> str:
        """Get the YouTube channel URL from the handle."""
        return f"https://www.youtube.com/{self.channel_handle}"
    
    def crawl_channel_metadata(self) -> Dict[str, Any]:
        """
        Crawl channel metadata using crawl4ai.
        
        Returns:
            Dictionary containing channel metadata
        """
        channel_url = self.get_channel_url()
        logger.info(f"Crawling channel metadata from {channel_url}")
        
        # Use crawl4ai to extract channel metadata
        result = self.crawler.crawl(channel_url)
        
        # Extract relevant channel information
        channel_data = {
            'handle': self.channel_handle,
            'url': channel_url,
            'title': result.get_title() or self.channel_handle,
            'description': result.get_description() or '',
            'crawl_date': datetime.now().isoformat(),
            'metadata': result.get_metadata() or {}
        }
        
        # Save channel metadata
        metadata_path = os.path.join(self.channel_dir, 'channel_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(channel_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Channel metadata saved to {metadata_path}")
        return channel_data
    
    def extract_video_urls(self) -> List[str]:
        """
        Extract video URLs from the channel using crawl4ai.
        
        Returns:
            List of video URLs
        """
        channel_url = self.get_channel_url()
        logger.info(f"Extracting video URLs from {channel_url}")
        
        # Use crawl4ai to extract links from the channel page
        result = self.crawler.crawl(channel_url)
        links = result.get_links() or []
        
        # Filter for video links
        video_urls = [
            link for link in links 
            if 'youtube.com/watch?v=' in link or 'youtu.be/' in link
        ]
        
        # Save video URLs
        urls_path = os.path.join(self.channel_dir, 'video_urls.json')
        with open(urls_path, 'w', encoding='utf-8') as f:
            json.dump(video_urls, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Found {len(video_urls)} videos, URLs saved to {urls_path}")
        return video_urls
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from a YouTube URL."""
        if 'youtube.com/watch?v=' in url:
            # Handle youtube.com/watch?v=VIDEO_ID format
            video_id = url.split('youtube.com/watch?v=')[1].split('&')[0]
        elif 'youtu.be/' in url:
            # Handle youtu.be/VIDEO_ID format
            video_id = url.split('youtu.be/')[1].split('?')[0]
        else:
            logger.warning(f"Could not extract video ID from URL: {url}")
            return None
        
        return video_id
    
    def crawl_video_content(self, video_url: str) -> Dict[str, Any]:
        """
        Crawl video content including metadata, description, and transcript.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Dictionary containing video data
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            return {}
        
        logger.info(f"Crawling content for video ID: {video_id}")
        
        # Use crawl4ai to extract video content
        result = self.crawler.crawl(video_url)
        
        # Extract video metadata
        video_data = {
            'video_id': video_id,
            'url': video_url,
            'title': result.get_title() or f"Video {video_id}",
            'description': result.get_description() or '',
            'metadata': result.get_metadata() or {},
            'crawl_date': datetime.now().isoformat(),
            'transcript': self.get_video_transcript(video_id)
        }
        
        # Save video data
        video_dir = os.path.join(self.channel_dir, 'videos', video_id)
        os.makedirs(video_dir, exist_ok=True)
        
        video_path = os.path.join(video_dir, 'video_data.json')
        with open(video_path, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Video data saved to {video_path}")
        return video_data
    
    def get_video_transcript(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get transcript for a video using youtube_transcript_api.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of transcript segments with text and timestamps
        """
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            logger.info(f"Successfully retrieved transcript for video {video_id}")
            return transcript_list
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.warning(f"No transcript available for video {video_id}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving transcript for video {video_id}: {str(e)}")
            return []
    
    def crawl_all_videos(self) -> List[Dict[str, Any]]:
        """
        Crawl all videos from the channel.
        
        Returns:
            List of video data dictionaries
        """
        video_urls = self.extract_video_urls()
        logger.info(f"Starting to crawl {len(video_urls)} videos")
        
        video_data_list = []
        for i, url in enumerate(video_urls):
            logger.info(f"Processing video {i+1}/{len(video_urls)}: {url}")
            video_data = self.crawl_video_content(url)
            if video_data:
                video_data_list.append(video_data)
        
        # Save summary of all videos
        summary_path = os.path.join(self.channel_dir, 'videos_summary.json')
        summary_data = [
            {
                'video_id': data['video_id'],
                'title': data['title'],
                'url': data['url'],
                'has_transcript': bool(data.get('transcript'))
            }
            for data in video_data_list
        ]
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Crawled {len(video_data_list)} videos, summary saved to {summary_path}")
        return video_data_list
    
    def crawl_channel(self) -> Dict[str, Any]:
        """
        Crawl the entire channel including metadata and all videos.
        
        Returns:
            Dictionary with channel metadata and video data
        """
        logger.info(f"Starting full crawl of channel {self.channel_handle}")
        
        # Get channel metadata
        channel_data = self.crawl_channel_metadata()
        
        # Crawl all videos
        video_data_list = self.crawl_all_videos()
        
        # Create full channel data
        full_data = {
            'channel': channel_data,
            'videos_count': len(video_data_list),
            'crawl_date': datetime.now().isoformat()
        }
        
        # Save full crawl summary
        summary_path = os.path.join(self.channel_dir, 'crawl_summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Channel crawl completed, summary saved to {summary_path}")
        return full_data
