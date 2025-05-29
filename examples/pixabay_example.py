#!/usr/bin/env python3
"""
Example script showing how to use the Pixabay scraper.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.pixabay_scraper import PixabayScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pixabay-example')

async def main():
    """Download wallpapers from Pixabay."""
    logger.info("Starting Pixabay wallpaper download")
    
    # Get the API key from environment variables
    api_key = os.environ.get("PIXABAY_API_KEY")
    if not api_key:
        logger.error("No Pixabay API key found. Set the PIXABAY_API_KEY environment variable.")
        logger.info("You can get an API key by registering at: https://pixabay.com/api/docs/")
        return
    
    # Create a directory for downloads
    download_dir = Path.home() / "Pictures" / "Wallpapers" / "Pixabay"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize the scraper
    scraper = PixabayScraper(
        download_directory=download_dir,
        api_key=api_key,
        rate_limit=1.0,
        max_concurrent_downloads=3
    )
    
    # Search for nature wallpapers
    nature_wallpapers = await scraper.get_wallpaper_list(
        query="landscape nature", 
        per_page=10,
        orientation="horizontal",
        min_width=1920,
        min_height=1080
    )
    
    logger.info(f"Found {len(nature_wallpapers)} nature wallpapers")
    
    # Download the wallpapers
    downloaded = []
    for wallpaper in nature_wallpapers:
        path = await scraper.download_wallpaper(wallpaper)
        if path:
            downloaded.append(path)
    
    logger.info(f"Successfully downloaded {len(downloaded)} nature wallpapers")
    
    # Search for space wallpapers
    space_wallpapers = await scraper.get_wallpaper_list(
        query="space galaxy", 
        per_page=10,
        orientation="horizontal",
        min_width=1920,
        min_height=1080
    )
    
    logger.info(f"Found {len(space_wallpapers)} space wallpapers")
    
    # Download the wallpapers
    downloaded = []
    for wallpaper in space_wallpapers:
        path = await scraper.download_wallpaper(wallpaper)
        if path:
            downloaded.append(path)
    
    logger.info(f"Successfully downloaded {len(downloaded)} space wallpapers")
    
    # Search for city wallpapers
    city_wallpapers = await scraper.get_wallpaper_list(
        query="city skyline", 
        per_page=10,
        orientation="horizontal",
        min_width=1920,
        min_height=1080
    )
    
    logger.info(f"Found {len(city_wallpapers)} city wallpapers")
    
    # Download the wallpapers
    downloaded = []
    for wallpaper in city_wallpapers:
        path = await scraper.download_wallpaper(wallpaper)
        if path:
            downloaded.append(path)
    
    logger.info(f"Successfully downloaded {len(downloaded)} city wallpapers")

if __name__ == "__main__":
    asyncio.run(main())
