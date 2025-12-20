# Plugin System Example

This directory contains example plugins for the Intuitive Music DAW.

## Creating a Custom Plugin

Plugins can extend the DAW with custom audio effects, MIDI processors, or virtual instruments.

### Audio Effect Plugin Example

```python
from intuitive_daw.audio.processor import AudioEffect
import numpy as np

class MyCustomEffect(AudioEffect):
    """Custom audio effect plugin"""
    
    def __init__(self, parameter1=0.5):
        super().__init__("My Custom Effect")
        self.parameter1 = parameter1
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        """Process audio"""
        # Your custom audio processing here
        result = audio * self.parameter1
        return result
```

### MIDI Processor Plugin Example

```python
from intuitive_daw.midi.processor import MIDIClip

class MyMIDIProcessor:
    """Custom MIDI processor plugin"""
    
    def process(self, clip: MIDIClip) -> MIDIClip:
        """Process MIDI clip"""
        # Your custom MIDI processing here
        for note in clip.notes:
            note.velocity = min(127, note.velocity * 1.2)
        return clip
```

## Installing Plugins

1. Place your plugin file in the `plugins/` or `user_plugins/` directory
2. Restart the DAW server
3. Your plugin will be automatically discovered and loaded

## Plugin API

See the documentation for the full plugin API reference.
