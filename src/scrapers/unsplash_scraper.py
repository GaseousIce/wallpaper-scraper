"""
Unsplash scraper implementation.
This scraper uses the Unsplash API to download wallpapers.
"""
import asyncio
import aiohttp
from aiohttp import ClientTimeout
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import os
import json

from src.scrapers.base_scraper import BaseScraper
from src.utils.download import download_file, sanitize_filename, get_file_extension_from_url

logger = logging.getLogger(__name__)

class UnsplashScraper(BaseScraper):
    """
    Unsplash scraper implementation using their API.
    
    Note: To use this scraper, you need to register for an Unsplash API key at:
    https://unsplash.com/developers
    
    The API has rate limits that are automatically respected by this implementation.
    """
    
    def __init__(self, 
                 download_directory: Path, 
                 api_key: Optional[str] = None,
                 **kwargs):
        """
        Initialize the Unsplash scraper.
        
        Args:
            download_directory: Where to save the downloaded wallpapers
            api_key: Your Unsplash API key
            **kwargs: Additional arguments to pass to BaseScraper
        """
        # Use a default rate limit of 1 second between requests to respect Unsplash's limits
        rate_limit = kwargs.get('rate_limit', 1.0)
        
        # Limit concurrent downloads to 3 by default
        max_concurrent = kwargs.get('max_concurrent_downloads', 3)
        
        # Get timeout from kwargs or use default
        timeout = kwargs.get('timeout', 60)
        
        # Initialize the base class
        super().__init__(
            base_url="https://api.unsplash.com",
            download_directory=download_directory,
            rate_limit=rate_limit,
            max_concurrent_downloads=max_concurrent,
            timeout=timeout
        )
        
        # Store API key
        self.api_key = api_key or os.environ.get("UNSPLASH_API_KEY")
        if not self.api_key:
            logger.warning("No Unsplash API key provided. Set UNSPLASH_API_KEY environment variable or pass api_key parameter.")
        
        # Set up headers for API requests
        self.headers = {
            'Authorization': f'Client-ID {self.api_key}',
            'Accept-Version': 'v1'
        }
    
    async def get_wallpaper_list(self, 
                               query: str = "", 
                               page: int = 1, 
                               per_page: int = 30,
                               orientation: str = "landscape",
                               **kwargs) -> List[Dict[str, Any]]:
        """
        Get a list of available wallpapers from Unsplash.
        
        Args:
            query: Search query (e.g., "nature", "city", etc.)
            page: Page number to fetch
            per_page: Number of results per page (max 30)
            orientation: Image orientation ("landscape", "portrait", or "squarish")
            **kwargs: Additional filter parameters
            
        Returns:
            A list of wallpaper metadata dictionaries
        """
        if not self.api_key:
            logger.error("Cannot fetch wallpapers: No API key provided")
            return []
        
        # Respect rate limiting
        await self._respect_rate_limit()
        
        # Construct the URL
        endpoint = "/photos/random" if not query else "/search/photos"
        
        params = {
            'query': query,
            'page': page,
            'per_page': min(per_page, 30),  # Unsplash limits to 30 per page
            'orientation': orientation
        }
        
        # Remove empty params
        params = {k: v for k, v in params.items() if v}
        
        # Make the request
        async with aiohttp.ClientSession() as session:
            timeout = ClientTimeout(total=self.timeout)
            async with session.get(f"{self.base_url}{endpoint}", 
                                headers=self.headers, 
                                params=params,
                                timeout=timeout) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch wallpapers: HTTP {response.status}")
                    try:
                        error_data = await response.json()
                        logger.error(f"Error details: {json.dumps(error_data)}")
                    except:
                        logger.error(f"Error details: {await response.text()}")
                    return []
                
                data = await response.json()
        
        # Parse the response
        wallpapers = []
        
        # Handle different response formats
        if endpoint == "/search/photos":
            results = data.get('results', [])
        else:
            results = data if isinstance(data, list) else []
        
        for item in results:
            try:
                # Extract metadata
                wallpaper = {
                    'id': item.get('id'),
                    'title': item.get('description') or item.get('alt_description') or f"unsplash_{item.get('id')}",
                    'thumbnail': item.get('urls', {}).get('thumb'),
                    'small': item.get('urls', {}).get('small'),
                    'regular': item.get('urls', {}).get('regular'),
                    'full': item.get('urls', {}).get('full'),
                    'raw': item.get('urls', {}).get('raw'),
                    'download_url': item.get('links', {}).get('download'),
                    'user': item.get('user', {}).get('name'),
                    'username': item.get('user', {}).get('username'),
                    'width': item.get('width'),
                    'height': item.get('height'),
                    'category': query or 'unsplash',
                    'orientation': orientation
                }
                wallpapers.append(wallpaper)
            except Exception as e:
                logger.warning(f"Error parsing wallpaper item: {e}")
        
        return wallpapers
    
    async def download_wallpaper(self, wallpaper_data: Dict[str, Any]) -> Optional[Path]:
        """
        Download a single wallpaper from Unsplash.
        
        Args:
            wallpaper_data: Metadata for the wallpaper to download
            
        Returns:
            Path to the downloaded file or None if download failed
        """
        # Use a semaphore to limit concurrent downloads
        async with self.semaphore:
            # Respect rate limiting
            await self._respect_rate_limit()
            
            # Get the download URL - use "regular" resolution by default
            # You can modify this to use 'full' or 'raw' for higher quality
            download_url = wallpaper_data.get('regular')
            if not download_url:
                logger.error("No URL available for download")
                return None
            
            # Create a filename based on the wallpaper title and photographer
            title = wallpaper_data.get('title', 'wallpaper')
            user = wallpaper_data.get('username', '')
            filename = sanitize_filename(f"{title}_by_{user}" if user else title)
            
            # Get the file extension from the URL
            ext = get_file_extension_from_url(download_url) or '.jpg'
            
            # Create the full path
            category_dir = wallpaper_data.get('category', 'unsplash')
            output_dir = self.download_directory / category_dir
            os.makedirs(output_dir, exist_ok=True)
            
            # Add resolution to filename if available
            width = wallpaper_data.get('width')
            height = wallpaper_data.get('height')
            if width and height:
                filename += f"_{width}x{height}"
                
            output_path = output_dir / f"{filename}{ext}"
            
            # Check if file already exists
            if output_path.exists():
                logger.info(f"Wallpaper already exists: {output_path}")
                return output_path
            
            # Create a trigger for the Unsplash API download endpoint
            # This properly attributes the download to your application
            if wallpaper_data.get('download_url') and self.api_key:
                try:
                    async with aiohttp.ClientSession() as session:
                        timeout = ClientTimeout(total=self.timeout)
                        async with session.get(
                            wallpaper_data['download_url'],
                            headers=self.headers,
                            timeout=timeout
                        ) as response:
                            if response.status == 200:
                                # This is just to trigger the download count
                                pass
                except Exception as e:
                    logger.warning(f"Failed to register download with Unsplash API: {e}")
            
            # Download the actual file
            async with aiohttp.ClientSession() as session:
                success, error = await download_file(
                    url=download_url,
                    destination=output_path,
                    session=session,
                    # Don't use API headers for the actual download
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                
                if success:
                    return output_path
                else:
                    logger.error(f"Failed to download wallpaper: {error}")
                    return None
