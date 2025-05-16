"""
Content Embedder Module

This module generates embeddings for chunked content using sentence-transformers.
These embeddings are used for semantic search and retrieval.
"""

import os
import json
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContentEmbedder:
    """
    Embedder for chunked content.
    """
    
    def __init__(self, chunked_data_dir: str, embeddings_dir: str, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the content embedder.
        
        Args:
            chunked_data_dir: Directory containing chunked content
            embeddings_dir: Directory to save embeddings
            model_name: Name of the sentence-transformers model to use
        """
        self.chunked_data_dir = chunked_data_dir
        self.embeddings_dir = embeddings_dir
        self.model_name = model_name
        
        # Create embeddings directory if it doesn't exist
        os.makedirs(self.embeddings_dir, exist_ok=True)
        
        # Load embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        logger.info(f"Initialized content embedder with model {model_name}")
    
    def embed_video_chunks(self, channel_name: str, video_id: str) -> Dict[str, Any]:
        """
        Generate embeddings for chunks of a single video.
        
        Args:
            channel_name: Name of the channel (without @ symbol)
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing embedding data
        """
        # Define paths
        chunked_data_path = os.path.join(self.chunked_data_dir, channel_name, f'{video_id}_chunks.json')
        
        # Check if chunked data exists
        if not os.path.exists(chunked_data_path):
            logger.warning(f"Chunked data not found for video {video_id}")
            return {}
        
        # Load chunked data
        with open(chunked_data_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        logger.info(f"Generating embeddings for {len(chunks)} chunks of video {video_id}")
        
        # Extract texts for embedding
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.model.encode(texts)
        
        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = embeddings[i].tolist()
        
        # Create embeddings directory for channel if it doesn't exist
        channel_embeddings_dir = os.path.join(self.embeddings_dir, channel_name)
        os.makedirs(channel_embeddings_dir, exist_ok=True)
        
        # Save embeddings
        embeddings_path = os.path.join(channel_embeddings_dir, f'{video_id}_embeddings.json')
        with open(embeddings_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Generated embeddings for video {video_id}, saved to {embeddings_path}")
        
        return {
            'video_id': video_id,
            'chunks_count': len(chunks),
            'embedding_model': self.model_name,
            'embedding_date': datetime.now().isoformat()
        }
    
    def process_channel_videos(self, channel_name: str) -> List[Dict[str, Any]]:
        """
        Generate embeddings for all videos of a channel.
        
        Args:
            channel_name: Name of the channel (without @ symbol)
            
        Returns:
            List of embedding results for each video
        """
        # Define paths
        chunked_channel_dir = os.path.join(self.chunked_data_dir, channel_name)
        
        # Check if chunked channel data exists
        if not os.path.exists(chunked_channel_dir):
            logger.warning(f"Chunked channel data not found for {channel_name}")
            return []
        
        # Get list of video IDs
        video_ids = []
        for filename in os.listdir(chunked_channel_dir):
            if filename.endswith('_chunks.json'):
                video_id = filename.replace('_chunks.json', '')
                video_ids.append(video_id)
        
        logger.info(f"Found {len(video_ids)} chunked videos for channel {channel_name}")
        
        # Process each video
        embedding_results = []
        for i, video_id in enumerate(video_ids):
            logger.info(f"Embedding video {i+1}/{len(video_ids)}: {video_id}")
            result = self.embed_video_chunks(channel_name, video_id)
            if result:
                embedding_results.append(result)
        
        # Create embeddings directory for channel if it doesn't exist
        channel_embeddings_dir = os.path.join(self.embeddings_dir, channel_name)
        os.makedirs(channel_embeddings_dir, exist_ok=True)
        
        # Save summary of embedded videos
        summary_path = os.path.join(channel_embeddings_dir, 'embedded_videos_summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(embedding_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Embedded {len(embedding_results)} videos, summary saved to {summary_path}")
        return embedding_results
