# INTUITIVES DAW - Integrated Tools Reference

> Analysis of 200+ audio tools, categorized and prioritized for our "experiment-first, no learning curve" philosophy.

## 🎯 Integration Philosophy

**Key Questions:**

1. Can a beginner use it immediately?
2. Does it enable experimentation?
3. Does it produce interesting results?
4. Is it open source / forkable?

---

## ✅ TIER 1: FULLY INTEGRATED

These tools are built into Intuitives DAW and work out of the box.

### Audio Analysis

| Tool               | Source                                     | What We Use                                 | Status                                |
| :----------------- | :----------------------------------------- | :------------------------------------------ | :------------------------------------ |
| **librosa**        | [librosa.org](https://librosa.org)         | BPM detection, pitch tracking, chroma, MFCC | ✅ `sglib.integrations.AudioAnalyzer` |
| **aubio**          | [aubio.org](https://aubio.org)             | Real-time pitch/onset detection             | ✅ `sglib.integrations.AudioAnalyzer` |
| **Meyda** concepts | [meyda.js](https://github.com/meyda/meyda) | Web audio features                          | ✅ Adapted for Python                 |

### AI Generation

| Tool                      | Source                                                                  | What We Use                        | Status                                 |
| :------------------------ | :---------------------------------------------------------------------- | :--------------------------------- | :------------------------------------- |
| **Magenta**               | [magenta.tensorflow.org](https://magenta.tensorflow.org)                | MelodyRNN, MusicVAE patterns       | ✅ `sglib.ai_models.MelodyRNN`         |
| **Scribbletune** concepts | [github.com/scribbletune](https://github.com/scribbletune/scribbletune) | Pattern strings, Euclidean rhythms | ✅ `sglib.integrations.PatternBuilder` |
| **Tonal** concepts        | [github.com/tonaljs/tonal](https://github.com/tonaljs/tonal)            | Chord parsing, scale helpers       | ✅ `sglib.integrations.AIGenerator`    |

### Stem Separation

| Tool         | Source                                                           | What We Use           | Status                             |
| :----------- | :--------------------------------------------------------------- | :-------------------- | :--------------------------------- |
| **Spleeter** | [github.com/deezer/spleeter](https://github.com/deezer/spleeter) | 2/4/5-stem separation | ✅ `sglib.ai_models.StemSeparator` |

### Audio to MIDI

| Tool            | Source                                                                   | What We Use              | Status                           |
| :-------------- | :----------------------------------------------------------------------- | :----------------------- | :------------------------------- |
| **basic-pitch** | [github.com/spotify/basic-pitch](https://github.com/spotify/basic-pitch) | Polyphonic transcription | ✅ `sglib.ai_models.AudioToMIDI` |

### Text to Music

| Tool                    | Source                                                                                   | What We Use              | Status                           |
| :---------------------- | :--------------------------------------------------------------------------------------- | :----------------------- | :------------------------------- |
| **AudioCraft/MusicGen** | [github.com/facebookresearch/audiocraft](https://github.com/facebookresearch/audiocraft) | Text-to-audio generation | ✅ `sglib.ai_models.TextToMusic` |

---

## 🔄 TIER 2: ARCHITECTURE INSPIRATION

We learned from these but built our own implementation.

### DAW Architecture

| Project           | Source                                                                             | What We Learned                      |
| :---------------- | :--------------------------------------------------------------------------------- | :----------------------------------- |
| **Intuitives DAW**  | [github.com/intuitivesdaw/intuitives](https://github.com/intuitivesdaw/intuitives)         | Full DAW architecture, plugin system |
| **Gridsound/DAW** | [github.com/gridsound/daw](https://github.com/gridsound/daw)                       | Web-based DAW patterns               |
| **LMMS**          | [github.com/LMMS/lmms](https://github.com/LMMS/lmms)                               | Cross-platform audio engine          |
| **Meadowlark**    | [github.com/MeadowlarkDAW/Meadowlark](https://github.com/MeadowlarkDAW/Meadowlark) | Rust audio architecture              |
| **Zrythm**        | [github.com/zrythm/zrythm](https://github.com/zrythm/zrythm)                       | GTK-based DAW patterns               |
| **AudioMass**     | [github.com/pkalogiros/AudioMass](https://github.com/pkalogiros/AudioMass)         | Web audio editing UI                 |

### Live Coding / Generative

| Project         | Source                                                                             | What We Learned        |
| :-------------- | :--------------------------------------------------------------------------------- | :--------------------- |
| **Sonic Pi**    | [github.com/sonic-pi-net/sonic-pi](https://github.com/sonic-pi-net/sonic-pi)       | Live coding philosophy |
| **TidalCycles** | [tidalcycles.org](https://tidalcycles.org)                                         | Pattern language       |
| **Sardine**     | [github.com/Bubobubobubobubo/sardine](https://github.com/Bubobubobubobubo/sardine) | Python live coding     |
| **Overtone**    | [github.com/overtone/overtone](https://github.com/overtone/overtone)               | Clojure music patterns |

### Synthesizers

| Project      | Source                                                                           | What We Learned         |
| :----------- | :------------------------------------------------------------------------------- | :---------------------- |
| **Surge**    | [github.com/surge-synthesizer/surge](https://github.com/surge-synthesizer/surge) | OSC/filter architecture |
| **Helm**     | [github.com/mtytel/helm](https://github.com/mtytel/helm)                         | Wavetable synthesis     |
| **Vital**    | Closed source                                                                    | Modern synth UX         |
| **VCV Rack** | [github.com/VCVRack/Rack](https://github.com/VCVRack/Rack)                       | Modular synthesis       |

---

## 📦 TIER 3: OPTIONAL EXTENSIONS

Install these for additional features.

### Neural Audio

| Tool                 | Install                  | Use Case                         |
| :------------------- | :----------------------- | :------------------------------- |
| **RAVE**             | `pip install acids-rave` | Real-time neural audio synthesis |
| **Demucs**           | `pip install demucs`     | Alternative stem separation      |
| **AudioLDM**         | `pip install audioldm`   | Latent diffusion audio           |
| **MusicLM** concepts | Research only            | Music understanding              |

### Advanced Generation

| Tool               | Install                 | Use Case              |
| :----------------- | :---------------------- | :-------------------- |
| **MuseGAN**        | Custom                  | GAN music generation  |
| **Magenta Studio** | Standalone              | Interactive AI tools  |
| **Riffusion**      | `pip install riffusion` | Diffusion-based music |

### Analysis

| Tool          | Install                                                       | Use Case                    |
| :------------ | :------------------------------------------------------------ | :-------------------------- |
| **openSMILE** | [audeering/opensmile](https://github.com/audeering/opensmile) | Feature extraction          |
| **Essentia**  | `pip install essentia`                                        | Music information retrieval |
| **audioFlux** | `pip install audioFlux`                                       | Advanced spectral           |

---

## 🌐 TIER 4: WEB AUDIO TOOLS

For future web version of Intuitives.

### Core Web Audio

| Library           | URL                                                                              | Purpose                |
| :---------------- | :------------------------------------------------------------------------------- | :--------------------- |
| **Tone.js**       | [tonejs.github.io](https://tonejs.github.io)                                     | Web Audio framework    |
| **Howler.js**     | [github.com/goldfire/howler.js](https://github.com/goldfire/howler.js)           | Audio playback         |
| **wavesurfer.js** | [github.com/katspaugh/wavesurfer.js](https://github.com/katspaugh/wavesurfer.js) | Waveform visualization |
| **Tuna**          | [github.com/Theodeus/tuna](https://github.com/Theodeus/tuna)                     | Web audio effects      |

### Web MIDI

| Library        | URL                                                          | Purpose       |
| :------------- | :----------------------------------------------------------- | :------------ |
| **WebMIDI.js** | [webmidijs.org](https://webmidijs.org)                       | MIDI I/O      |
| **JZZ**        | [github.com/jazz-soft/JZZ](https://github.com/jazz-soft/JZZ) | Advanced MIDI |

---

## 📊 DATA SOURCES

Free audio datasets for training and samples.

| Source                     | URL                                                                                      | Content             |
| :------------------------- | :--------------------------------------------------------------------------------------- | :------------------ |
| **Freesound**              | [freesound.org](https://freesound.org)                                                   | 500k+ samples       |
| **Internet Archive Audio** | [archive.org/details/audio](https://archive.org/details/audio)                           | Public domain audio |
| **NSynth**                 | [magenta.tensorflow.org/datasets/nsynth](https://magenta.tensorflow.org/datasets/nsynth) | Instrument samples  |
| **MUSDB18**                | [sigsep.github.io/datasets/musdb.html](https://sigsep.github.io/datasets/musdb.html)     | Multitrack music    |
| **FMA**                    | [github.com/mdeff/fma](https://github.com/mdeff/fma)                                     | Free music archive  |
| **Common Voice**           | [commonvoice.mozilla.org](https://commonvoice.mozilla.org/en)                            | Voice samples       |

---

## 🎨 UI COMPONENTS

For the Intuitives visual style.

| Library            | URL                                                                                    | Use              |
| :----------------- | :------------------------------------------------------------------------------------- | :--------------- |
| **Animate.css**    | [animate.style](https://animate.style)                                                 | CSS animations   |
| **Hover.css**      | [ianlunn.github.io/Hover](https://ianlunn.github.io/Hover/)                            | Hover effects    |
| **SpinKit**        | [tobiasahlin.com/spinkit](https://tobiasahlin.com/spinkit)                             | Loading spinners |
| **Wired Elements** | [github.com/rough-stuff/wired-elements](https://github.com/rough-stuff/wired-elements) | Sketchy UI       |

---

## 🔌 NATIVE AUDIO LIBRARIES

For C/C++ engine development.

| Library       | URL                                                                      | Purpose                  |
| :------------ | :----------------------------------------------------------------------- | :----------------------- |
| **miniaudio** | [github.com/mackron/miniaudio](https://github.com/mackron/miniaudio)     | Audio I/O (we use this!) |
| **PortAudio** | [github.com/PortAudio/portaudio](https://github.com/PortAudio/portaudio) | Cross-platform audio     |
| **JUCE**      | [github.com/juce-framework/JUCE](https://github.com/juce-framework/JUCE) | Audio app framework      |
| **iPlug2**    | [github.com/iPlug2/iPlug2](https://github.com/iPlug2/iPlug2)             | Plugin framework         |
| **KFR**       | [github.com/kfrlib/kfr](https://github.com/kfrlib/kfr)                   | Fast DSP                 |
| **FFTW**      | [fftw.org](https://fftw.org)                                             | FFT (we use this!)       |

---

## 📱 USAGE QUICK REFERENCE

### One-Liners

```python
from sglib.integrations import quick_analyze, quick_generate, quick_pattern
from sglib.ai_models import quick_transcribe, quick_separate_stems

# Analyze audio file
features = quick_analyze('song.mp3')
print(f"BPM: {features['bpm']}, Key: {features['key']} {features['mode']}")

# Generate melody
melody = quick_generate(style='markov', bars=4)

# Parse pattern
drums = quick_pattern("X-x- X-x- X-xx X---")

# Transcribe audio to MIDI
notes = quick_transcribe('recording.wav')

# Separate stems
stems = quick_separate_stems('song.mp3')
vocals = stems['vocals']
```

### Full Classes

```python
from sglib.integrations import AudioAnalyzer, AIGenerator, PatternBuilder

# Audio Analysis
analyzer = AudioAnalyzer(sample_rate=44100)
bpm = analyzer.detect_bpm(audio)
key, mode = analyzer.detect_key(audio)
onsets = analyzer.detect_onsets(audio)

# AI Generation
gen = AIGenerator()
melody = gen.generate_melody(num_bars=8, scale='pentatonic', style='genetic')
drums = gen.generate_drum_pattern(style='house')
chords = gen.color_to_harmony(255, 100, 50)  # RGB to chord

# Pattern Building
builder = PatternBuilder(bpm=120)
kick = builder.euclidean(5, 16)  # 5 hits in 16 steps
progression = builder.chord_pattern("Cmaj7 Am7 Fmaj7 G7")
```

---

## 📈 INTEGRATION ROADMAP

### Phase 1 (Current) ✅

- [x] librosa integration
- [x] Markov melody generation
- [x] Genetic algorithm melodies
- [x] Cellular automata rhythms
- [x] Text-to-melody
- [x] Color-to-harmony
- [x] Pattern string parsing
- [x] Euclidean rhythms

### Phase 2 (Next)

- [ ] Magenta model loading
- [ ] Spleeter stem separation
- [ ] basic-pitch transcription
- [ ] Real-time visualization

### Phase 3 (Future)

- [ ] AudioCraft text-to-music
- [ ] RAVE neural synthesis
- [ ] Web Audio version
- [ ] Webcam/gesture input

---

_"Does this sound cool?" - The only rule that matters._
