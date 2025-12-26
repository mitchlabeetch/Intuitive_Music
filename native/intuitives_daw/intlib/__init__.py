"""
INTUITIVES DAW - Core Library (intlib)

This is the new module namespace for Intuitives DAW core functionality.
It re-exports from sglib for backward compatibility during migration.

New code should import from intlib:
    from intlib.brand import APP_NAME
    from intlib.log import LOG

Legacy code using sglib will continue to work.
"""

# Re-export everything from sglib
from sglib import *

# Explicit re-exports for IDE support
from sglib.brand import (
    APP_NAME,
    APP_TAGLINE,
    VERSION_STRING,
    VERSION_NAME,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_TERTIARY,
    CHROMA_COLORS,
    FEATURES,
    SHORTCUTS,
)
from sglib.constants import (
    MAJOR_VERSION,
    HOME,
    PROJECT,
    READY,
)
from sglib.log import LOG

# Version info
__version__ = "0.6.0-beta"
__all__ = [
    "LOG",
    "APP_NAME",
    "APP_TAGLINE",
    "VERSION_STRING",
    "CHROMA_COLORS",
]
