# Intuitives DAW - Implementation Roadmap

> **Philosophy**: "Does this sound cool?" - The only rule.

This document captures the strategic vision for evolving Intuitives from a traditional DAW structure to a truly revolutionary musical creation tool.

---

## Current State vs. Vision Gap Analysis

| Component        | Current Reality                    | Vision                                              | Priority |
| ---------------- | ---------------------------------- | --------------------------------------------------- | -------- |
| **UI Framework** | Native Python/Qt (Desktop)         | "JS Studio" (Electron/Tone.js/Lume 3D) OR Qt+OpenGL | Medium   |
| **Audio Engine** | Monolithic C Engine (engine.c)     | Universal Host (CLAP, VST3, Faust, Pd)              | High     |
| **Visuals**      | 2D Qt Painting (Chromasynesthesia) | GPU Shaders, 3D reactive particles                  | High     |
| **Workflow**     | Traditional DAW (timeline, tracks) | "Playground" (nodes in space, non-linear)           | Medium   |

---

## Phase 1: Engine Modularity (Priority: HIGH)

### 1.1 AudioNode Abstraction

Create a generic processor interface for all sound sources:

```c
// include/intuitives/processor.h
typedef struct {
    void* instance_data;
    void (*process_audio)(void* inst, float** inputs, float** outputs, int frames);
    void (*process_midi)(void* inst, MidiEvent* events, int count);
    void (*get_parameter)(void* inst, int param_id, float* value);
    void (*set_parameter)(void* inst, int param_id, float value);
    void (*free)(void* inst);
} AudioNode;
```

### 1.2 Refactor Track Structure

Change `Track` in `engine.h` to hold a list of `AudioNode` pointers instead of hardcoded oscillators and effect chains.

### 1.3 Implement Loaders

- **Internal**: Current oscillators become `AudioNode` instances
- **CLAP/VST3**: Write `clap_host.cpp` wrapping the CLAP C API
- **Faust**: Use `llvm_dsp_factory` for JIT compilation

---

## Phase 2: High-Performance Visuals (Priority: HIGH)

### 2.1 GPU-Accelerated Chromasynesthesia

Current `visual_music.py` uses CPU-bound `QPainter`. Migrate to:

1. **QOpenGLWidget** for rendering
2. **Fragment Shaders** for particle effects
3. **Shared Memory RingBuffer** for engine→UI data flow

### 2.2 Data Pipeline

```
Engine (C) → Shared Memory RingBuffer → Python QTimer → OpenGL Uniforms
```

### 2.3 Spectrum/Analyzer Exposure

Modify `engine.c` to expose analyzer data via memory-mapped file or raw pointer accessible via `ctypes`.

---

## Phase 3: "No-Theory" Mode (Priority: HIGH)

### 3.1 Scale Lock Input

Intercept all MIDI input and auto-correct to nearest note in selected scale:

```python
# In intui/midi_processor.py
def process_note(note, scale):
    if note not in scale:
        corrected = find_nearest_in_scale(note, scale)
        flash_correction_feedback()  # Visual: flash red momentarily
        return corrected
    return note
```

### 3.2 Visual Feedback

- Flash UI Red when a note is auto-corrected
- Teaches user scale affinity intuitively

---

## Phase 4: "Happy Accident" Features (Priority: MEDIUM)

### 4.1 Global "Mutate" Action

Add keyboard shortcut `M` for parameter mutation:

```python
# In main.py
def on_mutate():
    track_id = get_active_track()
    constants.DAW_IPC.mutate_track(track_id, amount=0.05)
```

Engine randomizes active synth/effect parameters by ±5%.

### 4.2 Generative Suggestions

- Markov chain melody generation
- L-System rhythm patterns
- Genetic algorithm for evolving sounds

---

## Phase 5: Canvas-Based Workflow (Priority: MEDIUM)

### 5.1 Replace Playlist with Canvas

Replace `QListWidget` in `playlist.py` with `QGraphicsView`:

- Infinite canvas for dragging "Instrument Nodes"
- Visual signal flow routing (lines between nodes)
- Non-linear, spatial arrangement

### 5.2 Data Model

- Move from Tracks to Nodes
- Connections define audio routing
- Time becomes optional (loop-based or event-driven)

---

## Phase 6: AI Integration (Priority: LOW/FUTURE)

### 6.1 Ghost Tracks

Allow tracks with "Ghost" state (muted, visual only) for AI suggestions.

### 6.2 Jam Partner Loop

```python
# In ai/assistant.py
def on_silence_detected():
    prediction = magenta_model.continue_sequence(user_notes)
    ipc.send_ghost_clip(prediction)
    # Render as translucent path on canvas
    # Click to accept → becomes solid/real
```

---

## Immediate Action Items (Current Sprint)

1. ✅ **Fix crash on project creation** - Add guards for uninitialized UI components
2. ✅ **Replace deprecated Stargate logo** - New Neobrutalist icon.svg
3. ✅ **AudioNode abstraction** - Created processor.h with universal interface
4. ✅ **Enable high-performance visuals** - Created analyzer.h + Python wrapper
5. ✅ **Implement Scale Lock** - No-theory mode (scale_lock.py)
6. ✅ **Happy Accidents / Mutation** - Parameter randomization (mutation.py)
7. ✅ **Keyboard shortcuts** - Integrated controls (shortcuts.py)
8. ✅ **Neobrutalist knob painting** - NeobrutalistKnob class in knob.py

---

## Technical Decisions

### UI Framework Choice

**Option A: Stay with Qt + OpenGL**

- Pros: Current investment, native performance, PyQt expertise
- Cons: Less "web-fluid", harder 3D integration

**Option B: Embed QWebEngine**

- Pros: Full web tech (Tone.js, Lume), modern UI paradigms
- Cons: Complexity, performance overhead, two rendering contexts

**Recommendation**: Stay Qt but add **QOpenGLWidget** for visualization areas. This preserves existing work while enabling the visual philosophy.

### Engine Architecture

Keep the C engine as the "Universal Host" core but add:

1. Plugin hosting (CLAP priority, VST3 optional)
2. Memory-mapped audio analysis buffers
3. IPC commands for mutation/AI integration

---

## Success Metrics

- **Crash-free**: Zero crashes on project create/open/save
- **Visual Performance**: 60fps particle visualization
- **No-Theory**: Users can play without knowing scales
- **Happy Accidents**: One-click access to generative randomization
- **Philosophy Alignment**: "Does this sound cool?" is always answerable

---

_Document created: 2025-12-26_
_Last updated: 2025-12-26_
