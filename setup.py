#!/usr/bin/env python3
"""
Setup script for the wallpaper scraper.
This script creates a default configuration file and helps with initial setup.
"""
import os
import json
import argparse
from pathlib import Path

def main():
    """Run the setup script."""
    parser = argparse.ArgumentParser(description='Set up the wallpaper scraper.')
    parser.add_argument('--download-dir', help='Directory to save wallpapers')
    parser.add_argument('--unsplash-api-key', help='Unsplash API key')
    parser.add_argument('--wallhaven-api-key', help='Wallhaven API key')
    parser.add_argument('--pixabay-api-key', help='Pixabay API key')
    
    args = parser.parse_args()
    
    # Get the config directory
    config_dir = Path.home() / ".config" / "wallpaper-scraper"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "config.json"
    
    # Default configuration
    config = {
        "download_directory": args.download_dir or "~/Pictures/Wallpapers",
        "rate_limit": 1.0,
        "max_concurrent_downloads": 3,
        "timeout": 60,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "log_level": "INFO",
        "unsplash_api_key": args.unsplash_api_key or "",
        "wallhaven_api_key": args.wallhaven_api_key or "",
        "pixabay_api_key": args.pixabay_api_key or ""
    }
    
    # Check if configuration file already exists
    if config_file.exists():
        print(f"Configuration file already exists at {config_file}")
        overwrite = input("Do you want to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("Setup aborted.")
            return
    
    # Create the download directory
    download_dir = Path(os.path.expanduser(config["download_directory"]))
    download_dir.mkdir(parents=True, exist_ok=True)
    
    # Write the configuration file
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"Configuration file created at {config_file}")
    print(f"Download directory: {download_dir}")
    
    # Instructions for API keys
    if not config["unsplash_api_key"]:
        print("\nNote: You need an Unsplash API key to use the Unsplash scraper.")
        print("Register at https://unsplash.com/developers to get an API key.")
        print("Then, either:")
        print("1. Run this script again with --unsplash-api-key YOUR_API_KEY")
        print("2. Edit the configuration file manually")
        print("3. Set the UNSPLASH_API_KEY environment variable")
        print("4. Pass the API key directly with --api-key when running the scraper")
    
    if not config["pixabay_api_key"]:
        print("\nNote: You need a Pixabay API key to use the Pixabay scraper.")
        print("Register at https://pixabay.com/api/docs/ to get an API key.")
        print("Then, either:")
        print("1. Run this script again with --pixabay-api-key YOUR_API_KEY")
        print("2. Edit the configuration file manually")
        print("3. Set the PIXABAY_API_KEY environment variable")
        print("4. Pass the API key directly with --api-key when running the scraper")
    
    print("\nSetup complete!")
    print("You can now run the scraper with:")
    print("python main.py --source unsplash --query \"nature\"")

if __name__ == "__main__":
    main()
