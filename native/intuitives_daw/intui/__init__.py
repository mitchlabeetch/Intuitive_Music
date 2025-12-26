"""
INTUITIVES DAW - User Interface (intui)

This is the new module namespace for Intuitives DAW GUI components.
It re-exports from sgui for backward compatibility during migration.

New code should import from intui:
    from intui.widgets import GeneratorPanel
    from intui.sgqt import *

Legacy code using sgui will continue to work.
"""

# Re-export everything from sgui
from sgui import *

# Explicit re-exports for IDE support
from sgui import shared
from sgui.sgqt import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    Signal,
    Slot,
    QtCore,
)

# Version info
__version__ = "0.6.0-beta"
__all__ = [
    "shared",
    "widgets",
]
