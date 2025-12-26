/**
 * INTUITIVES DAW - Dear ImGui GUI Implementation
 *
 * Native C++ GUI using Dear ImGui for the Intuitives DAW.
 * Provides a complete visual interface with:
 * - Sequencer view with piano roll
 * - Mixer with channel strips
 * - Generator panel (Markov, Genetic, Cellular)
 * - Chromasynesthesia visualizer
 * - Transport controls
 *
 * Build with INTUITIVES_DAW_BUILD_GUI=ON in CMake.
 */

#ifndef INTUITIVES_GUI_H
#define INTUITIVES_GUI_H

#ifdef __cplusplus
extern "C" {
#endif

#include "../intuitives_daw.h"

// ============================================================================
// GUI THEME - Intuitives Neobrutalist Style
// ============================================================================

typedef struct {
  float primary[4];    // Main accent color (Chromasynesthesia-based)
  float secondary[4];  // Secondary accent
  float background[4]; // Dark background
  float surface[4];    // Slightly lighter surface
  float text[4];       // Primary text
  float text_dim[4];   // Dimmed text
  float success[4];    // Success/positive
  float warning[4];    // Warning
  float error[4];      // Error/stop
  float meter_low[4];  // Level meter low
  float meter_mid[4];  // Level meter mid
  float meter_high[4]; // Level meter high/clip
} IntuitivesTheme;

// Default theme
static const IntuitivesTheme THEME_DARK = {
    .primary = {0.40f, 0.80f, 0.95f, 1.0f},    // Cyan accent
    .secondary = {0.95f, 0.40f, 0.70f, 1.0f},  // Pink accent
    .background = {0.08f, 0.08f, 0.10f, 1.0f}, // Near black
    .surface = {0.12f, 0.12f, 0.15f, 1.0f},    // Dark gray
    .text = {0.95f, 0.95f, 0.95f, 1.0f},       // Near white
    .text_dim = {0.60f, 0.60f, 0.65f, 1.0f},   // Gray text
    .success = {0.30f, 0.85f, 0.45f, 1.0f},    // Green
    .warning = {0.95f, 0.75f, 0.20f, 1.0f},    // Yellow
    .error = {0.95f, 0.25f, 0.30f, 1.0f},      // Red
    .meter_low = {0.20f, 0.80f, 0.40f, 1.0f},  // Green
    .meter_mid = {0.85f, 0.75f, 0.20f, 1.0f},  // Yellow
    .meter_high = {0.95f, 0.25f, 0.30f, 1.0f}, // Red
};

// ============================================================================
// GUI STATE
// ============================================================================

typedef struct {
  // Window visibility
  bool show_sequencer;
  bool show_pattern_editor;
  bool show_mixer;
  bool show_generator_panel;
  bool show_visualizer;
  bool show_settings;
  bool show_about;
  bool show_synth_rack;
  bool show_lsystem_generator;

  // Editor state
  int selected_track;
  int selected_pattern;
  int selected_note;

  // Piano roll state
  float piano_roll_scroll_x;
  float piano_roll_scroll_y;
  float piano_roll_zoom;

  // Generator panel state
  int generator_type; // 0=Markov, 1=Genetic, 2=Cellular, 3=Text
  float generator_temperature;
  int generator_num_notes;
  int generator_generations;
  int cellular_rule;
  float cellular_density;
  char text_input[256];

  // Color picker
  float color_picker[3];

  // Theme
  IntuitivesTheme theme;

  // Performance
  float fps;
  float audio_cpu_percent;

} GuiState;

// ============================================================================
// GUI LIFECYCLE
// ============================================================================

/**
 * Initialize the GUI system.
 * Call after creating the DawApp but before main loop.
 */
bool gui_init(DawApp *app);

/**
 * Shutdown the GUI system.
 * Call before destroying the DawApp.
 */
void gui_shutdown(DawApp *app);

/**
 * Begin a new frame.
 * Call at the start of each render loop iteration.
 */
void gui_begin_frame(DawApp *app);

/**
 * End frame and render.
 * Call at the end of each render loop iteration.
 */
void gui_end_frame(DawApp *app);

/**
 * Check if GUI wants to close.
 */
bool gui_should_close(DawApp *app);

// ============================================================================
// GUI WINDOWS
// ============================================================================

/**
 * Draw the main menu bar.
 */
void gui_draw_menu_bar(DawApp *app, GuiState *state);

/**
 * Draw transport controls (play/pause/stop, BPM, time display).
 */
void gui_draw_transport(DawApp *app, GuiState *state);

/**
 * Draw the sequencer/arrangement view.
 */
void gui_draw_sequencer(DawApp *app, GuiState *state);

/**
 * Draw the pattern/piano roll editor.
 */
void gui_draw_pattern_editor(DawApp *app, GuiState *state);

/**
 * Draw the mixer with channel strips.
 */
void gui_draw_mixer(DawApp *app, GuiState *state);

/**
 * Draw the generator panel (AI/procedural tools).
 */
void gui_draw_generator_panel(DawApp *app, GuiState *state);

/**
 * Draw chromasynesthesia visualizer.
 */
void gui_draw_visualizer(DawApp *app, GuiState *state);

/**
 * Draw settings window.
 */
void gui_draw_settings(DawApp *app, GuiState *state);

/**
 * Draw about window.
 */
void gui_draw_about(DawApp *app, GuiState *state);

/**
 * Draw synth rack / effect chain editor.
 */
void gui_draw_synth_rack(DawApp *app, GuiState *state);

/**
 * Draw detailed effect parameter editor.
 */
void gui_draw_effect_editor(DawApp *app, GuiState *state, int effect_index);

/**
 * Draw 3D audio-reactive visualizer.
 */
void gui_draw_visualizer_3d(DawApp *app, GuiState *state);

// ============================================================================
// GUI WIDGETS
// ============================================================================

/**
 * Draw a knob control.
 * Returns true if value changed.
 */
bool gui_knob(const char *label, float *value, float min, float max,
              const float *color);

/**
 * Draw a vertical fader/slider.
 * Returns true if value changed.
 */
bool gui_fader(const char *label, float *value, float min, float max,
               float height);

/**
 * Draw a level meter.
 */
void gui_level_meter(float level, float width, float height,
                     const IntuitivesTheme *theme);

/**
 * Draw a stereo level meter pair.
 */
void gui_stereo_meter(float left, float right, float width, float height,
                      const IntuitivesTheme *theme);

/**
 * Draw a spectrum analyzer.
 */
void gui_spectrum(float *bands, int num_bands, float width, float height,
                  const float *color);

/**
 * Draw a waveform display.
 */
void gui_waveform(float *samples, int num_samples, float width, float height,
                  const float *color);

/**
 * Draw a piano roll grid cell.
 */
void gui_piano_cell(int note, float beat, float duration, float velocity,
                    uint32_t color, bool selected);

/**
 * Draw a mute/solo button pair.
 */
void gui_mute_solo(bool *mute, bool *solo, const IntuitivesTheme *theme);

// ============================================================================
// UTILITY
// ============================================================================

/**
 * Apply the Intuitives theme to Dear ImGui.
 */
void gui_apply_theme(const IntuitivesTheme *theme);

/**
 * Convert chromasynesthesia color to ImVec4.
 */
void gui_chroma_to_color(const SynesthesiaColor *chroma, float *out_rgba);

/**
 * Get color for a MIDI note (chromasynesthesia).
 */
void gui_note_color(int note, float *out_rgba);

#ifdef __cplusplus
}
#endif

#endif // INTUITIVES_GUI_H
