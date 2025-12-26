"""AI module for Intuitives DAW

Provides AI-powered music composition and production assistance.
"""

from .assistant import AIAssistant, AIProvider, OpenAIProvider, AIRequest, AIResponse
from .local_models import (
    LocalAI,
    MagentaMelodyRNN,
    ChordGenerator,
    RhythmGenerator,
    TextToAudio,
    AudioToMIDI,
    StemSeparator,
    AudioAnalyzer,
    MIDIClip,
    MIDINote,
    generate_melody,
    generate_chords,
    generate_rhythm,
)

__all__ = [
    # Cloud AI
    "AIAssistant",
    "AIProvider",
    "OpenAIProvider",
    "AIRequest",
    "AIResponse",
    # Local AI
    "LocalAI",
    "MagentaMelodyRNN",
    "ChordGenerator",
    "RhythmGenerator",
    "TextToAudio",
    "AudioToMIDI",
    "StemSeparator",
    "AudioAnalyzer",
    "MIDIClip",
    "MIDINote",
    # Quick functions
    "generate_melody",
    "generate_chords",
    "generate_rhythm",
]
