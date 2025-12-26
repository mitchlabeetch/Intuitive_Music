# INTUITIVES Native Audio Engine

**Rule-free, Experimental DAW Core** - High-performance C17 audio engine with **40 original features**.

> _"Does this sound cool?"_ - The only rule.

## Philosophy

INTUITIVES is built on the principle that music creation should be **intuitive, experimental, and free from traditional constraints**. This native engine provides the high-performance DSP core that enables:

- **Multimedia Input**: Start music from anywhere—images, gestures, text, emojis
- **Visual Feedback**: Sound visualization with spectrum, scope, and chromasynesthesia
- **AI as Jam Partner**: Generative systems that harmonize and evolve with you
- **No Guardrails**: Every parameter is accessible, every rule is optional

## 🎯 40 Original Features

### 🎹 Oscillators (7)

1. **Quantum Oscillator** - Multi-waveform with real-time morphing
2. **Chaos Oscillator** - Lorenz attractor-based synthesis
3. **Wavetable Oscillator** - Band-limited with interpolation
4. **FM Synthesis** - 6-operator with configurable algorithms
5. **Additive Synthesis** - Up to 64 partials with spectral shaping
6. **Noise Generator** - White, Pink, Brown, Blue, Velvet, Crackle
7. **Fractal Oscillator** - Mandelbrot/Julia-derived harmonics

### 🎛️ Effects (10)

8. **State Variable Filter** - Multi-mode (LP/HP/BP/Notch)
9. **Moog Ladder Filter** - Analog-modeled 4-pole with saturation
10. **Formant Filter** - Vowel-shaping (A/E/I/O/U morphing)
11. **Multi-tap Delay** - 8 taps with filtered feedback
12. **Schroeder Reverb** - Algorithmic with predelay/damping
13. **Waveshaper Distortion** - 8 algorithms (Tube, Foldback, Chebyshev...)
14. **Compressor/Limiter** - Soft-knee with sidechain
15. **Chorus** - Up to 8 voices with stereo spread
16. **Phaser** - 12-stage all-pass cascade
17. **Bitcrusher** - Bit/sample-rate reduction with dither

### 🎲 Generators (9)

18. **Granular Synthesis** - 128-grain cloud with position/pitch control
19. **Spectral Processing** - Freeze, blur, shift, robotize modes
20. **Markov Melody** - Temperature-controlled probabilistic generation
21. **Cellular Automata** - Rule 30/90/110/184 rhythm patterns
22. **Genetic Algorithm** - Melody evolution over generations
23. **L-System Generator** - Lindenmayer string to melody conversion
24. **Brownian Motion** - Constrained random walk with momentum
25. **Stochastic Sequencer** - Probability-based triggers
26. **Chord Progression** - Jazz/pop functional harmony generation

### 🖼️ Multimedia Input (8)

27. **Image-to-Spectrum** - Row-based additive synthesis from images
28. **Color-to-Harmony** - RGB/HSB to chord interval mapping
29. **Pixel Rhythm** - Brightness-to-trigger pattern conversion
30. **Gesture Envelope** - Hand XYZ position to ADSR
31. **Motion Filter** - Head tracking to filter parameters
32. **Text-to-Melody** - ASCII values to quantized notes
33. **Random Walk** - Scale-quantized melodic wandering
34. **Emoji Drums** - Unicode characters to percussion

### 📊 Visualization (6)

35. **Waveform Scope** - Triggered oscilloscope view
36. **Spectrum Analyzer** - FFT with log scale and peak hold
37. **Phase Correlator** - Stereo field goniometer
38. **Level Meters** - True peak with clip detection
39. **Fluid Simulation Bridge** - Audio parameters for physics
40. **Chromasynesthesia** - Pitch-to-color mapping

## 🔧 Technical Details

### Performance

- **Pure C17** for maximum portability and speed
- **SIMD-optimized** (AVX2/NEON auto-detection)
- **Lock-free** ring buffers for real-time safety
- **Zero allocations** in audio thread
- Compiles to **WebAssembly** for browser deployment

### Architecture

```
native/
├── include/intuitives/    # Public API headers
│   ├── core.h            # Types, constants, macros
│   ├── oscillators.h     # All oscillator types
│   ├── effects.h         # Effect processors
│   ├── generators.h      # Generative systems
│   ├── input.h           # Multimedia converters
│   ├── visual.h          # Audio analysis
│   └── engine.h          # Main engine API
├── src/
│   ├── core/engine.c     # Engine + BasicSynth
│   ├── dsp/              # Oscillators + effects
│   ├── generators/       # AI/procedural
│   ├── input/            # Multimedia input
│   └── visual/           # Visualization
├── demo/main.c           # Demo application
└── CMakeLists.txt        # Build system
```

## 🚀 Building

### Requirements

- CMake 3.16+
- C17 compiler (Clang, GCC, MSVC)

### Build Commands

```bash
cd native
mkdir build && cd build
cmake ..
make -j8

# Run demo
./intuitives_demo
```

### Build Options

```bash
cmake .. -DINTUITIVES_ENABLE_SIMD=ON    # Enable SIMD (default: ON)
cmake .. -DINTUITIVES_BUILD_WASM=ON     # Build WebAssembly
cmake .. -DINTUITIVES_BUILD_DEMO=OFF    # Skip demo
```

## 📝 Quick Start

### C API

```c
#include "intuitives.h"

// Create engine
AudioEngine* engine = intuitives_create_default_engine();
engine_add_track(engine, "Lead");
engine_play(engine);

// Process audio
Sample left[256], right[256];
engine_process_block(engine, left, right, 256);

// Create synth
BasicSynth synth;
synth_init(&synth, 48000);
synth_note_on(&synth, 60, 0.8f);  // Middle C
for (int i = 0; i < 48000; i++) {
    float sample = synth_process(&synth);
}
synth_note_off(&synth);

// Generate melody from text
TextMelody tm;
text_melody_init(&tm, "Hello World!");
int32_t notes[256];
size_t count;
text_melody_get_sequence(&tm, notes, &count, 256);
```

### Generative Examples

```c
// Markov chain melody
MarkovMelodyGenerator markov;
markov_init(&markov, 12345);
markov.temperature = 0.7f;
int32_t note = markov_next_note(&markov);

// Cellular automata rhythm
CellularAutomata ca;
cellular_init(&ca, 16, 90);  // Rule 90 (Sierpinski)
cellular_randomize(&ca, 0.3f);
bool triggers[16];
cellular_get_triggers(&ca, triggers, 16);
cellular_step(&ca);

// Genetic algorithm evolution
GeneticMelody genetic;
genetic_init(&genetic, 42);
for (int i = 0; i < 100; i++) {
    genetic_evolve(&genetic);
}
int32_t melody[GENETIC_LEN];
genetic_get_best(&genetic, melody);
```

## 📂 Generated Demo Files

Running `./intuitives_demo` creates:

- `demo_oscillators.wav` - Showcase of all oscillator types
- `demo_effects.wav` - Filter sweep with effects chain
- `demo_generative.wav` - Markov + Cellular automata
- `demo_text_melody.wav` - Text converted to music
- `demo_granular.wav` - Granular cloud synthesis
- `demo_genetic.wav` - Evolved melody
- `demo_lsystem.wav` - L-system fractal melody

## License

MIT License

---

_Built for the INTUITIVE_MUSIC project - where creativity knows no limits._
