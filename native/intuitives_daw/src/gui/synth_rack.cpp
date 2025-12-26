/**
 * INTUITIVES DAW - Synth Rack (Effect Chain Editor)
 *
 * Visual effect chain editor with drag-and-drop reordering.
 * Uses Dear ImGui for immediate-mode rendering.
 */

#include "../../include/gui/intuitives_gui.h"

#ifdef INTUITIVES_DAW_GUI

#include "imgui.h"
#include <stdio.h>
#include <string.h>

// ============================================================================
// EFFECT TYPES
// ============================================================================

typedef enum {
  EFFECT_GAIN = 0,
  EFFECT_EQ,
  EFFECT_COMPRESSOR,
  EFFECT_REVERB,
  EFFECT_DELAY,
  EFFECT_DISTORTION,
  EFFECT_CHORUS,
  EFFECT_PHASER,
  EFFECT_FILTER,
  EFFECT_LIMITER,
  EFFECT_COUNT
} EffectType;

static const char *EFFECT_NAMES[] = {
    "Gain",       "EQ",     "Compressor", "Reverb", "Delay",
    "Distortion", "Chorus", "Phaser",     "Filter", "Limiter",
};

static const char *EFFECT_ICONS[] = {
    "🔊", "📊", "🗜️", "🌊", "⏱️", "🔥", "🎵", "🌀", "🎚️", "🛑",
};

// Effect parameter ranges
typedef struct {
  const char *name;
  float min;
  float max;
  float default_val;
} EffectParam;

// ============================================================================
// SYNTH RACK STATE
// ============================================================================

typedef struct {
  int dragging_effect; // Index of effect being dragged (-1 if none)
  int drag_target;     // Drop target index
  bool show_add_menu;  // Show effect add popup
  int selected_effect; // Currently selected effect for editing
  float rack_scroll;   // Scroll position
} SynthRackState;

static SynthRackState g_rack_state = {-1, -1, false, -1, 0};

// ============================================================================
// SYNTH RACK DRAWING
// ============================================================================

void gui_draw_synth_rack(DawApp *app, GuiState *state) {
  if (!state->show_synth_rack)
    return;

  ImGui::SetNextWindowPos(ImVec2(50, 100), ImGuiCond_FirstUseEver);
  ImGui::SetNextWindowSize(ImVec2(350, 500), ImGuiCond_FirstUseEver);

  if (!ImGui::Begin("Synth Rack", &state->show_synth_rack)) {
    ImGui::End();
    return;
  }

  // Track selector
  if (app->project.num_tracks > 0) {
    DawTrack *track = &app->project.tracks[state->selected_track];

    // Track dropdown
    if (ImGui::BeginCombo("Track", track->name)) {
      for (uint32_t i = 0; i < app->project.num_tracks; i++) {
        bool is_selected = ((int)i == state->selected_track);
        if (ImGui::Selectable(app->project.tracks[i].name, is_selected)) {
          state->selected_track = (int)i;
        }
        if (is_selected) {
          ImGui::SetItemDefaultFocus();
        }
      }
      ImGui::EndCombo();
    }

    ImGui::Separator();

    // Effect chain header
    ImGui::Text("Effect Chain");
    ImGui::SameLine(ImGui::GetWindowWidth() - 80);
    if (ImGui::Button("+ Add")) {
      g_rack_state.show_add_menu = true;
      ImGui::OpenPopup("AddEffect");
    }

    // Add effect popup
    if (ImGui::BeginPopup("AddEffect")) {
      ImGui::Text("Add Effect");
      ImGui::Separator();
      for (int i = 0; i < EFFECT_COUNT; i++) {
        char label[64];
        snprintf(label, 64, "%s %s", EFFECT_ICONS[i], EFFECT_NAMES[i]);
        if (ImGui::MenuItem(label)) {
          // Add effect to chain
          // In real implementation, would call effect_chain_add()
          printf("Added effect: %s\n", EFFECT_NAMES[i]);
        }
      }
      ImGui::EndPopup();
    }

    // Effect chain list
    ImGui::BeginChild("EffectList", ImVec2(0, -50), true);

    EffectChain *chain = &track->effects;

    if (chain->count == 0) {
      ImGui::TextDisabled("No effects. Click '+ Add' to add one.");
    }

    for (uint32_t i = 0; i < chain->count && i < MAX_EFFECTS; i++) {
      ImGui::PushID(i);

      // Effect slot
      ImVec2 effect_size = ImVec2(ImGui::GetContentRegionAvail().x, 80);

      // Determine if this is a drag target
      bool is_drag_target = (g_rack_state.dragging_effect >= 0 &&
                             g_rack_state.drag_target == (int)i);

      // Effect background color
      ImVec4 bg_color = is_drag_target ? ImVec4(0.3f, 0.5f, 0.7f, 0.5f)
                                       : ImVec4(0.15f, 0.15f, 0.18f, 1.0f);

      if (g_rack_state.selected_effect == (int)i) {
        bg_color = ImVec4(0.25f, 0.25f, 0.3f, 1.0f);
      }

      ImGui::PushStyleColor(ImGuiCol_ChildBg, bg_color);
      ImGui::BeginChild("EffectSlot", effect_size, true);

      // Effect header with bypass toggle
      bool bypassed = chain->bypassed[i];
      ImGui::PushStyleColor(ImGuiCol_Button,
                            bypassed ? ImVec4(0.5f, 0.3f, 0.3f, 1.0f)
                                     : state->theme.success);
      if (ImGui::Button(bypassed ? "OFF" : "ON", ImVec2(40, 20))) {
        chain->bypassed[i] = !chain->bypassed[i];
      }
      ImGui::PopStyleColor();

      ImGui::SameLine();
      ImGui::Text("%s", EFFECT_NAMES[chain->types[i]]);

      ImGui::SameLine(ImGui::GetWindowWidth() - 60);

      // Remove button
      ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0.6f, 0.2f, 0.2f, 1.0f));
      if (ImGui::Button("X", ImVec2(20, 20))) {
        // Remove effect
        printf("Remove effect %d\n", i);
      }
      ImGui::PopStyleColor();

      // Effect parameters (simplified)
      ImGui::SetNextItemWidth(ImGui::GetContentRegionAvail().x - 10);

      // Example: Mix parameter
      float mix = chain->params[i][0];
      if (ImGui::SliderFloat("Mix", &mix, 0.0f, 1.0f, "%.2f")) {
        chain->params[i][0] = mix;
      }

      ImGui::EndChild();
      ImGui::PopStyleColor();

      // Drag source
      if (ImGui::BeginDragDropSource(ImGuiDragDropFlags_None)) {
        ImGui::SetDragDropPayload("EFFECT_DND", &i, sizeof(int));
        ImGui::Text("Move %s", EFFECT_NAMES[chain->types[i]]);
        g_rack_state.dragging_effect = i;
        ImGui::EndDragDropSource();
      }

      // Drop target
      if (ImGui::BeginDragDropTarget()) {
        g_rack_state.drag_target = i;
        if (const ImGuiPayload *payload =
                ImGui::AcceptDragDropPayload("EFFECT_DND")) {
          int source_idx = *(const int *)payload->Data;
          if (source_idx != (int)i) {
            // Swap effects
            printf("Move effect from %d to %d\n", source_idx, i);
            // In real implementation: effect_chain_swap(chain, source_idx, i);
          }
        }
        ImGui::EndDragDropTarget();
      } else if (g_rack_state.drag_target == (int)i) {
        g_rack_state.drag_target = -1;
      }

      ImGui::PopID();
      ImGui::Spacing();
    }

    // Reset drag state when not dragging
    if (!ImGui::IsMouseDown(0)) {
      g_rack_state.dragging_effect = -1;
      g_rack_state.drag_target = -1;
    }

    ImGui::EndChild();

    // Master bypass
    ImGui::Separator();
    bool chain_bypass = chain->master_bypass;
    if (ImGui::Checkbox("Bypass All", &chain_bypass)) {
      chain->master_bypass = chain_bypass;
    }

    ImGui::SameLine(ImGui::GetWindowWidth() - 100);
    if (ImGui::Button("Clear All")) {
      chain->count = 0;
    }

  } else {
    ImGui::TextDisabled("No tracks available");
  }

  ImGui::End();
}

// ============================================================================
// EFFECT EDITOR DETAIL PANEL
// ============================================================================

void gui_draw_effect_editor(DawApp *app, GuiState *state, int effect_index) {
  if (effect_index < 0 || app->project.num_tracks == 0)
    return;

  DawTrack *track = &app->project.tracks[state->selected_track];
  EffectChain *chain = &track->effects;

  if ((uint32_t)effect_index >= chain->count)
    return;

  EffectType type = (EffectType)chain->types[effect_index];

  ImGui::SetNextWindowPos(ImVec2(410, 100), ImGuiCond_FirstUseEver);
  ImGui::SetNextWindowSize(ImVec2(300, 350), ImGuiCond_FirstUseEver);

  char window_title[64];
  snprintf(window_title, 64, "%s %s###EffectEditor", EFFECT_ICONS[type],
           EFFECT_NAMES[type]);

  if (!ImGui::Begin(window_title)) {
    ImGui::End();
    return;
  }

  float *params = chain->params[effect_index];

  // Effect-specific parameters
  switch (type) {
  case EFFECT_GAIN:
    ImGui::SliderFloat("Gain", &params[0], 0.0f, 2.0f, "%.2f");
    break;

  case EFFECT_EQ:
    ImGui::Text("3-Band EQ");
    ImGui::SliderFloat("Low", &params[0], -12.0f, 12.0f, "%.1f dB");
    ImGui::SliderFloat("Mid", &params[1], -12.0f, 12.0f, "%.1f dB");
    ImGui::SliderFloat("High", &params[2], -12.0f, 12.0f, "%.1f dB");
    ImGui::SliderFloat("Low Freq", &params[3], 80.0f, 500.0f, "%.0f Hz");
    ImGui::SliderFloat("High Freq", &params[4], 2000.0f, 8000.0f, "%.0f Hz");
    break;

  case EFFECT_COMPRESSOR:
    ImGui::SliderFloat("Threshold", &params[0], -60.0f, 0.0f, "%.1f dB");
    ImGui::SliderFloat("Ratio", &params[1], 1.0f, 20.0f, "%.1f:1");
    ImGui::SliderFloat("Attack", &params[2], 0.1f, 100.0f, "%.1f ms");
    ImGui::SliderFloat("Release", &params[3], 10.0f, 1000.0f, "%.0f ms");
    ImGui::SliderFloat("Makeup", &params[4], 0.0f, 24.0f, "%.1f dB");
    break;

  case EFFECT_REVERB:
    ImGui::SliderFloat("Room Size", &params[0], 0.0f, 1.0f, "%.2f");
    ImGui::SliderFloat("Damping", &params[1], 0.0f, 1.0f, "%.2f");
    ImGui::SliderFloat("Width", &params[2], 0.0f, 1.0f, "%.2f");
    ImGui::SliderFloat("Mix", &params[3], 0.0f, 1.0f, "%.2f");
    break;

  case EFFECT_DELAY:
    ImGui::SliderFloat("Time", &params[0], 0.0f, 2.0f, "%.3f s");
    ImGui::SliderFloat("Feedback", &params[1], 0.0f, 0.95f, "%.2f");
    ImGui::SliderFloat("Mix", &params[2], 0.0f, 1.0f, "%.2f");
    if (ImGui::Button("Sync to BPM")) {
      // Sync delay time to BPM
      float bpm = app->project.transport.bpm;
      params[0] = 60.0f / bpm; // Quarter note
    }
    break;

  case EFFECT_DISTORTION:
    ImGui::SliderFloat("Drive", &params[0], 0.0f, 1.0f, "%.2f");
    ImGui::SliderFloat("Tone", &params[1], 0.0f, 1.0f, "%.2f");
    ImGui::SliderFloat("Mix", &params[2], 0.0f, 1.0f, "%.2f");
    break;

  case EFFECT_CHORUS:
    ImGui::SliderFloat("Rate", &params[0], 0.1f, 10.0f, "%.2f Hz");
    ImGui::SliderFloat("Depth", &params[1], 0.0f, 1.0f, "%.2f");
    ImGui::SliderFloat("Mix", &params[2], 0.0f, 1.0f, "%.2f");
    break;

  case EFFECT_PHASER:
    ImGui::SliderFloat("Rate", &params[0], 0.1f, 10.0f, "%.2f Hz");
    ImGui::SliderFloat("Depth", &params[1], 0.0f, 1.0f, "%.2f");
    ImGui::SliderFloat("Feedback", &params[2], -0.9f, 0.9f, "%.2f");
    ImGui::SliderFloat("Stages", &params[3], 2.0f, 12.0f, "%.0f");
    break;

  case EFFECT_FILTER:
    ImGui::SliderFloat("Cutoff", &params[0], 20.0f, 20000.0f, "%.0f Hz",
                       ImGuiSliderFlags_Logarithmic);
    ImGui::SliderFloat("Resonance", &params[1], 0.5f, 10.0f, "%.2f");
    const char *filter_types[] = {"Lowpass", "Highpass", "Bandpass"};
    int filter_type = (int)params[2];
    if (ImGui::Combo("Type", &filter_type, filter_types, 3)) {
      params[2] = (float)filter_type;
    }
    break;

  case EFFECT_LIMITER:
    ImGui::SliderFloat("Ceiling", &params[0], -12.0f, 0.0f, "%.1f dB");
    ImGui::SliderFloat("Release", &params[1], 10.0f, 500.0f, "%.0f ms");
    break;

  default:
    ImGui::Text("Unknown effect type");
    break;
  }

  ImGui::Separator();

  // Preset buttons
  if (ImGui::Button("Reset")) {
    // Reset to defaults
    memset(params, 0, sizeof(float) * MAX_EFFECT_PARAMS);
  }
  ImGui::SameLine();
  if (ImGui::Button("Randomize")) {
    // Randomize parameters (for experimentation)
    for (int i = 0; i < 5; i++) {
      params[i] = (float)rand() / RAND_MAX;
    }
  }

  ImGui::End();
}

#endif // INTUITIVES_DAW_GUI
