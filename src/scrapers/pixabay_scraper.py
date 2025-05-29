"""
Pixabay scraper implementation.
This scraper uses the Pixabay API to download wallpapers and images.
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

class PixabayScraper(BaseScraper):
    """
    Pixabay scraper implementation using their API.
    
    Note: To use this scraper, you need to register for a Pixabay API key at:
    https://pixabay.com/api/docs/
    
    The API has rate limits that are automatically respected by this implementation.
    """
    
    def __init__(self, 
                 download_directory: Path, 
                 api_key: Optional[str] = None,
                 **kwargs):
        """
        Initialize the Pixabay scraper.
        
        Args:
            download_directory: Where to save the downloaded wallpapers
            api_key: Your Pixabay API key
            **kwargs: Additional arguments to pass to BaseScraper
        """
        # Use a default rate limit of 1 second between requests to respect Pixabay's limits
        rate_limit = kwargs.get('rate_limit', 1.0)
        
        # Limit concurrent downloads to 3 by default
        max_concurrent = kwargs.get('max_concurrent_downloads', 3)
        
        # Get timeout from kwargs or use default
        timeout = kwargs.get('timeout', 60)
        
        # Initialize the base class
        super().__init__(
            base_url="https://pixabay.com/api/",
            download_directory=download_directory,
            rate_limit=rate_limit,
            max_concurrent_downloads=max_concurrent,
            timeout=timeout
        )
        
        # Store API key
        self.api_key = api_key or os.environ.get("PIXABAY_API_KEY")
        if not self.api_key:
            logger.warning("No Pixabay API key provided. Set PIXABAY_API_KEY environment variable or pass api_key parameter.")
        
    async def get_wallpaper_list(self, 
                               query: str = "", 
                               page: int = 1, 
                               per_page: int = 20,
                               image_type: str = "photo",
                               orientation: str = "horizontal",
                               category: str = "",
                               min_width: int = 1920,
                               min_height: int = 1080,
                               **kwargs) -> List[Dict[str, Any]]:
        """
        Get a list of available wallpapers from Pixabay.
        
        Args:
            query: Search query (e.g., "nature", "city", etc.)
            page: Page number to fetch
            per_page: Number of results per page (max 200)
            image_type: Type of image ("all", "photo", "illustration", "vector")
            orientation: Image orientation ("all", "horizontal", "vertical")
            category: Category filter (e.g., "nature", "backgrounds", "fashion", etc.)
            min_width: Minimum image width
            min_height: Minimum image height
            **kwargs: Additional filter parameters
            
        Returns:
            A list of wallpaper metadata dictionaries
        """
        if not self.api_key:
            logger.error("Cannot fetch wallpapers: No API key provided")
            return []
        
        # Respect rate limiting
        await self._respect_rate_limit()
        
        # Build params for the API request
        params = {
            'key': self.api_key,
            'q': query,
            'page': page,
            'per_page': min(per_page, 200),  # Pixabay allows up to 200 per page
            'image_type': image_type,
            'orientation': orientation,
            'min_width': min_width,
            'min_height': min_height,
        }
        
        # Add category if specified
        if category:
            params['category'] = category
            
        # Remove empty params
        params = {k: v for k, v in params.items() if v}
        
        # Make the request
        async with aiohttp.ClientSession() as session:
            timeout = ClientTimeout(total=self.timeout)
            async with session.get(self.base_url, params=params, timeout=timeout) as response:
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
        
        for item in data.get('hits', []):
            try:
                # Extract metadata
                wallpaper = {
                    'id': item.get('id'),
                    'title': item.get('tags', '').replace(',', ' ').strip() or f"pixabay_{item.get('id')}",
                    'thumbnail': item.get('previewURL'),
                    'preview': item.get('webformatURL'),
                    'small': item.get('largeImageURL'),
                    'full': item.get('fullHDURL') or item.get('largeImageURL'),
                    'original': item.get('imageURL') if 'imageURL' in item else None,
                    'user': item.get('user'),
                    'user_id': item.get('user_id'),
                    'width': item.get('imageWidth'),
                    'height': item.get('imageHeight'),
                    'downloads': item.get('downloads'),
                    'likes': item.get('likes'),
                    'views': item.get('views'),
                    'category': category or 'pixabay',
                    'tags': item.get('tags', '').split(','),
                    'orientation': orientation
                }
                wallpapers.append(wallpaper)
            except Exception as e:
                logger.warning(f"Error parsing wallpaper item: {e}")
        
        return wallpapers
    
    async def download_wallpaper(self, wallpaper_data: Dict[str, Any]) -> Optional[Path]:
        """
        Download a single wallpaper from Pixabay.
        
        Args:
            wallpaper_data: Metadata for the wallpaper to download
            
        Returns:
            Path to the downloaded file or None if download failed
        """
        # Use a semaphore to limit concurrent downloads
        async with self.semaphore:
            # Respect rate limiting
            await self._respect_rate_limit()
            
            # Get the download URL - use "full" resolution by default
            # Try original, fullHD, or large image in that order
            download_url = wallpaper_data.get('original') or wallpaper_data.get('full') or wallpaper_data.get('small')
            if not download_url:
                logger.error("No URL available for download")
                return None
            
            # Create a filename based on the wallpaper title and id
            title = wallpaper_data.get('title', 'pixabay')
            image_id = wallpaper_data.get('id', '')
            filename = sanitize_filename(f"{title}_{image_id}")
            
            # Get the file extension from the URL
            ext = get_file_extension_from_url(download_url) or '.jpg'
            
            # Create the full path
            category_dir = wallpaper_data.get('category', 'pixabay')
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
            
            # Download the file
            async with aiohttp.ClientSession() as session:
                success, error = await download_file(
                    url=download_url,
                    destination=output_path,
                    session=session,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                
                if success:
                    return output_path
                else:
                    logger.error(f"Failed to download wallpaper: {error}")
                    return None
