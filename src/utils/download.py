"""
Utility functions for the wallpaper scraper.
"""
import os
from pathlib import Path
import aiofiles
import aiohttp
import asyncio
from tqdm import tqdm
import logging
from typing import Optional, Tuple, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('wallpaper_utils')

async def download_file(url: str, 
                       destination: Path, 
                       session: aiohttp.ClientSession,
                       headers: Optional[Dict[str, str]] = None,
                       timeout: int = 60) -> Tuple[bool, Optional[str]]:
    """
    Download a file from a URL to a destination path.
    
    Args:
        url: URL of the file to download
        destination: Path where the file should be saved
        session: aiohttp ClientSession to use for the request
        headers: Optional HTTP headers to include in the request
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        async with session.get(url, headers=headers, timeout=timeout) as response:
            if response.status != 200:
                return False, f"HTTP error {response.status}: {response.reason}"
                
            # Get content length for progress bar if available
            total_size = int(response.headers.get('content-length', 0))
            
            # Open file for writing
            async with aiofiles.open(destination, 'wb') as f:
                downloaded = 0
                
                # Create progress bar if we have the total size
                if total_size > 0:
                    progress = tqdm(
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        desc=os.path.basename(destination)
                    )
                
                # Download the file in chunks
                async for chunk in response.content.iter_chunked(8192):
                    await f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Update progress bar if we have one
                    if total_size > 0:
                        progress.update(len(chunk))
                
                # Close progress bar if we created one
                if total_size > 0:
                    progress.close()
                    
        logger.info(f"Successfully downloaded {url} to {destination}")
        return True, None
    
    except aiohttp.ClientError as e:
        error_msg = f"Network error downloading {url}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    
    except asyncio.TimeoutError:
        error_msg = f"Timeout downloading {url} after {timeout} seconds"
        logger.error(error_msg)
        return False, error_msg
    
    except Exception as e:
        error_msg = f"Error downloading {url}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def get_file_extension_from_url(url: str) -> str:
    """
    Extract the file extension from a URL.
    
    Args:
        url: The URL to parse
        
    Returns:
        The file extension (with dot) or an empty string if none found
    """
    path = url.split('?')[0]  # Remove query parameters
    ext = os.path.splitext(path)[1]
    return ext

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to ensure it's valid on the file system.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        A sanitized filename
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip().strip('.')
    
    # Limit length (some filesystems have limits)
    if len(filename) > 255:
        base, ext = os.path.splitext(filename)
        filename = base[:255-len(ext)] + ext
        
    # Use a default name if the filename is empty after sanitization
    if not filename:
        filename = "wallpaper"
        
    return filename
