# To-Do - Intuitives DAW

## ✅ Completed

### Phase 1: Core Infrastructure

- [x] **Basic Project Structure:** Python package with core, audio, ai, midi, plugins modules
- [x] **Audio Effects:** Gain, EQ, Compressor, Reverb, Delay effects implemented
- [x] **AI Assistant:** OpenAI integration with cloud-based suggestions
- [x] **Local AI Models:** Magenta MelodyRNN, AudioCraft MusicGen, Basic Pitch, Spleeter integration
- [x] **MIDI Processing:** MIDIClip, notes, processors (humanize, chord builder, arpeggiator)
- [x] **Plugin System:** Complete plugin loader with manifest parsing and template generators
- [x] **Integration Hub:** librosa/aubio/Meyda feature parity with scipy fallbacks

### Phase 2: Native C++ GUI (Dear ImGui)

- [x] **GUI Framework:** Dear ImGui + GLFW + OpenGL setup with CMake
- [x] **Theme System:** Neobrutalist dark theme with chromasynesthesia colors
- [x] **Transport Controls:** Play/Pause/Stop, BPM, time display, loop toggle
- [x] **Mixer Window:** Channel strips with volume, pan, mute/solo, level meters
- [x] **Generator Panel:** Markov, Genetic, Cellular, Text-to-Melody, Color-to-Harmony
- [x] **Visualizer:** Spectrum analyzer (32 bands), level meters, chromasynesthesia preview
- [x] **Sequencer View:** Pattern arrangement grid with playhead and loop regions
- [x] **Piano Roll Editor:** MIDI note editing with interactive drawing and velocity display
- [x] **Synth Rack:** Effect chain editor with drag-and-drop reordering
- [x] **Settings Panel:** Audio device, MIDI, appearance tabs with theme customization

### Phase 3: Python Utilities

- [x] **FreeSound Integration:** Search, preview, download with caching
- [x] **Hardware MIDI I/O:** rtmidi wrapper with MIDI learn and CC mapping
- [x] **L-System Generator:** 7 fractal presets with SVG visualization

## 🚧 In Progress

### Phase 4: Advanced Features

- [ ] **WebSocket API Server:** FastAPI bridge for real-time streaming
- [ ] **Image-to-Sound:** Pixel color to frequency mapping
- [ ] **Gesture Control:** MediaPipe hand tracking

## 📋 High Priority (Next Steps)

- [ ] **Export System:** MIDI/WAV/Stems export dialogs
- [ ] **Piano Roll Selection:** Multi-note selection and editing tools
- [ ] **Copy/Paste:** Clipboard operations for notes and patterns
- [ ] **Undo/Redo:** Full undo history for project changes
- [ ] **File Dialogs:** Native save/open dialogs for project files

## 📋 Medium Priority

- [ ] **Three.js Visualizer:** 3D audio-reactive scene
- [ ] **Webcam Hook:** MediaPipe hand tracking for gesture control
- [ ] **Sample Browser UI:** Waveform preview in GUI

## 📋 Low Priority

- [ ] **MIDI Export:** Download creations as .mid files
- [ ] **Sample Library:** Bundle high-quality default samples
- [ ] **Plugin Marketplace:** Discover and install community plugins
- [ ] **Cloud Sync:** Project backup and collaboration

## 📚 Documentation Tasks

- [x] Update FULL_RESOURCE_IMPLEMENTATION_PLAN.md with Section 16
- [x] Document L-System Generator presets and usage
- [ ] Add API documentation for local AI models
- [ ] Create plugin development tutorial
- [ ] Write integration testing guide

## 🐛 Known Issues

- [ ] Magenta requires specific TensorFlow version
- [ ] AudioCraft MusicGen is GPU-intensive
- [ ] Spleeter needs FFmpeg installed
- [ ] Dear ImGui requires GLFW and OpenGL (macOS: brew install glfw)
- [x] **Standalone Build Stability:** Fixed null pointer guards for IPC when audio engine isn't running
- [x] **libsndfile Loading:** Added Homebrew path support for macOS

## 🏗️ Build Instructions

### Native C++ DAW with GUI

```bash
cd native/intuitives_daw

# Install dependencies (macOS)
brew install glfw

# Clone Dear ImGui
mkdir -p third_party
git clone https://github.com/ocornut/imgui.git third_party/imgui

# Build
cmake -B build -DINTUITIVES_DAW_BUILD_GUI=ON
cmake --build build

# Run
./build/bin/IntuitivesDAW.app/Contents/MacOS/IntuitivesDAW
```

### Python Package

```bash
cd src
pip install -e intuitive_daw

# Core (Required)
pip install numpy scipy

# AI (Optional - Local Models)
pip install magenta audiocraft basic-pitch spleeter librosa

# Cloud AI (Optional)
pip install openai anthropic

# Utilities (Optional)
pip install requests python-rtmidi
```

## 📂 Project Structure

```
INTUITIVE_MUSIC/
├── native/intuitives_daw/           # C/C++ native DAW
│   ├── include/
│   │   ├── intuitives_daw.h         # DAW API
│   │   └── gui/intuitives_gui.h     # GUI header
│   ├── src/
│   │   ├── main.cpp                 # Entry point
│   │   └── gui/
│   │       ├── intuitives_gui.cpp   # Core GUI (~750 lines)
│   │       ├── sequencer.cpp        # Sequencer/Piano roll
│   │       ├── synth_rack.cpp       # Effect chain editor
│   │       └── settings.cpp         # Settings panel
│   └── CMakeLists.txt               # Build config
│
├── src/intuitive_daw/               # Python package
│   ├── ai/
│   │   ├── assistant.py             # Cloud AI
│   │   └── local_models.py          # Local AI models
│   ├── audio/processor.py           # Audio effects
│   ├── core/integrations.py         # External tools
│   ├── generators/
│   │   └── lsystem.py               # L-System generator
│   ├── midi/processor.py            # MIDI processing
│   ├── plugins/loader.py            # Plugin system
│   └── utils/
│       ├── freesound.py             # FreeSound API
│       └── midi_io.py               # Hardware MIDI
│
└── FULL_RESOURCE_IMPLEMENTATION_PLAN.md  # 200+ tool integration guide
```

## 📊 Implementation Stats

| Category                | Modules | Lines      |
| ----------------------- | ------- | ---------- |
| Python AI               | 2       | ~1,115     |
| Python Audio/MIDI       | 2       | ~640       |
| Python Plugins/Core     | 2       | ~1,200     |
| Python Utils/Generators | 3       | ~1,300     |
| C++ Core                | 2       | ~1,200     |
| C++ GUI                 | 5       | ~2,035     |
| **Total**               | **16**  | **~7,500** |
