/**
 * INTUITIVES - WebAssembly Bindings
 * JavaScript-callable API for browser integration.
 */

#include "intuitives.h"
#include <emscripten.h>
#include <stdlib.h>
#include <string.h>

// Global engine instance for WASM
static AudioEngine *g_engine = NULL;
static BasicSynth *g_synth = NULL;
static Sample *g_output_l = NULL;
static Sample *g_output_r = NULL;

// ============================================================================
// ENGINE LIFECYCLE
// ============================================================================

EMSCRIPTEN_KEEPALIVE
int wasm_init(uint32_t sample_rate, uint32_t buffer_size) {
  if (g_engine)
    return 0; // Already initialized

  g_engine = (AudioEngine *)calloc(1, sizeof(AudioEngine));
  if (!g_engine)
    return -1;

  EngineConfig config = {.sample_rate = sample_rate,
                         .buffer_size = buffer_size,
                         .channels = 2,
                         .bit_depth = 32,
                         .realtime_priority = false,
                         .simd_enabled = false};

  if (engine_init(g_engine, &config) != INTUITIVES_OK) {
    free(g_engine);
    g_engine = NULL;
    return -1;
  }

  // Allocate output buffers
  g_output_l = (Sample *)calloc(buffer_size, sizeof(Sample));
  g_output_r = (Sample *)calloc(buffer_size, sizeof(Sample));

  // Create basic synth
  g_synth = (BasicSynth *)calloc(1, sizeof(BasicSynth));
  synth_init(g_synth, sample_rate);

  engine_start(g_engine);
  engine_play(g_engine);

  return 0;
}

EMSCRIPTEN_KEEPALIVE
void wasm_free(void) {
  if (g_engine) {
    engine_free(g_engine);
    free(g_engine);
    g_engine = NULL;
  }
  free(g_synth);
  free(g_output_l);
  free(g_output_r);
  g_synth = NULL;
  g_output_l = NULL;
  g_output_r = NULL;
}

// ============================================================================
// AUDIO PROCESSING
// ============================================================================

EMSCRIPTEN_KEEPALIVE
float *wasm_process(size_t frames) {
  if (!g_engine || !g_output_l)
    return NULL;

  // Process engine
  engine_process_block(g_engine, g_output_l, g_output_r, frames);

  // Add synth output
  if (g_synth) {
    for (size_t i = 0; i < frames; i++) {
      Sample s = synth_process(g_synth);
      g_output_l[i] += s;
      g_output_r[i] += s;
    }
  }

  // Soft clip
  for (size_t i = 0; i < frames; i++) {
    g_output_l[i] = intuitives_soft_clip(g_output_l[i]);
    g_output_r[i] = intuitives_soft_clip(g_output_r[i]);
  }

  return g_output_l;
}

EMSCRIPTEN_KEEPALIVE
float *wasm_get_output_l(void) { return g_output_l; }

EMSCRIPTEN_KEEPALIVE
float *wasm_get_output_r(void) { return g_output_r; }

// ============================================================================
// SYNTH CONTROL
// ============================================================================

EMSCRIPTEN_KEEPALIVE
void wasm_note_on(int32_t note, float velocity) {
  if (g_synth)
    synth_note_on(g_synth, note, velocity);
}

EMSCRIPTEN_KEEPALIVE
void wasm_note_off(void) {
  if (g_synth)
    synth_note_off(g_synth);
}

EMSCRIPTEN_KEEPALIVE
void wasm_set_waveform(int type) {
  if (g_synth) {
    g_synth->osc1.waveform_a = (WaveformType)type;
  }
}

EMSCRIPTEN_KEEPALIVE
void wasm_set_morph(float morph) {
  if (g_synth) {
    quantum_osc_set_morph(&g_synth->osc1, morph);
  }
}

EMSCRIPTEN_KEEPALIVE
void wasm_set_filter(float cutoff, float resonance) {
  if (g_synth) {
    svf_set_cutoff(&g_synth->filter, cutoff);
    svf_set_resonance(&g_synth->filter, resonance);
  }
}

EMSCRIPTEN_KEEPALIVE
void wasm_set_envelope(float attack, float decay, float sustain,
                       float release) {
  if (g_synth) {
    g_synth->amp_attack = attack;
    g_synth->amp_decay = decay;
    g_synth->amp_sustain = sustain;
    g_synth->amp_release = release;
  }
}

// ============================================================================
// OSCILLATOR BANK
// ============================================================================

static QuantumOscillator g_osc;
static bool g_osc_init = false;

EMSCRIPTEN_KEEPALIVE
void wasm_osc_init(uint32_t sample_rate) {
  quantum_osc_init(&g_osc, sample_rate);
  g_osc_init = true;
}

EMSCRIPTEN_KEEPALIVE
void wasm_osc_set_freq(float freq) {
  if (g_osc_init)
    quantum_osc_set_frequency(&g_osc, freq);
}

EMSCRIPTEN_KEEPALIVE
void wasm_osc_set_type(int waveform_a, int waveform_b) {
  if (g_osc_init) {
    g_osc.waveform_a = (WaveformType)waveform_a;
    g_osc.waveform_b = (WaveformType)waveform_b;
  }
}

EMSCRIPTEN_KEEPALIVE
float wasm_osc_process(void) {
  return g_osc_init ? quantum_osc_process(&g_osc) : 0.0f;
}

// ============================================================================
// EFFECTS
// ============================================================================

static Reverb g_reverb;
static bool g_reverb_init = false;

EMSCRIPTEN_KEEPALIVE
void wasm_reverb_init(uint32_t sample_rate) {
  reverb_init(&g_reverb, sample_rate);
  g_reverb_init = true;
}

EMSCRIPTEN_KEEPALIVE
void wasm_reverb_set(float room_size, float damping, float mix) {
  if (g_reverb_init) {
    g_reverb.room_size = room_size;
    g_reverb.damping = damping;
    g_reverb.mix = mix;
  }
}

EMSCRIPTEN_KEEPALIVE
void wasm_reverb_process(float *left, float *right, size_t frames) {
  if (g_reverb_init) {
    reverb_process_stereo(&g_reverb, left, right, frames);
  }
}

// ============================================================================
// GENERATIVE
// ============================================================================

static MarkovMelodyGenerator g_markov;
static bool g_markov_init = false;

EMSCRIPTEN_KEEPALIVE
void wasm_markov_init(uint32_t seed) {
  markov_init(&g_markov, seed);
  g_markov_init = true;
}

EMSCRIPTEN_KEEPALIVE
void wasm_markov_set_temperature(float temp) {
  if (g_markov_init)
    g_markov.temperature = temp;
}

EMSCRIPTEN_KEEPALIVE
int32_t wasm_markov_next(void) {
  return g_markov_init ? markov_next_note(&g_markov) : 60;
}

// Text to melody
static TextMelody g_text_melody;
static char g_text_buffer[1024];

EMSCRIPTEN_KEEPALIVE
void wasm_text_melody_init(const char *text) {
  strncpy(g_text_buffer, text, 1023);
  text_melody_init(&g_text_melody, g_text_buffer);
}

EMSCRIPTEN_KEEPALIVE
int32_t wasm_text_melody_next(void) {
  return text_melody_next_note(&g_text_melody);
}

// ============================================================================
// COLOR TO HARMONY
// ============================================================================

static ColorHarmony g_color_harmony;

EMSCRIPTEN_KEEPALIVE
void wasm_color_to_harmony(uint8_t r, uint8_t g, uint8_t b, int32_t octave) {
  color_harmony_from_rgb(&g_color_harmony, r, g, b, octave);
}

EMSCRIPTEN_KEEPALIVE
int32_t wasm_color_get_root(void) { return g_color_harmony.root_note; }

EMSCRIPTEN_KEEPALIVE
int32_t wasm_color_get_chord_note(int index) {
  if (index >= 0 && index < (int)g_color_harmony.num_notes) {
    return g_color_harmony.chord_notes[index];
  }
  return -1;
}

EMSCRIPTEN_KEEPALIVE
int32_t wasm_color_get_chord_size(void) { return g_color_harmony.num_notes; }

// ============================================================================
// VISUALIZATION
// ============================================================================

EMSCRIPTEN_KEEPALIVE
float *wasm_get_spectrum(size_t num_bands) {
  static float bands[128];
  if (g_engine) {
    spectrum_analyzer_get_bands(&g_engine->analyzer, bands,
                                num_bands > 128 ? 128 : num_bands);
  }
  return bands;
}

EMSCRIPTEN_KEEPALIVE
float wasm_get_level_l(void) {
  return g_engine ? g_engine->master_meter.peak_l : 0.0f;
}

EMSCRIPTEN_KEEPALIVE
float wasm_get_level_r(void) {
  return g_engine ? g_engine->master_meter.peak_r : 0.0f;
}

// ============================================================================
// CHROMASYNESTHESIA
// ============================================================================

EMSCRIPTEN_KEEPALIVE
uint32_t wasm_note_to_color(int32_t midi_note) {
  SynesthesiaColor color;
  chroma_note_to_color(midi_note, &color);
  return (color.r << 16) | (color.g << 8) | color.b;
}

// ============================================================================
// INFO
// ============================================================================

EMSCRIPTEN_KEEPALIVE
const char *wasm_version(void) { return intuitives_version_string(); }

EMSCRIPTEN_KEEPALIVE
size_t wasm_feature_count(void) {
  IntuitivesInfo info;
  intuitives_get_info(&info);
  return info.num_features;
}
