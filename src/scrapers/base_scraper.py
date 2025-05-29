"""
Base scraper module that defines the interface for all wallpaper scrapers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import aiohttp
from aiohttp import ClientTimeout
import asyncio
from pathlib import Path


class BaseScraper(ABC):
    """Base class for all wallpaper scrapers."""
    
    def __init__(self, 
                 base_url: str, 
                 download_directory: Path,
                 rate_limit: float = 1.0,  # Default: 1 request per second
                 max_concurrent_downloads: int = 3,
                 timeout: int = 60):  # Default timeout in seconds
        """
        Initialize the scraper.
        
        Args:
            base_url: The base URL of the wallpaper website
            download_directory: Where to save the downloaded wallpapers
            rate_limit: Minimum time in seconds between requests
            max_concurrent_downloads: Maximum number of concurrent downloads
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.download_directory = download_directory
        self.rate_limit = rate_limit
        self.max_concurrent_downloads = max_concurrent_downloads
        self.last_request_time = 0
        self.semaphore = asyncio.Semaphore(max_concurrent_downloads)
        self.timeout = timeout
        
    @abstractmethod
    async def get_wallpaper_list(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Get a list of available wallpapers.
        
        Returns:
            A list of wallpaper metadata dictionaries
        """
        pass
    
    @abstractmethod
    async def download_wallpaper(self, wallpaper_data: Dict[str, Any]) -> Optional[Path]:
        """
        Download a single wallpaper.
        
        Args:
            wallpaper_data: Metadata for the wallpaper to download
            
        Returns:
            Path to the downloaded file or None if download failed
        """
        pass
    
    async def download_all(self, **kwargs) -> List[Path]:
        """
        Download all wallpapers matching the criteria.
        
        Returns:
            List of paths to successfully downloaded wallpapers
        """
        wallpapers = await self.get_wallpaper_list(**kwargs)
        download_tasks = [self.download_wallpaper(wp) for wp in wallpapers]
        results = await asyncio.gather(*download_tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        successful_downloads = [r for r in results if isinstance(r, Path)]
        
        return successful_downloads
    
    async def _respect_rate_limit(self):
        """Ensure we respect the rate limit."""
        now = asyncio.get_event_loop().time()
        time_since_last = now - self.last_request_time
        
        if time_since_last < self.rate_limit:
            await asyncio.sleep(self.rate_limit - time_since_last)
            
        self.last_request_time = asyncio.get_event_loop().time()
