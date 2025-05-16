# YouTube Channel Conversational AI Expert - Updated README

## Overview

The YouTube Channel Conversational AI Expert is a system that ingests content from YouTube channels and enables conversational Q&A with source-referenced answers. This MVP implementation uses crawl4ai as the core engine for YouTube data extraction and provides a command-line interface for interacting with the channel content.

## New Feature: Auto/Manual Refresh Switch

The system now includes an auto/manual refresh switch that allows you to control how channel content is updated:

- **Auto Mode**: Automatically refreshes channel content every 7 days
- **Manual Mode**: Provides a "refresh now" option for on-demand updates

## Features

- **Complete Channel Ingestion**: Extracts all video metadata, descriptions, and transcripts
- **Semantic Search**: Enables natural language queries over channel content
- **Source-Referenced Answers**: All responses include timestamped links to original videos
- **Entity Recognition**: Identifies tools, brands, and key entities mentioned in videos
- **Flexible Refresh Controls**: Toggle between auto and manual refresh modes
- **Scheduled Updates**: Auto-refreshes content every 7 days when in auto mode

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

### Interactive Mode with Refresh Controls

To start an interactive Q&A session:

```
python main.py --channel @ChannelName --interactive
```

In interactive mode, you can use these special commands:
- `!mode` - Toggle between auto and manual refresh modes
- `!status` - Show current refresh status
- `!refresh` - Manually refresh channel (only available in manual mode)
- `!exit` - Exit the program

### Setting Refresh Mode

You can set the refresh mode when starting the program:

```
python main.py --channel @ChannelName --interactive --refresh-mode auto
```

or

```
python main.py --channel @ChannelName --interactive --refresh-mode manual
```

### Single Query

To run a single query:

```
python main.py --channel @ChannelName --query "What are the best tools for video editing?"
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
6. **Refresh Layer**: Manages auto and manual refresh modes

## Future Enhancements

For the production version, consider these enhancements:

1. **Web Interface**: Add a web-based UI for easier interaction
2. **API Endpoints**: Enable integration with other systems
3. **Multi-Channel Support**: Expand to handle multiple YouTube channels
4. **Enhanced Entity Tracking**: Improve tool and brand recognition
5. **Audio/Video Preview**: Include inline media in responses

## Troubleshooting

- **Crawling Issues**: Ensure internet connectivity and valid channel handle
- **Missing Transcripts**: Some videos may not have available transcripts
- **Memory Usage**: For large channels, consider batch processing
- **Refresh Mode**: If auto-refresh isn't working, check the refresh status with `!status`

## Support

For issues or questions, please contact the development team.
