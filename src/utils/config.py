"""
Configuration module for the wallpaper scraper.
"""
import os
from pathlib import Path
import json
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    "download_directory": "~/Pictures/Wallpapers",
    "rate_limit": 1.0,  # 1 request per second
    "max_concurrent_downloads": 3,
    "timeout": 60,  # seconds
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "log_level": "INFO"
}

class Config:
    """Configuration manager for the wallpaper scraper."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or os.path.expanduser("~/.config/wallpaper-scraper/config.json")
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration from the config file.
        
        Returns:
            The configuration dictionary
        """
        # Start with default configuration
        config = DEFAULT_CONFIG.copy()
        
        # Try to load configuration from file
        try:
            config_dir = os.path.dirname(self.config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            
        return config
    
    def save_config(self) -> bool:
        """
        Save the current configuration to the config file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            config_dir = os.path.dirname(self.config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
                
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key
            default: Default value if the key doesn't exist
            
        Returns:
            The configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key
            value: The value to set
        """
        self.config[key] = value
        
    def get_download_dir(self) -> Path:
        """
        Get the download directory as a Path object.
        
        Returns:
            The download directory Path
        """
        download_dir = self.get("download_directory")
        return Path(os.path.expanduser(download_dir))
