# INTUITIVES DAW

**Rule-free, Experimental Digital Audio Workstation**

> _"Does this sound cool?"_ - The only rule.

## What is Intuitives?

Intuitives is a revolutionary DAW that breaks free from traditional music production constraints. Instead of enforcing scales, quantization, and music theory rules, Intuitives embraces:

- **AI-Powered Generation** - Markov chains, genetic algorithms, cellular automata
- **Multimedia as Input** - Images, text, colors, and gestures become music
- **Chromasynesthesia** - Every note has a color, every frequency a shape
- **No Guardrails** - If it sounds cool, it's right

## Features

### 🎹 Professional DAW Core

- 64 tracks with unlimited patterns
- 18 built-in instruments and effects
- Real-time audio processing
- Cross-platform (macOS, Linux, Windows)

### 🎲 Generative Tools

| Tool                  | Description                               |
| :-------------------- | :---------------------------------------- |
| **Markov Melody**     | Probabilistic note generation             |
| **Genetic Evolution** | Evolve melodies through natural selection |
| **Cellular Automata** | Rule-based rhythm patterns                |
| **L-System**          | Fractal melody structures                 |
| **Text-to-Melody**    | Any text becomes music                    |
| **Color-to-Harmony**  | Pick a color, get a chord                 |

### 🎨 Chromasynesthesia

Intuitives maps pitch to color using synesthesia principles:

- **C** → Red | **D** → Orange | **E** → Yellow
- **F** → Green | **G** → Cyan | **A** → Blue | **B** → Violet

Every note you play or generate is visualized in its corresponding color.

### 🔊 Audio Engine (40 Original Features)

- **Oscillators**: Quantum, Chaos, Wavetable, FM, Additive, Noise, Fractal
- **Effects**: SVF, Moog, Formant, Delay, Reverb, Distortion, Compressor, Chorus, Phaser, Bitcrusher
- **Visualization**: Spectrum analyzer, waveform scope, phase correlator, level meters

## Quick Start

### Requirements

- Python 3.9+
- PyQt5 or PyQt6
- Audio device (any will work)

### Installation

```bash
cd native/intuitives_daw

# Install Python dependencies
pip install -r requirements.txt

# Run Intuitives
python intuitives.py
```

### Build Native Engine

```bash
mkdir build && cd build
cmake ..
make -j8

# Run the native DAW
./bin/IntuitivesDAW
```

## Philosophy

Traditional DAWs are built for professional musicians who know music theory. Intuitives is built for everyone:

1. **No Wrong Notes** - If it sounds interesting, keep it
2. **AI Collaboration** - Let algorithms suggest ideas
3. **Visual Feedback** - See your music as colors and shapes
4. **Experimentation First** - Break rules, discover sounds

## Keyboard Shortcuts

|      Key       | Action                 |
| :------------: | :--------------------- |
|    `Space`     | Play/Pause             |
|      `0`       | Stop                   |
|      `G`       | Open Generator Panel   |
|    `F1-F6`     | Switch Views           |
|    `Ctrl+G`    | Generate Markov Melody |
| `Ctrl+Shift+G` | Evolve Genetic Melody  |

## Theming

Intuitives uses a modern glassmorphism design with the chromasynesthesia color palette. Custom themes are fully supported:

```bash
# Apply Intuitives theme
Appearance → Open Theme → intuitives.sgtheme
```

## Project Structure

```
native/intuitives_daw/
├── intuitives.py           # Entry point
├── sgui/                   # Python GUI
│   ├── main.py             # Main window
│   ├── widgets/            # Custom widgets
│   │   └── generators.py   # AI tools panel
│   └── daw/                # DAW-specific views
├── sglib/                  # Core library
│   ├── brand.py            # Branding constants
│   └── constants.py        # Configuration
├── stargate_engine/        # C audio engine
├── files/themes/           # UI themes
│   └── intuitives/         # Default theme
└── build/                  # Native executables
```

## Credits

- **Intuitives DSP Engine** - 40 original audio features (MIT License)
- **Stargate DAW Core** - Professional engine foundation (GPLv3)
- **Design Philosophy** - Inspired by experimental musicians worldwide

## License

- GUI and Branding: MIT License
- Audio Engine: GPLv3

---

## Join the Community

- 🌐 Website: [intuitives.dev](https://intuitives.dev)
- 💬 Discord: [discord.gg/intuitives](https://discord.gg/intuitives)
- 🐙 GitHub: [github.com/intuitives/daw](https://github.com/intuitives/daw)

---

_Remember: "Does this sound cool?" is the only question that matters._
