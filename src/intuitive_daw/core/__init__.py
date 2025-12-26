"""Core module for Intuitives DAW

Provides the fundamental building blocks for the DAW.
"""

from .engine import AudioEngine
from .project import Project
from .track import Track
from .integrations import (
    AudioAnalyzer,
    AnalysisResult,
    PatternBuilder,
    ScaleHelper,
    analyze_audio,
    detect_tempo,
    detect_key,
)

__all__ = [
    # Core components
    "AudioEngine",
    "Project",
    "Track",
    # Integrations
    "AudioAnalyzer",
    "AnalysisResult",
    "PatternBuilder",
    "ScaleHelper",
    # Quick functions
    "analyze_audio",
    "detect_tempo",
    "detect_key",
]
