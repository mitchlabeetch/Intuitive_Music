/**
 * INTUITIVES DAW - Sequencer and Piano Roll
 *
 * Pattern arrangement and MIDI note editing components.
 * Uses Dear ImGui for immediate-mode rendering.
 */

#include "../../include/gui/intuitives_gui.h"

#ifdef INTUITIVES_DAW_GUI

#include "imgui.h"
#include <math.h>
#include <stdio.h>

// ============================================================================
// CONSTANTS
// ============================================================================

#define PIANO_ROLL_NOTE_HEIGHT 12
#define PIANO_ROLL_BEAT_WIDTH 48
#define SEQ_TRACK_HEIGHT 60
#define SEQ_BEAT_WIDTH 24

// Note names for piano keys
static const char *NOTE_NAMES[] = {"C",  "C#", "D",  "D#", "E",  "F",
                                   "F#", "G",  "G#", "A",  "A#", "B"};

// ============================================================================
// SEQUENCER VIEW
// ============================================================================

void gui_draw_sequencer(DawApp *app, GuiState *state) {
  if (!state->show_sequencer)
    return;

  ImGui::SetNextWindowPos(ImVec2(0, 80), ImGuiCond_FirstUseEver);
  ImGui::SetNextWindowSize(ImVec2(800, 300), ImGuiCond_FirstUseEver);

  if (!ImGui::Begin("Sequencer", &state->show_sequencer)) {
    ImGui::End();
    return;
  }

  Transport *transport = &app->project.transport;
  ImDrawList *draw_list = ImGui::GetWindowDrawList();
  ImVec2 canvas_pos = ImGui::GetCursorScreenPos();
  ImVec2 canvas_size = ImGui::GetContentRegionAvail();

  // Clamp minimum size
  if (canvas_size.x < 100)
    canvas_size.x = 100;
  if (canvas_size.y < 100)
    canvas_size.y = 100;

  // Background
  draw_list->AddRectFilled(
      canvas_pos,
      ImVec2(canvas_pos.x + canvas_size.x, canvas_pos.y + canvas_size.y),
      IM_COL32(20, 20, 25, 255));

  // Grid lines - vertical (beats)
  float total_beats = transport->loop_end > 0 ? transport->loop_end : 16.0f;
  float pixels_per_beat = canvas_size.x / total_beats;

  for (float beat = 0; beat <= total_beats; beat += 1.0f) {
    float x = canvas_pos.x + beat * pixels_per_beat;
    bool is_bar = (int)beat % transport->beats_per_bar == 0;

    draw_list->AddLine(
        ImVec2(x, canvas_pos.y), ImVec2(x, canvas_pos.y + canvas_size.y),
        is_bar ? IM_COL32(80, 80, 90, 255) : IM_COL32(40, 40, 50, 255),
        is_bar ? 2.0f : 1.0f);

    // Beat numbers at bar lines
    if (is_bar) {
      char label[8];
      snprintf(label, 8, "%d", (int)(beat / transport->beats_per_bar) + 1);
      draw_list->AddText(ImVec2(x + 2, canvas_pos.y + 2),
                         IM_COL32(120, 120, 130, 255), label);
    }
  }

  // Grid lines - horizontal (tracks)
  float track_height =
      canvas_size.y /
      (app->project.num_tracks > 0 ? app->project.num_tracks : 1);
  for (uint32_t t = 0; t <= app->project.num_tracks; t++) {
    float y = canvas_pos.y + t * track_height;
    draw_list->AddLine(ImVec2(canvas_pos.x, y),
                       ImVec2(canvas_pos.x + canvas_size.x, y),
                       IM_COL32(50, 50, 60, 255));
  }

  // Draw track labels
  for (uint32_t t = 0; t < app->project.num_tracks; t++) {
    DawTrack *track = &app->project.tracks[t];
    float y = canvas_pos.y + t * track_height + track_height / 2 - 6;

    // Track color bar
    draw_list->AddRectFilled(
        ImVec2(canvas_pos.x, canvas_pos.y + t * track_height),
        ImVec2(canvas_pos.x + 4, canvas_pos.y + (t + 1) * track_height),
        IM_COL32(track->color.r, track->color.g, track->color.b, 255));

    // Track name
    draw_list->AddText(ImVec2(canvas_pos.x + 8, y),
                       IM_COL32(180, 180, 190, 255), track->name);
  }

  // Draw pattern instances
  for (uint32_t i = 0; i < app->project.num_arrangement_items; i++) {
    PatternInstance *inst = &app->project.arrangement[i];
    if (inst->pattern_id >= app->project.num_patterns ||
        inst->track_id >= app->project.num_tracks)
      continue;

    Pattern *pattern = &app->project.patterns[inst->pattern_id];
    DawTrack *track = &app->project.tracks[inst->track_id];

    float x1 = canvas_pos.x + inst->start_beat * pixels_per_beat;
    float x2 = x1 + pattern->length_beats * pixels_per_beat;
    float y1 = canvas_pos.y + inst->track_id * track_height + 2;
    float y2 = y1 + track_height - 4;

    // Pattern block
    ImU32 pattern_color =
        inst->muted ? IM_COL32(60, 60, 70, 180)
                    : IM_COL32(track->color.r * 0.7f, track->color.g * 0.7f,
                               track->color.b * 0.7f, 200);

    draw_list->AddRectFilled(ImVec2(x1, y1), ImVec2(x2, y2), pattern_color);
    draw_list->AddRect(
        ImVec2(x1, y1), ImVec2(x2, y2),
        IM_COL32(track->color.r, track->color.g, track->color.b, 255));

    // Pattern name
    draw_list->AddText(ImVec2(x1 + 4, y1 + 4), IM_COL32(220, 220, 230, 255),
                       pattern->name);
  }

  // Playhead
  if (transport->current_beat >= 0 && transport->current_beat <= total_beats) {
    float playhead_x = canvas_pos.x + transport->current_beat * pixels_per_beat;
    draw_list->AddLine(ImVec2(playhead_x, canvas_pos.y),
                       ImVec2(playhead_x, canvas_pos.y + canvas_size.y),
                       IM_COL32(255, 100, 100, 255), 2.0f);

    // Playhead triangle
    draw_list->AddTriangleFilled(ImVec2(playhead_x - 6, canvas_pos.y),
                                 ImVec2(playhead_x + 6, canvas_pos.y),
                                 ImVec2(playhead_x, canvas_pos.y + 10),
                                 IM_COL32(255, 100, 100, 255));
  }

  // Loop region
  if (transport->looping) {
    float loop_start_x = canvas_pos.x + transport->loop_start * pixels_per_beat;
    float loop_end_x = canvas_pos.x + transport->loop_end * pixels_per_beat;

    // Loop markers
    draw_list->AddRectFilled(
        ImVec2(loop_start_x, canvas_pos.y),
        ImVec2(loop_start_x + 3, canvas_pos.y + canvas_size.y),
        IM_COL32(100, 200, 255, 100));
    draw_list->AddRectFilled(ImVec2(loop_end_x - 3, canvas_pos.y),
                             ImVec2(loop_end_x, canvas_pos.y + canvas_size.y),
                             IM_COL32(100, 200, 255, 100));
  }

  // Invisible button for mouse interaction
  ImGui::InvisibleButton("sequencer_canvas", canvas_size);

  // Handle clicks to set playhead
  if (ImGui::IsItemClicked(0)) {
    ImVec2 mouse_pos = ImGui::GetMousePos();
    float clicked_beat = (mouse_pos.x - canvas_pos.x) / pixels_per_beat;
    if (clicked_beat >= 0 && clicked_beat <= total_beats) {
      daw_set_position(app, clicked_beat);
    }
  }

  ImGui::End();
}

// ============================================================================
// PATTERN EDITOR (PIANO ROLL)
// ============================================================================

void gui_draw_pattern_editor(DawApp *app, GuiState *state) {
  if (!state->show_pattern_editor)
    return;

  ImGui::SetNextWindowPos(ImVec2(100, 100), ImGuiCond_FirstUseEver);
  ImGui::SetNextWindowSize(ImVec2(700, 400), ImGuiCond_FirstUseEver);

  if (!ImGui::Begin("Pattern Editor", &state->show_pattern_editor)) {
    ImGui::End();
    return;
  }

  // Pattern selector
  if (app->project.num_patterns > 0) {
    if (ImGui::BeginCombo(
            "Pattern", app->project.patterns[state->selected_pattern].name)) {
      for (uint32_t i = 0; i < app->project.num_patterns; i++) {
        bool is_selected = (state->selected_pattern == (int)i);
        if (ImGui::Selectable(app->project.patterns[i].name, is_selected)) {
          state->selected_pattern = i;
        }
        if (is_selected) {
          ImGui::SetItemDefaultFocus();
        }
      }
      ImGui::EndCombo();
    }
  } else {
    ImGui::TextDisabled("No patterns");
    ImGui::End();
    return;
  }

  Pattern *pattern = &app->project.patterns[state->selected_pattern];

  // Tools toolbar
  ImGui::SameLine(200);
  ImGui::Text("Notes: %d", pattern->num_notes);
  ImGui::SameLine(300);
  ImGui::Text("Length: %.1f beats", pattern->length_beats);

  ImGui::SameLine(ImGui::GetWindowWidth() - 150);
  if (ImGui::Button("Clear")) {
    pattern->num_notes = 0;
  }

  ImGui::Separator();

  // Piano roll area
  ImGui::BeginChild("PianoRoll", ImVec2(0, 0), true,
                    ImGuiWindowFlags_HorizontalScrollbar);

  ImDrawList *draw_list = ImGui::GetWindowDrawList();
  ImVec2 canvas_pos = ImGui::GetCursorScreenPos();

  // Calculate dimensions
  int octaves = 5;
  int total_notes = octaves * 12;
  float note_height = PIANO_ROLL_NOTE_HEIGHT;
  float beat_width = PIANO_ROLL_BEAT_WIDTH * state->piano_roll_zoom;
  float keyboard_width = 40;
  float total_width = keyboard_width + pattern->length_beats * beat_width;
  float total_height = total_notes * note_height;

  // Make scrollable area
  ImGui::Dummy(ImVec2(total_width, total_height));
  ImVec2 scroll = ImVec2(ImGui::GetScrollX(), ImGui::GetScrollY());

  // Adjust canvas for scroll
  canvas_pos.x -= scroll.x;
  canvas_pos.y -= scroll.y;

  // Draw background
  draw_list->AddRectFilled(
      ImVec2(canvas_pos.x + keyboard_width, canvas_pos.y),
      ImVec2(canvas_pos.x + total_width, canvas_pos.y + total_height),
      IM_COL32(25, 25, 30, 255));

  // Draw piano keyboard
  for (int n = 0; n < total_notes; n++) {
    int note = (octaves * 12 - 1 - n) + 36; // C2 to C7
    int pitch_class = note % 12;
    float y = canvas_pos.y + n * note_height;

    // Is this a black key?
    bool is_black = (pitch_class == 1 || pitch_class == 3 || pitch_class == 6 ||
                     pitch_class == 8 || pitch_class == 10);

    // Key color
    ImU32 key_color =
        is_black ? IM_COL32(40, 40, 45, 255) : IM_COL32(200, 200, 210, 255);
    ImU32 text_color =
        is_black ? IM_COL32(150, 150, 160, 255) : IM_COL32(50, 50, 60, 255);

    // Draw key
    draw_list->AddRectFilled(
        ImVec2(canvas_pos.x, y),
        ImVec2(canvas_pos.x + keyboard_width - 2, y + note_height - 1),
        key_color);

    // Note name on C notes
    if (pitch_class == 0) {
      char label[8];
      snprintf(label, 8, "C%d", note / 12 - 1);
      draw_list->AddText(ImVec2(canvas_pos.x + 2, y + 1), text_color, label);
    }

    // Row background (alternating for black keys)
    if (is_black) {
      draw_list->AddRectFilled(
          ImVec2(canvas_pos.x + keyboard_width, y),
          ImVec2(canvas_pos.x + total_width, y + note_height),
          IM_COL32(20, 20, 25, 255));
    }
  }

  // Draw beat grid
  for (float beat = 0; beat <= pattern->length_beats; beat += 0.25f) {
    float x = canvas_pos.x + keyboard_width + beat * beat_width;
    bool is_bar = fmod(beat, 4.0f) < 0.01f;
    bool is_beat = fmod(beat, 1.0f) < 0.01f;

    ImU32 grid_color = is_bar    ? IM_COL32(80, 80, 90, 255)
                       : is_beat ? IM_COL32(50, 50, 60, 255)
                                 : IM_COL32(35, 35, 45, 255);

    draw_list->AddLine(ImVec2(x, canvas_pos.y),
                       ImVec2(x, canvas_pos.y + total_height), grid_color);
  }

  // Draw notes
  for (uint32_t i = 0; i < pattern->num_notes; i++) {
    PatternNote *note = &pattern->notes[i];

    // Calculate position
    int row = (octaves * 12 - 1) - (note->note - 36);
    if (row < 0 || row >= total_notes)
      continue;

    float x1 = canvas_pos.x + keyboard_width + note->start_beat * beat_width;
    float x2 = x1 + note->duration * beat_width;
    float y1 = canvas_pos.y + row * note_height + 1;
    float y2 = y1 + note_height - 2;

    // Get chromasynesthesia color
    float note_rgba[4];
    gui_note_color(note->note, note_rgba);

    ImU32 note_color = IM_COL32(note_rgba[0] * 255 * note->velocity,
                                note_rgba[1] * 255 * note->velocity,
                                note_rgba[2] * 255 * note->velocity, 230);

    bool is_selected = ((int)i == state->selected_note);

    // Draw note
    draw_list->AddRectFilled(ImVec2(x1, y1), ImVec2(x2, y2), note_color);
    if (is_selected) {
      draw_list->AddRect(ImVec2(x1 - 1, y1 - 1), ImVec2(x2 + 1, y2 + 1),
                         IM_COL32(255, 255, 255, 255), 0, 0, 2.0f);
    }

    // Velocity bar
    float vel_height = (y2 - y1) * note->velocity;
    draw_list->AddRectFilled(ImVec2(x2 - 3, y2 - vel_height),
                             ImVec2(x2 - 1, y2), IM_COL32(255, 255, 255, 100));
  }

  // Handle mouse input for adding/selecting notes
  ImVec2 mouse_pos = ImGui::GetMousePos();
  bool in_note_area = mouse_pos.x > canvas_pos.x + keyboard_width &&
                      mouse_pos.x < canvas_pos.x + total_width &&
                      mouse_pos.y > canvas_pos.y &&
                      mouse_pos.y < canvas_pos.y + total_height;

  if (in_note_area && ImGui::IsMouseClicked(0)) {
    // Calculate clicked position
    float clicked_beat =
        (mouse_pos.x - canvas_pos.x - keyboard_width) / beat_width;
    int clicked_row = (int)((mouse_pos.y - canvas_pos.y) / note_height);
    int clicked_note = (octaves * 12 - 1 - clicked_row) + 36;

    // Quantize to grid
    clicked_beat = floorf(clicked_beat * 4) / 4;

    // Add note
    if (clicked_note >= 0 && clicked_note <= 127) {
      daw_add_note_to_pattern(app, state->selected_pattern, clicked_note, 0.8f,
                              clicked_beat, 0.25f);
    }
  }

  ImGui::EndChild();

  // Zoom controls
  ImGui::Separator();
  ImGui::SetNextItemWidth(100);
  ImGui::SliderFloat("Zoom", &state->piano_roll_zoom, 0.5f, 4.0f, "%.1fx");

  ImGui::End();
}

#endif // INTUITIVES_DAW_GUI
