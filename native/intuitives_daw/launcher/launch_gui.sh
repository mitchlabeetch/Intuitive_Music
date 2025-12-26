#!/bin/bash

# ============================================================
# INTUITIVES DAW v0.6 BETA - App Launcher
# ============================================================
# This script is the main entry point for the .app bundle.
# It launches the full Python GUI interface.
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOURCES_DIR="$(dirname "$SCRIPT_DIR")/Resources"
APP_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Find the DAW source directory (where Python files are)
DAW_SRC_DIR="$(cd "$APP_DIR/../.." 2>/dev/null && pwd)"

if [ ! -f "$DAW_SRC_DIR/intuitives.py" ]; then
    # Try alternate location
    DAW_SRC_DIR="$(cd "$APP_DIR/.." 2>/dev/null && pwd)"
fi

if [ ! -f "$DAW_SRC_DIR/intuitives.py" ]; then
    # Development mode - look in standard location
    DAW_SRC_DIR="/Users/utilisateur/Desktop/INTUITIVE_MUSIC/native/intuitives_daw"
fi

# Set up environment
export PYTHONPATH="$DAW_SRC_DIR:$PYTHONPATH"
export INTUITIVES_APP_MODE=1

# Log startup
LOG_FILE="$HOME/.intuitives/launch.log"
mkdir -p "$HOME/.intuitives"
echo "$(date): Launching Intuitives DAW from $DAW_SRC_DIR" >> "$LOG_FILE"

# Find Python
PYTHON=""
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
fi

if [ -z "$PYTHON" ]; then
    osascript -e 'display alert "Python Required" message "Please install Python 3 to run Intuitives DAW." as critical'
    exit 1
fi

# Check if intuitives.py exists
if [ -f "$DAW_SRC_DIR/intuitives.py" ]; then
    cd "$DAW_SRC_DIR"
    exec "$PYTHON" intuitives.py "$@"
else
    # Fallback: try to run the sgui main module
    if [ -f "$DAW_SRC_DIR/sgui/main.py" ]; then
        cd "$DAW_SRC_DIR"
        exec "$PYTHON" -m sgui.main "$@"
    else
        osascript -e 'display alert "Intuitives DAW" message "Could not find DAW files. Please run from the source directory." as critical'
        exit 1
    fi
fi
