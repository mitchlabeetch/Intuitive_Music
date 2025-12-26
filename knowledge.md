# Knowledge - Intuitives

## Background
Music production software (Ableton, Logic) is intimidating. Intuitives aims to capture the joy of "happy accidents" by making the interface abstract and playful.

## Technical Architecture
- **Audio Engine:** A high-performance DSP engine, likely written in **Rust** and compiled to **WebAssembly**, handling synthesis, effects, and mixing. **Tone.js** might be used for higher-level scheduling.
- **Input Transformers:** Modules that convert non-musical data into musical events.
    - *Image-to-MIDI:* Analyzing pixel brightness/hue to generate note sequences.
    - *Webcam-to-CC:* Using **MediaPipe** or **TensorFlow.js** to track hand positions and map them to synthesizer parameters (Cutoff, Resonance).
- **AI Harmonizer:** Uses **Magenta.js** (e.g., MusicVAE or RNN) to listen to the user's input and generate accompanying tracks in real-time.
- **Visualizer:** A 3D canvas (Three.js) where every track is a 3D object. Mixing is done by moving these objects in 3D space (Left/Right = Pan, Front/Back = Volume, Up/Down = Pitch/EQ).

## Key Features
- **The "Chaos" Slider:** A global control that introduces randomness to every parameter in the project.
- **Fractal Mixer:** Instead of a fader board, the mix is represented as a fractal. Pulling shapes changes the audio characteristics.
- **Instant Remix:** "I like this loop, but make it Dubstep." One-click genre transformation using AI style transfer.
