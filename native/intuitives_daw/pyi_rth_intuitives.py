# PyInstaller runtime hook for path configuration
import os
import sys

# Fix paths for macOS PyInstaller bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Set environment variable to help modules find resources
    os.environ['INTUITIVES_BUNDLE_DIR'] = os.path.abspath(
        os.path.join(sys._MEIPASS, '..', 'Resources')
    )
