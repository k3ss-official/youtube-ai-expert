"""
Test Script for Refresh Switch Functionality

This script tests the auto/manual refresh switch functionality in the enhanced CLI.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interface.enhanced_cli import EnhancedCLI
from src.utils.config import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_refresh_switch.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_refresh_switch(base_dir, channel_name):
    """
    Test the refresh switch functionality.
    
    Args:
        base_dir: Base directory of the project
        channel_name: Name of the channel (without @ symbol)
    """
    logger.info(f"Starting refresh switch validation for channel {channel_name}")
    
    # Initialize CLI
    cli = EnhancedCLI(base_dir=base_dir, channel_name=channel_name)
    
    # Test 1: Check initial refresh mode
    initial_mode = cli.refresh_manager.get_refresh_mode()
    logger.info(f"Initial refresh mode: {initial_mode}")
    print(f"Initial refresh mode: {initial_mode}")
    
    # Test 2: Toggle refresh mode
    new_mode = cli.toggle_refresh_mode()
    logger.info(f"Toggled refresh mode to: {new_mode}")
    print(f"Toggled refresh mode to: {new_mode}")
    
    # Test 3: Toggle back
    new_mode = cli.toggle_refresh_mode()
    logger.info(f"Toggled refresh mode back to: {new_mode}")
    print(f"Toggled refresh mode back to: {new_mode}")
    
    # Test 4: Get refresh status
    status = cli.get_refresh_status()
    logger.info(f"Refresh status: {json.dumps(status, indent=2)}")
    print(f"Refresh status: {json.dumps(status, indent=2)}")
    
    # Test 5: Set to manual mode and test refresh
    cli.refresh_manager.set_refresh_mode('manual')
    logger.info("Set refresh mode to manual")
    print("Set refresh mode to manual")
    
    # Test 6: Test auto refresh check (should not refresh in manual mode)
    should_refresh = cli.refresh_manager.check_auto_refresh(f"@{channel_name}")
    logger.info(f"Should refresh in manual mode: {should_refresh}")
    print(f"Should refresh in manual mode: {should_refresh}")
    
    # Test 7: Set to auto mode
    cli.refresh_manager.set_refresh_mode('auto')
    logger.info("Set refresh mode to auto")
    print("Set refresh mode to auto")
    
    # Test 8: Simulate last refresh 8 days ago
    config_manager = ConfigManager(base_dir)
    last_refresh = datetime.now() - timedelta(days=8)
    config_manager.set_last_refresh(last_refresh)
    logger.info(f"Set last refresh to 8 days ago: {last_refresh.isoformat()}")
    print(f"Set last refresh to 8 days ago: {last_refresh.isoformat()}")
    
    # Test 9: Test auto refresh check (should refresh in auto mode with old timestamp)
    should_refresh = cli.refresh_manager.check_auto_refresh(f"@{channel_name}")
    logger.info(f"Should refresh in auto mode with old timestamp: {should_refresh}")
    print(f"Should refresh in auto mode with old timestamp: {should_refresh}")
    
    # Test 10: Reset to manual mode for user
    cli.refresh_manager.set_refresh_mode('manual')
    logger.info("Reset refresh mode to manual")
    print("Reset refresh mode to manual")
    
    logger.info("Refresh switch validation completed")
    print("\nRefresh switch validation completed")
    
    return {
        "initial_mode": initial_mode,
        "final_mode": "manual",
        "status": cli.get_refresh_status()
    }

if __name__ == "__main__":
    # Get base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Get channel name from command line or use default
    channel_name = sys.argv[1] if len(sys.argv) > 1 else "ManusAGI"
    
    # Run tests
    test_refresh_switch(base_dir, channel_name)
