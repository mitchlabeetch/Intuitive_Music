/**
 * INTUITIVES DAW - Main Header
 *
 * "Does this sound cool?" - The only rule.
 *
 * A rule-free, experimental digital audio workstation that prioritizes
 * intuition, randomness, and AI-assisted discovery over traditional
 * music theory constraints.
 */

#ifndef INTUITIVES_DAW_H
#define INTUITIVES_DAW_H

#ifdef __cplusplus
extern "C" {
#endif

#include "intuitives.h" // Our DSP library with 40 features

// ============================================================================
// VERSION
// ============================================================================

#define INTUITIVES_DAW_VERSION_MAJOR 1
#define INTUITIVES_DAW_VERSION_MINOR 0
#define INTUITIVES_DAW_VERSION_PATCH 0
#define INTUITIVES_DAW_NAME "Intuitives"
#define INTUITIVES_DAW_TAGLINE "Rule-free Experimental DAW"

// ============================================================================
// CORE CONSTANTS
// ============================================================================

#define MAX_DAW_TRACKS 64
#define MAX_PATTERNS 256
#define MAX_PATTERN_LENGTH 256
#define MAX_NOTES_PER_PATTERN 1024
#define MAX_AUTOMATION_POINTS 4096
#define MAX_UNDO_STEPS 100

// ============================================================================
// PROJECT STRUCTURES
// ============================================================================

typedef enum {
  NOTE_EVENT_OFF = 0,
  NOTE_EVENT_ON,
  NOTE_EVENT_SUSTAIN
} NoteEventType;

typedef struct {
  uint32_t id;
  int32_t note;     // MIDI note (-1 for rest)
  float velocity;   // 0.0 - 1.0
  float start_beat; // Start position in beats
  float duration;   // Duration in beats
  float pan;        // -1.0 to 1.0
  uint32_t color;   // Assigned color (for chromasynesthesia)
} PatternNote;

typedef struct {
  uint32_t id;
  char name[64];
  float length_beats; // Pattern length in beats
  PatternNote notes[MAX_NOTES_PER_PATTERN];
  uint32_t num_notes;
  int32_t root_note;  // Suggested root (0 = C, etc.) - optional
  bool use_scale;     // Whether to quantize to scale
  int32_t scale_type; // Scale type if use_scale is true
} Pattern;

typedef struct {
  uint32_t pattern_id;
  float start_beat; // Position in arrangement
  uint32_t track_id;
  float velocity_mul; // Velocity multiplier
  bool muted;
} PatternInstance;

typedef struct {
  uint32_t id;
  char name[64];

  // Synth/Instrument
  BasicSynth synth;

  // Effects chain (up to 8 effects)
  EffectChain effects;

  // Track parameters
  float volume;
  float pan;
  bool mute;
  bool solo;
  bool armed;

  // Visualization
  float peak_l, peak_r;
  SynesthesiaColor color;

  // Generator (optional - for AI-driven tracks)
  bool has_generator;
  MarkovMelodyGenerator markov;
  CellularAutomata cellular;
  GeneticMelody genetic;
} DawTrack;

typedef struct {
  // Transport
  float bpm;
  bool playing;
  bool recording;
  bool looping;
  float loop_start;
  float loop_end;
  float current_beat;
  uint64_t current_sample;

  // Time signature
  int32_t beats_per_bar;
  int32_t beat_unit;
} Transport;

typedef struct {
  char name[256];
  char filepath[1024];

  Transport transport;

  // Tracks
  DawTrack tracks[MAX_DAW_TRACKS];
  uint32_t num_tracks;
  uint32_t selected_track;

  // Patterns
  Pattern patterns[MAX_PATTERNS];
  uint32_t num_patterns;
  uint32_t selected_pattern;

  // Arrangement
  PatternInstance arrangement[MAX_PATTERNS * MAX_DAW_TRACKS];
  uint32_t num_arrangement_items;

  // Master section
  EffectChain master_effects;
  float master_volume;

  // Undo/Redo (simplified)
  uint32_t undo_index;

  bool modified;
  bool initialized;
} DawProject;

// ============================================================================
// DAW APPLICATION
// ============================================================================

typedef enum {
  VIEW_SEQUENCER = 0,
  VIEW_PATTERN_EDITOR,
  VIEW_MIXER,
  VIEW_SYNTH_RACK,
  VIEW_GENERATORS,
  VIEW_VISUALIZER,
  VIEW_MEDIA_INPUT,
  VIEW_SETTINGS
} DawView;

typedef struct {
  // Audio engine
  AudioEngine *engine;
  uint32_t sample_rate;
  uint32_t buffer_size;

  // Current project
  DawProject project;

  // UI state
  DawView current_view;
  bool show_transport;
  bool show_mixer;
  bool show_inspector;
  bool show_visualizer;
  bool show_generator_panel;

  // Visualization data
  WaveformScope scope;
  SpectrumAnalyzer spectrum;
  LevelMeter master_meter;
  SynesthesiaColor current_color; // Current chromasynesthesia color

  // Multimedia input state
  TextMelody text_melody;
  ColorHarmony color_harmony;

  // Rendering
  bool audio_running;
  bool needs_repaint;
} DawApp;

// ============================================================================
// LIFECYCLE
// ============================================================================

DawApp *daw_create(uint32_t sample_rate, uint32_t buffer_size);
void daw_destroy(DawApp *app);
void daw_init_audio(DawApp *app);
void daw_stop_audio(DawApp *app);

// ============================================================================
// PROJECT
// ============================================================================

void daw_new_project(DawApp *app, const char *name);
bool daw_save_project(DawApp *app, const char *filepath);
bool daw_load_project(DawApp *app, const char *filepath);
void daw_close_project(DawApp *app);

// ============================================================================
// TRANSPORT
// ============================================================================

void daw_play(DawApp *app);
void daw_pause(DawApp *app);
void daw_stop(DawApp *app);
void daw_set_bpm(DawApp *app, float bpm);
void daw_set_position(DawApp *app, float beat);
void daw_toggle_loop(DawApp *app);
void daw_set_loop_range(DawApp *app, float start, float end);

// ============================================================================
// TRACKS
// ============================================================================

int32_t daw_add_track(DawApp *app, const char *name);
void daw_remove_track(DawApp *app, uint32_t track_id);
void daw_set_track_volume(DawApp *app, uint32_t track_id, float volume);
void daw_set_track_pan(DawApp *app, uint32_t track_id, float pan);
void daw_toggle_track_mute(DawApp *app, uint32_t track_id);
void daw_toggle_track_solo(DawApp *app, uint32_t track_id);

// ============================================================================
// PATTERNS
// ============================================================================

int32_t daw_create_pattern(DawApp *app, const char *name, float length);
void daw_delete_pattern(DawApp *app, uint32_t pattern_id);
void daw_add_note_to_pattern(DawApp *app, uint32_t pattern_id, int32_t note,
                             float velocity, float start, float duration);
void daw_remove_note_from_pattern(DawApp *app, uint32_t pattern_id,
                                  uint32_t note_id);

// ============================================================================
// GENERATORS (AI/PROCEDURAL)
// ============================================================================

void daw_generate_melody_markov(DawApp *app, uint32_t pattern_id,
                                float temperature, uint32_t num_notes);
void daw_generate_melody_genetic(DawApp *app, uint32_t pattern_id,
                                 uint32_t generations);
void daw_generate_rhythm_cellular(DawApp *app, uint32_t pattern_id,
                                  uint32_t rule, float density);
void daw_generate_from_text(DawApp *app, uint32_t pattern_id, const char *text);
void daw_generate_from_image(DawApp *app, uint32_t pattern_id,
                             const uint8_t *pixels, uint32_t width,
                             uint32_t height);
void daw_generate_from_color(DawApp *app, uint32_t track_id, uint8_t r,
                             uint8_t g, uint8_t b);

// ============================================================================
// AUDIO PROCESSING (called from audio thread)
// ============================================================================

void daw_process_audio(DawApp *app, float *output_l, float *output_r,
                       size_t frames);

// ============================================================================
// VISUALIZATION
// ============================================================================

void daw_get_waveform(DawApp *app, float *buffer, size_t *size);
void daw_get_spectrum(DawApp *app, float *bands, size_t num_bands);
void daw_get_levels(DawApp *app, float *left, float *right);
uint32_t daw_get_current_color(DawApp *app); // Chromasynesthesia

#ifdef __cplusplus
}
#endif

#endif // INTUITIVES_DAW_H
