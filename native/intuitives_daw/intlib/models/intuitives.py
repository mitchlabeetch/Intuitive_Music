"""
Intuitives DAW - Core Models

Core model re-exports and Intuitives-specific additions.
Following the "experiment-first" philosophy: Does this sound cool?
"""

import os
from typing import List, Dict, Any, Optional

# Re-export SgProject from core module (required for main.py)
from intlib.models.core.project import SgProject

# Re-export from core models (avoid circular imports)
# These will be imported after this module is loaded
SgAudioItem = None
MIDINote = None
MIDIControl = None
MIDIPitchbend = None

def _lazy_import():
    """Lazy import to avoid circular dependencies"""
    global SgAudioItem, MIDINote, MIDIControl, MIDIPitchbend
    if SgAudioItem is None:
        from intlib.models.core.audio_item import SgAudioItem as _SgAudioItem
        from intlib.models.core.midi_events import (
            MIDINote as _MIDINote,
            MIDIControl as _MIDIControl,
            MIDIPitchbend as _MIDIPitchbend,
        )
        SgAudioItem = _SgAudioItem
        MIDINote = _MIDINote
        MIDIControl = _MIDIControl
        MIDIPitchbend = _MIDIPitchbend

# Aliases for backwards compatibility
def note(*args, **kwargs):
    _lazy_import()
    return MIDINote(*args, **kwargs)

def cc(*args, **kwargs):
    _lazy_import()
    return MIDIControl(*args, **kwargs)

def pitchbend(*args, **kwargs):
    _lazy_import()
    return MIDIPitchbend(*args, **kwargs)

# Plugin directories
BUILTIN_PLUGINS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "plugins"
)


USER_PLUGINS_DIR = os.path.expanduser("~/.intuitives/plugins")


def folder_plugins(folder: str = None) -> List[Dict[str, Any]]:
    """
    Discover plugins in the specified folder.
    """
    plugins = []
    
    search_dirs = []
    if folder:
        search_dirs.append(folder)
    else:
        search_dirs.append(BUILTIN_PLUGINS_DIR)
        search_dirs.append(USER_PLUGINS_DIR)
    
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
            
        try:
            for item in os.listdir(search_dir):
                item_path = os.path.join(search_dir, item)
                
                manifest = os.path.join(item_path, "manifest.json")
                if os.path.isdir(item_path) and os.path.exists(manifest):
                    plugins.append({
                        'name': item,
                        'path': item_path,
                        'type': 'effect',
                    })
                elif item.endswith('.so') or item.endswith('.dylib'):
                    plugins.append({
                        'name': os.path.splitext(item)[0],
                        'path': item_path,
                        'type': 'native',
                    })
        except Exception:
            pass
    
    return plugins


def get_plugin_info(plugin_path: str) -> Dict[str, Any]:
    """Get detailed plugin information"""
    import json
    
    manifest_path = os.path.join(plugin_path, "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            return json.load(f)
    
    return {
        'name': os.path.basename(plugin_path),
        'version': '1.0.0',
        'author': 'Unknown',
        'type': 'effect',
    }


class IntuitivesProject:
    """Wrapper for project with Intuitives defaults"""
    
    def __init__(self, name: str = "Untitled"):
        self.name = name
        self.bpm = 120.0
        self.tracks = []
        self.patterns = []
        self.generators = []
        
    def add_track(self, name: str = "Track"):
        track_id = len(self.tracks)
        self.tracks.append({
            'id': track_id,
            'name': name,
            'volume': 1.0,
            'pan': 0.0,
            'mute': False,
            'solo': False,
        })
        return track_id


class GeneratorPreset:
    """Preset for AI generators"""
    
    def __init__(
        self,
        name: str,
        generator_type: str = 'markov',
        params: Optional[Dict] = None
    ):
        self.name = name
        self.generator_type = generator_type
        self.params = params or {
            'temperature': 0.7,
            'scale': 'pentatonic',
            'root': 60,
            'num_bars': 4,
        }
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'type': self.generator_type,
            'params': self.params,
        }
    
    @staticmethod
    def from_dict(d: Dict) -> 'GeneratorPreset':
        return GeneratorPreset(
            name=d.get('name', 'Preset'),
            generator_type=d.get('type', 'markov'),
            params=d.get('params', {}),
        )
