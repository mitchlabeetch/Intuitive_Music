# Intuitives DAW 🎵

<p align="center">
  <strong>Revolutionary Rule-Free Digital Audio Workstation</strong>
</p>

<p align="center">
  <em>"Does this sound cool?" - The only rule.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.6.0--beta-purple" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT%2FGPLv3-green" alt="License">
  <img src="https://img.shields.io/badge/open%20source-100%25-blue" alt="Open Source">
  <img src="https://img.shields.io/badge/AI-optional%20%26%20local--first-orange" alt="AI Optional">
</p>

---

## 🎯 What is Intuitives?

**Intuitives DAW** is an open-source, experimental Digital Audio Workstation that revolutionizes music creation by removing barriers and embracing creativity. Unlike traditional DAWs that enforce music theory rules and technical constraints, Intuitives empowers **everyone** to create music through:

- **🎲 Experiment-First Design** - Try ideas instantly without theory knowledge
- **🚫 No Learning Curve** - Create music within minutes, not months
- **🎨 Visual & Intuitive** - See your sound, shape it visually  
- **🤖 AI Optional** - Use AI when you want it, not when forced
- **🌱 Sustainability Focus** - Locally-run models preferred, no cloud dependency
- **🔌 Plugin-Open** - Extend and customize everything
- **📖 100% Open Source** - Free forever, community-driven

## ✨ Key Features

### 🎹 Professional DAW, Zero Learning Curve

**Complete Production Suite:**
- 🎵 **Unlimited Tracks** - Audio & MIDI, no artificial limits
- 🎚️ **40+ Native Effects** - Oscillators, filters, reverb, delay, distortion, and more
- 🎛️ **Real-time Processing** - 48kHz/24-bit low-latency audio engine
- 🎼 **Full MIDI Support** - Complete editing, automation, MPE controllers
- 💾 **Project Management** - Save, load, version control

**But Approachable for Beginners:**
- Generate music from text, images, or colors
- Visual sound manipulation (no technical knowledge needed)
- AI-assisted composition (fully optional)
- Progressive revelation of advanced features

### 🚀 Experiment-First Approach

**Bypass Traditional Music Theory:**
- ❌ No scale constraints or key signatures
- ❌ No forced quantization or time signatures  
- ❌ No "right" or "wrong" notes
- ✅ Visual feedback (Chromasynesthesia: every note has a color)
- ✅ Instant experimentation
- ✅ Happy accidents encouraged

**Generative Tools:**
- Markov chain melody generation
- Genetic algorithm sound evolution
- Cellular automata rhythm patterns
- L-system fractal compositions
- Random walk explorations

### 🤖 AI Integration (Optional & Local-First)

**Privacy-Preserving AI:**
- 🔒 **Local Models Default** - Magenta, MusicGen, Spleeter (runs on your computer)
- 🌱 **Sustainable** - 99% lower carbon footprint than cloud AI
- 💰 **Free** - No API costs or subscriptions
- 🔌 **Offline** - Work anywhere, anytime

**AI Features:**
- Chord progression suggestions
- Melody generation and harmonization
- Audio analysis (BPM, key, pitch detection)
- Stem separation (vocals, drums, bass, other)
- Audio-to-MIDI conversion
- Text-to-audio generation

**Cloud APIs Optional:** OpenAI, Anthropic for advanced chat features

### 🔌 Plugin-Open Architecture

**Extend Everything:**
- 🎚️ Create custom audio effects
- 🎹 Build virtual instruments
- 🎵 Design MIDI processors  
- 🎨 Add visualizers
- 🤖 Integrate AI models
- 📁 Support new file formats

**Simple Python API:**
```python
from intuitive_daw.audio.processor import AudioEffect

class MyEffect(AudioEffect):
    def __init__(self, param=0.5):
        super().__init__("My Effect")
        self.param = param
    
    def _process_impl(self, audio):
        return audio * self.param
```

### 🌍 100% Open Source

**Free Forever:**
- MIT/GPLv3 licenses
- No subscriptions or premium tiers
- No vendor lock-in
- Community-driven development
- Transparent decision-making

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

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- **Python 3.9+** - `python --version`
- **pip** - Included with Python
- **(Optional) Node.js 16+** - For web UI

### Installation

#### Option A: Python Package (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/mitchlabeetch/Intuitive_Music.git
cd Intuitive_Music

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install
pip install -e .

# 4. Initialize
intuitive-daw init

# 5. Start creating!
intuitive-daw serve  # Start web UI
```

#### Option B: Native App (macOS/Linux/Windows)

```bash
# Navigate to native app
cd native/intuitives_daw

# Build
./build.sh

# Run
./build/IntuitivesDAW.app/Contents/MacOS/IntuitivesDAW  # macOS
# Or: ./build/IntuitivesDAW  # Linux/Windows
```

### Your First Music (2 Minutes)

```python
from intuitive_daw import Project
from intuitive_daw.ai.local_models import LocalAI

# Create project
project = Project("My First Song")

# Generate melody from text (no theory needed!)
ai = LocalAI()
melody = ai.text_to_melody("Hello World")

# Add to project
track = project.add_midi_track("Melody")
track.add_clip(melody)

# Save
project.save()
```

**Congratulations!** You've created music without knowing a single music theory concept.

### Optional: Local AI Models

For enhanced AI features (still runs locally, no cloud):

```bash
# Install local AI models (recommended)
pip install magenta audiocraft basic-pitch spleeter

# These download on first use (~2GB total)
```

### Optional: Cloud AI APIs

Only if you want advanced chat features:

```bash
# Copy environment template
cp .env.example .env

# Add API keys (optional)
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

**Note:** Cloud APIs are completely optional. All core features work without them.

## 📚 Documentation

### Complete Guides

- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Comprehensive guide covering everything
- **[PHILOSOPHY.md](PHILOSOPHY.md)** - Project vision, values, and approach
- **[AI_INTEGRATION.md](AI_INTEGRATION.md)** - Local-first AI setup and usage
- **[PLUGINS.md](PLUGINS.md)** - Plugin development guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute

### Quick Links

- [Installation & Setup](DOCUMENTATION.md#installation--setup)
- [Your First 5 Minutes](DOCUMENTATION.md#your-first-5-minutes)
- [Core Concepts](DOCUMENTATION.md#core-concepts)
- [Plugin Development](PLUGINS.md)
- [Local AI Models](AI_INTEGRATION.md#getting-started-with-local-models)
- [Why Intuitives is Different](PHILOSOPHY.md)

### Usage Examples

See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed usage examples including:
- Creating projects and tracks
- Using the Python API
- Working with AI features
- MIDI processing
- Audio effects
- Command-line interface

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# Audio settings
audio:
  sample_rate: 48000
  buffer_size: 512
  bit_depth: 24

# AI settings (all optional)
ai:
  enabled: true
  provider: "local"  # Use local models by default
  local_models:
    melody: "magenta"
    harmony: "musicgen"

# Plugin directories
plugins:
  directories:
    - "./plugins"
    - "./user_plugins"
```

See [config.yaml](config.yaml) for all options.

## 🧪 Development

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

## 🤝 Contributing

**We welcome all contributions!** Whether you're:

- 🎵 A musician sharing feedback
- 💻 A developer fixing bugs or adding features
- 🎨 A designer improving UI/UX
- 📖 A writer creating tutorials
- 🔌 A plugin developer extending functionality

**Everyone is welcome here.**

### Quick Start Contributing

```bash
# 1. Fork on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Intuitive_Music.git

# 3. Create branch
git checkout -b feature/my-feature

# 4. Make changes and test
pytest tests/

# 5. Submit pull request
```

**See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.**

### Ways to Contribute

- 🐛 **Report Bugs** - Found an issue? Let us know!
- ✨ **Suggest Features** - Have an idea? Share it!
- 💻 **Submit Code** - Fix bugs or add features
- 📖 **Improve Docs** - Help others understand
- 🔌 **Create Plugins** - Extend functionality
- 🎵 **Share Music** - Show what you've created

## 📜 License

**Open Source Forever:**

- **Native Engine** - MIT License (permissive)
- **Stargate Components** - GPLv3 (copyleft)
- **Python Tools** - MIT License (permissive)

**What this means:**
- ✅ Free to use, modify, and distribute
- ✅ Use in commercial projects
- ✅ No vendor lock-in
- ✅ Community-owned

See [LICENSE](LICENSE) for details.

## 🗺️ Roadmap

### Coming Soon
- [ ] **VST/AU Plugin Support** - Use your favorite plugins
- [ ] **Mobile App** - Create music on phone/tablet
- [ ] **WebAssembly Version** - Run in browser
- [ ] **Collaborative Editing** - Make music with friends
- [ ] **Hardware Integration** - Better MIDI controller support
- [ ] **More AI Models** - Expanded generative tools

### Long-Term Vision
- **AR/VR Support** - Sculpt sound in 3D space
- **Universal Plugin Standard** - Cross-DAW compatibility
- **Educational Tools** - Learn music by creating

**See [GitHub Issues](https://github.com/mitchlabeetch/Intuitive_Music/issues) for detailed roadmap.**

## 🙋 Support & Community

### Get Help

- 📖 **[Documentation](DOCUMENTATION.md)** - Comprehensive guides
- 💬 **[Discord](https://discord.gg/intuitives)** - Live community chat
- 🐛 **[GitHub Issues](https://github.com/mitchlabeetch/Intuitive_Music/issues)** - Bug reports & features
- 💡 **[Discussions](https://github.com/mitchlabeetch/Intuitive_Music/discussions)** - Ideas & questions

### Stay Updated

- ⭐ **Star on GitHub** - Show support
- 👁️ **Watch Repository** - Get notified
- 🐦 **[X/Twitter](https://twitter.com/IntuitivesDAW)** - Follow updates
- 📺 **YouTube** - Tutorials coming soon

### Share Your Music

Created something with Intuitives? Share it!

- Tag **#IntuitivesDAW** on social media
- Post in Discord **#showcase** channel
- Submit to community gallery

## 🙏 Acknowledgments

### Core Technologies

- **[Stargate DAW](https://github.com/stargatedaw/stargate)** - Professional audio engine foundation
- **[Magenta](https://magenta.tensorflow.org/)** - Google's music AI
- **[AudioCraft](https://github.com/facebookresearch/audiocraft)** - Meta's text-to-music
- **[Librosa](https://librosa.org/)** - Audio analysis
- **Flask** - Web framework
- **React** - UI framework
- **NumPy/SciPy** - Scientific computing

### Inspiration

- **SuperCollider** - Live coding music
- **Sonic Pi** - Code-based creation
- **VCV Rack** - Modular synthesis
- **Hydra** - Visual live coding

### Community

Thank you to all contributors, testers, and users who make Intuitives possible!

---

## 💡 Philosophy

> **"Does this sound cool?"**
>
> That's the only question that matters.
>
> No rules. No theory requirements. No judgment.
>
> Just create.

**Music is for everyone.** Intuitives removes the barriers between your ideas and your creations.

---

<p align="center">
  <strong>🎵 Make Music Your Way 🎵</strong><br>
  <em>Experiment • Create • Share</em>
</p>

<p align="center">
  Made with ❤️ by the Intuitives community
</p>

<p align="center">
  <a href="DOCUMENTATION.md">Documentation</a> •
  <a href="PHILOSOPHY.md">Philosophy</a> •
  <a href="CONTRIBUTING.md">Contributing</a> •
  <a href="https://discord.gg/intuitives">Discord</a> •
  <a href="https://github.com/mitchlabeetch/Intuitive_Music">GitHub</a>
</p>