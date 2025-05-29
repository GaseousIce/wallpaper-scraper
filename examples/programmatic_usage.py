#!/usr/bin/env python3
"""
Example script showing how to use the wallpaper scrapers programmatically.
"""
import asyncio
import logging
import os
from pathlib import Path

from src.scrapers.unsplash_scraper import UnsplashScraper
from src.scrapers.wallhaven_scraper import WallhavenScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('wallpaper-example')

async def download_from_unsplash():
    """Download wallpapers from Unsplash."""
    logger.info("Starting Unsplash wallpaper download")
    
    # Get the API key from environment variables
    api_key = os.environ.get("UNSPLASH_API_KEY")
    if not api_key:
        logger.error("No Unsplash API key found. Set the UNSPLASH_API_KEY environment variable.")
        logger.info("You can get an API key by registering at: https://unsplash.com/developers")
        return
    
    # Create a directory for downloads
    download_dir = Path.home() / "Pictures" / "Wallpapers" / "Unsplash"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize the scraper
    scraper = UnsplashScraper(
        download_directory=download_dir,
        api_key=api_key,
        rate_limit=1.0,  # 1 request per second
        max_concurrent_downloads=3
    )
    
    # Search for nature wallpapers
    wallpapers = await scraper.get_wallpaper_list(
        query="nature", 
        per_page=10,
        orientation="landscape"
    )
    
    logger.info(f"Found {len(wallpapers)} nature wallpapers")
    
    # Download the wallpapers
    downloaded = []
    for wallpaper in wallpapers:
        path = await scraper.download_wallpaper(wallpaper)
        if path:
            downloaded.append(path)
    
    logger.info(f"Successfully downloaded {len(downloaded)} nature wallpapers")
    
    # Search for city wallpapers
    wallpapers = await scraper.get_wallpaper_list(
        query="city", 
        per_page=10,
        orientation="landscape"
    )
    
    logger.info(f"Found {len(wallpapers)} city wallpapers")
    
    # Download the wallpapers
    downloaded = []
    for wallpaper in wallpapers:
        path = await scraper.download_wallpaper(wallpaper)
        if path:
            downloaded.append(path)
    
    logger.info(f"Successfully downloaded {len(downloaded)} city wallpapers")

async def download_from_wallhaven():
    """Download wallpapers from Wallhaven."""
    logger.info("Starting Wallhaven wallpaper download")
    
    # Create a directory for downloads
    download_dir = Path.home() / "Pictures" / "Wallpapers" / "Wallhaven"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize the scraper (API key is optional)
    scraper = WallhavenScraper(
        download_directory=download_dir,
        rate_limit=2.0,  # 2 seconds between requests
        max_concurrent_downloads=2
    )
    
    # Search for space wallpapers
    wallpapers = await scraper.get_wallpaper_list(
        query="space", 
        categories="111",  # General, Anime, People
        purity="100",      # SFW only
        sorting="relevance",
        resolution="1920x1080"
    )
    
    logger.info(f"Found {len(wallpapers)} space wallpapers")
    
    # Download the wallpapers
    downloaded = []
    for wallpaper in wallpapers[:5]:  # Only download the first 5
        path = await scraper.download_wallpaper(wallpaper)
        if path:
            downloaded.append(path)
    
    logger.info(f"Successfully downloaded {len(downloaded)} space wallpapers")

async def main():
    """Run the example."""
    # Download from Unsplash
    await download_from_unsplash()
    
    # Download from Wallhaven
    await download_from_wallhaven()

if __name__ == "__main__":
    asyncio.run(main())
