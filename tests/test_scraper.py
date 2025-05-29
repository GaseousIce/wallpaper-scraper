"""
Tests for the wallpaper scraper.
"""
import unittest
import asyncio
from pathlib import Path
import tempfile
import os

from src.scrapers.example_scraper import ExampleScraper
from src.utils.config import Config
from src.utils.download import sanitize_filename, get_file_extension_from_url


class TestConfig(unittest.TestCase):
    """Tests for the Config class."""
    
    def test_default_config(self):
        """Test that default configuration is loaded."""
        config = Config()
        self.assertIsNotNone(config.get("download_directory"))
        self.assertIsNotNone(config.get("rate_limit"))
        self.assertIsNotNone(config.get("max_concurrent_downloads"))
    
    def test_get_download_dir(self):
        """Test that get_download_dir returns a Path object."""
        config = Config()
        download_dir = config.get_download_dir()
        self.assertIsInstance(download_dir, Path)


class TestUtils(unittest.TestCase):
    """Tests for utility functions."""
    
    def test_sanitize_filename(self):
        """Test that sanitize_filename removes invalid characters."""
        filename = 'test<>:"/\\|?*file.jpg'
        sanitized = sanitize_filename(filename)
        self.assertEqual(sanitized, 'test________file.jpg')
    
    def test_get_file_extension_from_url(self):
        """Test that get_file_extension_from_url extracts the correct extension."""
        url = 'https://example.com/wallpaper.jpg?size=large'
        ext = get_file_extension_from_url(url)
        self.assertEqual(ext, '.jpg')


class TestExampleScraper(unittest.IsolatedAsyncioTestCase):
    """Tests for the ExampleScraper class."""
    
    async def asyncSetUp(self):
        """Set up the test environment."""
        # Create a temporary directory for downloads
        self.temp_dir = tempfile.TemporaryDirectory()
        self.download_dir = Path(self.temp_dir.name)
        
        # Create the scraper
        self.scraper = ExampleScraper(
            download_directory=self.download_dir,
            rate_limit=0.1,  # Use a small rate limit for testing
            max_concurrent_downloads=2
        )
    
    async def asyncTearDown(self):
        """Clean up the test environment."""
        self.temp_dir.cleanup()
    
    async def test_respect_rate_limit(self):
        """Test that _respect_rate_limit enforces the rate limit."""
        # Make note of the current time
        start_time = asyncio.get_event_loop().time()
        
        # Call _respect_rate_limit twice
        await self.scraper._respect_rate_limit()
        await self.scraper._respect_rate_limit()
        
        # Check that at least rate_limit seconds have passed
        elapsed = asyncio.get_event_loop().time() - start_time
        self.assertGreaterEqual(elapsed, self.scraper.rate_limit)


if __name__ == '__main__':
    unittest.main()
