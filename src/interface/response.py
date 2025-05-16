"""
Response Generator Module

This module generates comprehensive, source-referenced answers
based on search results from the vector database.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Generator for creating comprehensive, source-referenced answers.
    """
    
    def __init__(self):
        """Initialize the response generator."""
        logger.info("Initialized response generator")
    
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
    
    def generate_response(self, query: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive, source-referenced answer.
        
        Args:
            query: Original query string
            search_results: List of search results from vector database
            
        Returns:
            Dictionary with generated response
        """
        if not search_results:
            return {
                'query': query,
                'answer': "I couldn't find any relevant information about that topic in the channel's content.",
                'sources': [],
                'has_sources': False,
                'generation_date': datetime.now().isoformat()
            }
        
        # Group results by video
        videos = {}
        for result in search_results:
            video_id = result.get('video_id')
            if video_id not in videos:
                videos[video_id] = {
                    'video_id': video_id,
                    'title': result.get('video_title', ''),
                    'url': result.get('video_url', ''),
                    'chunks': []
                }
            videos[video_id]['chunks'].append(result)
        
        # Sort videos by highest scoring chunk
        sorted_videos = sorted(
            videos.values(),
            key=lambda v: max(chunk.get('score', 0) for chunk in v['chunks']),
            reverse=True
        )
        
        # Generate answer
        answer_parts = []
        answer_parts.append(f"Based on the content from the YouTube channel, here's what I found about '{query}':")
        answer_parts.append("")
        
        # Add summary from top results
        top_chunks = sorted(search_results, key=lambda x: x.get('score', 0), reverse=True)[:3]
        for chunk in top_chunks:
            answer_parts.append(chunk.get('text', ''))
        
        answer_parts.append("")
        answer_parts.append("Here are the specific sources:")
        
        # Format sources
        sources = []
        for video in sorted_videos[:3]:  # Limit to top 3 videos
            video_sources = []
            for chunk in sorted(video['chunks'], key=lambda x: x.get('score', 0), reverse=True)[:2]:  # Top 2 chunks per video
                timestamp = self.format_timestamp(chunk.get('start_time', 0))
                source = {
                    'video_id': video['video_id'],
                    'video_title': video['title'],
                    'video_url': video['url'],
                    'timestamp': timestamp,
                    'timestamp_url': chunk.get('timestamp_url', video['url']),
                    'text': chunk.get('text', '')[:150] + "..."  # Truncate for brevity
                }
                video_sources.append(source)
                
                # Add to answer
                source_text = f"- {video['title']} at {timestamp}: {source['text']}"
                answer_parts.append(source_text)
                answer_parts.append(f"  Link: {source['timestamp_url']}")
                answer_parts.append("")
            
            sources.extend(video_sources)
        
        # Add follow-up suggestions
        answer_parts.append("Would you like more specific information about any of these points?")
        
        # Combine answer parts
        answer = "\n".join(answer_parts)
        
        return {
            'query': query,
            'answer': answer,
            'sources': sources,
            'has_sources': bool(sources),
            'generation_date': datetime.now().isoformat()
        }
