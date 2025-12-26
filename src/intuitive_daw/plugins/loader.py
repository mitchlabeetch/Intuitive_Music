"""Plugin loader and management system

This module provides a complete plugin system for extending the Intuitives DAW
with custom audio effects, MIDI processors, generators, visualizers, and AI models.
"""
from typing import List, Dict, Optional, Any, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod
from pathlib import Path
import json
import os
import sys
import importlib.util
import logging

logger = logging.getLogger(__name__)


@dataclass
class PluginManifest:
    """Plugin metadata from manifest.json"""
    name: str
    id: str
    version: str
    author: str
    description: str
    plugin_type: str  # audio_effect, midi_processor, generator, visualizer, ai_model
    entry_point: str
    
    # Optional fields
    email: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    requirements: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    min_version: Optional[str] = None
    max_version: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginManifest':
        """Create manifest from dictionary"""
        compatibility = data.get("compatibility", {})
        return cls(
            name=data.get("name", "Unknown Plugin"),
            id=data.get("id", "unknown-plugin"),
            version=data.get("version", "1.0.0"),
            author=data.get("author", "Unknown"),
            description=data.get("description", ""),
            plugin_type=data.get("type", "audio_effect"),
            entry_point=data.get("entry_point", "plugin.Plugin"),
            email=data.get("email"),
            homepage=data.get("homepage"),
            license=data.get("license"),
            parameters=data.get("parameters"),
            requirements=data.get("requirements"),
            tags=data.get("tags"),
            category=data.get("category"),
            min_version=compatibility.get("min_version"),
            max_version=compatibility.get("max_version"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "name": self.name,
            "id": self.id,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "type": self.plugin_type,
            "entry_point": self.entry_point,
        }
        if self.email:
            data["email"] = self.email
        if self.homepage:
            data["homepage"] = self.homepage
        if self.license:
            data["license"] = self.license
        if self.parameters:
            data["parameters"] = self.parameters
        if self.requirements:
            data["requirements"] = self.requirements
        if self.tags:
            data["tags"] = self.tags
        if self.category:
            data["category"] = self.category
        if self.min_version or self.max_version:
            data["compatibility"] = {}
            if self.min_version:
                data["compatibility"]["min_version"] = self.min_version
            if self.max_version:
                data["compatibility"]["max_version"] = self.max_version
        return data


class Plugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self, manifest: PluginManifest):
        self.manifest = manifest
        self.enabled = True
        self._initialized = False
    
    @property
    def name(self) -> str:
        return self.manifest.name
    
    @property
    def id(self) -> str:
        return self.manifest.id
    
    @property
    def version(self) -> str:
        return self.manifest.version
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the plugin"""
        pass
    
    def get_parameter(self, name: str) -> Any:
        """Get parameter value"""
        if self.manifest.parameters and name in self.manifest.parameters:
            return self.manifest.parameters[name].get("value", 
                   self.manifest.parameters[name].get("default"))
        return None
    
    def set_parameter(self, name: str, value: Any) -> bool:
        """Set parameter value"""
        if self.manifest.parameters and name in self.manifest.parameters:
            param = self.manifest.parameters[name]
            # Validate value
            if param.get("type") == "float":
                if "min" in param and value < param["min"]:
                    value = param["min"]
                if "max" in param and value > param["max"]:
                    value = param["max"]
            param["value"] = value
            return True
        return False


class PluginLoader:
    """Discovers and loads plugins from the filesystem"""
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        self.plugin_dirs = plugin_dirs or []
        self._discovered: Dict[str, Path] = {}
        self._loaded: Dict[str, Plugin] = {}
        self._manifests: Dict[str, PluginManifest] = {}
        
        # Add default plugin directories
        self._add_default_dirs()
    
    def _add_default_dirs(self) -> None:
        """Add default plugin directories"""
        # User plugins
        user_plugins = Path.home() / ".intuitive_daw" / "plugins"
        if user_plugins.exists():
            self.plugin_dirs.append(str(user_plugins))
        
        # App plugins
        app_plugins = Path(__file__).parent.parent / "plugins"
        if app_plugins.exists():
            self.plugin_dirs.append(str(app_plugins))
    
    def add_plugin_dir(self, path: str) -> None:
        """Add a plugin directory"""
        if path not in self.plugin_dirs:
            self.plugin_dirs.append(path)
    
    def discover(self) -> Dict[str, PluginManifest]:
        """
        Discover all available plugins.
        
        Returns:
            Dictionary of plugin ID to manifest
        """
        self._discovered.clear()
        self._manifests.clear()
        
        for dir_path in self.plugin_dirs:
            if not os.path.exists(dir_path):
                continue
            
            for item in os.listdir(dir_path):
                plugin_path = Path(dir_path) / item
                
                # Check if it's a valid plugin directory
                if not plugin_path.is_dir():
                    continue
                
                manifest_path = plugin_path / "manifest.json"
                if not manifest_path.exists():
                    continue
                
                try:
                    with open(manifest_path, 'r') as f:
                        manifest_data = json.load(f)
                    
                    manifest = PluginManifest.from_dict(manifest_data)
                    
                    # Check for duplicate IDs
                    if manifest.id in self._discovered:
                        logger.warning(
                            f"Duplicate plugin ID: {manifest.id}, "
                            f"ignoring {plugin_path}"
                        )
                        continue
                    
                    self._discovered[manifest.id] = plugin_path
                    self._manifests[manifest.id] = manifest
                    
                    logger.info(f"Discovered plugin: {manifest.name} v{manifest.version}")
                    
                except Exception as e:
                    logger.error(f"Error loading manifest from {plugin_path}: {e}")
        
        return self._manifests.copy()
    
    def load(self, plugin_id: str) -> Optional[Plugin]:
        """
        Load a plugin by ID.
        
        Args:
            plugin_id: Plugin identifier
        
        Returns:
            Loaded plugin instance or None
        """
        if plugin_id in self._loaded:
            return self._loaded[plugin_id]
        
        if plugin_id not in self._discovered:
            logger.error(f"Plugin not found: {plugin_id}")
            return None
        
        plugin_path = self._discovered[plugin_id]
        manifest = self._manifests[plugin_id]
        
        try:
            # Install requirements if any
            if manifest.requirements:
                self._install_requirements(manifest.requirements)
            
            # Parse entry point
            module_name, class_name = manifest.entry_point.rsplit('.', 1)
            
            # Load the module
            module_path = plugin_path / f"{module_name}.py"
            if not module_path.exists():
                # Try as package
                module_path = plugin_path / module_name / "__init__.py"
            
            if not module_path.exists():
                logger.error(f"Entry point module not found: {module_path}")
                return None
            
            # Import the module
            spec = importlib.util.spec_from_file_location(
                f"plugins.{manifest.id}.{module_name}",
                module_path
            )
            module = importlib.util.module_from_spec(spec)
            
            # Add plugin path to sys.path temporarily
            sys.path.insert(0, str(plugin_path))
            try:
                spec.loader.exec_module(module)
            finally:
                sys.path.pop(0)
            
            # Get the class
            plugin_class = getattr(module, class_name)
            
            # Check if class has required methods
            if not hasattr(plugin_class, 'initialize') or not hasattr(plugin_class, 'shutdown'):
                # Wrap in a simple plugin class
                plugin = self._wrap_plugin(plugin_class, manifest)
            else:
                plugin = plugin_class(manifest)
            
            # Initialize
            if plugin.initialize():
                self._loaded[plugin_id] = plugin
                logger.info(f"Loaded plugin: {manifest.name}")
                return plugin
            else:
                logger.error(f"Plugin initialization failed: {manifest.name}")
                return None
            
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_id}: {e}")
            return None
    
    def _wrap_plugin(self, plugin_class: Type, manifest: PluginManifest) -> Plugin:
        """Wrap a simple class in a Plugin wrapper"""
        
        class PluginWrapper(Plugin):
            def __init__(self, manifest: PluginManifest, inner_class: Type):
                super().__init__(manifest)
                self._inner_class = inner_class
                self._instance = None
            
            def initialize(self) -> bool:
                try:
                    self._instance = self._inner_class()
                    self._initialized = True
                    return True
                except Exception as e:
                    logger.error(f"Failed to create plugin instance: {e}")
                    return False
            
            def shutdown(self) -> None:
                if self._instance and hasattr(self._instance, 'reset'):
                    self._instance.reset()
                self._instance = None
                self._initialized = False
            
            def get_instance(self):
                return self._instance
        
        return PluginWrapper(manifest, plugin_class)
    
    def _install_requirements(self, requirements: List[str]) -> bool:
        """Install plugin requirements"""
        try:
            import subprocess
            for req in requirements:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", req],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    logger.warning(f"Failed to install {req}: {result.stderr}")
            return True
        except Exception as e:
            logger.error(f"Error installing requirements: {e}")
            return False
    
    def unload(self, plugin_id: str) -> bool:
        """Unload a plugin"""
        if plugin_id not in self._loaded:
            return False
        
        try:
            plugin = self._loaded[plugin_id]
            plugin.shutdown()
            del self._loaded[plugin_id]
            logger.info(f"Unloaded plugin: {plugin.name}")
            return True
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_id}: {e}")
            return False
    
    def unload_all(self) -> None:
        """Unload all plugins"""
        for plugin_id in list(self._loaded.keys()):
            self.unload(plugin_id)
    
    def get_loaded(self) -> Dict[str, Plugin]:
        """Get all loaded plugins"""
        return self._loaded.copy()
    
    def get_available(self) -> Dict[str, PluginManifest]:
        """Get all available plugins"""
        return self._manifests.copy()
    
    def get_by_type(self, plugin_type: str) -> Dict[str, PluginManifest]:
        """Get plugins by type"""
        return {
            pid: manifest 
            for pid, manifest in self._manifests.items()
            if manifest.plugin_type == plugin_type
        }


class PluginRegistry:
    """
    Central registry for all plugins.
    Singleton pattern for global access.
    """
    
    _instance: Optional['PluginRegistry'] = None
    
    def __new__(cls) -> 'PluginRegistry':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loader = PluginLoader()
            cls._instance._initialized = False
        return cls._instance
    
    def initialize(self) -> None:
        """Initialize the registry"""
        if self._initialized:
            return
        
        self._loader.discover()
        self._initialized = True
        logger.info(f"Plugin registry initialized with {len(self._loader.get_available())} plugins")
    
    def get_loader(self) -> PluginLoader:
        """Get the plugin loader"""
        return self._loader
    
    def get_audio_effects(self) -> Dict[str, PluginManifest]:
        """Get available audio effect plugins"""
        return self._loader.get_by_type("audio_effect")
    
    def get_midi_processors(self) -> Dict[str, PluginManifest]:
        """Get available MIDI processor plugins"""
        return self._loader.get_by_type("midi_processor")
    
    def get_generators(self) -> Dict[str, PluginManifest]:
        """Get available generator plugins"""
        return self._loader.get_by_type("generator")
    
    def get_visualizers(self) -> Dict[str, PluginManifest]:
        """Get available visualizer plugins"""
        return self._loader.get_by_type("visualizer")
    
    def get_ai_models(self) -> Dict[str, PluginManifest]:
        """Get available AI model plugins"""
        return self._loader.get_by_type("ai_model")
    
    def load_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Load a plugin by ID"""
        return self._loader.load(plugin_id)
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin"""
        return self._loader.unload(plugin_id)
    
    def shutdown(self) -> None:
        """Shutdown the registry"""
        self._loader.unload_all()
        self._initialized = False


# Template generators for creating new plugins
def create_audio_effect_template(
    name: str,
    plugin_id: str,
    author: str,
    output_dir: str
) -> Path:
    """
    Create a new audio effect plugin template.
    
    Args:
        name: Plugin name
        plugin_id: Plugin ID (lowercase with dashes)
        author: Author name
        output_dir: Directory to create plugin in
    
    Returns:
        Path to created plugin directory
    """
    plugin_dir = Path(output_dir) / plugin_id.replace("-", "_")
    plugin_dir.mkdir(parents=True, exist_ok=True)
    
    # Create manifest
    manifest = {
        "name": name,
        "id": plugin_id,
        "version": "1.0.0",
        "author": author,
        "description": f"{name} audio effect plugin",
        "type": "audio_effect",
        "entry_point": "plugin.{0}".format(name.replace(" ", "")),
        "parameters": {
            "mix": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.5,
                "label": "Mix"
            }
        },
        "tags": ["effect"]
    }
    
    with open(plugin_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Create plugin code
    class_name = name.replace(" ", "")
    plugin_code = f'''"""
{name} - Audio Effect Plugin for Intuitives DAW
"""
import numpy as np


class {class_name}:
    """
    {name} audio effect.
    
    Inherits from AudioEffect for integration with the DAW.
    """
    
    def __init__(self, mix: float = 0.5):
        self.name = "{name}"
        self.mix = mix
        self.sample_rate = 48000
        self.is_enabled = True
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Process audio through the effect.
        
        Args:
            audio: Input audio (samples, channels)
        
        Returns:
            Processed audio (same shape)
        """
        if not self.is_enabled:
            return audio
        
        # Implement your effect processing here
        processed = audio.copy()
        
        # Example: Simple gain change
        processed = processed * 1.0
        
        # Mix wet/dry
        output = audio * (1 - self.mix) + processed * self.mix
        
        return output
    
    def set_parameter(self, name: str, value: float) -> None:
        """Update parameter value"""
        if name == "mix":
            self.mix = max(0.0, min(1.0, value))
    
    def reset(self) -> None:
        """Reset internal state"""
        pass
'''
    
    with open(plugin_dir / "plugin.py", 'w') as f:
        f.write(plugin_code)
    
    # Create __init__.py
    with open(plugin_dir / "__init__.py", 'w') as f:
        f.write(f'from .plugin import {class_name}\n\n__all__ = ["{class_name}"]\n')
    
    # Create README
    readme = f'''# {name}

A custom audio effect plugin for Intuitives DAW.

## Installation

Copy this folder to your plugins directory:
- macOS/Linux: `~/.intuitive_daw/plugins/`
- Windows: `%USERPROFILE%\\.intuitive_daw\\plugins\\`

## Usage

```python
from intuitive_daw.plugins import PluginRegistry

registry = PluginRegistry()
registry.initialize()

plugin = registry.load_plugin("{plugin_id}")
```

## Parameters

- **mix** (0.0-1.0): Wet/dry mix

## Author

{author}
'''
    
    with open(plugin_dir / "README.md", 'w') as f:
        f.write(readme)
    
    logger.info(f"Created audio effect template at {plugin_dir}")
    return plugin_dir


def create_generator_template(
    name: str,
    plugin_id: str,
    author: str,
    output_dir: str
) -> Path:
    """Create a new generator plugin template"""
    plugin_dir = Path(output_dir) / plugin_id.replace("-", "_")
    plugin_dir.mkdir(parents=True, exist_ok=True)
    
    # Create manifest
    manifest = {
        "name": name,
        "id": plugin_id,
        "version": "1.0.0",
        "author": author,
        "description": f"{name} generator plugin",
        "type": "generator",
        "entry_point": "plugin.{0}".format(name.replace(" ", "")),
        "parameters": {
            "length": {
                "type": "int",
                "min": 1,
                "max": 64,
                "default": 16,
                "label": "Length"
            }
        },
        "tags": ["generator", "midi"]
    }
    
    with open(plugin_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    class_name = name.replace(" ", "")
    plugin_code = f'''"""
{name} - Generator Plugin for Intuitives DAW
"""
from dataclasses import dataclass
from typing import List
import numpy as np


@dataclass
class Note:
    """Simple MIDI note"""
    pitch: int
    velocity: int
    start: float
    duration: float


class {class_name}:
    """
    {name} generator.
    
    Generates MIDI patterns algorithmically.
    """
    
    def __init__(self, length: int = 16):
        self.name = "{name}"
        self.length = length
    
    def generate(self, **kwargs) -> List[Note]:
        """
        Generate MIDI notes.
        
        Args:
            **kwargs: Generator-specific parameters
        
        Returns:
            List of generated notes
        """
        notes = []
        step_duration = 0.25  # 16th notes
        
        for i in range(self.length):
            # Generate note (customize this logic)
            if np.random.random() < 0.5:  # 50% chance
                notes.append(Note(
                    pitch=60 + np.random.randint(0, 12),  # C4-B4
                    velocity=80 + np.random.randint(-20, 20),
                    start=i * step_duration,
                    duration=step_duration * 0.9
                ))
        
        return notes
'''
    
    with open(plugin_dir / "plugin.py", 'w') as f:
        f.write(plugin_code)
    
    with open(plugin_dir / "__init__.py", 'w') as f:
        f.write(f'from .plugin import {class_name}\n\n__all__ = ["{class_name}"]\n')
    
    logger.info(f"Created generator template at {plugin_dir}")
    return plugin_dir
