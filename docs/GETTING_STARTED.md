# Getting Started with Intuitive Music DAW

Welcome to Intuitive Music DAW! This guide will help you get up and running quickly.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.9+** installed ([Download Python](https://www.python.org/downloads/))
- **Git** for version control
- **Audio drivers** (ASIO for Windows, CoreAudio for macOS, ALSA/JACK for Linux)
- **(Optional)** Node.js 16+ for the frontend UI

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mitchlabeetch/Intuitive_Music.git
cd Intuitive_Music
```

### 2. Create a Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

This will install all required Python packages and the DAW itself in development mode.

### 4. Initialize the Environment

```bash
intuitive-daw init
```

This creates necessary directories:
- `projects/` - For your music projects
- `plugins/` - For plugin files
- `temp_audio/` - For temporary audio files
- `render_output/` - For rendered audio exports

### 5. Configure API Keys (Optional)

If you want to use AI features, you'll need API keys:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

   Get API keys from:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

### 6. Start the Server

```bash
intuitive-daw serve
```

The server will start on `http://localhost:5000`

You should see:
```
Starting Intuitive Music DAW Server on 127.0.0.1:5000
Available audio devices: X
 * Running on http://127.0.0.1:5000
```

## Quick Start Tutorial

### Creating Your First Project

#### Method 1: Using the CLI

```bash
# Create a new project
intuitive-daw create "My First Song"

# View project info
intuitive-daw info ./projects/My\ First\ Song/

# Run the example script
python examples/create_song.py
```

#### Method 2: Using Python Code

```python
from intuitive_daw.core.project import Project
from intuitive_daw.core.track import AudioTrack, MIDITrack

# Create a project
project = Project("My Song")
project.set_tempo(120)

# Add tracks
audio_track = AudioTrack("Vocals")
midi_track = MIDITrack("Piano")

project.add_track(audio_track)
project.add_track(midi_track)

# Save
project.save()
print(f"Project saved to {project.path}")
```

#### Method 3: Using the Web UI

1. Start the server: `intuitive-daw serve`
2. Open your browser to `http://localhost:5000`
3. Click "New Project"
4. Add tracks using "Add Audio Track" or "Add MIDI Track"
5. Use transport controls to play/record

### Working with MIDI

```python
from intuitive_daw.midi.processor import MIDIProcessor, MIDIClip

# Create a MIDI clip
clip = MIDIClip("My Melody")

# Add a note (Middle C for 1 beat)
clip.add_note(
    pitch=60,      # C4
    velocity=80,   # Medium velocity
    start=0.0,     # Start at beat 0
    duration=1.0   # 1 beat long
)

# Create a chord
notes = MIDIProcessor.create_chord(
    root=60,           # C4
    chord_type="major", # C major
    velocity=70
)

# Transpose the clip
clip.transpose(5)  # Transpose up 5 semitones

# Quantize to 16th notes
clip.quantize(0.25)
```

### Using AI Assistance

```python
from intuitive_daw.ai.assistant import AIAssistant

# Initialize AI assistant
ai = AIAssistant()

# Get chord suggestions
response = ai.suggest_chords(
    key="C major",
    style="pop"
)
print(response.content)

# Generate melody ideas
response = ai.generate_melody(
    key="C major",
    chord_progression=["C", "Am", "F", "G"],
    style="pop"
)
print(response.content)

# Get mixing advice
response = ai.mixing_advice(
    track_name="Vocals",
    track_type="vocals",
    issues=["muddy low end", "harsh sibilance"]
)
print(response.content)
```

### Adding Audio Effects

```python
from intuitive_daw.audio.processor import (
    EQEffect, CompressorEffect, ReverbEffect
)
from intuitive_daw.core.track import AudioTrack

# Create a track
track = AudioTrack("Vocals")

# Add effects
eq = EQEffect(
    sample_rate=48000,
    low_gain=-3.0,     # Cut low frequencies
    mid_gain=2.0,      # Boost mids
    high_gain=1.0      # Slightly boost highs
)

compressor = CompressorEffect(
    threshold_db=-20.0,
    ratio=4.0,
    attack_ms=10.0,
    release_ms=100.0
)

reverb = ReverbEffect(
    room_size=0.5,
    wet_level=0.3
)

# Add to track
track.add_effect(eq)
track.add_effect(compressor)
track.add_effect(reverb)
```

## Common Tasks

### Export/Render a Project

```bash
intuitive-daw export ./projects/My\ Song/ output.wav --format wav
```

Or in Python:
```python
from intuitive_daw.core.engine import AudioEngine

# Load project and render
engine = AudioEngine()
engine.initialize()

# Add tracks...
for track in project.tracks:
    engine.add_track(track)

# Render to file
engine.render("output.wav", duration=30.0)  # 30 seconds
```

### Run Tests

```bash
# Test the installation
intuitive-daw test

# Run full test suite
pytest tests/
```

### Configure Audio Settings

Edit `config.yaml`:

```yaml
audio:
  sample_rate: 48000  # 44100, 48000, 96000
  buffer_size: 512    # 128, 256, 512, 1024
  bit_depth: 24       # 16, 24, 32
  channels: 2         # 1 (mono), 2 (stereo)
```

## Troubleshooting

### Audio Engine Issues

**Problem:** "Failed to initialize audio engine"

**Solution:**
- Check your audio drivers are installed
- Try different buffer sizes in `config.yaml`
- On Linux, install ALSA or JACK: `sudo apt-get install libasound2-dev`

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'intuitive_daw'`

**Solution:**
```bash
# Make sure you installed in development mode
pip install -e .
```

### AI Features Not Working

**Problem:** AI suggestions return errors

**Solution:**
- Check your API keys in `.env`
- Make sure you have internet connectivity
- Verify your API quota isn't exceeded

### Frontend Issues

**Problem:** Frontend won't start

**Solution:**
```bash
cd frontend
npm install
npm start
```

## Next Steps

- Read the [Architecture Documentation](docs/ARCHITECTURE.md)
- Explore the [API Reference](docs/API.md)
- Check out [Examples](examples/)
- Experiment with creating custom plugins
- Join our community (link to be added)

## Getting Help

- **Documentation:** Check the `docs/` folder
- **Examples:** See `examples/` for code samples
- **Issues:** Report bugs on GitHub Issues
- **Questions:** Open a discussion on GitHub

## Learning Resources

### Music Production Basics
- Understanding tempo, time signatures, and keys
- MIDI note numbers (60 = Middle C)
- Audio effects (EQ, compression, reverb)
- Mixing and mastering concepts

### Python & Audio
- NumPy for audio processing
- Understanding sample rates and buffers
- Real-time audio concepts

Happy music making! 🎵
