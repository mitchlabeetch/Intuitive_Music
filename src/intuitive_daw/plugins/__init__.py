"""Plugin system for Intuitives DAW

Provides plugin discovery, loading, and management.
"""

from .loader import (
    Plugin,
    PluginManifest,
    PluginLoader,
    PluginRegistry,
    create_audio_effect_template,
    create_generator_template,
)

__all__ = [
    "Plugin",
    "PluginManifest",
    "PluginLoader",
    "PluginRegistry",
    "create_audio_effect_template",
    "create_generator_template",
]
