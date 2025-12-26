/**
 * INTUITIVES - Standalone Native Application
 * Cross-platform audio I/O using miniaudio.
 *
 * This is the production-ready native backend, not browser-limited.
 */

#define MINIAUDIO_IMPLEMENTATION
#include "intuitives.h"
#include "miniaudio.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>

// Global state
static AudioEngine *g_engine = NULL;
static BasicSynth *g_synth = NULL;
static ma_device g_device;
static volatile bool g_running = true;

// Audio callback - called from audio thread
void audio_callback(ma_device *device, void *output, const void *input,
                    ma_uint32 frame_count) {
  (void)device;
  (void)input;

  float *out = (float *)output;

  if (!g_engine || !g_synth) {
    memset(out, 0, frame_count * 2 * sizeof(float));
    return;
  }

  // Process synth
  for (ma_uint32 i = 0; i < frame_count; i++) {
    float sample = synth_process(g_synth);
    sample = intuitives_soft_clip(sample);
    out[i * 2 + 0] = sample; // Left
    out[i * 2 + 1] = sample; // Right
  }
}

// Signal handler
void signal_handler(int sig) {
  (void)sig;
  g_running = false;
  printf("\n🛑 Stopping...\n");
}

// Interactive keyboard input (non-blocking)
#ifdef _WIN32
#include <conio.h>
int get_key(void) {
  if (_kbhit())
    return _getch();
  return -1;
}
#else
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>

static struct termios g_old_termios;

void setup_terminal(void) {
  struct termios new_termios;
  tcgetattr(STDIN_FILENO, &g_old_termios);
  new_termios = g_old_termios;
  new_termios.c_lflag &= ~(ICANON | ECHO);
  tcsetattr(STDIN_FILENO, TCSANOW, &new_termios);
  fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK);
}

void restore_terminal(void) {
  tcsetattr(STDIN_FILENO, TCSANOW, &g_old_termios);
}

int get_key(void) {
  char c;
  if (read(STDIN_FILENO, &c, 1) == 1)
    return c;
  return -1;
}
#endif

// Keyboard to MIDI mapping
int key_to_note(int key) {
  // Lower row: Z-M = C3-B3
  // Upper row: Q-U = C4-B4
  switch (key) {
  case 'z':
    return 48; // C3
  case 's':
    return 49; // C#3
  case 'x':
    return 50; // D3
  case 'd':
    return 51; // D#3
  case 'c':
    return 52; // E3
  case 'v':
    return 53; // F3
  case 'g':
    return 54; // F#3
  case 'b':
    return 55; // G3
  case 'h':
    return 56; // G#3
  case 'n':
    return 57; // A3
  case 'j':
    return 58; // A#3
  case 'm':
    return 59; // B3

  case 'q':
    return 60; // C4 (Middle C)
  case '2':
    return 61; // C#4
  case 'w':
    return 62; // D4
  case '3':
    return 63; // D#4
  case 'e':
    return 64; // E4
  case 'r':
    return 65; // F4
  case '5':
    return 66; // F#4
  case 't':
    return 67; // G4
  case '6':
    return 68; // G#4
  case 'y':
    return 69; // A4 (440Hz)
  case '7':
    return 70; // A#4
  case 'u':
    return 71; // B4
  case 'i':
    return 72; // C5

  default:
    return -1;
  }
}

void print_keyboard_layout(void) {
  printf("\n");
  printf("╔══════════════════════════════════════════════════════════════╗\n");
  printf(
      "║                    INTUITIVES KEYBOARD                         ║\n");
  printf("╠══════════════════════════════════════════════════════════════╣\n");
  printf("║  2   3       5   6   7                                        ║\n");
  printf("║ C#  D#      F#  G#  A#                                        ║\n");
  printf("║ Q   W   E   R   T   Y   U   I     ← Upper Row (C4-C5)        ║\n");
  printf("║ C   D   E   F   G   A   B   C                                 ║\n");
  printf("╠══════════════════════════════════════════════════════════════╣\n");
  printf("║  S   D       G   H   J                                        ║\n");
  printf("║ C#  D#      F#  G#  A#                                        ║\n");
  printf("║ Z   X   C   V   B   N   M        ← Lower Row (C3-B3)         ║\n");
  printf("║ C   D   E   F   G   A   B                                     ║\n");
  printf("╠══════════════════════════════════════════════════════════════╣\n");
  printf("║  [1-4] Waveform  [+/-] Octave  [,/.] Filter  [ESC] Quit      ║\n");
  printf(
      "╚══════════════════════════════════════════════════════════════╝\n\n");
}

int main(int argc, char *argv[]) {
  (void)argc;
  (void)argv;

  printf("\n");
  printf("╔══════════════════════════════════════════════════════════════╗\n");
  printf(
      "║           INTUITIVES Standalone Synthesizer                    ║\n");
  printf("║              Native C17 Audio Engine                          ║\n");
  printf(
      "╚══════════════════════════════════════════════════════════════╝\n\n");

  // Print version info
  IntuitivesInfo info;
  intuitives_get_info(&info);
  printf("Version: %s | Platform: %s | SIMD: %s\n", intuitives_version_string(),
         info.platform, info.simd_enabled ? "YES" : "NO");
  printf("Features: %zu implemented\n\n", info.num_features);

  // Initialize audio engine
  uint32_t sample_rate = 48000;

  g_engine = (AudioEngine *)calloc(1, sizeof(AudioEngine));
  EngineConfig config = {.sample_rate = sample_rate,
                         .buffer_size = 256,
                         .channels = 2,
                         .bit_depth = 32,
                         .realtime_priority = true,
                         .simd_enabled = true};

  if (engine_init(g_engine, &config) != INTUITIVES_OK) {
    fprintf(stderr, "❌ Failed to initialize engine\n");
    return 1;
  }

  // Initialize synth
  g_synth = (BasicSynth *)calloc(1, sizeof(BasicSynth));
  synth_init(g_synth, sample_rate);

  // Configure synth defaults
  g_synth->osc1.waveform_a = WAVE_SAW;
  g_synth->osc1.waveform_b = WAVE_SQUARE;
  g_synth->osc1_level = 0.6f;
  g_synth->osc2_level = 0.3f;
  svf_set_cutoff(&g_synth->filter, 2000.0f);
  svf_set_resonance(&g_synth->filter, 0.5f);

  printf("✓ Audio engine initialized\n");

  // Initialize miniaudio device
  ma_device_config device_config =
      ma_device_config_init(ma_device_type_playback);
  device_config.playback.format = ma_format_f32;
  device_config.playback.channels = 2;
  device_config.sampleRate = sample_rate;
  device_config.dataCallback = audio_callback;
  device_config.pUserData = NULL;

  if (ma_device_init(NULL, &device_config, &g_device) != MA_SUCCESS) {
    fprintf(stderr, "❌ Failed to initialize audio device\n");
    return 1;
  }

  printf("✓ Audio device: %s\n", g_device.playback.name);
  printf("✓ Sample rate: %u Hz\n", g_device.sampleRate);

  if (ma_device_start(&g_device) != MA_SUCCESS) {
    fprintf(stderr, "❌ Failed to start audio device\n");
    ma_device_uninit(&g_device);
    return 1;
  }

  printf("✓ Audio stream started\n\n");

  // Setup signal handler
  signal(SIGINT, signal_handler);

// Setup terminal for non-blocking input
#ifndef _WIN32
  setup_terminal();
#endif

  print_keyboard_layout();

  // State
  int octave_offset = 0;
  float filter_cutoff = 2000.0f;
  int current_waveform = 1; // SAW
  int current_note = -1;

  printf("🎹 Ready! Press keys to play...\n\n");

  // Main loop
  while (g_running) {
    int key = get_key();

    if (key != -1) {
      // ESC or 'q' to quit (but 'q' is C4, so use ESC)
      if (key == 27) {
        g_running = false;
        break;
      }

      // Waveform selection
      if (key == '1') {
        current_waveform = WAVE_SINE;
        g_synth->osc1.waveform_a = WAVE_SINE;
        printf("\r🔊 Waveform: SINE     \n");
      } else if (key == '2' && key_to_note(key) < 0) {
        // '2' is also a note, skip if it's a note
      } else if (key == '!') { // Shift+1
        current_waveform = WAVE_SAW;
        g_synth->osc1.waveform_a = WAVE_SAW;
        printf("\r🔊 Waveform: SAW      \n");
      } else if (key == '@') { // Shift+2
        current_waveform = WAVE_SQUARE;
        g_synth->osc1.waveform_a = WAVE_SQUARE;
        printf("\r🔊 Waveform: SQUARE   \n");
      } else if (key == '#') { // Shift+3
        current_waveform = WAVE_TRIANGLE;
        g_synth->osc1.waveform_a = WAVE_TRIANGLE;
        printf("\r🔊 Waveform: TRIANGLE \n");
      }

      // Octave shift
      else if (key == '+' || key == '=') {
        octave_offset += 12;
        if (octave_offset > 24)
          octave_offset = 24;
        printf("\r🎹 Octave: +%d        \n", octave_offset / 12);
      } else if (key == '-' || key == '_') {
        octave_offset -= 12;
        if (octave_offset < -24)
          octave_offset = -24;
        printf("\r🎹 Octave: %d         \n", octave_offset / 12);
      }

      // Filter
      else if (key == '.' || key == '>') {
        filter_cutoff *= 1.2f;
        if (filter_cutoff > 16000.0f)
          filter_cutoff = 16000.0f;
        svf_set_cutoff(&g_synth->filter, filter_cutoff);
        printf("\r🎛️  Filter: %.0f Hz    \n", filter_cutoff);
      } else if (key == ',' || key == '<') {
        filter_cutoff /= 1.2f;
        if (filter_cutoff < 100.0f)
          filter_cutoff = 100.0f;
        svf_set_cutoff(&g_synth->filter, filter_cutoff);
        printf("\r🎛️  Filter: %.0f Hz    \n", filter_cutoff);
      }

      // Note input
      else {
        int note = key_to_note(key);
        if (note >= 0) {
          note += octave_offset;
          if (current_note != note) {
            synth_note_on(g_synth, note, 0.8f);
            current_note = note;

            // Get note color
            SynesthesiaColor color;
            chroma_note_to_color(note, &color);
            printf("\r🎵 Note: %d (freq: %.1f Hz) 🎨 #%02X%02X%02X\n", note,
                   INTUITIVES_MIDI_TO_FREQ((float)note), color.r, color.g,
                   color.b);
          }
        }
      }
    } else {
      // No key pressed - release note
      if (current_note >= 0) {
        synth_note_off(g_synth);
        current_note = -1;
      }
    }

// Small sleep to avoid CPU spinning
#ifdef _WIN32
    Sleep(1);
#else
    usleep(1000);
#endif
  }

// Cleanup
#ifndef _WIN32
  restore_terminal();
#endif

  printf("\n🧹 Cleaning up...\n");

  ma_device_uninit(&g_device);
  engine_free(g_engine);
  free(g_engine);
  free(g_synth);

  printf("✅ Goodbye!\n\n");

  return 0;
}
