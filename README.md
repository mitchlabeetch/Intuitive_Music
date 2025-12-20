# Intuitive Music DAW 🎵

An experimental, AI-assisted, extremely extensive Digital Audio Workstation (DAW) designed for local deployment. This project combines professional audio production capabilities with cutting-edge AI assistance to revolutionize music creation.

## Features

### Core DAW Features
- **Multi-track Audio & MIDI** - Unlimited tracks with professional audio and MIDI editing
- **Real-time Audio Processing** - Low-latency audio engine with 48kHz/24-bit support
- **Professional Effects** - EQ, Compression, Reverb, Delay, and more
- **MIDI Processing** - Complete MIDI editing, quantization, and manipulation
- **Project Management** - Comprehensive project save/load with metadata
- **Audio Rendering** - Export projects to various audio formats

### AI-Powered Features
- **Chord Progression Suggestions** - AI-generated chord progressions based on style and key
- **Melody Generation** - Intelligent melody composition assistance
- **Arrangement Analysis** - Get feedback on your arrangement and mix
- **Mixing Advice** - AI-powered mixing recommendations
- **Mastering Suggestions** - Professional mastering chain recommendations
- **Interactive AI Chat** - Ask questions and get expert music production advice

### Advanced Capabilities
- **Plugin System** - Extensible architecture for custom plugins
- **Automation** - Full parameter automation support
- **Session Recording** - Track your production sessions
- **Database Integration** - SQLite database for project management
- **Real-time Collaboration** - WebSocket-based communication
- **Web-based UI** - Modern React-based interface

## Architecture

```
intuitive_music/
├── src/intuitive_daw/        # Main Python package
│   ├── core/                 # Core audio engine & project management
│   ├── audio/                # Audio processing & effects
│   ├── midi/                 # MIDI processing & manipulation
│   ├── ai/                   # AI assistant integration
│   ├── api/                  # Flask REST API & WebSocket server
│   ├── db/                   # Database models
│   ├── utils/                # Utility functions
│   └── cli.py                # Command-line interface
├── frontend/                 # React-based web UI
│   ├── src/                  # Frontend source code
│   └── public/               # Static assets
├── tests/                    # Test suite
├── docs/                     # Documentation
├── config.yaml               # Configuration file
└── requirements.txt          # Python dependencies
```

## Installation

### Prerequisites
- Python 3.9 or higher
- Node.js 16+ and npm (for frontend)
- Audio drivers (ASIO on Windows, CoreAudio on macOS, ALSA/JACK on Linux)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/mitchlabeetch/Intuitive_Music.git
cd Intuitive_Music
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Install the package**
```bash
pip install -e .
```

5. **Initialize the environment**
```bash
intuitive-daw init
```

6. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

7. **Install frontend dependencies** (optional)
```bash
cd frontend
npm install
```

## Usage

### Starting the Server

```bash
# Start the DAW server
intuitive-daw serve

# Or with custom configuration
intuitive-daw serve --host 0.0.0.0 --port 8000 --config config.yaml
```

The server will be available at `http://localhost:5000`

### Command Line Interface

```bash
# Create a new project
intuitive-daw create "My Project"

# Show project information
intuitive-daw info ./projects/my-project

# Export project to audio
intuitive-daw export ./projects/my-project output.wav --format wav

# Run system tests
intuitive-daw test
```

### Python API

```python
from intuitive_daw import AudioEngine, Project, Track

# Create a new project
project = Project("My Song")
project.set_tempo(120)
project.set_time_signature(4, 4)

# Add tracks
from intuitive_daw.core.track import AudioTrack, MIDITrack
audio_track = AudioTrack("Vocals")
midi_track = MIDITrack("Piano")

project.add_track(audio_track)
project.add_track(midi_track)

# Initialize audio engine
engine = AudioEngine()
engine.initialize()

# Add tracks to engine
engine.add_track(audio_track)
engine.add_track(midi_track)

# Start playback
engine.start_playback()

# Save project
project.save()
```

### AI Assistant

```python
from intuitive_daw.ai.assistant import AIAssistant

# Create AI assistant
ai = AIAssistant()

# Get chord suggestions
response = ai.suggest_chords(key="C major", style="pop")
print(response.content)

# Generate melody
response = ai.generate_melody(
    key="C major",
    chord_progression=["C", "Am", "F", "G"]
)
print(response.content)

# Get mixing advice
response = ai.mixing_advice(
    track_name="Vocals",
    track_type="vocals",
    issues=["muddy", "harsh sibilance"]
)
print(response.content)
```

### MIDI Processing

```python
from intuitive_daw.midi.processor import MIDIProcessor, MIDIClip
from intuitive_daw.midi.processor import MIDIUtilities

# Create a MIDI clip
clip = MIDIClip("Piano Melody")

# Add notes
clip.add_note(pitch=60, velocity=80, start=0.0, duration=0.5)  # C4
clip.add_note(pitch=64, velocity=80, start=0.5, duration=0.5)  # E4
clip.add_note(pitch=67, velocity=80, start=1.0, duration=0.5)  # G4

# Create chord
notes = MIDIProcessor.create_chord(
    root=60,  # C4
    chord_type="major",
    velocity=80
)

# Create arpeggio
arp_notes = MIDIProcessor.create_arpeggio(
    notes=[60, 64, 67],  # C major triad
    pattern="up",
    note_duration=0.25
)
```

### Audio Effects

```python
from intuitive_daw.audio.processor import (
    EQEffect, CompressorEffect, ReverbEffect
)
import numpy as np

# Create effects
eq = EQEffect(sample_rate=48000, low_gain=-3.0, high_gain=2.0)
compressor = CompressorEffect(threshold_db=-20, ratio=4.0)
reverb = ReverbEffect(room_size=0.6, wet_level=0.3)

# Process audio
audio = np.random.randn(48000, 2)  # 1 second of audio
audio = eq.process(audio)
audio = compressor.process(audio)
audio = reverb.process(audio)
```

## Configuration

Edit `config.yaml` to customize:
- Audio settings (sample rate, buffer size, bit depth)
- MIDI configuration
- AI provider settings
- Database configuration
- Plugin directories
- Processing parameters

## API Endpoints

### REST API
- `GET /health` - Health check
- `POST /api/project` - Create new project
- `GET /api/project/<path>` - Load project
- `POST /api/project/save` - Save project
- `GET /api/tracks` - Get all tracks
- `POST /api/tracks` - Add new track
- `POST /api/transport/play` - Start playback
- `POST /api/transport/stop` - Stop playback
- `POST /api/transport/record` - Start recording
- `POST /api/ai/suggest-chords` - Get AI chord suggestions
- `POST /api/ai/chat` - Chat with AI assistant

### WebSocket Events
- `connect` - Client connection
- `disconnect` - Client disconnection
- `transport_update` - Transport state changes
- `transport_state` - Broadcast transport state

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black src/
flake8 src/
```

### Building Frontend
```bash
cd frontend
npm run build
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Roadmap

- [ ] VST/AU plugin support
- [ ] Advanced audio editing tools
- [ ] Spectral editing
- [ ] Score editor
- [ ] Cloud collaboration features
- [ ] Mobile companion app
- [ ] Advanced AI features (stem separation, style transfer)
- [ ] Performance optimizations
- [ ] Extensive plugin library

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

Built with:
- Flask & Flask-SocketIO
- React
- NumPy & SciPy
- librosa
- soundfile
- OpenAI API
- SQLAlchemy

---

Made with ❤️ by the Intuitive Music Team