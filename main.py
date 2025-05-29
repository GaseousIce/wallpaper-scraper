#!/usr/bin/env python3
"""
Wallpaper Scraper - A tool to download wallpapers from various websites 
while respecting their resource usage.
"""
import asyncio
import logging
import argparse
import sys
import os
from pathlib import Path

# Add the current directory to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.scrapers.example_scraper import ExampleScraper
from src.scrapers.unsplash_scraper import UnsplashScraper
from src.scrapers.wallhaven_scraper import WallhavenScraper
from src.scrapers.pixabay_scraper import PixabayScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('wallpaper-scraper')

# Dictionary of available scrapers
SCRAPERS = {
    'example': ExampleScraper,
    'unsplash': UnsplashScraper,
    'wallhaven': WallhavenScraper,
    'pixabay': PixabayScraper
}

async def main():
    """Main entry point for the wallpaper scraper."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Download wallpapers from various websites.')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--output', '-o', help='Directory to save wallpapers')
    parser.add_argument('--source', '-s', choices=SCRAPERS.keys(), default='unsplash',
                        help='Wallpaper source to use')
    parser.add_argument('--query', '-q', help='Search query')
    parser.add_argument('--category', '-c', help='Category to download')
    parser.add_argument('--limit', '-l', type=int, help='Maximum number of wallpapers to download')
    parser.add_argument('--rate-limit', '-r', type=float, help='Seconds between requests')
    parser.add_argument('--max-concurrent', '-m', type=int, help='Maximum concurrent downloads')
    parser.add_argument('--api-key', '-k', help='API key for the selected source')
    parser.add_argument('--pages', '-p', type=int, default=1, help='Number of pages to download')
    parser.add_argument('--orientation', choices=['landscape', 'portrait', 'squarish'], 
                        default='landscape', help='Image orientation')
    parser.add_argument('--resolution', help='Resolution filter (e.g., "1920x1080")')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    config = Config(args.config)
    
    # Override config with command line arguments
    download_dir = args.output or config.get_download_dir()
    rate_limit = args.rate_limit or config.get('rate_limit')
    max_concurrent = args.max_concurrent or config.get('max_concurrent_downloads')
    timeout = config.get('timeout', 60)  # Get timeout from config or use default
    
    # Get API key from args, environment, or config
    api_key = args.api_key
    if not api_key:
        if args.source == 'unsplash':
            api_key = os.environ.get('UNSPLASH_API_KEY') or config.get('unsplash_api_key')
        elif args.source == 'wallhaven':
            api_key = os.environ.get('WALLHAVEN_API_KEY') or config.get('wallhaven_api_key')
        elif args.source == 'pixabay':
            api_key = os.environ.get('PIXABAY_API_KEY') or config.get('pixabay_api_key')
    
    # Ensure download directory exists
    download_dir = Path(download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Using {args.source} as the wallpaper source")
    logger.info(f"Downloading wallpapers to: {download_dir}")
    logger.info(f"Rate limit: {rate_limit} seconds between requests")
    logger.info(f"Max concurrent downloads: {max_concurrent}")
    
    # Initialize the selected scraper
    scraper_class = SCRAPERS[args.source]
    scraper = scraper_class(
        download_directory=download_dir,
        api_key=api_key,
        rate_limit=rate_limit,
        max_concurrent_downloads=max_concurrent,
        timeout=timeout
    )
    
    try:
        all_wallpapers = []
        total_downloaded = []
        
        # Download from multiple pages if specified
        for page in range(1, args.pages + 1):
            if page > 1:
                logger.info(f"Fetching page {page} of {args.pages}")
            
            # Get wallpapers with the appropriate parameters
            wallpapers = await scraper.get_wallpaper_list(
                query=args.query or "",
                category=args.category or "",
                page=page,
                orientation=args.orientation,
                resolution=args.resolution
            )
            
            all_wallpapers.extend(wallpapers)
            
            # Apply limit if specified
            if args.limit and len(all_wallpapers) > args.limit:
                all_wallpapers = all_wallpapers[:args.limit]
                break
                
            logger.info(f"Found {len(wallpapers)} wallpapers on page {page}")
            
            # Download wallpapers from this page
            if wallpapers:
                downloaded = await scraper.download_all()
                total_downloaded.extend(downloaded)
        
        logger.info(f"Successfully downloaded {len(total_downloaded)} wallpapers")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
        sys.exit(130)