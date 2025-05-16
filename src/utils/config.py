"""
Configuration Module

This module manages system configuration, including refresh mode settings.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manager for system configuration.
    """
    
    def __init__(self, base_dir: str):
        """
        Initialize the configuration manager.
        
        Args:
            base_dir: Base directory of the project
        """
        self.base_dir = base_dir
        self.config_dir = os.path.join(base_dir, 'data', 'config')
        self.config_file = os.path.join(self.config_dir, 'system_config.json')
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load or create config
        self.config = self._load_config()
        
        logger.info(f"Initialized configuration manager")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default.
        
        Returns:
            Configuration dictionary
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
                return config
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
        
        # Create default configuration
        default_config = {
            'refresh_mode': 'manual',  # 'auto' or 'manual'
            'last_refresh': datetime.now().isoformat(),
            'auto_refresh_interval_days': 7,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Save default configuration
        self._save_config(default_config)
        
        logger.info(f"Created default configuration")
        return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary
        """
        # Update timestamp
        config['updated_at'] = datetime.now().isoformat()
        
        # Save to file
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved configuration to {self.config_file}")
    
    def get_refresh_mode(self) -> str:
        """
        Get current refresh mode.
        
        Returns:
            Refresh mode ('auto' or 'manual')
        """
        return self.config.get('refresh_mode', 'manual')
    
    def set_refresh_mode(self, mode: str) -> None:
        """
        Set refresh mode.
        
        Args:
            mode: Refresh mode ('auto' or 'manual')
        """
        if mode not in ['auto', 'manual']:
            raise ValueError(f"Invalid refresh mode: {mode}")
        
        self.config['refresh_mode'] = mode
        self._save_config(self.config)
        
        logger.info(f"Set refresh mode to {mode}")
    
    def get_last_refresh(self) -> datetime:
        """
        Get last refresh timestamp.
        
        Returns:
            Datetime of last refresh
        """
        last_refresh_str = self.config.get('last_refresh')
        if last_refresh_str:
            return datetime.fromisoformat(last_refresh_str)
        return datetime.now() - timedelta(days=30)  # Default to long ago
    
    def set_last_refresh(self, timestamp: Optional[datetime] = None) -> None:
        """
        Set last refresh timestamp.
        
        Args:
            timestamp: Datetime of last refresh (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        self.config['last_refresh'] = timestamp.isoformat()
        self._save_config(self.config)
        
        logger.info(f"Set last refresh to {timestamp.isoformat()}")
    
    def get_auto_refresh_interval(self) -> int:
        """
        Get auto refresh interval in days.
        
        Returns:
            Number of days between auto refreshes
        """
        return self.config.get('auto_refresh_interval_days', 7)
    
    def set_auto_refresh_interval(self, days: int) -> None:
        """
        Set auto refresh interval in days.
        
        Args:
            days: Number of days between auto refreshes
        """
        if days < 1:
            raise ValueError(f"Invalid refresh interval: {days}")
        
        self.config['auto_refresh_interval_days'] = days
        self._save_config(self.config)
        
        logger.info(f"Set auto refresh interval to {days} days")
    
    def should_refresh(self) -> bool:
        """
        Check if channel should be refreshed based on mode and last refresh.
        
        Returns:
            Boolean indicating whether refresh is needed
        """
        # If manual mode, don't auto-refresh
        if self.get_refresh_mode() == 'manual':
            return False
        
        # If auto mode, check if interval has passed
        last_refresh = self.get_last_refresh()
        interval_days = self.get_auto_refresh_interval()
        
        now = datetime.now()
        next_refresh = last_refresh + timedelta(days=interval_days)
        
        return now >= next_refresh
