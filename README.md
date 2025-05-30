# Wallpaper Scraper

A simple tool to download wallpapers from various websites while respecting their resource usage.

## Features

- Fast, efficient downloading
- Multiple wallpaper sources (Unsplash, Wallhaven, Pixabay)
- Search by keywords, categories, and more
- Customizable download settings
- Live download progress bars

## Quick Start

1. **Clone and install**:
   ```bash
   git clone https://github.com/yourusername/wallpaper-scraper.git
   cd wallpaper-scraper
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Download wallpapers**:
   ```bash
   # Basic usage
   python main.py --source unsplash --query "nature" --api-key YOUR_API_KEY
   
   # Or use the simple download script
   ./download-wallpapers.sh --nature --source unsplash
   ```

## API Keys

You'll need API keys for these services:
- [Unsplash Developers](https://unsplash.com/developers)
- [Wallhaven](https://wallhaven.cc/settings/account) (optional)
- [Pixabay API](https://pixabay.com/api/docs/)

Set them as environment variables:
```bash
export UNSPLASH_API_KEY="your_key"
export WALLHAVEN_API_KEY="your_key"
export PIXABAY_API_KEY="your_key"
```

## Usage

### Basic Commands

```bash
# Download nature wallpapers
python main.py --source unsplash --query "nature"

# Download mountain wallpapers with size limit
python main.py --source wallhaven --query "mountains" --limit 20

# Download from multiple sources
./download-wallpapers.sh --nature --source all
```

### Common Options

- `--source`: Choose wallpaper provider (unsplash, wallhaven, pixabay)
- `--query`: Search terms
- `--limit`: Maximum number of wallpapers to download
- `--output`: Custom download folder

Progress bars will automatically show download status for each file when downloading.

See `python main.py --help` for all available options.

## Troubleshooting

If you run into issues:
- Check that your API keys are correct
- Try a different search term
- Use the `--verbose` flag for more detailed information
