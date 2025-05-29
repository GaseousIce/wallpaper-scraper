"""
Wallhaven scraper implementation.
This scraper fetches wallpapers from wallhaven.cc.
"""
import asyncio
import aiohttp
from aiohttp import ClientTimeout
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import os
from bs4 import BeautifulSoup
import re

from src.scrapers.base_scraper import BaseScraper
from src.utils.download import download_file, sanitize_filename, get_file_extension_from_url

logger = logging.getLogger(__name__)

class WallhavenScraper(BaseScraper):
    """
    Wallhaven scraper implementation.
    Fetches wallpapers from wallhaven.cc with appropriate rate limiting.
    """
    
    def __init__(self, 
                 download_directory: Path, 
                 api_key: Optional[str] = None,
                 **kwargs):
        """
        Initialize the Wallhaven scraper.
        
        Args:
            download_directory: Where to save the downloaded wallpapers
            api_key: Optional Wallhaven API key for accessing NSFW content
            **kwargs: Additional arguments to pass to BaseScraper
        """
        # Use a default rate limit of 2 seconds between requests to be respectful
        rate_limit = kwargs.get('rate_limit', 2.0)
        
        # Use a default of 2 concurrent downloads to avoid overwhelming the server
        max_concurrent = kwargs.get('max_concurrent_downloads', 2)
        
        # Get timeout from kwargs or use default
        timeout = kwargs.get('timeout', 60)
        
        # Initialize the base class
        super().__init__(
            base_url="https://wallhaven.cc",
            download_directory=download_directory,
            rate_limit=rate_limit,
            max_concurrent_downloads=max_concurrent,
            timeout=timeout
        )
        
        # Store API key
        self.api_key = api_key or os.environ.get("WALLHAVEN_API_KEY", "")
        
        # Set up headers for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def get_wallpaper_list(self, 
                               query: str = "", 
                               page: int = 1,
                               categories: str = "111",  # General, Anime, People
                               purity: str = "100",      # SFW only by default
                               sorting: str = "date_added",
                               order: str = "desc",
                               resolution: str = "",
                               **kwargs) -> List[Dict[str, Any]]:
        """
        Get a list of available wallpapers from Wallhaven.
        
        Args:
            query: Search query
            page: Page number to fetch
            categories: Category filter (100=General, 010=Anime, 001=People)
            purity: Content filter (100=SFW, 010=Sketchy, 001=NSFW)
            sorting: Sort method (date_added, relevance, random, views, favorites, toplist)
            order: Sort order (desc, asc)
            resolution: Resolution filter (e.g., "1920x1080")
            **kwargs: Additional filter parameters
            
        Returns:
            A list of wallpaper metadata dictionaries
        """
        # Respect rate limiting
        await self._respect_rate_limit()
        
        # Construct the URL
        if self.api_key:
            # Use API if available
            url = f"{self.base_url}/api/v1/search"
            params = {
                'q': query,
                'categories': categories,
                'purity': purity,
                'sorting': sorting,
                'order': order,
                'page': page,
                'apikey': self.api_key
            }
            
            if resolution:
                params['resolutions'] = resolution
                
            # Make the API request
            async with aiohttp.ClientSession() as session:
                timeout = ClientTimeout(total=self.timeout)
                async with session.get(url, params=params, headers=self.headers, timeout=timeout) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch wallpaper list: HTTP {response.status}")
                        return []
                    
                    data = await response.json()
                    
            # Parse the API response
            wallpapers = []
            for item in data.get('data', []):
                try:
                    wallpaper = {
                        'id': item.get('id'),
                        'title': f"wallhaven_{item.get('id')}",
                        'thumbnail': item.get('thumbs', {}).get('small'),
                        'url': item.get('url'),
                        'download_url': item.get('path'),
                        'category': query or 'wallhaven',
                        'width': item.get('dimension_x'),
                        'height': item.get('dimension_y'),
                        'resolution': f"{item.get('dimension_x')}x{item.get('dimension_y')}",
                        'file_size': item.get('file_size'),
                        'colors': item.get('colors', []),
                        'tags': [tag.get('name') for tag in item.get('tags', [])]
                    }
                    wallpapers.append(wallpaper)
                except Exception as e:
                    logger.warning(f"Error parsing wallpaper item: {e}")
        else:
            # Use web scraping as fallback
            url = f"{self.base_url}/search"
            params = {
                'q': query,
                'categories': categories,
                'purity': purity,
                'sorting': sorting,
                'order': order,
                'page': page
            }
            
            if resolution:
                params['resolutions'] = resolution
                
            # Make the request
            async with aiohttp.ClientSession() as session:
                timeout = ClientTimeout(total=self.timeout)
                async with session.get(url, params=params, headers=self.headers, timeout=timeout) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch wallpaper list: HTTP {response.status}")
                        return []
                    
                    html = await response.text()
            
            # Parse the HTML
            soup = BeautifulSoup(html, 'html.parser')
            wallpapers = []
            
            # Find all wallpaper thumbs
            for figure in soup.select('figure'):
                try:
                    wallpaper_id = figure.get('data-wallpaper-id')
                    if not wallpaper_id:
                        continue
                        
                    # Extract resolution from the figure
                    resolution_elem = figure.select_one('span.wall-res')
                    resolution_text = resolution_elem.text.strip() if resolution_elem else ""
                    
                    # Extract width and height from resolution
                    width, height = 0, 0
                    if resolution_text:
                        match = re.match(r'(\d+)\s*x\s*(\d+)', resolution_text)
                        if match:
                            width, height = map(int, match.groups())
                    
                    # Get the preview image URL
                    img = figure.select_one('img')
                    thumb_url = img.get('data-src') if img else ""
                    
                    # Construct the detail page URL
                    detail_url = f"{self.base_url}/w/{wallpaper_id}"
                    
                    wallpaper = {
                        'id': wallpaper_id,
                        'title': f"wallhaven_{wallpaper_id}",
                        'thumbnail': thumb_url,
                        'url': detail_url,
                        'category': query or 'wallhaven',
                        'width': width,
                        'height': height,
                        'resolution': resolution_text
                    }
                    wallpapers.append(wallpaper)
                except Exception as e:
                    logger.warning(f"Error parsing wallpaper item: {e}")
        
        return wallpapers
    
    async def download_wallpaper(self, wallpaper_data: Dict[str, Any]) -> Optional[Path]:
        """
        Download a single wallpaper from Wallhaven.
        
        Args:
            wallpaper_data: Metadata for the wallpaper to download
            
        Returns:
            Path to the downloaded file or None if download failed
        """
        # Use a semaphore to limit concurrent downloads
        async with self.semaphore:
            # Respect rate limiting
            await self._respect_rate_limit()
            
            # Get the download URL
            download_url = wallpaper_data.get('download_url')
            
            # If we don't have a direct download URL, we need to fetch the detail page
            if not download_url:
                detail_url = wallpaper_data.get('url')
                if not detail_url:
                    logger.error("No URL available for download")
                    return None
                
                # Fetch the detail page to get the download URL
                async with aiohttp.ClientSession() as session:
                    timeout = ClientTimeout(total=self.timeout)
                    async with session.get(detail_url, headers=self.headers, timeout=timeout) as response:
                        if response.status != 200:
                            logger.error(f"Failed to fetch wallpaper detail page: HTTP {response.status}")
                            return None
                        
                        html = await response.text()
                
                # Parse the detail page
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find the download link
                download_elem = soup.select_one('img#wallpaper')
                if download_elem and download_elem.get('src'):
                    download_url = download_elem.get('src')
                else:
                    logger.error("Could not find download URL on detail page")
                    return None
            
            # Create a filename based on the wallpaper title
            title = wallpaper_data.get('title', 'wallpaper')
            filename = sanitize_filename(title)
            
            # Get the file extension from the URL
            ext = get_file_extension_from_url(download_url) or '.jpg'
            
            # Create the full path
            category_dir = wallpaper_data.get('category', 'wallhaven')
            output_dir = self.download_directory / category_dir
            os.makedirs(output_dir, exist_ok=True)
            
            # Add resolution to filename if available
            resolution = wallpaper_data.get('resolution', '')
            if resolution:
                filename += f"_{resolution}"
                
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
                    headers=self.headers
                )
                
                if success:
                    return output_path
                else:
                    logger.error(f"Failed to download wallpaper: {error}")
                    return None
