#!/usr/bin/env python3
"""
INTUITIVES DAW - Entry Point

"Does this sound cool?" - The only rule.

A rule-free, experimental digital audio workstation that prioritizes
intuition, randomness, and AI-assisted discovery over traditional
music theory constraints.
"""

import os
import sys

# Ensure proper path setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from sglib.brand import (
    APP_NAME,
    APP_TAGLINE,
    VERSION_STRING,
    VERSION_NAME,
    LOGO_ASCII,
    SPLASH_MESSAGES,
)


def print_banner():
    """Print the Intuitives startup banner"""
    print()
    print("=" * 66)
    print(f"  {APP_NAME} v{VERSION_STRING} ({VERSION_NAME})")
    print(f"  {APP_TAGLINE}")
    print("=" * 66)
    print()
    print('  "Does this sound cool?" - The only rule.')
    print()


def check_dependencies():
    """Check that all required dependencies are available"""
    missing = []
    
    try:
        import PyQt5
    except ImportError:
        try:
            import PyQt6
        except ImportError:
            missing.append("PyQt5 or PyQt6")
    
    if missing:
        print(f"ERROR: Missing dependencies: {', '.join(missing)}")
        print("Please install with: pip install PyQt5")
        sys.exit(1)


def main():
    """Main entry point for Intuitives DAW"""
    print_banner()
    check_dependencies()
    
    # Import after dependency check
    from sgui._main import main as gui_main
    
    print("Starting Intuitives DAW...")
    print()
    
    # Run the GUI
    gui_main()


if __name__ == "__main__":
    main()
