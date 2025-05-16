"""
Video Processor Module

This module processes video data extracted by the crawler, including transcripts,
and prepares it for semantic chunking and embedding.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoProcessor:
    """
    Processor for video data extracted by the crawler.
    """
    
    def __init__(self, raw_data_dir: str, processed_data_dir: str):
        """
        Initialize the video processor.
        
        Args:
            raw_data_dir: Directory containing raw crawled data
            processed_data_dir: Directory to save processed data
        """
        self.raw_data_dir = raw_data_dir
        self.processed_data_dir = processed_data_dir
        
        # Create processed data directory if it doesn't exist
        os.makedirs(self.processed_data_dir, exist_ok=True)
        
        logger.info(f"Initialized video processor")
    
    def process_video(self, channel_name: str, video_id: str) -> Dict[str, Any]:
        """
        Process a single video.
        
        Args:
            channel_name: Name of the channel (without @ symbol)
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing processed video data
        """
        # Define paths
        raw_video_dir = os.path.join(self.raw_data_dir, channel_name, 'videos', video_id)
        raw_video_path = os.path.join(raw_video_dir, 'video_data.json')
        
        # Check if raw video data exists
        if not os.path.exists(raw_video_path):
            logger.warning(f"Raw video data not found for {video_id}")
            return {}
        
        # Load raw video data
        with open(raw_video_path, 'r', encoding='utf-8') as f:
            raw_video_data = json.load(f)
        
        # Process transcript
        transcript = raw_video_data.get('transcript', [])
        processed_transcript = self.process_transcript(transcript)
        
        # Extract entities (tools, brands, etc.)
        entities = self.extract_entities(raw_video_data)
        
        # Create processed video data
        processed_video_data = {
            'video_id': video_id,
            'channel_name': channel_name,
            'title': raw_video_data.get('title', ''),
            'description': raw_video_data.get('description', ''),
            'url': raw_video_data.get('url', f'https://www.youtube.com/watch?v={video_id}'),
            'timestamp_base_url': f'https://www.youtube.com/watch?v={video_id}&t=',
            'transcript': processed_transcript,
            'transcript_text': self.get_full_transcript_text(processed_transcript),
            'entities': entities,
            'metadata': raw_video_data.get('metadata', {}),
            'processing_date': datetime.now().isoformat()
        }
        
        # Create processed data directory for channel if it doesn't exist
        channel_processed_dir = os.path.join(self.processed_data_dir, channel_name)
        os.makedirs(channel_processed_dir, exist_ok=True)
        
        # Save processed video data
        processed_video_path = os.path.join(channel_processed_dir, f'{video_id}.json')
        with open(processed_video_path, 'w', encoding='utf-8') as f:
            json.dump(processed_video_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Processed video {video_id} saved to {processed_video_path}")
        return processed_video_data
    
    def process_transcript(self, transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process transcript segments.
        
        Args:
            transcript: List of transcript segments from YouTube
            
        Returns:
            List of processed transcript segments
        """
        processed_segments = []
        
        for i, segment in enumerate(transcript):
            # Extract segment data
            text = segment.get('text', '').strip()
            start = segment.get('start', 0)
            duration = segment.get('duration', 0)
            
            # Skip empty segments
            if not text:
                continue
            
            # Create processed segment
            processed_segment = {
                'index': i,
                'text': text,
                'start_time': start,
                'end_time': start + duration,
                'duration': duration,
                'timestamp_seconds': int(start),
                'timestamp_formatted': self.format_timestamp(start)
            }
            
            processed_segments.append(processed_segment)
        
        return processed_segments
    
    def format_timestamp(self, seconds: float) -> str:
        """
        Format seconds into a human-readable timestamp.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted timestamp string (MM:SS)
        """
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}:{remaining_seconds:02d}"
    
    def get_full_transcript_text(self, processed_transcript: List[Dict[str, Any]]) -> str:
        """
        Get full transcript text from processed segments.
        
        Args:
            processed_transcript: List of processed transcript segments
            
        Returns:
            Full transcript text
        """
        return ' '.join(segment['text'] for segment in processed_transcript)
    
    def extract_entities(self, video_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Extract entities (tools, brands, etc.) from video data.
        
        Args:
            video_data: Raw video data
            
        Returns:
            Dictionary of entity types and their values
        """
        # This is a simple implementation; could be enhanced with NLP techniques
        entities = {
            'tools': [],
            'brands': [],
            'topics': []
        }
        
        # Extract from title and description
        title = video_data.get('title', '')
        description = video_data.get('description', '')
        
        # Extract from transcript
        transcript = video_data.get('transcript', [])
        transcript_text = ' '.join(segment.get('text', '') for segment in transcript)
        
        # Combine all text for entity extraction
        all_text = f"{title} {description} {transcript_text}"
        
        # TODO: Implement more sophisticated entity extraction
        # For now, just return empty entities
        
        return entities
    
    def process_channel_videos(self, channel_name: str) -> List[Dict[str, Any]]:
        """
        Process all videos for a channel.
        
        Args:
            channel_name: Name of the channel (without @ symbol)
            
        Returns:
            List of processed video data
        """
        # Define paths
        raw_channel_dir = os.path.join(self.raw_data_dir, channel_name)
        raw_videos_dir = os.path.join(raw_channel_dir, 'videos')
        
        # Check if raw channel data exists
        if not os.path.exists(raw_channel_dir):
            logger.warning(f"Raw channel data not found for {channel_name}")
            return []
        
        # Get list of video IDs
        video_ids = []
        if os.path.exists(raw_videos_dir):
            video_ids = [d for d in os.listdir(raw_videos_dir) if os.path.isdir(os.path.join(raw_videos_dir, d))]
        
        logger.info(f"Found {len(video_ids)} videos for channel {channel_name}")
        
        # Process each video
        processed_videos = []
        for i, video_id in enumerate(video_ids):
            logger.info(f"Processing video {i+1}/{len(video_ids)}: {video_id}")
            processed_video = self.process_video(channel_name, video_id)
            if processed_video:
                processed_videos.append(processed_video)
        
        # Create processed data directory for channel if it doesn't exist
        channel_processed_dir = os.path.join(self.processed_data_dir, channel_name)
        os.makedirs(channel_processed_dir, exist_ok=True)
        
        # Save summary of processed videos
        summary_path = os.path.join(channel_processed_dir, 'processed_videos_summary.json')
        summary_data = [
            {
                'video_id': video['video_id'],
                'title': video['title'],
                'url': video['url'],
                'transcript_segments': len(video.get('transcript', [])),
                'processing_date': video['processing_date']
            }
            for video in processed_videos
        ]
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Processed {len(processed_videos)} videos, summary saved to {summary_path}")
        return processed_videos
