#!/usr/bin/env python3
"""
Simple script to download wallpapers.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.wallhaven_scraper import WallhavenScraper

async def main():
    """Download some wallpapers."""
    print("Wallpaper Scraper Demo")
    
    # Create download directory
    download_dir = Path.home() / "Pictures" / "Wallpapers"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading to: {download_dir}")
    
    # Initialize scraper
    scraper = WallhavenScraper(
        download_directory=download_dir,
        rate_limit=2.0,
        max_concurrent_downloads=2
    )
    
    # Get wallpapers
    wallpapers = await scraper.get_wallpaper_list(
        query="mountains",
        categories="111",
        purity="100",
        sorting="relevance",
        limit=5
    )
    
    print(f"Found {len(wallpapers)} wallpapers")
    
    # Only download a few to test
    for i, wallpaper in enumerate(wallpapers[:3]):
        print(f"Downloading wallpaper {i+1}/{min(3, len(wallpapers))}")
        path = await scraper.download_wallpaper(wallpaper)
        if path:
            print(f"Downloaded to: {path}")
    
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
