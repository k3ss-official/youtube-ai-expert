# YouTube Channel Conversational AI Expert - Usage Guide

## Overview

The YouTube Channel Conversational AI Expert is a system that ingests content from YouTube channels and enables conversational Q&A with source-referenced answers. This MVP implementation uses crawl4ai as the core engine for YouTube data extraction and provides a command-line interface for interacting with the channel content.

## Features

- **Complete Channel Ingestion**: Extracts all video metadata, descriptions, and transcripts
- **Semantic Search**: Enables natural language queries over channel content
- **Source-Referenced Answers**: All responses include timestamped links to original videos
- **Entity Recognition**: Identifies tools, brands, and key entities mentioned in videos
- **Manual Update Trigger**: Allows refreshing the system with new channel content

## System Requirements

- Python 3.8+
- Internet connection for crawling YouTube content
- Sufficient disk space for storing video metadata and transcripts

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Initial Setup

To set up the system for a YouTube channel, run:

```
python main.py --channel @ChannelName --update
```

This will:
1. Crawl the channel using crawl4ai
2. Process all videos and transcripts
3. Chunk content into semantic units
4. Generate embeddings
5. Build the searchable index

### Interactive Mode

To start an interactive Q&A session:

```
python main.py --channel @ChannelName --interactive
```

### Single Query

To run a single query:

```
python main.py --channel @ChannelName --query "What are the best tools for video editing?"
```

### Updating Content

To update the system with new channel content:

```
python main.py --channel @ChannelName --update
```

### Individual Operations

You can also run individual operations:

- Crawl only: `--crawl`
- Process videos: `--process`
- Chunk content: `--chunk`
- Generate embeddings: `--embed`
- Build index: `--index`

Example:
```
python main.py --channel @ChannelName --crawl --process
```

## Architecture

The system follows a modular architecture with these main components:

1. **Ingestion Layer**: Uses crawl4ai to extract YouTube channel content
2. **Processing Layer**: Validates and processes video transcripts
3. **Semantic Layer**: Chunks content and generates embeddings
4. **Memory Layer**: Builds and manages the searchable index
5. **Interface Layer**: Provides conversational Q&A capabilities

## Future Enhancements

For the production version, consider these enhancements:

1. **Automated 7-day Recrawl**: Schedule automatic updates every 7 days
2. **Web Interface**: Add a web-based UI for easier interaction
3. **API Endpoints**: Enable integration with other systems
4. **Multi-Channel Support**: Expand to handle multiple YouTube channels
5. **Enhanced Entity Tracking**: Improve tool and brand recognition
6. **Audio/Video Preview**: Include inline media in responses

## Troubleshooting

- **Crawling Issues**: Ensure internet connectivity and valid channel handle
- **Missing Transcripts**: Some videos may not have available transcripts
- **Memory Usage**: For large channels, consider batch processing

## Support

For issues or questions, please contact the development team.
