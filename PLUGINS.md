# Plugin Development Guide - Intuitives DAW

<p align="center">
  <strong>Extend Everything • Share Everything • Create Everything</strong>
</p>

---

## Table of Contents

1. [Introduction](#introduction)
2. [Plugin Architecture](#plugin-architecture)
3. [Getting Started](#getting-started)
4. [Audio Effect Plugins](#audio-effect-plugins)
5. [MIDI Processor Plugins](#midi-processor-plugins)
6. [Generator Plugins](#generator-plugins)
7. [Visualizer Plugins](#visualizer-plugins)
8. [AI Model Plugins](#ai-model-plugins)
9. [Testing & Debugging](#testing--debugging)
10. [Distribution](#distribution)
11. [Best Practices](#best-practices)

---

## Introduction

### Plugin Philosophy

**Everything in Intuitives is extensible.** The plugin system allows you to:

- 🎚️ **Create Audio Effects** - Custom sound processors
- 🎹 **Build Instruments** - Virtual synthesizers
- 🎵 **Process MIDI** - Note manipulation and generation
- 🎨 **Add Visualizers** - Custom visual feedback
- 🤖 **Integrate AI** - New AI models and capabilities
- 📁 **Support Formats** - Import/export new file types
- 🎮 **Add Controllers** - Custom hardware integration

### Why Create Plugins?

- ✅ **Share Your Ideas** - Make tools others can use
- ✅ **Learn by Doing** - Understand DSP and audio
- ✅ **Solve Your Needs** - Build exactly what you want
- ✅ **Join Community** - Collaborate with other developers
- ✅ **Build Portfolio** - Showcase your skills

### Plugin Types

| Type | Purpose | Difficulty |
|------|---------|-----------|
| **Audio Effect** | Process audio signals | ⭐⭐ Moderate |
| **MIDI Processor** | Manipulate MIDI notes | ⭐ Easy |
| **Generator** | Create melodies/rhythms | ⭐⭐ Moderate |
| **Visualizer** | Display audio/data | ⭐⭐ Moderate |
| **AI Model** | Custom AI integration | ⭐⭐⭐ Advanced |
| **Instrument** | Virtual synthesizers | ⭐⭐⭐ Advanced |
| **Controller** | Hardware integration | ⭐⭐⭐ Advanced |

---

## Plugin Architecture

### Directory Structure

```
plugins/
└── my_plugin/
    ├── __init__.py          # Plugin entry point
    ├── plugin.py            # Main plugin code
    ├── manifest.json        # Plugin metadata
    ├── README.md            # Documentation
    ├── requirements.txt     # Dependencies (optional)
    ├── tests/               # Unit tests (optional)
    │   └── test_plugin.py
    └── assets/              # Resources (optional)
        ├── icon.png
        └── presets/
```

### Manifest File

Every plugin needs a `manifest.json`:

```json
{
  "name": "My Awesome Plugin",
  "id": "my-awesome-plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "email": "you@example.com",
  "description": "A brief description of what your plugin does",
  "homepage": "https://github.com/you/my-plugin",
  "license": "MIT",
  
  "type": "audio_effect",
  "entry_point": "plugin.MyEffect",
  
  "parameters": {
    "intensity": {
      "type": "float",
      "min": 0.0,
      "max": 1.0,
      "default": 0.5,
      "label": "Intensity",
      "description": "How strong the effect is"
    }
  },
  
  "requirements": [
    "numpy>=1.20.0",
    "scipy>=1.7.0"
  ],
  
  "tags": ["effect", "distortion", "creative"],
  "category": "Effects/Distortion",
  
  "compatibility": {
    "min_version": "0.6.0",
    "max_version": null
  }
}
```

### Plugin Lifecycle

```
1. Discovery
   ↓
2. Load manifest.json
   ↓
3. Check compatibility
   ↓
4. Install requirements
   ↓
5. Import entry_point
   ↓
6. Initialize plugin
   ↓
7. Register with DAW
   ↓
8. Ready to use
```

---

## Getting Started

### Quick Start: Your First Plugin

Let's create a simple volume booster plugin:

#### Step 1: Create Directory

```bash
mkdir -p plugins/volume_booster
cd plugins/volume_booster
touch __init__.py plugin.py manifest.json README.md
```

#### Step 2: Write Manifest

```json
{
  "name": "Volume Booster",
  "id": "volume-booster",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Increase volume with optional limiting",
  "type": "audio_effect",
  "entry_point": "plugin.VolumeBooster",
  "parameters": {
    "gain": {
      "type": "float",
      "min": 0.0,
      "max": 2.0,
      "default": 1.0,
      "label": "Gain"
    }
  }
}
```

#### Step 3: Implement Plugin

```python
# plugin.py
from intuitive_daw.audio.processor import AudioEffect
import numpy as np

class VolumeBooster(AudioEffect):
    """Simple volume booster effect"""
    
    def __init__(self, gain=1.0):
        super().__init__("Volume Booster")
        self.gain = gain
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        """
        Process audio by multiplying by gain.
        
        Args:
            audio: Input audio (samples, channels)
        
        Returns:
            Processed audio (same shape)
        """
        # Apply gain
        output = audio * self.gain
        
        # Optional: prevent clipping
        output = np.clip(output, -1.0, 1.0)
        
        return output
    
    def set_parameter(self, name: str, value: float):
        """Update parameter value"""
        if name == "gain":
            self.gain = value
```

#### Step 4: Add __init__.py

```python
# __init__.py
from .plugin import VolumeBooster

__all__ = ["VolumeBooster"]
```

#### Step 5: Test It

```python
# test.py
import numpy as np
from volume_booster.plugin import VolumeBooster

# Create test signal
sample_rate = 48000
duration = 1.0
samples = int(sample_rate * duration)
test_audio = np.random.randn(samples, 2) * 0.1

# Apply effect
effect = VolumeBooster(gain=1.5)
effect.sample_rate = sample_rate
output = effect.process(test_audio)

# Verify
assert output.shape == test_audio.shape
assert np.max(np.abs(output)) > np.max(np.abs(test_audio))
print("✅ Plugin works!")
```

#### Step 6: Use in DAW

```python
from intuitive_daw import Project
from plugins.volume_booster.plugin import VolumeBooster

project = Project("Test")
track = project.add_audio_track("Audio")

# Add your plugin
booster = VolumeBooster(gain=1.5)
track.add_effect(booster)
```

**Congratulations!** You've created your first plugin.

---

## Audio Effect Plugins

### Base Class

All audio effects inherit from `AudioEffect`:

```python
from intuitive_daw.audio.processor import AudioEffect
import numpy as np

class MyEffect(AudioEffect):
    def __init__(self, param1=0.5):
        super().__init__("My Effect Name")
        self.param1 = param1
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        """
        Process audio.
        
        Args:
            audio: Shape (samples, channels)
                   dtype: float32, range [-1.0, 1.0]
        
        Returns:
            Processed audio (same shape)
        """
        # Your DSP code here
        return audio
    
    def set_parameter(self, name: str, value: float):
        """Update parameter"""
        if name == "param1":
            self.param1 = value
    
    def reset(self):
        """Reset internal state (called on transport stop)"""
        super().reset()
        # Reset buffers, filters, etc.
```

### Example: Simple Delay Effect

```python
from intuitive_daw.audio.processor import AudioEffect
import numpy as np

class SimpleDelay(AudioEffect):
    """Basic delay effect with feedback"""
    
    def __init__(self, delay_time=0.5, feedback=0.3, mix=0.5):
        super().__init__("Simple Delay")
        self.delay_time = delay_time  # seconds
        self.feedback = feedback       # 0.0 to 1.0
        self.mix = mix                 # wet/dry mix
        self.buffer = None
        self.buffer_pos = 0
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        # Initialize buffer on first call
        if self.buffer is None:
            buffer_size = int(self.sample_rate * self.delay_time)
            self.buffer = np.zeros((buffer_size, audio.shape[1]))
        
        output = np.zeros_like(audio)
        
        for i in range(len(audio)):
            # Read from delay buffer
            delayed = self.buffer[self.buffer_pos]
            
            # Mix dry and wet
            dry = audio[i]
            wet = delayed
            output[i] = dry * (1 - self.mix) + wet * self.mix
            
            # Write to buffer with feedback
            self.buffer[self.buffer_pos] = audio[i] + delayed * self.feedback
            
            # Advance buffer position
            self.buffer_pos = (self.buffer_pos + 1) % len(self.buffer)
        
        return output
    
    def set_parameter(self, name: str, value: float):
        if name == "delay_time":
            self.delay_time = value
            self.buffer = None  # Recreate buffer
        elif name == "feedback":
            self.feedback = value
        elif name == "mix":
            self.mix = value
    
    def reset(self):
        """Clear delay buffer"""
        if self.buffer is not None:
            self.buffer.fill(0.0)
        self.buffer_pos = 0
```

### Example: Parametric EQ

```python
from intuitive_daw.audio.processor import AudioEffect
import numpy as np
from scipy import signal

class ParametricEQ(AudioEffect):
    """Three-band parametric equalizer"""
    
    def __init__(self, low_freq=100, low_gain=0, mid_freq=1000, 
                 mid_gain=0, mid_q=1.0, high_freq=10000, high_gain=0):
        super().__init__("Parametric EQ")
        
        # Parameters
        self.low_freq = low_freq
        self.low_gain = low_gain
        self.mid_freq = mid_freq
        self.mid_gain = mid_gain
        self.mid_q = mid_q
        self.high_freq = high_freq
        self.high_gain = high_gain
        
        # Filter states (per channel)
        self.zi_low = None
        self.zi_mid = None
        self.zi_high = None
    
    def _design_filters(self):
        """Design biquad filters for each band"""
        nyquist = self.sample_rate / 2
        
        # Low shelf
        self.b_low, self.a_low = signal.iirfilter(
            2, self.low_freq / nyquist, 
            btype='lowshelf', 
            ftype='butter',
            output='ba'
        )
        
        # Parametric mid (peaking filter)
        self.b_mid, self.a_mid = signal.iirpeak(
            self.mid_freq / nyquist,
            self.mid_q
        )
        
        # High shelf
        self.b_high, self.a_high = signal.iirfilter(
            2, self.high_freq / nyquist,
            btype='highshelf',
            ftype='butter',
            output='ba'
        )
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        # Initialize filters if needed
        if self.zi_low is None:
            self._design_filters()
            self.zi_low = [signal.lfilter_zi(self.b_low, self.a_low) * audio[0, ch] 
                          for ch in range(audio.shape[1])]
            self.zi_mid = [signal.lfilter_zi(self.b_mid, self.a_mid) * audio[0, ch]
                          for ch in range(audio.shape[1])]
            self.zi_high = [signal.lfilter_zi(self.b_high, self.a_high) * audio[0, ch]
                           for ch in range(audio.shape[1])]
        
        output = np.copy(audio)
        
        # Process each channel
        for ch in range(audio.shape[1]):
            # Apply gain to filters
            b_low = self.b_low * (10 ** (self.low_gain / 20))
            b_mid = self.b_mid * (10 ** (self.mid_gain / 20))
            b_high = self.b_high * (10 ** (self.high_gain / 20))
            
            # Apply filters
            output[:, ch], self.zi_low[ch] = signal.lfilter(
                b_low, self.a_low, audio[:, ch], zi=self.zi_low[ch]
            )
            output[:, ch], self.zi_mid[ch] = signal.lfilter(
                b_mid, self.a_mid, output[:, ch], zi=self.zi_mid[ch]
            )
            output[:, ch], self.zi_high[ch] = signal.lfilter(
                b_high, self.a_high, output[:, ch], zi=self.zi_high[ch]
            )
        
        return output
    
    def reset(self):
        """Reset filter states"""
        self.zi_low = None
        self.zi_mid = None
        self.zi_high = None
```

---

## MIDI Processor Plugins

### Base Interface

```python
from intuitive_daw.midi.processor import MIDIClip

class MIDIProcessor:
    """Base for MIDI processing plugins"""
    
    def __init__(self, name: str):
        self.name = name
    
    def process(self, clip: MIDIClip) -> MIDIClip:
        """
        Process MIDI clip.
        
        Args:
            clip: Input MIDI clip
        
        Returns:
            Processed MIDI clip (can be the same or new)
        """
        raise NotImplementedError
```

### Example: Humanizer

```python
from intuitive_daw.midi.processor import MIDIClip
import numpy as np

class MIDIHumanizer:
    """Add human feel to MIDI by randomizing timing and velocity"""
    
    def __init__(self, timing_amount=0.05, velocity_amount=10):
        self.name = "MIDI Humanizer"
        self.timing_amount = timing_amount  # seconds
        self.velocity_amount = velocity_amount  # MIDI units
    
    def process(self, clip: MIDIClip) -> MIDIClip:
        """Add human imperfections"""
        output = MIDIClip(f"{clip.name} - Humanized")
        
        for note in clip.notes:
            # Randomize timing slightly
            timing_offset = np.random.uniform(
                -self.timing_amount,
                self.timing_amount
            )
            new_start = max(0, note.start + timing_offset)
            
            # Randomize velocity
            velocity_offset = np.random.randint(
                -self.velocity_amount,
                self.velocity_amount + 1
            )
            new_velocity = np.clip(note.velocity + velocity_offset, 1, 127)
            
            # Add modified note
            output.add_note(
                pitch=note.pitch,
                velocity=new_velocity,
                start=new_start,
                duration=note.duration
            )
        
        return output
```

### Example: Chord Generator

```python
class ChordGenerator:
    """Generate chords from single notes"""
    
    def __init__(self, chord_type="major", voicing="close"):
        self.name = "Chord Generator"
        self.chord_type = chord_type
        self.voicing = voicing
        
        # Chord intervals (semitones from root)
        self.chord_intervals = {
            "major": [0, 4, 7],
            "minor": [0, 3, 7],
            "diminished": [0, 3, 6],
            "augmented": [0, 4, 8],
            "major7": [0, 4, 7, 11],
            "minor7": [0, 3, 7, 10],
            "dominant7": [0, 4, 7, 10]
        }
    
    def process(self, clip: MIDIClip) -> MIDIClip:
        """Convert notes to chords"""
        output = MIDIClip(f"{clip.name} - Chords")
        
        intervals = self.chord_intervals.get(self.chord_type, [0, 4, 7])
        
        for note in clip.notes:
            # Add each chord tone
            for interval in intervals:
                chord_note_pitch = note.pitch + interval
                
                # Keep within MIDI range
                if 0 <= chord_note_pitch <= 127:
                    output.add_note(
                        pitch=chord_note_pitch,
                        velocity=note.velocity,
                        start=note.start,
                        duration=note.duration
                    )
        
        return output
```

---

## Generator Plugins

### Base Class

```python
from intuitive_daw.midi.processor import MIDIClip
from typing import List, Dict, Any

class Generator:
    """Base for generative plugins"""
    
    def __init__(self, name: str):
        self.name = name
    
    def generate(self, length: int, **kwargs) -> MIDIClip:
        """
        Generate MIDI content.
        
        Args:
            length: Number of steps/notes to generate
            **kwargs: Generator-specific parameters
        
        Returns:
            Generated MIDI clip
        """
        raise NotImplementedError
```

### Example: Euclidean Rhythm Generator

```python
class EuclideanRhythm:
    """Generate Euclidean rhythms (evenly distributed hits)"""
    
    def __init__(self, name="Euclidean Rhythm"):
        self.name = name
    
    def generate(self, length: int, hits: int, rotation=0) -> MIDIClip:
        """
        Generate Euclidean rhythm.
        
        Args:
            length: Total number of steps
            hits: Number of hits to distribute
            rotation: Rotate pattern by N steps
        
        Returns:
            MIDI clip with rhythm pattern
        """
        # Bjorklund's algorithm
        pattern = self._bjorklund(hits, length)
        
        # Rotate if needed
        if rotation:
            pattern = pattern[rotation:] + pattern[:rotation]
        
        # Convert to MIDI
        clip = MIDIClip("Euclidean Rhythm")
        step_duration = 0.25  # 16th notes
        
        for step, hit in enumerate(pattern):
            if hit:
                clip.add_note(
                    pitch=36,  # Kick drum (GM)
                    velocity=100,
                    start=step * step_duration,
                    duration=step_duration * 0.9  # Slight gap
                )
        
        return clip
    
    def _bjorklund(self, hits: int, length: int) -> List[int]:
        """Bjorklund's algorithm for Euclidean rhythms"""
        if hits >= length:
            return [1] * length
        if hits == 0:
            return [0] * length
        
        # Start with hits ones and (length - hits) zeros
        groups = [[1]] * hits + [[0]] * (length - hits)
        
        # Iteratively pair groups
        while len(set(map(len, groups))) > 1:
            groups.sort(key=len, reverse=True)
            i = 0
            while i < len(groups) - 1 and len(groups[i]) != len(groups[i + 1]):
                groups[i].extend(groups.pop())
                i += 1
        
        # Flatten
        return [item for group in groups for item in group]
```

### Example: L-System Generator

```python
class LSystemGenerator:
    """Generate melodies using L-systems (Lindenmayer systems)"""
    
    def __init__(self):
        self.name = "L-System Generator"
        
        # Predefined L-systems
        self.systems = {
            "fibonacci": {
                "axiom": "A",
                "rules": {"A": "AB", "B": "A"},
                "mapping": {"A": 2, "B": -1}  # semitone changes
            },
            "cantor": {
                "axiom": "A",
                "rules": {"A": "ABA", "B": "BBB"},
                "mapping": {"A": 0, "B": 3}
            }
        }
    
    def generate(self, system="fibonacci", iterations=5, 
                 root_note=60, max_length=32) -> MIDIClip:
        """Generate melody from L-system"""
        # Get system definition
        sys_def = self.systems[system]
        
        # Generate string
        string = sys_def["axiom"]
        for _ in range(iterations):
            string = self._apply_rules(string, sys_def["rules"])
        
        # Convert to melody
        clip = MIDIClip(f"L-System: {system}")
        note = root_note
        time = 0.0
        duration = 0.25
        
        for i, char in enumerate(string[:max_length]):
            if char in sys_def["mapping"]:
                # Change pitch
                note += sys_def["mapping"][char]
                note = np.clip(note, 0, 127)
                
                # Add note
                clip.add_note(
                    pitch=note,
                    velocity=80,
                    start=time,
                    duration=duration
                )
                
                time += duration
        
        return clip
    
    def _apply_rules(self, string: str, rules: Dict[str, str]) -> str:
        """Apply L-system rules to string"""
        return ''.join(rules.get(char, char) for char in string)
```

---

## Visualizer Plugins

### Base Class

```python
from typing import Any
import numpy as np

class Visualizer:
    """Base for visualizer plugins"""
    
    def __init__(self, name: str):
        self.name = name
        self.width = 800
        self.height = 600
    
    def update(self, audio: np.ndarray, sample_rate: int) -> Any:
        """
        Update visualization with new audio.
        
        Args:
            audio: Audio buffer (samples, channels)
            sample_rate: Sample rate in Hz
        
        Returns:
            Visualization data (format depends on renderer)
        """
        raise NotImplementedError
    
    def resize(self, width: int, height: int):
        """Resize visualization"""
        self.width = width
        self.height = height
```

### Example: Oscilloscope

```python
class Oscilloscope(Visualizer):
    """Simple oscilloscope visualization"""
    
    def __init__(self):
        super().__init__("Oscilloscope")
        self.trigger_level = 0.0
        self.trigger_slope = "rising"
    
    def update(self, audio: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Generate oscilloscope data"""
        # Use left channel (or mono)
        signal = audio[:, 0] if audio.ndim > 1 else audio
        
        # Find trigger point
        trigger_idx = self._find_trigger(signal)
        
        # Extract display window
        window_size = min(self.width, len(signal) - trigger_idx)
        display_data = signal[trigger_idx:trigger_idx + window_size]
        
        # Normalize to screen height
        display_data = (display_data + 1.0) * (self.height / 2)
        
        return {
            "type": "waveform",
            "data": display_data.tolist(),
            "width": self.width,
            "height": self.height
        }
    
    def _find_trigger(self, signal: np.ndarray) -> int:
        """Find trigger point in signal"""
        for i in range(len(signal) - 1):
            if self.trigger_slope == "rising":
                if signal[i] < self.trigger_level <= signal[i + 1]:
                    return i
            else:  # falling
                if signal[i] > self.trigger_level >= signal[i + 1]:
                    return i
        return 0  # No trigger found
```

---

## AI Model Plugins

### Base Class

```python
from intuitive_daw.ai.base import AIModel
from typing import List, Dict, Any

class CustomAIModel(AIModel):
    """Base for custom AI model plugins"""
    
    def __init__(self, name: str, model_path: str = None):
        super().__init__(name)
        self.model_path = model_path
        self.model = None
    
    def load_model(self):
        """Load AI model from disk"""
        raise NotImplementedError
    
    def generate_melody(self, **kwargs) -> List[Dict]:
        """Generate melody"""
        raise NotImplementedError
    
    def get_info(self) -> Dict[str, Any]:
        """Return model metadata"""
        return {
            "name": self.name,
            "version": "1.0.0",
            "size_mb": 0,
            "capabilities": []
        }
```

### Example: Custom PyTorch Model

```python
import torch
import torch.nn as nn

class LSTMMelodyModel(CustomAIModel):
    """LSTM-based melody generation model"""
    
    def __init__(self, model_path: str):
        super().__init__("LSTM Melody Generator", model_path)
        self.load_model()
    
    def load_model(self):
        """Load PyTorch model"""
        self.model = torch.load(self.model_path)
        self.model.eval()
    
    def generate_melody(self, seed_notes: List[int], 
                       length: int, temperature: float = 1.0) -> List[Dict]:
        """Generate melody using LSTM"""
        # Prepare input
        input_tensor = torch.tensor(seed_notes, dtype=torch.long)
        input_tensor = input_tensor.unsqueeze(0)  # Add batch dimension
        
        # Generate
        generated = []
        hidden = None
        
        with torch.no_grad():
            for _ in range(length):
                # Forward pass
                output, hidden = self.model(input_tensor, hidden)
                
                # Apply temperature
                output = output / temperature
                probs = torch.softmax(output, dim=-1)
                
                # Sample next note
                next_note = torch.multinomial(probs[0, -1], 1).item()
                generated.append(next_note)
                
                # Update input
                input_tensor = torch.tensor([[next_note]], dtype=torch.long)
        
        # Convert to MIDI format
        notes = []
        for i, pitch in enumerate(generated):
            notes.append({
                "pitch": pitch,
                "velocity": 80,
                "start": i * 0.25,
                "duration": 0.25
            })
        
        return notes
```

---

## Testing & Debugging

### Unit Tests

```python
# tests/test_plugin.py
import unittest
import numpy as np
from my_plugin.plugin import MyEffect

class TestMyEffect(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.effect = MyEffect()
        self.effect.sample_rate = 48000
        self.test_audio = np.random.randn(4800, 2) * 0.1
    
    def test_process_shape(self):
        """Test that output shape matches input"""
        output = self.effect.process(self.test_audio)
        self.assertEqual(output.shape, self.test_audio.shape)
    
    def test_process_range(self):
        """Test that output is in valid range"""
        output = self.effect.process(self.test_audio)
        self.assertTrue(np.all(output >= -1.0))
        self.assertTrue(np.all(output <= 1.0))
    
    def test_parameter_update(self):
        """Test parameter updates"""
        self.effect.set_parameter("param1", 0.8)
        self.assertEqual(self.effect.param1, 0.8)
    
    def test_reset(self):
        """Test reset functionality"""
        self.effect.process(self.test_audio)
        self.effect.reset()
        # Verify state is cleared

if __name__ == "__main__":
    unittest.main()
```

### Debugging Tips

#### 1. Print Audio Statistics

```python
def _process_impl(self, audio: np.ndarray) -> np.ndarray:
    print(f"Input: shape={audio.shape}, min={audio.min():.3f}, max={audio.max():.3f}")
    
    output = self._do_processing(audio)
    
    print(f"Output: shape={output.shape}, min={output.min():.3f}, max={output.max():.3f}")
    return output
```

#### 2. Visualize Intermediate Steps

```python
import matplotlib.pyplot as plt

def debug_filter(audio, filtered):
    """Plot before and after filtering"""
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(audio[:1000, 0])
    plt.title("Input")
    
    plt.subplot(1, 2, 2)
    plt.plot(filtered[:1000, 0])
    plt.title("Output")
    
    plt.savefig("debug.png")
    plt.close()
```

#### 3. Profiling

```python
import time

def _process_impl(self, audio: np.ndarray) -> np.ndarray:
    start = time.time()
    
    output = self._do_processing(audio)
    
    elapsed = time.time() - start
    samples_per_sec = len(audio) / elapsed
    real_time_factor = samples_per_sec / self.sample_rate
    
    if real_time_factor < 1.0:
        print(f"⚠️ Not real-time! Factor: {real_time_factor:.2f}")
    
    return output
```

---

## Distribution

### Packaging

#### 1. Create setup.py

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="intuitive-plugin-myeffect",
    version="1.0.0",
    author="Your Name",
    author_email="you@example.com",
    description="My awesome effect plugin for Intuitives DAW",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/you/myeffect",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.9",
)
```

#### 2. Build Package

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# This creates:
# dist/intuitive-plugin-myeffect-1.0.0.tar.gz
# dist/intuitive_plugin_myeffect-1.0.0-py3-none-any.whl
```

#### 3. Publish to PyPI

```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ intuitive-plugin-myeffect

# Upload to production PyPI
twine upload dist/*
```

### GitHub Release

```bash
# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Create release on GitHub
# Upload dist files as release assets
```

### Plugin Registry

Submit to Intuitives Plugin Registry:

1. Fork https://github.com/intuitivesdaw/plugin-registry
2. Add your plugin to `plugins.json`:

```json
{
  "id": "my-awesome-effect",
  "name": "My Awesome Effect",
  "author": "Your Name",
  "version": "1.0.0",
  "description": "Brief description",
  "type": "audio_effect",
  "repository": "https://github.com/you/myeffect",
  "install": "pip install intuitive-plugin-myeffect",
  "tags": ["effect", "distortion"],
  "license": "MIT"
}
```

3. Submit pull request

---

## Best Practices

### Performance

1. **Minimize Allocations**
```python
# ❌ Bad: Creates new array each time
def _process_impl(self, audio):
    return audio * 2

# ✅ Good: Reuse buffer
def __init__(self):
    self.buffer = None

def _process_impl(self, audio):
    if self.buffer is None or self.buffer.shape != audio.shape:
        self.buffer = np.empty_like(audio)
    np.multiply(audio, 2, out=self.buffer)
    return self.buffer
```

2. **Vectorize Operations**
```python
# ❌ Bad: Python loop
for i in range(len(audio)):
    output[i] = audio[i] * gain

# ✅ Good: NumPy vectorization
output = audio * gain
```

3. **Profile Real-Time Performance**
```python
# Must process faster than real-time
# At 48kHz, buffer_size=512: must process in < 10.67ms
```

### Code Quality

1. **Type Hints**
```python
from typing import Optional
import numpy as np

def process(self, audio: np.ndarray) -> np.ndarray:
    """Process audio with type hints"""
    pass
```

2. **Documentation**
```python
def _process_impl(self, audio: np.ndarray) -> np.ndarray:
    """
    Process audio through effect.
    
    Args:
        audio: Input audio buffer, shape (samples, channels),
               float32 in range [-1.0, 1.0]
    
    Returns:
        Processed audio, same shape as input
    
    Raises:
        ValueError: If audio shape is invalid
    """
    pass
```

3. **Error Handling**
```python
def _process_impl(self, audio: np.ndarray) -> np.ndarray:
    if audio.ndim != 2:
        raise ValueError(f"Expected 2D audio, got {audio.ndim}D")
    
    if not -1.0 <= audio.max() <= 1.0:
        raise ValueError("Audio out of range [-1.0, 1.0]")
    
    return self._safe_process(audio)
```

### User Experience

1. **Sensible Defaults**
```python
def __init__(self, gain=1.0):  # ✅ 1.0 = no change (unity)
    pass

def __init__(self, gain=0.0):  # ❌ 0.0 = silence (confusing)
    pass
```

2. **Parameter Ranges**
```json
{
  "gain": {
    "min": 0.0,
    "max": 2.0,
    "default": 1.0,
    "label": "Gain",
    "unit": "x"
  }
}
```

3. **Presets**
```python
# Include useful presets
PRESETS = {
    "subtle": {"gain": 1.2, "mix": 0.3},
    "moderate": {"gain": 1.5, "mix": 0.5},
    "extreme": {"gain": 2.0, "mix": 0.8}
}
```

---

## Examples & Resources

### Example Plugins

Browse these open-source plugins:

- **Simple Gain** - https://github.com/intuitivesdaw/plugin-simple-gain
- **Chorus Effect** - https://github.com/intuitivesdaw/plugin-chorus
- **MIDI Humanizer** - https://github.com/intuitivesdaw/plugin-humanizer
- **Markov Generator** - https://github.com/intuitivesdaw/plugin-markov

### Learning Resources

- **DSP Guide** - https://dspguide.com/
- **Audio Plugin Development** - https://www.audio.dev/
- **NumPy for Audio** - https://realpython.com/numpy-array-programming/

### Community

- 💬 **Discord** - Plugin development channel
- 📖 **Forum** - https://forum.intuitivesdaw.com/plugins
- 🐛 **Report Issues** - GitHub Issues

---

<p align="center">
  <strong>Create • Share • Extend</strong>
</p>

<p align="center">
  <em>Make Intuitives your own</em>
</p>
