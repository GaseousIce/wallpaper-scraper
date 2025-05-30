@echo off
:: Wallpaper Scraper - Windows batch script for easy downloading
:: Usage: download-wallpapers.bat [options]

setlocal enabledelayedexpansion

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Default values
set SOURCE=unsplash
set QUERY=nature
set LIMIT=10
set ANIME_FLAG=

:: Process command-line arguments
:parse_args
if "%~1"=="" goto execute
if "%~1"=="--source" (
    set SOURCE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--query" (
    set QUERY=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--limit" (
    set LIMIT=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--nature" (
    set QUERY=nature
    shift
    goto parse_args
)
if "%~1"=="--abstract" (
    set QUERY=abstract
    shift
    goto parse_args
)
if "%~1"=="--city" (
    set QUERY=city
    shift
    goto parse_args
)
if "%~1"=="--mountains" (
    set QUERY=mountains
    shift
    goto parse_args
)
if "%~1"=="--space" (
    set QUERY=space
    shift
    goto parse_args
)
if "%~1"=="--anime" (
    set QUERY=anime
    set ANIME_FLAG=--anime
    shift
    goto parse_args
)
if "%~1"=="--help" (
    echo Usage: download-wallpapers.bat [options]
    echo Options:
    echo   --source SOURCE    Specify the wallpaper source (unsplash, wallhaven, pixabay)
    echo   --query QUERY      Search query for wallpapers
    echo   --limit LIMIT      Maximum number of wallpapers to download
    echo   --nature           Download nature wallpapers (shortcut for --query nature)
    echo   --abstract         Download abstract wallpapers (shortcut for --query abstract)
    echo   --city             Download city wallpapers (shortcut for --query city)
    echo   --mountains        Download mountain wallpapers (shortcut for --query mountains)
    echo   --space            Download space wallpapers (shortcut for --query space)
    echo   --anime            Download anime wallpapers (works best with Wallhaven)
    echo   --help             Show this help message
    exit /b 0
)

shift
goto parse_args

:execute
:: Execute the wallpaper scraper
python main.py --source %SOURCE% --query "%QUERY%" --limit %LIMIT% %ANIME_FLAG%

:: Deactivate the virtual environment
call venv\Scripts\deactivate.bat

echo Wallpaper download complete!
