/**
 * INTUITIVES DAW - Dear ImGui GUI Implementation
 *
 * Native visual interface for the rule-free DAW.
 * Uses Dear ImGui for immediate-mode rendering.
 *
 * Compile with: -DINTUITIVES_DAW_GUI=1
 * Link with: glfw, OpenGL, Dear ImGui
 */

#include "../../include/gui/intuitives_gui.h"

#ifdef INTUITIVES_DAW_GUI

#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include <GLFW/glfw3.h>

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ============================================================================
// STATIC STATE
// ============================================================================

static GLFWwindow *g_window = NULL;
static GuiState g_state = {0};

// ============================================================================
// LIFECYCLE
// ============================================================================

bool gui_init(DawApp *app) {
  if (!app)
    return false;

  // Initialize GLFW
  if (!glfwInit()) {
    fprintf(stderr, "Failed to initialize GLFW\n");
    return false;
  }

  // Configure OpenGL context
  glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
  glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
  glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);

  // Create window
  g_window = glfwCreateWindow(1400, 900, "Intuitives DAW", NULL, NULL);
  if (!g_window) {
    fprintf(stderr, "Failed to create GLFW window\n");
    glfwTerminate();
    return false;
  }

  glfwMakeContextCurrent(g_window);
  glfwSwapInterval(1); // VSync

  // Initialize Dear ImGui
  IMGUI_CHECKVERSION();
  ImGui::CreateContext();
  ImGuiIO &io = ImGui::GetIO();
  io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
  io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;

  // Setup platform/renderer backends
  ImGui_ImplGlfw_InitForOpenGL(g_window, true);
  ImGui_ImplOpenGL3_Init("#version 330");

  // Initialize state
  memset(&g_state, 0, sizeof(g_state));
  g_state.show_sequencer = true;
  g_state.show_mixer = true;
  g_state.show_generator_panel = true;
  g_state.show_visualizer = true;
  g_state.theme = THEME_DARK;
  g_state.piano_roll_zoom = 1.0f;
  g_state.generator_temperature = 0.7f;
  g_state.generator_num_notes = 16;
  g_state.generator_generations = 50;
  g_state.cellular_rule = 30;
  g_state.cellular_density = 0.3f;

  // Apply theme
  gui_apply_theme(&g_state.theme);

  printf("✓ GUI initialized (Dear ImGui + GLFW)\n");
  return true;
}

void gui_shutdown(DawApp *app) {
  (void)app;

  ImGui_ImplOpenGL3_Shutdown();
  ImGui_ImplGlfw_Shutdown();
  ImGui::DestroyContext();

  if (g_window) {
    glfwDestroyWindow(g_window);
    g_window = NULL;
  }
  glfwTerminate();
}

void gui_begin_frame(DawApp *app) {
  (void)app;

  glfwPollEvents();

  ImGui_ImplOpenGL3_NewFrame();
  ImGui_ImplGlfw_NewFrame();
  ImGui::NewFrame();
}

void gui_end_frame(DawApp *app) {
  (void)app;

  ImGui::Render();

  int display_w, display_h;
  glfwGetFramebufferSize(g_window, &display_w, &display_h);
  glViewport(0, 0, display_w, display_h);

  // Clear with theme background color
  glClearColor(g_state.theme.background[0], g_state.theme.background[1],
               g_state.theme.background[2], 1.0f);
  glClear(GL_COLOR_BUFFER_BIT);

  ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

  glfwSwapBuffers(g_window);
}

bool gui_should_close(DawApp *app) {
  (void)app;
  return g_window ? glfwWindowShouldClose(g_window) : true;
}

// ============================================================================
// THEME
// ============================================================================

void gui_apply_theme(const IntuitivesTheme *theme) {
  ImGuiStyle &style = ImGui::GetStyle();

  // Colors
  style.Colors[ImGuiCol_WindowBg] =
      ImVec4(theme->surface[0], theme->surface[1], theme->surface[2],
             theme->surface[3]);
  style.Colors[ImGuiCol_ChildBg] =
      ImVec4(theme->background[0], theme->background[1], theme->background[2],
             theme->background[3]);
  style.Colors[ImGuiCol_Text] =
      ImVec4(theme->text[0], theme->text[1], theme->text[2], theme->text[3]);
  style.Colors[ImGuiCol_TextDisabled] =
      ImVec4(theme->text_dim[0], theme->text_dim[1], theme->text_dim[2],
             theme->text_dim[3]);
  style.Colors[ImGuiCol_FrameBg] =
      ImVec4(theme->background[0], theme->background[1], theme->background[2],
             theme->background[3]);
  style.Colors[ImGuiCol_FrameBgHovered] =
      ImVec4(theme->surface[0] * 1.2f, theme->surface[1] * 1.2f,
             theme->surface[2] * 1.2f, 1.0f);
  style.Colors[ImGuiCol_Button] =
      ImVec4(theme->surface[0] * 1.5f, theme->surface[1] * 1.5f,
             theme->surface[2] * 1.5f, 1.0f);
  style.Colors[ImGuiCol_ButtonHovered] =
      ImVec4(theme->primary[0] * 0.8f, theme->primary[1] * 0.8f,
             theme->primary[2] * 0.8f, 1.0f);
  style.Colors[ImGuiCol_ButtonActive] =
      ImVec4(theme->primary[0], theme->primary[1], theme->primary[2], 1.0f);
  style.Colors[ImGuiCol_SliderGrab] =
      ImVec4(theme->primary[0], theme->primary[1], theme->primary[2], 1.0f);
  style.Colors[ImGuiCol_Header] =
      ImVec4(theme->surface[0] * 1.3f, theme->surface[1] * 1.3f,
             theme->surface[2] * 1.3f, 1.0f);
  style.Colors[ImGuiCol_HeaderHovered] =
      ImVec4(theme->primary[0] * 0.6f, theme->primary[1] * 0.6f,
             theme->primary[2] * 0.6f, 1.0f);
  style.Colors[ImGuiCol_Tab] =
      ImVec4(theme->surface[0], theme->surface[1], theme->surface[2], 1.0f);
  style.Colors[ImGuiCol_TabHovered] =
      ImVec4(theme->primary[0] * 0.7f, theme->primary[1] * 0.7f,
             theme->primary[2] * 0.7f, 1.0f);
  style.Colors[ImGuiCol_TabActive] =
      ImVec4(theme->primary[0] * 0.5f, theme->primary[1] * 0.5f,
             theme->primary[2] * 0.5f, 1.0f);

  // Style
  style.WindowRounding = 4.0f;
  style.FrameRounding = 3.0f;
  style.GrabRounding = 3.0f;
  style.TabRounding = 4.0f;
  style.WindowPadding = ImVec2(10, 10);
  style.FramePadding = ImVec2(6, 4);
  style.ItemSpacing = ImVec2(8, 6);
}

// ============================================================================
// MENU BAR
// ============================================================================

void gui_draw_menu_bar(DawApp *app, GuiState *state) {
  if (ImGui::BeginMainMenuBar()) {
    if (ImGui::BeginMenu("File")) {
      if (ImGui::MenuItem("New Project", "Cmd+N")) {
        daw_new_project(app, "Untitled");
      }
      if (ImGui::MenuItem("Open...", "Cmd+O")) {
        // TODO: File dialog
      }
      if (ImGui::MenuItem("Save", "Cmd+S")) {
        if (strlen(app->project.filepath) > 0) {
          daw_save_project(app, app->project.filepath);
        }
      }
      if (ImGui::MenuItem("Save As...", "Cmd+Shift+S")) {
        // TODO: File dialog
      }
      ImGui::Separator();
      if (ImGui::MenuItem("Quit", "Cmd+Q")) {
        glfwSetWindowShouldClose(g_window, true);
      }
      ImGui::EndMenu();
    }

    if (ImGui::BeginMenu("Edit")) {
      if (ImGui::MenuItem("Undo", "Cmd+Z")) {
      }
      if (ImGui::MenuItem("Redo", "Cmd+Shift+Z")) {
      }
      ImGui::Separator();
      if (ImGui::MenuItem("Cut", "Cmd+X")) {
      }
      if (ImGui::MenuItem("Copy", "Cmd+C")) {
      }
      if (ImGui::MenuItem("Paste", "Cmd+V")) {
      }
      ImGui::EndMenu();
    }

    if (ImGui::BeginMenu("View")) {
      ImGui::MenuItem("Sequencer", NULL, &state->show_sequencer);
      ImGui::MenuItem("Pattern Editor", NULL, &state->show_pattern_editor);
      ImGui::MenuItem("Mixer", NULL, &state->show_mixer);
      ImGui::MenuItem("Generator Panel", NULL, &state->show_generator_panel);
      ImGui::MenuItem("Visualizer", NULL, &state->show_visualizer);
      ImGui::Separator();
      ImGui::MenuItem("Settings", NULL, &state->show_settings);
      ImGui::EndMenu();
    }

    if (ImGui::BeginMenu("Help")) {
      ImGui::MenuItem("About Intuitives", NULL, &state->show_about);
      ImGui::EndMenu();
    }

    ImGui::EndMainMenuBar();
  }
}

// ============================================================================
// TRANSPORT
// ============================================================================

void gui_draw_transport(DawApp *app, GuiState *state) {
  ImGui::SetNextWindowPos(ImVec2(0, 20), ImGuiCond_FirstUseEver);
  ImGui::SetNextWindowSize(ImVec2(ImGui::GetIO().DisplaySize.x, 60),
                           ImGuiCond_Always);

  ImGuiWindowFlags flags = ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoMove |
                           ImGuiWindowFlags_NoCollapse |
                           ImGuiWindowFlags_NoTitleBar;

  ImGui::Begin("Transport", NULL, flags);

  Transport *transport = &app->project.transport;

  // Play/Pause/Stop buttons
  ImGui::PushStyleColor(ImGuiCol_Button,
                        transport->playing
                            ? ImVec4(state->theme.success[0],
                                     state->theme.success[1],
                                     state->theme.success[2], 1.0f)
                            : ImVec4(state->theme.surface[0] * 1.5f,
                                     state->theme.surface[1] * 1.5f,
                                     state->theme.surface[2] * 1.5f, 1.0f));

  if (ImGui::Button(transport->playing ? "⏸ Pause" : "▶ Play",
                    ImVec2(80, 35))) {
    if (transport->playing) {
      daw_pause(app);
    } else {
      daw_play(app);
    }
  }
  ImGui::PopStyleColor();

  ImGui::SameLine();
  if (ImGui::Button("⏹ Stop", ImVec2(80, 35))) {
    daw_stop(app);
  }

  // BPM
  ImGui::SameLine(200);
  ImGui::SetNextItemWidth(80);
  float bpm = transport->bpm;
  if (ImGui::DragFloat("BPM", &bpm, 0.5f, 20.0f, 400.0f, "%.1f")) {
    daw_set_bpm(app, bpm);
  }

  // Time display
  ImGui::SameLine(350);
  int bars = (int)(transport->current_beat / transport->beats_per_bar) + 1;
  int beats = ((int)transport->current_beat % transport->beats_per_bar) + 1;
  int ticks =
      (int)((transport->current_beat - (int)transport->current_beat) * 960);
  ImGui::Text("%03d : %d : %03d", bars, beats, ticks);

  // Loop toggle
  ImGui::SameLine(500);
  if (ImGui::Checkbox("Loop", &transport->looping)) {
    // State updated directly
  }

  // Master volume
  ImGui::SameLine(ImGui::GetWindowWidth() - 200);
  ImGui::SetNextItemWidth(120);
  ImGui::SliderFloat("Master", &app->project.master_volume, 0.0f, 2.0f, "%.2f");

  ImGui::End();
}

// ============================================================================
// MIXER
// ============================================================================

void gui_draw_mixer(DawApp *app, GuiState *state) {
  if (!state->show_mixer)
    return;

  ImGui::SetNextWindowPos(ImVec2(0, ImGui::GetIO().DisplaySize.y - 200),
                          ImGuiCond_FirstUseEver);
  ImGui::SetNextWindowSize(ImVec2(ImGui::GetIO().DisplaySize.x, 200),
                           ImGuiCond_FirstUseEver);

  if (!ImGui::Begin("Mixer", &state->show_mixer)) {
    ImGui::End();
    return;
  }

  // Draw channel strips
  float strip_width = 80.0f;

  for (uint32_t i = 0; i < app->project.num_tracks; i++) {
    DawTrack *track = &app->project.tracks[i];

    ImGui::PushID(i);
    ImGui::BeginGroup();

    // Track name
    ImGui::Text("%s", track->name);

    // Mute/Solo
    ImGui::PushStyleColor(ImGuiCol_Button,
                          track->mute ? ImVec4(1.0f, 0.3f, 0.3f, 1.0f)
                                      : ImVec4(0.3f, 0.3f, 0.3f, 1.0f));
    if (ImGui::Button("M", ImVec2(25, 20))) {
      daw_toggle_track_mute(app, i);
    }
    ImGui::PopStyleColor();

    ImGui::SameLine();
    ImGui::PushStyleColor(ImGuiCol_Button,
                          track->solo ? ImVec4(0.3f, 1.0f, 0.3f, 1.0f)
                                      : ImVec4(0.3f, 0.3f, 0.3f, 1.0f));
    if (ImGui::Button("S", ImVec2(25, 20))) {
      daw_toggle_track_solo(app, i);
    }
    ImGui::PopStyleColor();

    // Volume fader
    ImGui::VSliderFloat("##vol", ImVec2(30, 100), &track->volume, 0.0f, 2.0f,
                        "");

    // Pan knob
    ImGui::SetNextItemWidth(strip_width - 10);
    ImGui::SliderFloat("##pan", &track->pan, -1.0f, 1.0f, "%.2f");

    // Level meter
    gui_level_meter(track->peak_l, 10, 100, &state->theme);
    ImGui::SameLine();
    gui_level_meter(track->peak_r, 10, 100, &state->theme);

    ImGui::EndGroup();
    ImGui::PopID();

    if (i < app->project.num_tracks - 1) {
      ImGui::SameLine();
    }
  }

  // Add track button
  ImGui::SameLine();
  if (ImGui::Button("+\nAdd\nTrack", ImVec2(60, 150))) {
    char name[32];
    snprintf(name, 32, "Track %d", app->project.num_tracks + 1);
    daw_add_track(app, name);
  }

  ImGui::End();
}

// ============================================================================
// GENERATOR PANEL
// ============================================================================

void gui_draw_generator_panel(DawApp *app, GuiState *state) {
  if (!state->show_generator_panel)
    return;

  ImGui::SetNextWindowPos(ImVec2(ImGui::GetIO().DisplaySize.x - 300, 80),
                          ImGuiCond_FirstUseEver);
  ImGui::SetNextWindowSize(ImVec2(290, 400), ImGuiCond_FirstUseEver);

  if (!ImGui::Begin("Generators", &state->show_generator_panel)) {
    ImGui::End();
    return;
  }

  // Generator type selector
  const char *generators[] = {"Markov Chain", "Genetic Algorithm",
                              "Cellular Automata", "Text to Melody"};
  ImGui::Combo("Type", &state->generator_type, generators, 4);

  ImGui::Separator();

  // Pattern selector
  if (app->project.num_patterns > 0) {
    const char *pattern_name =
        app->project.patterns[state->selected_pattern].name;
    ImGui::Text("Target Pattern: %s", pattern_name);
  } else {
    ImGui::TextDisabled("No patterns available");
  }

  ImGui::Separator();

  // Generator-specific controls
  switch (state->generator_type) {
  case 0: // Markov
    ImGui::SliderFloat("Temperature", &state->generator_temperature, 0.1f, 2.0f,
                       "%.2f");
    ImGui::SliderInt("Notes", &state->generator_num_notes, 4, 64);

    ImGui::PushStyleColor(ImGuiCol_Button,
                          ImVec4(state->theme.primary[0],
                                 state->theme.primary[1],
                                 state->theme.primary[2], 1.0f));
    if (ImGui::Button("Generate Markov Melody", ImVec2(-1, 35))) {
      if (app->project.num_patterns > 0) {
        daw_generate_melody_markov(app, state->selected_pattern,
                                   state->generator_temperature,
                                   state->generator_num_notes);
      }
    }
    ImGui::PopStyleColor();

    ImGui::TextWrapped("Uses probabilistic note transitions based on "
                       "learned patterns. Higher temperature = more random.");
    break;

  case 1: // Genetic
    ImGui::SliderInt("Generations", &state->generator_generations, 10, 200);

    ImGui::PushStyleColor(ImGuiCol_Button,
                          ImVec4(state->theme.secondary[0],
                                 state->theme.secondary[1],
                                 state->theme.secondary[2], 1.0f));
    if (ImGui::Button("Evolve Melody", ImVec2(-1, 35))) {
      if (app->project.num_patterns > 0) {
        daw_generate_melody_genetic(app, state->selected_pattern,
                                    state->generator_generations);
      }
    }
    ImGui::PopStyleColor();

    ImGui::TextWrapped("Evolves melodies through mutation and selection. "
                       "More generations = more refined results.");
    break;

  case 2: // Cellular
    ImGui::SliderInt("Rule", &state->cellular_rule, 0, 255);
    ImGui::SliderFloat("Density", &state->cellular_density, 0.1f, 0.9f);

    ImGui::PushStyleColor(ImGuiCol_Button,
                          ImVec4(state->theme.success[0],
                                 state->theme.success[1],
                                 state->theme.success[2], 1.0f));
    if (ImGui::Button("Generate Cellular Rhythm", ImVec2(-1, 35))) {
      if (app->project.num_patterns > 0) {
        daw_generate_rhythm_cellular(app, state->selected_pattern,
                                     state->cellular_rule,
                                     state->cellular_density);
      }
    }
    ImGui::PopStyleColor();

    ImGui::TextWrapped("Rule 30, 90, 110 produce interesting patterns. "
                       "Creates rhythmic triggers from automata state.");
    break;

  case 3: // Text
    ImGui::InputText("Text", state->text_input, 256);

    ImGui::PushStyleColor(ImGuiCol_Button,
                          ImVec4(state->theme.warning[0],
                                 state->theme.warning[1],
                                 state->theme.warning[2], 1.0f));
    if (ImGui::Button("Convert Text to Melody", ImVec2(-1, 35))) {
      if (app->project.num_patterns > 0 && strlen(state->text_input) > 0) {
        daw_generate_from_text(app, state->selected_pattern, state->text_input);
      }
    }
    ImGui::PopStyleColor();

    ImGui::TextWrapped("Maps ASCII characters to MIDI notes. "
                       "Each letter has a unique pitch.");
    break;
  }

  ImGui::Separator();

  // Color-to-harmony
  ImGui::Text("Color to Harmony");
  if (ImGui::ColorEdit3("Color", state->color_picker)) {
    if (app->project.num_tracks > 0) {
      daw_generate_from_color(app, state->selected_track,
                              (uint8_t)(state->color_picker[0] * 255),
                              (uint8_t)(state->color_picker[1] * 255),
                              (uint8_t)(state->color_picker[2] * 255));
    }
  }

  ImGui::End();
}

// ============================================================================
// VISUALIZER
// ============================================================================

void gui_draw_visualizer(DawApp *app, GuiState *state) {
  if (!state->show_visualizer)
    return;

  ImGui::SetNextWindowPos(ImVec2(300, 80), ImGuiCond_FirstUseEver);
  ImGui::SetNextWindowSize(ImVec2(400, 250), ImGuiCond_FirstUseEver);

  if (!ImGui::Begin("Visualizer", &state->show_visualizer)) {
    ImGui::End();
    return;
  }

  ImDrawList *draw_list = ImGui::GetWindowDrawList();
  ImVec2 pos = ImGui::GetCursorScreenPos();
  float width = ImGui::GetContentRegionAvail().x;
  float height = 180.0f;

  // Get current chromasynesthesia color
  uint32_t color32 = daw_get_current_color(app);
  float r = ((color32 >> 16) & 0xFF) / 255.0f;
  float g = ((color32 >> 8) & 0xFF) / 255.0f;
  float b = (color32 & 0xFF) / 255.0f;

  // Background with gradient
  ImU32 bg_top = IM_COL32(r * 30, g * 30, b * 30, 255);
  ImU32 bg_bot = IM_COL32(r * 10, g * 10, b * 10, 255);
  draw_list->AddRectFilledMultiColor(pos, ImVec2(pos.x + width, pos.y + height),
                                     bg_top, bg_top, bg_bot, bg_bot);

  // Get spectrum data
  float bands[32];
  daw_get_spectrum(app, bands, 32);

  // Draw spectrum bars
  float bar_width = width / 32.0f;
  ImU32 bar_color = IM_COL32(r * 255, g * 255, b * 255, 200);

  for (int i = 0; i < 32; i++) {
    float bar_height = bands[i] * height * 0.9f;
    float x = pos.x + i * bar_width;

    draw_list->AddRectFilled(ImVec2(x + 1, pos.y + height - bar_height),
                             ImVec2(x + bar_width - 1, pos.y + height),
                             bar_color);
  }

  // Draw level meters
  float left, right;
  daw_get_levels(app, &left, &right);

  ImGui::SetCursorPosY(ImGui::GetCursorPosY() + height + 10);
  ImGui::Text("Levels: L %.2f | R %.2f", left, right);

  // Chromasynesthesia color preview
  ImGui::SameLine(width - 100);
  draw_list->AddRectFilled(
      ImVec2(ImGui::GetCursorScreenPos().x, ImGui::GetCursorScreenPos().y),
      ImVec2(ImGui::GetCursorScreenPos().x + 80,
             ImGui::GetCursorScreenPos().y + 20),
      IM_COL32(r * 255, g * 255, b * 255, 255));

  ImGui::End();
}

// ============================================================================
// WIDGETS
// ============================================================================

void gui_level_meter(float level, float width, float height,
                     const IntuitivesTheme *theme) {
  ImDrawList *draw_list = ImGui::GetWindowDrawList();
  ImVec2 pos = ImGui::GetCursorScreenPos();

  // Background
  draw_list->AddRectFilled(pos, ImVec2(pos.x + width, pos.y + height),
                           IM_COL32(20, 20, 25, 255));

  // Level bar
  float level_height = level * height;
  float level_y = pos.y + height - level_height;

  // Determine color based on level
  ImU32 color;
  if (level < 0.7f) {
    color = IM_COL32(theme->meter_low[0] * 255, theme->meter_low[1] * 255,
                     theme->meter_low[2] * 255, 255);
  } else if (level < 0.9f) {
    color = IM_COL32(theme->meter_mid[0] * 255, theme->meter_mid[1] * 255,
                     theme->meter_mid[2] * 255, 255);
  } else {
    color = IM_COL32(theme->meter_high[0] * 255, theme->meter_high[1] * 255,
                     theme->meter_high[2] * 255, 255);
  }

  draw_list->AddRectFilled(ImVec2(pos.x, level_y),
                           ImVec2(pos.x + width, pos.y + height), color);

  // Advance cursor
  ImGui::Dummy(ImVec2(width, height));
}

void gui_note_color(int note, float *out_rgba) {
  // Chromasynesthesia: map note to color
  static const float note_colors[12][3] = {
      {1.0f, 0.2f, 0.2f}, // C - Red
      {1.0f, 0.5f, 0.2f}, // C# - Orange-red
      {1.0f, 0.7f, 0.2f}, // D - Orange
      {1.0f, 1.0f, 0.2f}, // D# - Yellow
      {0.5f, 1.0f, 0.2f}, // E - Yellow-green
      {0.2f, 1.0f, 0.4f}, // F - Green
      {0.2f, 1.0f, 0.8f}, // F# - Cyan-green
      {0.2f, 0.8f, 1.0f}, // G - Cyan
      {0.2f, 0.4f, 1.0f}, // G# - Blue
      {0.5f, 0.2f, 1.0f}, // A - Purple
      {0.8f, 0.2f, 1.0f}, // A# - Violet
      {1.0f, 0.2f, 0.8f}, // B - Magenta
  };

  int pitch_class = note % 12;
  out_rgba[0] = note_colors[pitch_class][0];
  out_rgba[1] = note_colors[pitch_class][1];
  out_rgba[2] = note_colors[pitch_class][2];
  out_rgba[3] = 1.0f;
}

// ============================================================================
// ABOUT
// ============================================================================

void gui_draw_about(DawApp *app, GuiState *state) {
  if (!state->show_about)
    return;

  ImGui::SetNextWindowSize(ImVec2(400, 300), ImGuiCond_FirstUseEver);

  if (!ImGui::Begin("About Intuitives", &state->show_about,
                    ImGuiWindowFlags_NoResize)) {
    ImGui::End();
    return;
  }

  ImGui::Text("INTUITIVES DAW");
  ImGui::Text("Version %d.%d.%d", INTUITIVES_DAW_VERSION_MAJOR,
              INTUITIVES_DAW_VERSION_MINOR, INTUITIVES_DAW_VERSION_PATCH);

  ImGui::Separator();

  ImGui::TextWrapped(
      "\"Does this sound cool?\" - The only rule.\n\n"
      "Intuitives is an experimental, rule-free digital audio workstation "
      "that prioritizes intuition, randomness, and AI-assisted discovery "
      "over traditional music theory constraints.\n\n"
      "Features:\n"
      "• 40 Original DSP Features\n"
      "• Markov/Genetic/Cellular Generators\n"
      "• Text-to-Melody, Color-to-Harmony\n"
      "• Chromasynesthesia Visualization\n"
      "• Image-to-Sound Processing");

  ImGui::Separator();

  if (app) {
    ImGui::Text("Audio: %d Hz | %d buffer", app->sample_rate, app->buffer_size);
    ImGui::Text("Tracks: %d | Patterns: %d", app->project.num_tracks,
                app->project.num_patterns);
  }

  ImGui::End();
}

// ============================================================================
// MAIN GUI RENDER LOOP
// ============================================================================

void gui_render(DawApp *app) {
  if (!app)
    return;

  // Draw all windows
  gui_draw_menu_bar(app, &g_state);
  gui_draw_transport(app, &g_state);
  gui_draw_mixer(app, &g_state);
  gui_draw_generator_panel(app, &g_state);
  gui_draw_visualizer(app, &g_state);
  gui_draw_about(app, &g_state);

  // Demo window for development
  // ImGui::ShowDemoWindow();
}

#endif // INTUITIVES_DAW_GUI
