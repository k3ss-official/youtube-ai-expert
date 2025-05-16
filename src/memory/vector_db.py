"""
Vector Database Module

This module implements a vector database for storing and searching embeddings.
It uses FAISS for efficient similarity search.
"""

import os
import json
import logging
import numpy as np
import faiss
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VectorDatabase:
    """
    Vector database for storing and searching embeddings.
    """
    
    def __init__(self, embeddings_dir: str, index_dir: str):
        """
        Initialize the vector database.
        
        Args:
            embeddings_dir: Directory containing embeddings
            index_dir: Directory to save indices
        """
        self.embeddings_dir = embeddings_dir
        self.index_dir = index_dir
        
        # Create index directory if it doesn't exist
        os.makedirs(self.index_dir, exist_ok=True)
        
        logger.info(f"Initialized vector database")
    
    def build_index(self, channel_name: str) -> bool:
        """
        Build a FAISS index for a channel.
        
        Args:
            channel_name: Name of the channel (without @ symbol)
            
        Returns:
            Boolean indicating success
        """
        # Define paths
        channel_embeddings_dir = os.path.join(self.embeddings_dir, channel_name)
        
        # Check if embeddings exist
        if not os.path.exists(channel_embeddings_dir):
            logger.warning(f"Embeddings not found for channel {channel_name}")
            return False
        
        # Get list of embedding files
        embedding_files = []
        for filename in os.listdir(channel_embeddings_dir):
            if filename.endswith('_embeddings.json') and not filename.startswith('embedded_videos_summary'):
                embedding_files.append(os.path.join(channel_embeddings_dir, filename))
        
        if not embedding_files:
            logger.warning(f"No embedding files found for channel {channel_name}")
            return False
        
        logger.info(f"Building index for channel {channel_name} with {len(embedding_files)} embedding files")
        
        # Load all embeddings
        all_chunks = []
        for embedding_file in embedding_files:
            with open(embedding_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
                all_chunks.extend(chunks)
        
        if not all_chunks:
            logger.warning(f"No chunks found in embedding files for channel {channel_name}")
            return False
        
        logger.info(f"Loaded {len(all_chunks)} chunks for indexing")
        
        # Extract embeddings
        embeddings = np.array([chunk['embedding'] for chunk in all_chunks], dtype=np.float32)
        
        # Get embedding dimension
        dimension = embeddings.shape[1]
        
        # Create FAISS index
        index = faiss.IndexFlatL2(dimension)
        
        # Add embeddings to index
        index.add(embeddings)
        
        # Create index directory for channel if it doesn't exist
        channel_index_dir = os.path.join(self.index_dir, channel_name)
        os.makedirs(channel_index_dir, exist_ok=True)
        
        # Save index
        index_path = os.path.join(channel_index_dir, 'faiss_index.bin')
        faiss.write_index(index, index_path)
        
        # Save metadata
        metadata = {
            'channel_name': channel_name,
            'chunks_count': len(all_chunks),
            'dimension': dimension,
            'index_date': datetime.now().isoformat()
        }
        
        metadata_path = os.path.join(channel_index_dir, 'index_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # Save chunks without embeddings
        chunks_without_embeddings = []
        for chunk in all_chunks:
            chunk_copy = chunk.copy()
            chunk_copy.pop('embedding', None)
            chunks_without_embeddings.append(chunk_copy)
        
        chunks_path = os.path.join(channel_index_dir, 'chunks.json')
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump(chunks_without_embeddings, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Built index for channel {channel_name}, saved to {index_path}")
        logger.info(f"Saved {len(chunks_without_embeddings)} chunks without embeddings to {chunks_path}")
        
        return True
    
    def search(self, channel_name: str, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the index for similar chunks.
        
        Args:
            channel_name: Name of the channel (without @ symbol)
            query_embedding: Query embedding
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        # Define paths
        channel_index_dir = os.path.join(self.index_dir, channel_name)
        index_path = os.path.join(channel_index_dir, 'faiss_index.bin')
        chunks_path = os.path.join(channel_index_dir, 'chunks.json')
        
        # Check if index exists
        if not os.path.exists(index_path) or not os.path.exists(chunks_path):
            logger.warning(f"Index or chunks not found for channel {channel_name}")
            return []
        
        # Load index
        index = faiss.read_index(index_path)
        
        # Load chunks
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        # Convert query embedding to numpy array
        query_embedding_np = np.array([query_embedding], dtype=np.float32)
        
        # Search index
        distances, indices = index.search(query_embedding_np, top_k)
        
        # Get results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(chunks):
                continue
            
            chunk = chunks[idx]
            result = chunk.copy()
            result['score'] = float(1.0 / (1.0 + distances[0][i]))  # Convert distance to score
            results.append(result)
        
        return results
