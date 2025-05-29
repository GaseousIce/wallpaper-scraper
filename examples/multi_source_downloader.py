#!/usr/bin/env python3
"""
Multi-source wallpaper downloader.
This script demonstrates how to use multiple scrapers to download wallpapers from different sources.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path
import argparse

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.unsplash_scraper import UnsplashScraper
from src.scrapers.wallhaven_scraper import WallhavenScraper
from src.scrapers.pixabay_scraper import PixabayScraper
from src.utils.config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('multi-source-downloader')

async def download_from_unsplash(query, download_dir, api_key, limit=10):
    """Download wallpapers from Unsplash."""
    if not api_key:
        logger.warning("Skipping Unsplash: No API key provided")
        return []
        
    logger.info(f"Downloading from Unsplash with query: '{query}'")
    
    # Create scraper
    scraper = UnsplashScraper(
        download_directory=download_dir,
        api_key=api_key,
        rate_limit=1.0,
        max_concurrent_downloads=3
    )
    
    # Get wallpapers
    wallpapers = await scraper.get_wallpaper_list(
        query=query,
        per_page=limit,
        orientation="landscape"
    )
    
    logger.info(f"Found {len(wallpapers)} wallpapers on Unsplash")
    
    # Download wallpapers
    downloaded = []
    for wallpaper in wallpapers:
        path = await scraper.download_wallpaper(wallpaper)
        if path:
            downloaded.append(path)
    
    logger.info(f"Downloaded {len(downloaded)} wallpapers from Unsplash")
    return downloaded

async def download_from_wallhaven(query, download_dir, api_key=None, limit=10):
    """Download wallpapers from Wallhaven."""
    logger.info(f"Downloading from Wallhaven with query: '{query}'")
    
    # Create scraper
    scraper = WallhavenScraper(
        download_directory=download_dir,
        api_key=api_key,
        rate_limit=2.0,
        max_concurrent_downloads=2
    )
    
    # Get wallpapers
    wallpapers = await scraper.get_wallpaper_list(
        query=query,
        categories="111",  # General, Anime, People
        purity="100",      # SFW only
        sorting="relevance"
    )
    
    # Limit the number of wallpapers
    wallpapers = wallpapers[:limit]
    
    logger.info(f"Found {len(wallpapers)} wallpapers on Wallhaven")
    
    # Download wallpapers
    downloaded = []
    for wallpaper in wallpapers:
        path = await scraper.download_wallpaper(wallpaper)
        if path:
            downloaded.append(path)
    
    logger.info(f"Downloaded {len(downloaded)} wallpapers from Wallhaven")
    return downloaded

async def download_from_pixabay(query, download_dir, api_key, limit=10):
    """Download wallpapers from Pixabay."""
    if not api_key:
        logger.warning("Skipping Pixabay: No API key provided")
        return []
        
    logger.info(f"Downloading from Pixabay with query: '{query}'")
    
    # Create scraper
    scraper = PixabayScraper(
        download_directory=download_dir,
        api_key=api_key,
        rate_limit=1.0,
        max_concurrent_downloads=3
    )
    
    # Get wallpapers
    wallpapers = await scraper.get_wallpaper_list(
        query=query,
        per_page=limit,
        orientation="horizontal",
        min_width=1920,
        min_height=1080
    )
    
    logger.info(f"Found {len(wallpapers)} wallpapers on Pixabay")
    
    # Download wallpapers
    downloaded = []
    for wallpaper in wallpapers:
        path = await scraper.download_wallpaper(wallpaper)
        if path:
            downloaded.append(path)
    
    logger.info(f"Downloaded {len(downloaded)} wallpapers from Pixabay")
    return downloaded

async def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Download wallpapers from multiple sources.')
    parser.add_argument('--query', '-q', required=True, help='Search query')
    parser.add_argument('--output', '-o', help='Directory to save wallpapers')
    parser.add_argument('--limit', '-l', type=int, default=5, help='Maximum number of wallpapers to download per source')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--sources', nargs='+', default=['unsplash', 'wallhaven', 'pixabay'],
                        choices=['unsplash', 'wallhaven', 'pixabay'],
                        help='Wallpaper sources to use')
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config(args.config)
    
    # Get download directory
    download_dir = args.output or config.get_download_dir()
    download_dir = Path(download_dir) / "multi-source" / args.query.replace(" ", "_")
    download_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Downloading wallpapers to: {download_dir}")
    
    # Get API keys
    unsplash_api_key = os.environ.get('UNSPLASH_API_KEY') or config.get('unsplash_api_key')
    wallhaven_api_key = os.environ.get('WALLHAVEN_API_KEY') or config.get('wallhaven_api_key')
    pixabay_api_key = os.environ.get('PIXABAY_API_KEY') or config.get('pixabay_api_key')
    
    # Download wallpapers from selected sources
    tasks = []
    
    if 'unsplash' in args.sources:
        tasks.append(download_from_unsplash(args.query, download_dir, unsplash_api_key, args.limit))
        
    if 'wallhaven' in args.sources:
        tasks.append(download_from_wallhaven(args.query, download_dir, wallhaven_api_key, args.limit))
        
    if 'pixabay' in args.sources:
        tasks.append(download_from_pixabay(args.query, download_dir, pixabay_api_key, args.limit))
    
    # Run all tasks
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Count total downloads
    total_downloads = 0
    for result in results:
        if isinstance(result, list):
            total_downloads += len(result)
        elif isinstance(result, Exception):
            logger.error(f"Error during download: {result}")
    
    logger.info(f"Total wallpapers downloaded: {total_downloads}")
    logger.info(f"All wallpapers saved to: {download_dir}")

if __name__ == "__main__":
    asyncio.run(main())
