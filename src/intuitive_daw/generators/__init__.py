"""Generators module for Intuitives DAW

Procedural and generative music algorithms including:
- L-Systems for fractal melodies and rhythms
- Image-to-Sound conversion with chromasynesthesia
- Cellular automata rhythm generation
- Markov chain melody generation
- Genetic algorithm composition
"""

from .lsystem import (
    LSystemGenerator,
    LSystemConfig,
    LSystemRule,
    LSystemOutput,
    LSystemState,
    LSystemVisualizer,
    generate_lsystem,
    lsystem_to_midi,
    lsystem_to_svg,
)

from .image_to_sound import (
    ImageToSound,
    ImageToSoundConfig,
    ChromaSynesthesia,
    SpectralSonifier,
    image_to_midi,
    image_to_audio,
    color_to_note,
    color_to_freq,
)

__all__ = [
    # L-System
    "LSystemGenerator",
    "LSystemConfig",
    "LSystemRule",
    "LSystemOutput",
    "LSystemState",
    "LSystemVisualizer",
    "generate_lsystem",
    "lsystem_to_midi",
    "lsystem_to_svg",
    # Image-to-Sound
    "ImageToSound",
    "ImageToSoundConfig",
    "ChromaSynesthesia",
    "SpectralSonifier",
    "image_to_midi",
    "image_to_audio",
    "color_to_note",
    "color_to_freq",
]
