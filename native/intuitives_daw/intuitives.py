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

from intlib.brand import (
    APP_NAME,
    APP_TAGLINE,
    VERSION_STRING,
    VERSION_NAME,
    LOGO_ASCII,
    SPLASH_MESSAGES,
)


def print_banner():
    """
    PURPOSE: Displays the Intuitives DAW startup banner and application information to the console.
    ACTION: Prints the ASCII logo, application name, version, tagline, and the core philosophy rule.
    MECHANISM: Uses standard print statements to output formatted text and constants imported from intlib.brand.
    """
    print()
    print("=" * 66)
    print(f"  {APP_NAME} v{VERSION_STRING} ({VERSION_NAME})")
    print(f"  {APP_TAGLINE}")
    print("=" * 66)
    print()
    print('  "Does this sound cool?" - The only rule.')
    print()


def check_dependencies():
    """
    PURPOSE: Validates that necessary runtime dependencies (like PyQt) are installed before launching the application.
    ACTION: Attempts to import PyQt5 or PyQt6. If both fail, it collects the missing dependency name and exits the program with an error message.
    MECHANISM: Uses nested try-except blocks to test for ImportError. If dependencies are missing, it prints a user-friendly installation command and calls sys.exit(1).
    """
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
    """
    PURPOSE: Serves as the primary entry point for launching the Intuitives DAW application.
    ACTION: Initializes the console output, verifies dependencies, processes command-line arguments, and hands over control to the GUI main loop.
    MECHANISM: 
        1. Calls print_banner() and check_dependencies().
        2. Dynamically imports the GUI main function from intui._main.
        3. Parses sys.argv to identify any project files passed as arguments.
        4. Invokes gui_main(args) to start the application's event loop.
    """
    print_banner()
    check_dependencies()
    
    # Import after dependency check
    from intui._main import main as gui_main
    
    print("Starting Intuitives DAW...")
    print()
    
    # Create args object
    class Args:
        def __init__(self):
            self.project_file = None
    
    args = Args()
    
    # Check for project file argument
    if len(sys.argv) > 1:
        args.project_file = sys.argv[1]
    
    # Run the GUI
    gui_main(args)


if __name__ == "__main__":
    main()
