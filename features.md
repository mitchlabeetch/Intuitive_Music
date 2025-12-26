# Features - Intuitives

## Native Audio Engine (C17) - 40 Features Implemented ✅

| Category        | Feature               | Description                                | Status  |
| :-------------- | :-------------------- | :----------------------------------------- | :------ |
| **Oscillators** | Quantum Oscillator    | Multi-waveform with real-time morphing     | ✅ 100% |
|                 | Chaos Oscillator      | Lorenz attractor-based synthesis           | ✅ 100% |
|                 | Wavetable Oscillator  | Band-limited with interpolation            | ✅ 100% |
|                 | FM Synthesis          | 6-operator with configurable algorithms    | ✅ 100% |
|                 | Additive Synthesis    | 64 partials with spectral shaping          | ✅ 100% |
|                 | Noise Generator       | 6 types (White, Pink, Brown, Velvet, etc.) | ✅ 100% |
|                 | Fractal Oscillator    | Mandelbrot/Julia-derived harmonics         | ✅ 100% |
| **Effects**     | State Variable Filter | Multi-mode LP/HP/BP/Notch                  | ✅ 100% |
|                 | Moog Ladder Filter    | Analog-modeled 4-pole with saturation      | ✅ 100% |
|                 | Formant Filter        | Vowel-shaping (A/E/I/O/U)                  | ✅ 100% |
|                 | Multi-tap Delay       | 8 taps with filtered feedback              | ✅ 100% |
|                 | Schroeder Reverb      | Algorithmic with damping                   | ✅ 100% |
|                 | Waveshaper Distortion | 8 algorithms (Tube, Foldback, etc.)        | ✅ 100% |
|                 | Compressor/Limiter    | Soft-knee with sidechain                   | ✅ 100% |
|                 | Chorus                | 8 voices with stereo spread                | ✅ 100% |
|                 | Phaser                | 12-stage all-pass cascade                  | ✅ 100% |
|                 | Bitcrusher            | Bit/sample-rate reduction                  | ✅ 100% |
| **Generators**  | Granular Synthesis    | 128-grain cloud engine                     | ✅ 100% |
|                 | Spectral Processing   | Freeze, blur, shift, robotize              | ✅ 100% |
|                 | Markov Melody         | Probabilistic note generation              | ✅ 100% |
|                 | Cellular Automata     | Rule 30/90/110 rhythm patterns             | ✅ 100% |
|                 | Genetic Algorithm     | Melody evolution over generations          | ✅ 100% |
|                 | L-System Generator    | Lindenmayer string to melody               | ✅ 100% |
|                 | Brownian Motion       | Constrained random walk                    | ✅ 100% |
|                 | Stochastic Sequencer  | Probability-based triggers                 | ✅ 100% |
|                 | Chord Progression     | Functional harmony generation              | ✅ 100% |
| **Input**       | Image-to-Spectrum     | Row-based additive synthesis               | ✅ 100% |
|                 | Color-to-Harmony      | RGB/HSB to chord mapping                   | ✅ 100% |
|                 | Pixel Rhythm          | Brightness to trigger patterns             | ✅ 100% |
|                 | Gesture Envelope      | Hand position to ADSR                      | ✅ 100% |
|                 | Motion Filter         | Head tracking to filter                    | ✅ 100% |
|                 | Text-to-Melody        | ASCII values to notes                      | ✅ 100% |
|                 | Random Walk           | Scale-quantized melodic walk               | ✅ 100% |
|                 | Emoji Drums           | Unicode to percussion                      | ✅ 100% |
| **Visual**      | Waveform Scope        | Triggered oscilloscope                     | ✅ 100% |
|                 | Spectrum Analyzer     | FFT with peak hold                         | ✅ 100% |
|                 | Phase Correlator      | Stereo field goniometer                    | ✅ 100% |
|                 | Level Meters          | True peak with clip detection              | ✅ 100% |
|                 | Fluid Sim Bridge      | Audio params for physics                   | ✅ 100% |
|                 | Chromasynesthesia     | Pitch-to-color mapping                     | ✅ 100% |

## Standalone DAW Application ✅ NEW

**Intuitives DAW** - Native C/C++ digital audio workstation (927KB executable)

| Component          | Description                              | Status  |
| :----------------- | :--------------------------------------- | :------ |
| **Transport**      | Play/Pause/Stop, BPM, loop mode          | ✅ 100% |
| **Track System**   | 64 tracks with synth, effects, mute/solo | ✅ 100% |
| **Pattern Editor** | Note sequencing with color coding        | ✅ 100% |
| **Markov Gen**     | Temperature-controlled melody generation | ✅ 100% |
| **Genetic Gen**    | Evolved melodies via selection           | ✅ 100% |
| **Cellular Gen**   | Rule-based rhythm patterns               | ✅ 100% |
| **Text-to-Melody** | Any text becomes music                   | ✅ 100% |
| **Color Harmony**  | RGB input creates chords                 | ✅ 100% |
| **Audio I/O**      | miniaudio (CoreAudio/ALSA/WASAPI)        | ✅ 100% |

### Build & Run

```bash
cd native/intuitives_daw/build
cmake .. && make -j8
./bin/IntuitivesDAW
```

## Roadmap - Next Steps

| Feature               | Description                       | Priority  |
| :-------------------- | :-------------------------------- | :-------- |
| **Dear ImGui GUI**    | Visual interface for DAW          | 🔴 High   |
| **MIDI Support**      | Input from controllers            | 🔴 High   |
| **Audio File I/O**    | WAV/MP3 import and export         | 🔴 High   |
| **Project Save**      | Binary/JSON project files         | 🟠 Medium |
| **Webcam Controller** | MediaPipe hand gesture mapping    | 🟠 Medium |
| **AI Accompaniment**  | Real-time drum/bass generation    | 🟠 Medium |
| **Plugin Format**     | Intuitives native plugin standard | 🟡 Low    |
| **Cloud Save**        | Share projects as URLs            | 🟡 Low    |

## Technical Implementation

### Native Engine (`native/`)

- **Language**: Pure C17 for maximum performance
- **SIMD**: AVX2/NEON auto-detection
- **Real-time Safe**: Lock-free ring buffers, zero allocations in audio thread
- **Cross-platform**: macOS, Linux, Windows, WebAssembly

### Native DAW (`native/intuitives_daw/`)

- **C++17** application linking C17 engine
- **miniaudio** for cross-platform audio I/O
- **Dear ImGui** (optional) for native GUI
- **927KB** standalone executable

### Demo Outputs

The native engine generates playable WAV files demonstrating:

- All 7 oscillator types morphing
- Filter sweeps with effects chain
- Markov + Cellular automata generative music
- Text converted to melody
- Granular cloud synthesis
- Genetic algorithm evolved melodies
- L-system fractal patterns

---

_Philosophy: "Does this sound cool?" - The only rule._
