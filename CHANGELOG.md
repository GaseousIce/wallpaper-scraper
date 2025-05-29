# Changelog

All notable changes to the Wallpaper Scraper project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Pre-commit hook to prevent accidental commit of API keys
- Better documentation for security best practices
- Environment variables example file (.env.example)
- Contribution guidelines in README
- This CHANGELOG file

### Fixed
- Removed standard library modules from requirements.txt
- Added proper timeout handling to all scrapers
- Updated documentation for clarity

## [1.0.0] - 2025-05-27

### Added
- Initial release
- Support for Unsplash, Wallhaven, and Pixabay scrapers
- Asynchronous downloading with rate limiting
- Command line interface
- Configuration system
- Wallpaper setting utilities for Windows, macOS, and Linux
- Example scripts
- Basic test suite
