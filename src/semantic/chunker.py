"""
Content Chunker Module

This module chunks processed video content into semantic units for embedding and indexing.
It ensures that content is properly segmented for effective semantic search.
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

class ContentChunker:
    """
    Chunker for processed video content.
    """
    
    def __init__(self, processed_data_dir: str, chunked_data_dir: str):
        """
        Initialize the content chunker.
        
        Args:
            processed_data_dir: Directory containing processed video data
            chunked_data_dir: Directory to save chunked data
        """
        self.processed_data_dir = processed_data_dir
        self.chunked_data_dir = chunked_data_dir
        
        # Create chunked data directory if it doesn't exist
        os.makedirs(self.chunked_data_dir, exist_ok=True)
        
        logger.info(f"Initialized content chunker")
    
    def chunk_video_content(self, channel_name: str, video_id: str) -> List[Dict[str, Any]]:
        """
        Chunk content for a single video.
        
        Args:
            channel_name: Name of the channel (without @ symbol)
            video_id: YouTube video ID
            
        Returns:
            List of content chunks
        """
        # Define paths
        processed_video_path = os.path.join(self.processed_data_dir, channel_name, f'{video_id}.json')
        
        # Check if processed video data exists
        if not os.path.exists(processed_video_path):
            logger.warning(f"Processed video data not found for {video_id}")
            return []
        
        # Load processed video data
        with open(processed_video_path, 'r', encoding='utf-8') as f:
            processed_video_data = json.load(f)
        
        # Extract video metadata
        video_title = processed_video_data.get('title', '')
        video_description = processed_video_data.get('description', '')
        video_url = processed_video_data.get('url', '')
        timestamp_base_url = processed_video_data.get('timestamp_base_url', '')
        
        # Chunk video metadata
        metadata_chunks = self.chunk_metadata(
            video_id=video_id,
            channel_name=channel_name,
            title=video_title,
            description=video_description,
            url=video_url,
            timestamp_base_url=timestamp_base_url
        )
        
        # Chunk transcript
        transcript = processed_video_data.get('transcript', [])
        transcript_chunks = self.chunk_transcript(
            video_id=video_id,
            channel_name=channel_name,
            title=video_title,
            transcript=transcript,
            url=video_url,
            timestamp_base_url=timestamp_base_url
        )
        
        # Combine all chunks
        all_chunks = metadata_chunks + transcript_chunks
        
        # Create chunked data directory for channel if it doesn't exist
        channel_chunked_dir = os.path.join(self.chunked_data_dir, channel_name)
        os.makedirs(channel_chunked_dir, exist_ok=True)
        
        # Save chunked data
        chunked_data_path = os.path.join(channel_chunked_dir, f'{video_id}_chunks.json')
        with open(chunked_data_path, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Created {len(all_chunks)} chunks for video {video_id}, saved to {chunked_data_path}")
        return all_chunks
    
    def chunk_metadata(self, video_id: str, channel_name: str, title: str, description: str, 
                      url: str, timestamp_base_url: str) -> List[Dict[str, Any]]:
        """
        Chunk video metadata.
        
        Args:
            video_id: YouTube video ID
            channel_name: Name of the channel
            title: Video title
            description: Video description
            url: Video URL
            timestamp_base_url: Base URL for timestamps
            
        Returns:
            List of metadata chunks
        """
        chunks = []
        
        # Create title chunk
        if title:
            title_chunk = {
                'chunk_id': f"{video_id}_title",
                'video_id': video_id,
                'channel_name': channel_name,
                'chunk_type': 'title',
                'text': title,
                'video_title': title,
                'video_url': url,
                'timestamp_url': url,
                'start_time': 0,
                'end_time': 0,
                'chunking_date': datetime.now().isoformat()
            }
            chunks.append(title_chunk)
        
        # Chunk description
        if description:
            # Split description into paragraphs
            paragraphs = description.split('\n\n')
            
            for i, paragraph in enumerate(paragraphs):
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                description_chunk = {
                    'chunk_id': f"{video_id}_description_{i}",
                    'video_id': video_id,
                    'channel_name': channel_name,
                    'chunk_type': 'description',
                    'text': paragraph,
                    'video_title': title,
                    'video_url': url,
                    'timestamp_url': url,
                    'start_time': 0,
                    'end_time': 0,
                    'chunking_date': datetime.now().isoformat()
                }
                chunks.append(description_chunk)
        
        return chunks
    
    def chunk_transcript(self, video_id: str, channel_name: str, title: str, transcript: List[Dict[str, Any]],
                        url: str, timestamp_base_url: str) -> List[Dict[str, Any]]:
        """
        Chunk video transcript.
        
        Args:
            video_id: YouTube video ID
            channel_name: Name of the channel
            title: Video title
            transcript: List of transcript segments
            url: Video URL
            timestamp_base_url: Base URL for timestamps
            
        Returns:
            List of transcript chunks
        """
        chunks = []
        
        # If transcript is empty, return empty list
        if not transcript:
            return []
        
        # Define chunk parameters
        max_chunk_size = 5  # Maximum number of segments per chunk
        overlap = 1  # Number of overlapping segments between chunks
        
        # Create chunks with sliding window
        for i in range(0, len(transcript), max_chunk_size - overlap):
            # Get segment range for this chunk
            start_idx = i
            end_idx = min(i + max_chunk_size, len(transcript))
            
            # Skip if we've reached the end
            if start_idx >= len(transcript):
                break
            
            # Get segments for this chunk
            segments = transcript[start_idx:end_idx]
            
            # Skip if no segments
            if not segments:
                continue
            
            # Extract segment data
            start_time = segments[0]['start_time']
            end_time = segments[-1]['end_time']
            timestamp_seconds = segments[0]['timestamp_seconds']
            timestamp_formatted = segments[0]['timestamp_formatted']
            
            # Combine segment text
            text = ' '.join(segment['text'] for segment in segments)
            
            # Create timestamp URL
            timestamp_url = f"{timestamp_base_url}{timestamp_seconds}"
            
            # Create chunk
            chunk = {
                'chunk_id': f"{video_id}_transcript_{start_idx}_{end_idx}",
                'video_id': video_id,
                'channel_name': channel_name,
                'chunk_type': 'transcript',
                'text': text,
                'video_title': title,
                'video_url': url,
                'timestamp_url': timestamp_url,
                'start_time': start_time,
                'end_time': end_time,
                'timestamp_seconds': timestamp_seconds,
                'timestamp_formatted': timestamp_formatted,
                'segment_indices': list(range(start_idx, end_idx)),
                'chunking_date': datetime.now().isoformat()
            }
            
            chunks.append(chunk)
        
        return chunks
    
    def process_channel_videos(self, channel_name: str) -> List[Dict[str, Any]]:
        """
        Process all videos for a channel.
        
        Args:
            channel_name: Name of the channel (without @ symbol)
            
        Returns:
            List of video IDs that were processed
        """
        # Define paths
        processed_channel_dir = os.path.join(self.processed_data_dir, channel_name)
        
        # Check if processed channel data exists
        if not os.path.exists(processed_channel_dir):
            logger.warning(f"Processed channel data not found for {channel_name}")
            return []
        
        # Get list of video IDs
        video_ids = []
        for filename in os.listdir(processed_channel_dir):
            if filename.endswith('.json') and filename != 'processed_videos_summary.json':
                video_id = filename.replace('.json', '')
                video_ids.append(video_id)
        
        logger.info(f"Found {len(video_ids)} processed videos for channel {channel_name}")
        
        # Process each video
        processed_videos = []
        for i, video_id in enumerate(video_ids):
            logger.info(f"Chunking video {i+1}/{len(video_ids)}: {video_id}")
            chunks = self.chunk_video_content(channel_name, video_id)
            if chunks:
                processed_videos.append({
                    'video_id': video_id,
                    'chunks_count': len(chunks)
                })
        
        # Create chunked data directory for channel if it doesn't exist
        channel_chunked_dir = os.path.join(self.chunked_data_dir, channel_name)
        os.makedirs(channel_chunked_dir, exist_ok=True)
        
        # Save summary of chunked videos
        summary_path = os.path.join(channel_chunked_dir, 'chunked_videos_summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(processed_videos, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Chunked {len(processed_videos)} videos, summary saved to {summary_path}")
        return processed_videos
