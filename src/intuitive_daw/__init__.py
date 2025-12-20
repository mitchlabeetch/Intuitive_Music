"""
Intuitive Music DAW - An AI-Assisted Digital Audio Workstation
"""

__version__ = "0.1.0"
__author__ = "Intuitive Music Team"

from .core.engine import AudioEngine
from .core.project import Project
from .core.track import Track

__all__ = ["AudioEngine", "Project", "Track"]
