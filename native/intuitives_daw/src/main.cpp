/**
 * INTUITIVES DAW v0.6 BETA
 *
 * Native C/C++ DAW with fully integrated generative tools.
 * "Does this sound cool?" - The only rule.
 *
 * Features:
 * - 40 Original DSP Features (oscillators, effects, generators)
 * - Markov/Genetic/Cellular melody generation
 * - Text-to-melody, Color-to-harmony
 * - Chromasynesthesia visualization
 * - Zero learning curve interface
 *
 * Built for macOS Intel (x86_64)
 */

#define MINIAUDIO_IMPLEMENTATION
#include "miniaudio.h"

// Dear ImGui (needs to be installed)
// #include "imgui.h"
// #include "imgui_impl_glfw.h"
// #include "imgui_impl_opengl3.h"

// OpenGL/GLFW (for windowing)
// #include <GLFW/glfw3.h>

#include <math.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifndef _WIN32
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif
#include "intuitives_daw.h"
#ifdef __cplusplus
}
#endif

// ============================================================================
// GLOBAL STATE
// ============================================================================

static DawApp *g_app = NULL;
static ma_device g_audio_device;
static volatile bool g_running = true;

// ============================================================================
// AUDIO CALLBACK
// ============================================================================

void audio_callback(ma_device *device, void *output, const void *input,
                    ma_uint32 frame_count) {
  (void)device;
  (void)input;

  float *out = (float *)output;

  if (!g_app) {
    memset(out, 0, frame_count * 2 * sizeof(float));
    return;
  }

  // Process DAW audio
  float *left = (float *)alloca(frame_count * sizeof(float));
  float *right = (float *)alloca(frame_count * sizeof(float));

  daw_process_audio(g_app, left, right, frame_count);

  // Interleave stereo output
  for (ma_uint32 i = 0; i < frame_count; i++) {
    out[i * 2 + 0] = left[i];
    out[i * 2 + 1] = right[i];
  }
}

// ============================================================================
// DAW CORE IMPLEMENTATION
// ============================================================================

#ifdef __cplusplus
extern "C" {
#endif

DawApp *daw_create(uint32_t sample_rate, uint32_t buffer_size) {
  DawApp *app = (DawApp *)calloc(1, sizeof(DawApp));
  if (!app)
    return NULL;

  app->sample_rate = sample_rate;
  app->buffer_size = buffer_size;

  // Initialize audio engine
  app->engine = (AudioEngine *)calloc(1, sizeof(AudioEngine));
  EngineConfig config = {.sample_rate = sample_rate,
                         .buffer_size = buffer_size,
                         .channels = 2,
                         .bit_depth = 32,
                         .realtime_priority = true,
                         .simd_enabled = true};
  engine_init(app->engine, &config);

  // Initialize visualization
  scope_init(&app->scope, sample_rate);
  spectrum_analyzer_init(&app->spectrum, sample_rate);
  meter_init(&app->master_meter, sample_rate);
  // Initialize chromasynesthesia default color
  chroma_note_to_color(60, &app->current_color);

  // Default view
  app->current_view = VIEW_SEQUENCER;
  app->show_transport = true;
  app->show_mixer = true;
  app->show_visualizer = true;

  // Create default project
  daw_new_project(app, "Untitled");

  return app;
}

void daw_destroy(DawApp *app) {
  if (!app)
    return;

  daw_stop_audio(app);

  if (app->engine) {
    engine_free(app->engine);
    free(app->engine);
  }

  spectrum_analyzer_free(&app->spectrum);

  free(app);
}

void daw_init_audio(DawApp *app) {
  if (!app || app->audio_running)
    return;

  ma_device_config config = ma_device_config_init(ma_device_type_playback);
  config.playback.format = ma_format_f32;
  config.playback.channels = 2;
  config.sampleRate = app->sample_rate;
  config.dataCallback = audio_callback;
  config.pUserData = app;

  if (ma_device_init(NULL, &config, &g_audio_device) != MA_SUCCESS) {
    fprintf(stderr, "Failed to initialize audio device\n");
    return;
  }

  if (ma_device_start(&g_audio_device) != MA_SUCCESS) {
    fprintf(stderr, "Failed to start audio device\n");
    ma_device_uninit(&g_audio_device);
    return;
  }

  app->audio_running = true;
  printf("🔊 Audio: %s @ %d Hz\n", g_audio_device.playback.name,
         g_audio_device.sampleRate);
}

void daw_stop_audio(DawApp *app) {
  if (!app || !app->audio_running)
    return;

  ma_device_uninit(&g_audio_device);
  app->audio_running = false;
}

// ============================================================================
// PROJECT MANAGEMENT
// ============================================================================

void daw_new_project(DawApp *app, const char *name) {
  if (!app)
    return;

  memset(&app->project, 0, sizeof(DawProject));
  strncpy(app->project.name, name, 255);

  // Default transport settings
  app->project.transport.bpm = 120.0f;
  app->project.transport.beats_per_bar = 4;
  app->project.transport.beat_unit = 4;
  app->project.transport.loop_end = 16.0f;

  // Create initial track
  daw_add_track(app, "Lead");

  // Create initial pattern
  daw_create_pattern(app, "Pattern 1", 4.0f);

  app->project.initialized = true;
  app->project.modified = false;

  printf("📁 New project: %s\n", name);
}

bool daw_save_project(DawApp *app, const char *filepath) {
  if (!app)
    return false;

  FILE *f = fopen(filepath, "wb");
  if (!f)
    return false;

  // Simple binary format (production would use JSON or similar)
  fwrite("INTV", 4, 1, f); // Magic
  fwrite(&app->project, sizeof(DawProject), 1, f);
  fclose(f);

  strncpy(app->project.filepath, filepath, 1023);
  app->project.modified = false;

  printf("💾 Saved: %s\n", filepath);
  return true;
}

bool daw_load_project(DawApp *app, const char *filepath) {
  if (!app)
    return false;

  FILE *f = fopen(filepath, "rb");
  if (!f)
    return false;

  char magic[4];
  fread(magic, 4, 1, f);
  if (memcmp(magic, "INTV", 4) != 0) {
    fclose(f);
    return false;
  }

  fread(&app->project, sizeof(DawProject), 1, f);
  fclose(f);

  strncpy(app->project.filepath, filepath, 1023);
  app->project.modified = false;

  printf("📂 Loaded: %s\n", filepath);
  return true;
}

void daw_close_project(DawApp *app) {
  if (!app)
    return;
  memset(&app->project, 0, sizeof(DawProject));
}

// ============================================================================
// TRANSPORT CONTROL
// ============================================================================

void daw_play(DawApp *app) {
  if (app) {
    app->project.transport.playing = true;
    printf("▶️  Play\n");
  }
}

void daw_pause(DawApp *app) {
  if (app) {
    app->project.transport.playing = false;
    printf("⏸️  Pause\n");
  }
}

void daw_stop(DawApp *app) {
  if (app) {
    app->project.transport.playing = false;
    app->project.transport.current_beat = 0;
    app->project.transport.current_sample = 0;
    printf("⏹️  Stop\n");
  }
}

void daw_set_bpm(DawApp *app, float bpm) {
  if (app) {
    app->project.transport.bpm = INTUITIVES_CLAMP(bpm, 20.0f, 400.0f);
  }
}

void daw_set_position(DawApp *app, float beat) {
  if (app) {
    app->project.transport.current_beat = beat;
    float samples_per_beat =
        (60.0f / app->project.transport.bpm) * app->sample_rate;
    app->project.transport.current_sample = (uint64_t)(beat * samples_per_beat);
  }
}

void daw_toggle_loop(DawApp *app) {
  if (app) {
    app->project.transport.looping = !app->project.transport.looping;
  }
}

void daw_set_loop_range(DawApp *app, float start, float end) {
  if (app) {
    app->project.transport.loop_start = start;
    app->project.transport.loop_end = end;
  }
}

// ============================================================================
// TRACK MANAGEMENT
// ============================================================================

int32_t daw_add_track(DawApp *app, const char *name) {
  if (!app || app->project.num_tracks >= MAX_DAW_TRACKS)
    return -1;

  uint32_t id = app->project.num_tracks;
  DawTrack *track = &app->project.tracks[id];

  memset(track, 0, sizeof(DawTrack));
  track->id = id;
  strncpy(track->name, name, 63);
  track->volume = 1.0f;
  track->pan = 0.0f;

  // Initialize synth
  synth_init(&track->synth, app->sample_rate);

  // Initialize effects chain
  effect_chain_init(&track->effects, app->sample_rate);

  // Assign a color based on track number (chromasynesthesia)
  chroma_note_to_color(60 + id * 7, &track->color); // Cycle of fifths

  app->project.num_tracks++;
  app->project.modified = true;

  printf("➕ Track %d: %s\n", id, name);
  return (int32_t)id;
}

void daw_remove_track(DawApp *app, uint32_t track_id) {
  if (!app || track_id >= app->project.num_tracks)
    return;

  // Shift tracks
  for (uint32_t i = track_id; i < app->project.num_tracks - 1; i++) {
    app->project.tracks[i] = app->project.tracks[i + 1];
    app->project.tracks[i].id = i;
  }

  app->project.num_tracks--;
  app->project.modified = true;
}

void daw_set_track_volume(DawApp *app, uint32_t track_id, float volume) {
  if (!app || track_id >= app->project.num_tracks)
    return;
  app->project.tracks[track_id].volume = INTUITIVES_CLAMP(volume, 0.0f, 2.0f);
}

void daw_set_track_pan(DawApp *app, uint32_t track_id, float pan) {
  if (!app || track_id >= app->project.num_tracks)
    return;
  app->project.tracks[track_id].pan = INTUITIVES_CLAMP(pan, -1.0f, 1.0f);
}

void daw_toggle_track_mute(DawApp *app, uint32_t track_id) {
  if (!app || track_id >= app->project.num_tracks)
    return;
  app->project.tracks[track_id].mute = !app->project.tracks[track_id].mute;
}

void daw_toggle_track_solo(DawApp *app, uint32_t track_id) {
  if (!app || track_id >= app->project.num_tracks)
    return;
  app->project.tracks[track_id].solo = !app->project.tracks[track_id].solo;
}

// ============================================================================
// PATTERN MANAGEMENT
// ============================================================================

int32_t daw_create_pattern(DawApp *app, const char *name, float length) {
  if (!app || app->project.num_patterns >= MAX_PATTERNS)
    return -1;

  uint32_t id = app->project.num_patterns;
  Pattern *pattern = &app->project.patterns[id];

  memset(pattern, 0, sizeof(Pattern));
  pattern->id = id;
  strncpy(pattern->name, name, 63);
  pattern->length_beats = length;

  app->project.num_patterns++;
  app->project.modified = true;

  printf("🎼 Pattern %d: %s (%.1f beats)\n", id, name, length);
  return (int32_t)id;
}

void daw_delete_pattern(DawApp *app, uint32_t pattern_id) {
  if (!app || pattern_id >= app->project.num_patterns)
    return;

  // Shift patterns
  for (uint32_t i = pattern_id; i < app->project.num_patterns - 1; i++) {
    app->project.patterns[i] = app->project.patterns[i + 1];
    app->project.patterns[i].id = i;
  }

  app->project.num_patterns--;
  app->project.modified = true;
}

void daw_add_note_to_pattern(DawApp *app, uint32_t pattern_id, int32_t note,
                             float velocity, float start, float duration) {
  if (!app || pattern_id >= app->project.num_patterns)
    return;

  Pattern *pattern = &app->project.patterns[pattern_id];
  if (pattern->num_notes >= MAX_NOTES_PER_PATTERN)
    return;

  PatternNote *pn = &pattern->notes[pattern->num_notes];
  pn->id = pattern->num_notes;
  pn->note = note;
  pn->velocity = velocity;
  pn->start_beat = start;
  pn->duration = duration;
  pn->pan = 0.0f;

  // Assign color via chromasynesthesia
  SynesthesiaColor color;
  chroma_note_to_color(note, &color);
  pn->color = (color.r << 16) | (color.g << 8) | color.b;

  pattern->num_notes++;
  app->project.modified = true;
}

void daw_remove_note_from_pattern(DawApp *app, uint32_t pattern_id,
                                  uint32_t note_id) {
  if (!app || pattern_id >= app->project.num_patterns)
    return;

  Pattern *pattern = &app->project.patterns[pattern_id];
  if (note_id >= pattern->num_notes)
    return;

  // Shift notes
  for (uint32_t i = note_id; i < pattern->num_notes - 1; i++) {
    pattern->notes[i] = pattern->notes[i + 1];
    pattern->notes[i].id = i;
  }

  pattern->num_notes--;
  app->project.modified = true;
}

// ============================================================================
// GENERATORS (AI/PROCEDURAL)
// ============================================================================

void daw_generate_melody_markov(DawApp *app, uint32_t pattern_id,
                                float temperature, uint32_t num_notes) {
  if (!app || pattern_id >= app->project.num_patterns)
    return;

  Pattern *pattern = &app->project.patterns[pattern_id];

  MarkovMelodyGenerator markov;
  markov_init(&markov, (uint32_t)time(NULL));
  markov.temperature = temperature;

  float beat = 0;
  float note_length = pattern->length_beats / num_notes;

  for (uint32_t i = 0;
       i < num_notes && pattern->num_notes < MAX_NOTES_PER_PATTERN; i++) {
    int32_t note = markov_next_note(&markov);
    if (note >= 0) {
      daw_add_note_to_pattern(app, pattern_id, note,
                              0.7f + (float)rand() / RAND_MAX * 0.3f, beat,
                              note_length * 0.9f);
    }
    beat += note_length;
  }

  printf("🎲 Generated %d Markov notes\n", num_notes);
}

void daw_generate_melody_genetic(DawApp *app, uint32_t pattern_id,
                                 uint32_t generations) {
  if (!app || pattern_id >= app->project.num_patterns)
    return;

  Pattern *pattern = &app->project.patterns[pattern_id];

  GeneticMelody genetic;
  genetic_init(&genetic, (uint32_t)time(NULL));

  for (uint32_t g = 0; g < generations; g++) {
    genetic_evolve(&genetic);
  }

  int32_t melody[GENETIC_LEN];
  genetic_get_best(&genetic, melody);

  float note_length = pattern->length_beats / GENETIC_LEN;
  for (int i = 0; i < GENETIC_LEN && pattern->num_notes < MAX_NOTES_PER_PATTERN;
       i++) {
    daw_add_note_to_pattern(app, pattern_id, melody[i], 0.8f, i * note_length,
                            note_length * 0.9f);
  }

  printf("🧬 Evolved melody over %d generations\n", generations);
}

void daw_generate_rhythm_cellular(DawApp *app, uint32_t pattern_id,
                                  uint32_t rule, float density) {
  if (!app || pattern_id >= app->project.num_patterns)
    return;

  Pattern *pattern = &app->project.patterns[pattern_id];

  CellularAutomata ca;
  cellular_init(&ca, 16, rule);
  cellular_randomize(&ca, density);

  float beat = 0;
  float step_length = pattern->length_beats / 16.0f;

  for (int step = 0; step < 16; step++) {
    bool triggers[16];
    cellular_get_triggers(&ca, triggers, 16);
    cellular_step(&ca);

    // Generate notes based on cellular state
    for (int i = 0; i < 16; i++) {
      if (triggers[i] && pattern->num_notes < MAX_NOTES_PER_PATTERN) {
        int32_t note = 36 + i * 2; // Drum-like mapping
        daw_add_note_to_pattern(app, pattern_id, note, 0.9f, beat,
                                step_length * 0.5f);
      }
    }
    beat += step_length;
  }

  printf("🔲 Generated cellular rhythm (Rule %d)\n", rule);
}

void daw_generate_from_text(DawApp *app, uint32_t pattern_id,
                            const char *text) {
  if (!app || pattern_id >= app->project.num_patterns || !text)
    return;

  Pattern *pattern = &app->project.patterns[pattern_id];

  TextMelody tm;
  text_melody_init(&tm, text);

  int32_t notes[256];
  size_t count;
  text_melody_get_sequence(&tm, notes, &count, 256);

  float note_length = pattern->length_beats / count;
  for (size_t i = 0; i < count && pattern->num_notes < MAX_NOTES_PER_PATTERN;
       i++) {
    daw_add_note_to_pattern(app, pattern_id, notes[i], 0.75f, i * note_length,
                            note_length * 0.8f);
  }

  printf("📝 Generated melody from: \"%s\" (%zu notes)\n", text, count);
}

void daw_generate_from_image(DawApp *app, uint32_t pattern_id,
                             const uint8_t *pixels, uint32_t width,
                             uint32_t height) {
  if (!app || pattern_id >= app->project.num_patterns || !pixels)
    return;

  // Simplified image to melody - directly use brightness
  (void)app;
  (void)pixels;
  (void)width;
  (void)height;

  // Extract brightness values from rows to create melody
  Pattern *pattern = &app->project.patterns[pattern_id];
  float note_length = pattern->length_beats / width;

  for (uint32_t x = 0; x < width && pattern->num_notes < MAX_NOTES_PER_PATTERN;
       x++) {
    // Average brightness of column x
    float brightness = 0;
    for (uint32_t y = 0; y < height; y++) {
      uint32_t idx = (y * width + x) * 3;
      brightness +=
          (pixels[idx] + pixels[idx + 1] + pixels[idx + 2]) / (3.0f * 255.0f);
    }
    brightness /= height;

    // Map brightness to note
    int32_t note = 48 + (int32_t)(brightness * 36); // C3 to C6
    daw_add_note_to_pattern(app, pattern_id, note, brightness, x * note_length,
                            note_length);
  }

  printf("🖼️  Generated melody from %dx%d image\n", width, height);
}

void daw_generate_from_color(DawApp *app, uint32_t track_id, uint8_t r,
                             uint8_t g, uint8_t b) {
  if (!app || track_id >= app->project.num_tracks)
    return;

  DawTrack *track = &app->project.tracks[track_id];

  ColorHarmony ch;
  color_harmony_from_rgb(&ch, r, g, b, 4);

  // Set track synth to root note
  synth_note_on(&track->synth, ch.root_note, 0.8f);

  // Update track color
  track->color.r = r;
  track->color.g = g;
  track->color.b = b;

  printf("🎨 Color #%02X%02X%02X → Note %d\n", r, g, b, ch.root_note);
}

// ============================================================================
// AUDIO PROCESSING
// ============================================================================

void daw_process_audio(DawApp *app, float *output_l, float *output_r,
                       size_t frames) {
  if (!app || !app->project.initialized) {
    memset(output_l, 0, frames * sizeof(float));
    memset(output_r, 0, frames * sizeof(float));
    return;
  }

  Transport *transport = &app->project.transport;

  // Clear output buffers
  memset(output_l, 0, frames * sizeof(float));
  memset(output_r, 0, frames * sizeof(float));

  if (!transport->playing)
    return;

  // Process each track
  for (uint32_t t = 0; t < app->project.num_tracks; t++) {
    DawTrack *track = &app->project.tracks[t];
    if (track->mute)
      continue;

    // Check solo
    bool any_solo = false;
    for (uint32_t s = 0; s < app->project.num_tracks; s++) {
      if (app->project.tracks[s].solo)
        any_solo = true;
    }
    if (any_solo && !track->solo)
      continue;

    // Process synth
    for (size_t i = 0; i < frames; i++) {
      float sample = synth_process(&track->synth);

      // Apply volume and pan
      float vol = track->volume;
      float pan_l = (track->pan <= 0) ? 1.0f : (1.0f - track->pan);
      float pan_r = (track->pan >= 0) ? 1.0f : (1.0f + track->pan);

      output_l[i] += sample * vol * pan_l;
      output_r[i] += sample * vol * pan_r;
    }
  }

  // Master volume and soft clip
  for (size_t i = 0; i < frames; i++) {
    output_l[i] =
        intuitives_soft_clip(output_l[i] * app->project.master_volume);
    output_r[i] =
        intuitives_soft_clip(output_r[i] * app->project.master_volume);
  }

  // Update visualization
  scope_write(&app->scope, output_l, output_r, frames);

  float mono[256];
  size_t mono_frames = frames > 256 ? 256 : frames;
  for (size_t i = 0; i < mono_frames; i++) {
    mono[i] = (output_l[i] + output_r[i]) * 0.5f;
  }
  spectrum_analyzer_write(&app->spectrum, mono, mono_frames);
  meter_analyze(&app->master_meter, output_l, output_r, frames);

  // Advance transport
  float samples_per_beat = (60.0f / transport->bpm) * app->sample_rate;
  transport->current_sample += frames;
  transport->current_beat = (float)transport->current_sample / samples_per_beat;

  // Handle looping
  if (transport->looping && transport->current_beat >= transport->loop_end) {
    transport->current_beat = transport->loop_start;
    transport->current_sample =
        (uint64_t)(transport->loop_start * samples_per_beat);
  }
}

// ============================================================================
// VISUALIZATION
// ============================================================================

void daw_get_waveform(DawApp *app, float *buffer, size_t *size) {
  // Simplified - just copy from scope buffer
  (void)app;
  (void)buffer;
  (void)size;
}

void daw_get_spectrum(DawApp *app, float *bands, size_t num_bands) {
  if (!app || !bands)
    return;
  spectrum_analyzer_get_bands(&app->spectrum, bands, num_bands);
}

void daw_get_levels(DawApp *app, float *left, float *right) {
  if (!app)
    return;
  *left = app->master_meter.peak_l;
  *right = app->master_meter.peak_r;
}

uint32_t daw_get_current_color(DawApp *app) {
  if (!app)
    return 0;
  // Chromasynesthesia: get color from current note
  SynesthesiaColor color;
  chroma_note_to_color(60, &color); // Use middle C as default
  return (color.r << 16) | (color.g << 8) | color.b;
}

#ifdef __cplusplus
}
#endif

// ============================================================================
// SIGNAL HANDLER
// ============================================================================

void signal_handler(int sig) {
  (void)sig;
  g_running = false;
}

// ============================================================================
// MAIN
// ============================================================================

int main(int argc, char *argv[]) {
  (void)argc;
  (void)argv;

  printf("\n");
  printf("╔══════════════════════════════════════════════════════════════╗\n");
  printf(
      "║                    INTUITIVES DAW                              ║\n");
  printf("║            Rule-free Experimental Music Creation              ║\n");
  printf(
      "╚══════════════════════════════════════════════════════════════╝\n\n");

  // Print version info
  printf("Engine v%s | 40 Original Features\n", intuitives_version_string());
  printf("Philosophy: \"Does this sound cool?\" - The only rule.\n\n");

  // Create DAW application
  g_app = daw_create(48000, 256);
  if (!g_app) {
    fprintf(stderr, "❌ Failed to create DAW application\n");
    return 1;
  }
  printf("✓ DAW engine initialized\n");

  // Initialize audio
  daw_init_audio(g_app);

  // Setup signal handler
  signal(SIGINT, signal_handler);

  // Check if we have a terminal (stdin is a TTY)
  bool has_terminal = false;
#ifndef _WIN32
  has_terminal = isatty(STDIN_FILENO);
#endif

  if (has_terminal) {
    // Terminal mode - show commands
    printf("\n");
    printf("═══════════════════════════════════════════════════════════════\n");
    printf(" COMMANDS (Terminal Mode)\n");
    printf("═══════════════════════════════════════════════════════════════\n");
    printf("  [space] Play/Pause    [s] Stop    [t] Add Track\n");
    printf("  [m] Generate Markov   [g] Generate Genetic    [c] Cellular\n");
    printf("  [x] Generate from text    [q] Quit\n");
    printf(
        "═══════════════════════════════════════════════════════════════\n\n");

#ifndef _WIN32
    struct termios old_termios, new_termios;
    tcgetattr(STDIN_FILENO, &old_termios);
    new_termios = old_termios;
    new_termios.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &new_termios);
    fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK);
#endif

    while (g_running) {
      char c;
      if (read(STDIN_FILENO, &c, 1) == 1) {
        switch (c) {
        case ' ':
          if (g_app->project.transport.playing) {
            daw_pause(g_app);
          } else {
            daw_play(g_app);
          }
          break;
        case 's':
          daw_stop(g_app);
          break;
        case 't':
          daw_add_track(g_app, "New Track");
          break;
        case 'm':
          daw_generate_melody_markov(g_app, 0, 0.7f, 16);
          break;
        case 'g':
          daw_generate_melody_genetic(g_app, 0, 50);
          break;
        case 'c':
          daw_generate_rhythm_cellular(g_app, 0, 90, 0.3f);
          break;
        case 'x': {
          printf("Generating from text: 'Intuitives DAW'\n");
          char text[256] = "Intuitives DAW";
          daw_generate_from_text(g_app, 0, text);
          break;
        }
        case 'q':
        case 27: // ESC
          g_running = false;
          break;
        }
      }
      usleep(10000);
    }

#ifndef _WIN32
    tcsetattr(STDIN_FILENO, TCSANOW, &old_termios);
#endif
  } else {
    // GUI/App mode - no terminal available
    printf("\n");
    printf("═══════════════════════════════════════════════════════════════\n");
    printf(" Running in App Mode (no terminal)\n");
    printf(" Audio engine active. Close app window to quit.\n");
    printf(
        "═══════════════════════════════════════════════════════════════\n\n");

    // Start playback automatically in app mode
    daw_play(g_app);

    // Generate a demo melody
    printf("🎲 Generating demo melody...\n");
    daw_generate_melody_markov(g_app, 0, 0.7f, 16);

    // Simple event loop (in production would be GUI event loop)
    while (g_running) {
      usleep(100000); // 100ms sleep
    }
  }

  printf("\n🧹 Cleaning up...\n");
  daw_destroy(g_app);
  printf("✅ Goodbye!\n\n");

  return 0;
}
