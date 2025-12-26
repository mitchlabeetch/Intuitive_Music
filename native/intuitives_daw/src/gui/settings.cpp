/**
 * INTUITIVES DAW - Settings Panel
 *
 * Audio device selection, buffer size, theme customization.
 * Uses Dear ImGui for immediate-mode rendering.
 */

#include "../../include/gui/intuitives_gui.h"

#ifdef INTUITIVES_DAW_GUI

#include "imgui.h"
#include <stdio.h>
#include <string.h>

// ============================================================================
// SETTINGS STATE
// ============================================================================

typedef struct {
  // Audio settings
  int audio_device_index;
  int sample_rate_index;
  int buffer_size_index;

  // Theme settings
  int theme_preset;
  float accent_color[3];

  // MIDI settings
  int midi_input_index;
  int midi_output_index;

  // UI settings
  bool show_tooltips;
  bool animate_meters;
  float ui_scale;

  // Performance
  bool low_latency_mode;
  bool gpu_acceleration;

  // Dirty flag
  bool needs_apply;
} SettingsState;

static SettingsState g_settings = {
    .audio_device_index = 0,
    .sample_rate_index = 2, // 48000
    .buffer_size_index = 2, // 256
    .theme_preset = 0,
    .accent_color = {0.4f, 0.8f, 0.95f},
    .midi_input_index = -1,
    .midi_output_index = -1,
    .show_tooltips = true,
    .animate_meters = true,
    .ui_scale = 1.0f,
    .low_latency_mode = false,
    .gpu_acceleration = true,
    .needs_apply = false,
};

// Sample rate options
static const int SAMPLE_RATES[] = {22050, 44100, 48000, 88200, 96000, 192000};
static const char *SAMPLE_RATE_NAMES[] = {"22050 Hz", "44100 Hz", "48000 Hz",
                                          "88200 Hz", "96000 Hz", "192000 Hz"};
static const int NUM_SAMPLE_RATES = 6;

// Buffer size options
static const int BUFFER_SIZES[] = {64, 128, 256, 512, 1024, 2048};
static const char *BUFFER_SIZE_NAMES[] = {"64 (1.3ms)",    "128 (2.7ms)",
                                          "256 (5.3ms)",   "512 (10.7ms)",
                                          "1024 (21.3ms)", "2048 (42.7ms)"};
static const int NUM_BUFFER_SIZES = 6;

// Theme presets
static const char *THEME_PRESETS[] = {"Dark (Default)", "Midnight Blue",
                                      "Purple Haze", "Matrix Green", "Custom"};
static const int NUM_THEME_PRESETS = 5;

// ============================================================================
// SETTINGS WINDOW
// ============================================================================

void gui_draw_settings(DawApp *app, GuiState *state) {
  if (!state->show_settings)
    return;

  ImGui::SetNextWindowPos(ImVec2(200, 150), ImGuiCond_FirstUseEver);
  ImGui::SetNextWindowSize(ImVec2(500, 450), ImGuiCond_FirstUseEver);

  if (!ImGui::Begin("Settings", &state->show_settings,
                    ImGuiWindowFlags_NoCollapse)) {
    ImGui::End();
    return;
  }

  // Tab bar for settings categories
  if (ImGui::BeginTabBar("SettingsTabs")) {

    // ====================================================================
    // AUDIO TAB
    // ====================================================================
    if (ImGui::BeginTabItem("Audio")) {
      ImGui::Text("Audio Configuration");
      ImGui::Separator();

      // Current audio info
      ImGui::TextColored(ImVec4(0.7f, 0.7f, 0.7f, 1.0f),
                         "Current: %d Hz, %d samples buffer", app->sample_rate,
                         app->buffer_size);

      ImGui::Spacing();

      // Audio device (simulated list)
      static const char *audio_devices[] = {"Default System Output",
                                            "Built-in Output", "External DAC",
                                            "Virtual Audio Device"};
      ImGui::SetNextItemWidth(300);
      if (ImGui::Combo("Output Device", &g_settings.audio_device_index,
                       audio_devices, 4)) {
        g_settings.needs_apply = true;
      }

      ImGui::Spacing();

      // Sample rate
      ImGui::SetNextItemWidth(200);
      if (ImGui::Combo("Sample Rate", &g_settings.sample_rate_index,
                       SAMPLE_RATE_NAMES, NUM_SAMPLE_RATES)) {
        g_settings.needs_apply = true;
      }

      // Buffer size
      ImGui::SetNextItemWidth(200);
      if (ImGui::Combo("Buffer Size", &g_settings.buffer_size_index,
                       BUFFER_SIZE_NAMES, NUM_BUFFER_SIZES)) {
        g_settings.needs_apply = true;
      }

      // Calculate latency
      int sr = SAMPLE_RATES[g_settings.sample_rate_index];
      int bs = BUFFER_SIZES[g_settings.buffer_size_index];
      float latency_ms = (float)bs / sr * 1000.0f;
      ImGui::TextColored(ImVec4(0.5f, 0.8f, 0.5f, 1.0f),
                         "Estimated latency: %.1f ms", latency_ms);

      ImGui::Spacing();
      ImGui::Separator();

      // Advanced options
      if (ImGui::CollapsingHeader("Advanced")) {
        ImGui::Checkbox("Low Latency Mode", &g_settings.low_latency_mode);
        if (g_settings.low_latency_mode) {
          ImGui::TextColored(ImVec4(1.0f, 0.7f, 0.3f, 1.0f),
                             "⚠ May increase CPU usage");
        }

        ImGui::Checkbox("GPU Acceleration", &g_settings.gpu_acceleration);
      }

      ImGui::EndTabItem();
    }

    // ====================================================================
    // MIDI TAB
    // ====================================================================
    if (ImGui::BeginTabItem("MIDI")) {
      ImGui::Text("MIDI Configuration");
      ImGui::Separator();

      // MIDI Input
      static const char *midi_inputs[] = {"None", "USB MIDI Controller",
                                          "Virtual MIDI Port", "Network MIDI"};
      ImGui::SetNextItemWidth(250);
      if (ImGui::Combo("MIDI Input", &g_settings.midi_input_index, midi_inputs,
                       4)) {
        printf("Selected MIDI input: %d\n", g_settings.midi_input_index);
      }

      // MIDI Output
      static const char *midi_outputs[] = {
          "None", "IAC Driver Bus 1", "External Synth", "Virtual Instrument"};
      ImGui::SetNextItemWidth(250);
      ImGui::Combo("MIDI Output", &g_settings.midi_output_index, midi_outputs,
                   4);

      ImGui::Spacing();
      ImGui::Separator();

      // MIDI Learn
      ImGui::Text("MIDI Learn");
      if (ImGui::Button("Start MIDI Learn")) {
        printf("MIDI Learn started\n");
      }
      ImGui::SameLine();
      if (ImGui::Button("Clear All Mappings")) {
        printf("MIDI mappings cleared\n");
      }

      ImGui::Spacing();

      // MIDI activity indicator
      ImGui::Text("MIDI Activity:");
      ImGui::SameLine();
      ImGui::TextColored(ImVec4(0.3f, 0.3f, 0.3f, 1.0f), "●"); // No activity

      ImGui::EndTabItem();
    }

    // ====================================================================
    // APPEARANCE TAB
    // ====================================================================
    if (ImGui::BeginTabItem("Appearance")) {
      ImGui::Text("Theme & Appearance");
      ImGui::Separator();

      // Theme preset
      ImGui::SetNextItemWidth(200);
      if (ImGui::Combo("Theme", &g_settings.theme_preset, THEME_PRESETS,
                       NUM_THEME_PRESETS)) {
        // Apply preset colors
        switch (g_settings.theme_preset) {
        case 0: // Dark
          g_settings.accent_color[0] = 0.4f;
          g_settings.accent_color[1] = 0.8f;
          g_settings.accent_color[2] = 0.95f;
          break;
        case 1: // Midnight Blue
          g_settings.accent_color[0] = 0.2f;
          g_settings.accent_color[1] = 0.4f;
          g_settings.accent_color[2] = 0.9f;
          break;
        case 2: // Purple Haze
          g_settings.accent_color[0] = 0.7f;
          g_settings.accent_color[1] = 0.3f;
          g_settings.accent_color[2] = 0.9f;
          break;
        case 3: // Matrix Green
          g_settings.accent_color[0] = 0.2f;
          g_settings.accent_color[1] = 0.9f;
          g_settings.accent_color[2] = 0.3f;
          break;
        default:
          break;
        }
        g_settings.needs_apply = true;
      }

      ImGui::Spacing();

      // Custom accent color
      if (ImGui::ColorEdit3("Accent Color", g_settings.accent_color)) {
        g_settings.theme_preset = 4; // Custom
        g_settings.needs_apply = true;
      }

      // Preview
      ImGui::Text("Preview:");
      ImDrawList *draw_list = ImGui::GetWindowDrawList();
      ImVec2 pos = ImGui::GetCursorScreenPos();
      ImU32 accent = IM_COL32(g_settings.accent_color[0] * 255,
                              g_settings.accent_color[1] * 255,
                              g_settings.accent_color[2] * 255, 255);
      draw_list->AddRectFilled(pos, ImVec2(pos.x + 100, pos.y + 20), accent);
      ImGui::Dummy(ImVec2(100, 25));

      ImGui::Spacing();
      ImGui::Separator();

      // UI Scale
      ImGui::SetNextItemWidth(150);
      if (ImGui::SliderFloat("UI Scale", &g_settings.ui_scale, 0.75f, 2.0f,
                             "%.2fx")) {
        // Would apply: ImGui::GetIO().FontGlobalScale = g_settings.ui_scale;
      }

      // Animation toggles
      ImGui::Checkbox("Show Tooltips", &g_settings.show_tooltips);
      ImGui::Checkbox("Animate Meters", &g_settings.animate_meters);

      ImGui::EndTabItem();
    }

    // ====================================================================
    // ABOUT TAB
    // ====================================================================
    if (ImGui::BeginTabItem("About")) {
      ImGui::Text("INTUITIVES DAW");
      ImGui::TextColored(ImVec4(0.6f, 0.6f, 0.6f, 1.0f), "Version %d.%d.%d",
                         INTUITIVES_DAW_VERSION_MAJOR,
                         INTUITIVES_DAW_VERSION_MINOR,
                         INTUITIVES_DAW_VERSION_PATCH);

      ImGui::Spacing();
      ImGui::Separator();

      ImGui::TextWrapped(
          "\"Does this sound cool?\" - The only rule.\n\n"
          "Intuitives is an experimental, rule-free digital audio "
          "workstation that prioritizes intuition, randomness, and "
          "AI-assisted discovery over traditional music theory constraints.");

      ImGui::Spacing();
      ImGui::Separator();

      ImGui::Text("Features:");
      ImGui::BulletText("40 Original DSP Effects");
      ImGui::BulletText("Markov/Genetic/Cellular Generators");
      ImGui::BulletText("Text-to-Melody, Color-to-Harmony");
      ImGui::BulletText("Chromasynesthesia Visualization");
      ImGui::BulletText("L-System Generative Patterns");

      ImGui::Spacing();
      ImGui::Separator();

      // System info
      ImGui::Text("System Information:");
      ImGui::TextColored(ImVec4(0.6f, 0.6f, 0.6f, 1.0f),
                         "Audio: %d Hz, %d buffer", app->sample_rate,
                         app->buffer_size);
      ImGui::TextColored(ImVec4(0.6f, 0.6f, 0.6f, 1.0f),
                         "Tracks: %d, Patterns: %d", app->project.num_tracks,
                         app->project.num_patterns);

      ImGui::EndTabItem();
    }

    ImGui::EndTabBar();
  }

  // Apply/Cancel buttons
  ImGui::Separator();

  if (g_settings.needs_apply) {
    ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0.3f, 0.6f, 0.3f, 1.0f));
    if (ImGui::Button("Apply Changes", ImVec2(120, 30))) {
      // Apply audio settings
      // In real implementation: reinitialize audio with new settings
      printf("Applying settings: SR=%d, Buffer=%d\n",
             SAMPLE_RATES[g_settings.sample_rate_index],
             BUFFER_SIZES[g_settings.buffer_size_index]);

      // Update theme
      state->theme.primary[0] = g_settings.accent_color[0];
      state->theme.primary[1] = g_settings.accent_color[1];
      state->theme.primary[2] = g_settings.accent_color[2];
      state->theme.primary[3] = 1.0f;
      gui_apply_theme(&state->theme);

      g_settings.needs_apply = false;
    }
    ImGui::PopStyleColor();

    ImGui::SameLine();
    if (ImGui::Button("Cancel", ImVec2(80, 30))) {
      g_settings.needs_apply = false;
      state->show_settings = false;
    }
  } else {
    if (ImGui::Button("Close", ImVec2(80, 30))) {
      state->show_settings = false;
    }
  }

  ImGui::End();
}

#endif // INTUITIVES_DAW_GUI
