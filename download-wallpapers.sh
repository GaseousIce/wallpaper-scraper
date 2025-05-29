#!/bin/bash
# Quick wallpaper download script with various presets

# Display help message
function show_help {
    echo "Wallpaper Downloader Script"
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --nature     Download nature wallpapers"
    echo "  --space      Download space wallpapers"
    echo "  --city       Download city wallpapers"
    echo "  --abstract   Download abstract wallpapers"
    echo "  --animals    Download animal wallpapers"
    echo "  --landscape  Download landscape wallpapers"
    echo "  --custom QUERY   Download wallpapers with custom query"
    echo "  --source SOURCE  Specify source (unsplash, wallhaven, pixabay, all)"
    echo "  --limit N        Limit to N wallpapers per source"
    echo "  --help           Display this help message"
    echo ""
    echo "Example: $0 --nature --source all --limit 10"
    exit 0
}

# Set defaults
QUERY=""
SOURCE="unsplash"
LIMIT=5
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --nature)
            QUERY="nature mountains forest"
            shift
            ;;
        --space)
            QUERY="space galaxy stars universe"
            shift
            ;;
        --city)
            QUERY="city skyline urban night"
            shift
            ;;
        --abstract)
            QUERY="abstract pattern geometric"
            shift
            ;;
        --animals)
            QUERY="animals wildlife"
            shift
            ;;
        --landscape)
            QUERY="landscape scenery"
            shift
            ;;
        --custom)
            QUERY="$2"
            shift 2
            ;;
        --source)
            SOURCE="$2"
            shift 2
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for available options"
            exit 1
            ;;
    esac
done

# Check if query is provided
if [ -z "$QUERY" ]; then
    echo "Error: No wallpaper type specified."
    echo "Use --help for available options"
    exit 1
fi

# Activate virtual environment if it exists
if [ -f "$SCRIPT_DIR/bin/activate" ]; then
    source "$SCRIPT_DIR/bin/activate"
fi

# Print summary
echo "Downloading wallpapers with query: $QUERY"
echo "Source: $SOURCE"
echo "Limit: $LIMIT per source"

# Run the appropriate command
if [ "$SOURCE" = "all" ]; then
    echo "Downloading from all sources..."
    python "$SCRIPT_DIR/examples/multi_source_downloader.py" --query "$QUERY" --limit "$LIMIT"
else
    echo "Downloading from $SOURCE..."
    python "$SCRIPT_DIR/main.py" --source "$SOURCE" --query "$QUERY" --limit "$LIMIT"
fi

echo "Download complete!"
