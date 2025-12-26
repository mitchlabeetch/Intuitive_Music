/**
 * INTUITIVES DAW - 3D Visualizer
 *
 * Audio-reactive 3D visualization using OpenGL.
 * Inspired by Three.js but native C++ for the DAW.
 *
 * Features:
 * - Spectrum bars
 * - Waveform mesh
 * - Particle system
 * - Chromasynesthesia color mapping
 */

#include "../../include/gui/intuitives_gui.h"

#ifdef INTUITIVES_DAW_GUI

#include "imgui.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ============================================================================
// VISUALIZER TYPES
// ============================================================================

typedef enum {
  VIZ_BARS = 0,  // Spectrum bars
  VIZ_WAVEFORM,  // Waveform display
  VIZ_PARTICLES, // Particle system
  VIZ_CIRCULAR,  // Circular spectrum
  VIZ_MESH,      // 3D-like mesh
  VIZ_COUNT
} VisualizerType;

static const char *VIZ_NAMES[] = {"Spectrum Bars", "Waveform", "Particles",
                                  "Circular", "3D Mesh"};

// ============================================================================
// PARTICLE SYSTEM
// ============================================================================

#define MAX_PARTICLES 256

typedef struct {
  float x, y;
  float vx, vy;
  float life;
  float size;
  float r, g, b;
} Particle;

static Particle g_particles[MAX_PARTICLES];
static int g_num_particles = 0;

static void spawn_particle(float x, float y, float energy, float r, float g,
                           float b) {
  if (g_num_particles >= MAX_PARTICLES)
    return;

  Particle *p = &g_particles[g_num_particles++];
  p->x = x;
  p->y = y;
  p->vx = ((float)rand() / RAND_MAX - 0.5f) * energy * 100;
  p->vy = -((float)rand() / RAND_MAX) * energy * 200;
  p->life = 1.0f;
  p->size = 2.0f + energy * 8.0f;
  p->r = r;
  p->g = g;
  p->b = b;
}

static void update_particles(float dt) {
  for (int i = g_num_particles - 1; i >= 0; i--) {
    Particle *p = &g_particles[i];

    // Physics
    p->x += p->vx * dt;
    p->y += p->vy * dt;
    p->vy += 300.0f * dt; // Gravity
    p->life -= dt * 0.8f;
    p->size *= 0.98f;

    // Remove dead particles
    if (p->life <= 0 || p->size < 0.5f) {
      g_particles[i] = g_particles[--g_num_particles];
    }
  }
}

// ============================================================================
// MESH GENERATION
// ============================================================================

typedef struct {
  float x, y, z;
} Vec3;

static void rotate_y(Vec3 *v, float angle) {
  float c = cosf(angle);
  float s = sinf(angle);
  float x = v->x * c - v->z * s;
  float z = v->x * s + v->z * c;
  v->x = x;
  v->z = z;
}

static void project_3d(Vec3 *v, float *out_x, float *out_y, float fov,
                       float canvas_w, float canvas_h) {
  float z_offset = 300.0f;
  float scale = fov / (v->z + z_offset);
  *out_x = v->x * scale + canvas_w / 2;
  *out_y = v->y * scale + canvas_h / 2;
}

// ============================================================================
// VISUALIZER DRAWING
// ============================================================================

typedef struct {
  VisualizerType type;
  float rotation;
  float scale;
  bool auto_rotate;
  float particle_spawn_rate;
  float smoothing;

  // Smoothed values
  float smoothed_bands[64];
  float smoothed_level;
} Visualizer3DState;

static Visualizer3DState g_viz_state = {
    .type = VIZ_BARS,
    .rotation = 0.0f,
    .scale = 1.0f,
    .auto_rotate = true,
    .particle_spawn_rate = 0.5f,
    .smoothing = 0.8f,
};

void gui_draw_visualizer_3d(DawApp *app, GuiState *state) {
  if (!state->show_visualizer)
    return;

  ImGui::SetNextWindowPos(ImVec2(100, 100), ImGuiCond_FirstUseEver);
  ImGui::SetNextWindowSize(ImVec2(600, 450), ImGuiCond_FirstUseEver);

  if (!ImGui::Begin("3D Visualizer", &state->show_visualizer)) {
    ImGui::End();
    return;
  }

  // Controls bar
  ImGui::SetNextItemWidth(120);
  ImGui::Combo("Mode", (int *)&g_viz_state.type, VIZ_NAMES, VIZ_COUNT);
  ImGui::SameLine();
  ImGui::Checkbox("Auto-Rotate", &g_viz_state.auto_rotate);
  ImGui::SameLine();
  ImGui::SetNextItemWidth(100);
  ImGui::SliderFloat("Scale", &g_viz_state.scale, 0.5f, 3.0f, "%.1f");

  ImGui::Separator();

  // Canvas
  ImDrawList *draw_list = ImGui::GetWindowDrawList();
  ImVec2 canvas_pos = ImGui::GetCursorScreenPos();
  ImVec2 canvas_size = ImGui::GetContentRegionAvail();
  canvas_size.y -= 40; // Leave room for controls

  if (canvas_size.x < 100)
    canvas_size.x = 100;
  if (canvas_size.y < 100)
    canvas_size.y = 100;

  // Background
  draw_list->AddRectFilled(
      canvas_pos,
      ImVec2(canvas_pos.x + canvas_size.x, canvas_pos.y + canvas_size.y),
      IM_COL32(8, 8, 12, 255));

  // Get audio data
  float bands[32];
  daw_get_spectrum(app, bands, 32);

  float level_l, level_r;
  daw_get_levels(app, &level_l, &level_r);
  float level = (level_l + level_r) * 0.5f;

  // Smooth values
  for (int i = 0; i < 32; i++) {
    g_viz_state.smoothed_bands[i] =
        g_viz_state.smoothed_bands[i] * g_viz_state.smoothing +
        bands[i] * (1.0f - g_viz_state.smoothing);
  }
  g_viz_state.smoothed_level =
      g_viz_state.smoothed_level * g_viz_state.smoothing +
      level * (1.0f - g_viz_state.smoothing);

  // Get chromasynesthesia color
  uint32_t color32 = daw_get_current_color(app);
  float cr = ((color32 >> 16) & 0xFF) / 255.0f;
  float cg = ((color32 >> 8) & 0xFF) / 255.0f;
  float cb = (color32 & 0xFF) / 255.0f;

  // Update rotation
  if (g_viz_state.auto_rotate) {
    g_viz_state.rotation += 0.5f * ImGui::GetIO().DeltaTime;
  }

  float center_x = canvas_pos.x + canvas_size.x / 2;
  float center_y = canvas_pos.y + canvas_size.y / 2;
  float dt = ImGui::GetIO().DeltaTime;

  // Draw based on mode
  switch (g_viz_state.type) {
  case VIZ_BARS: {
    float bar_width = canvas_size.x / 32.0f;

    for (int i = 0; i < 32; i++) {
      float h = g_viz_state.smoothed_bands[i] * canvas_size.y * 0.8f *
                g_viz_state.scale;
      float x = canvas_pos.x + i * bar_width;
      float y = canvas_pos.y + canvas_size.y - h;

      // Color gradient based on height and chromasynesthesia
      float t = (float)i / 31.0f;
      float r = cr * (1.0f - t) + state->theme.secondary[0] * t;
      float g = cg * (1.0f - t) + state->theme.secondary[1] * t;
      float b = cb * (1.0f - t) + state->theme.secondary[2] * t;

      ImU32 color = IM_COL32(r * 255, g * 255, b * 255, 220);

      draw_list->AddRectFilled(
          ImVec2(x + 1, y),
          ImVec2(x + bar_width - 1, canvas_pos.y + canvas_size.y), color);

      // Glow effect
      draw_list->AddRect(ImVec2(x, y - 2),
                         ImVec2(x + bar_width, canvas_pos.y + canvas_size.y),
                         IM_COL32(r * 255, g * 255, b * 255, 50));
    }
    break;
  }

  case VIZ_WAVEFORM: {
    // Get waveform data (simulated from spectrum)
    float prev_x = canvas_pos.x;
    float prev_y = center_y;

    for (int i = 0; i < 64; i++) {
      float t = (float)i / 63.0f;
      float x = canvas_pos.x + t * canvas_size.x;

      // Construct waveform from spectrum
      float wave = 0;
      for (int j = 0; j < 32; j++) {
        wave += g_viz_state.smoothed_bands[j] * sinf(t * (j + 1) * 6.28f);
      }
      wave = wave / 32.0f * canvas_size.y * 0.4f * g_viz_state.scale;

      float y = center_y + wave;

      ImU32 color = IM_COL32(cr * 255, cg * 255, cb * 255, 200);
      draw_list->AddLine(ImVec2(prev_x, prev_y), ImVec2(x, y), color, 2.0f);

      prev_x = x;
      prev_y = y;
    }
    break;
  }

  case VIZ_PARTICLES: {
    // Spawn particles based on audio
    for (int i = 0; i < 32; i++) {
      if (g_viz_state.smoothed_bands[i] > 0.3f &&
          (float)rand() / RAND_MAX <
              g_viz_state.particle_spawn_rate * dt * 60) {

        float x = canvas_pos.x + (i + 0.5f) * canvas_size.x / 32.0f;
        float y = canvas_pos.y + canvas_size.y - 10;

        spawn_particle(x, y, g_viz_state.smoothed_bands[i], cr, cg, cb);
      }
    }

    // Update and draw particles
    update_particles(dt);

    for (int i = 0; i < g_num_particles; i++) {
      Particle *p = &g_particles[i];
      ImU32 color = IM_COL32(p->r * 255, p->g * 255, p->b * 255, p->life * 200);
      draw_list->AddCircleFilled(ImVec2(p->x, p->y), p->size, color);
    }
    break;
  }

  case VIZ_CIRCULAR: {
    float radius =
        fminf(canvas_size.x, canvas_size.y) * 0.35f * g_viz_state.scale;

    for (int i = 0; i < 32; i++) {
      float angle1 = (float)i / 32.0f * 6.28f + g_viz_state.rotation;
      float angle2 = (float)(i + 1) / 32.0f * 6.28f + g_viz_state.rotation;

      float r_inner = radius * 0.5f;
      float r_outer = radius * (0.5f + g_viz_state.smoothed_bands[i] * 0.5f);

      float x1_in = center_x + cosf(angle1) * r_inner;
      float y1_in = center_y + sinf(angle1) * r_inner;
      float x1_out = center_x + cosf(angle1) * r_outer;
      float y1_out = center_y + sinf(angle1) * r_outer;
      float x2_in = center_x + cosf(angle2) * r_inner;
      float y2_in = center_y + sinf(angle2) * r_inner;
      float x2_out = center_x + cosf(angle2) * r_outer;
      float y2_out = center_y + sinf(angle2) * r_outer;

      // Color based on band index
      float t = (float)i / 31.0f;
      float r = cr * (1.0f - t) + state->theme.secondary[0] * t;
      float g = cg * (1.0f - t) + state->theme.secondary[1] * t;
      float b = cb * (1.0f - t) + state->theme.secondary[2] * t;
      ImU32 color = IM_COL32(r * 255, g * 255, b * 255, 200);

      draw_list->AddQuadFilled(ImVec2(x1_in, y1_in), ImVec2(x1_out, y1_out),
                               ImVec2(x2_out, y2_out), ImVec2(x2_in, y2_in),
                               color);
    }

    // Center circle
    draw_list->AddCircleFilled(ImVec2(center_x, center_y),
                               radius * 0.4f *
                                   (0.8f + g_viz_state.smoothed_level * 0.4f),
                               IM_COL32(cr * 100, cg * 100, cb * 100, 255));
    break;
  }

  case VIZ_MESH: {
    // 3D mesh grid
    int grid_size = 16;
    float mesh_scale = 10.0f * g_viz_state.scale;

    for (int z = 0; z < grid_size - 1; z++) {
      for (int x = 0; x < grid_size - 1; x++) {
        // Get heights from spectrum
        int band_x = x * 32 / grid_size;
        int band_z = z * 32 / grid_size;
        float h1 = g_viz_state.smoothed_bands[band_x] * 50;
        float h2 = g_viz_state.smoothed_bands[(band_x + 1) % 32] * 50;

        // Create quad vertices
        Vec3 v1 = {(x - grid_size / 2.0f) * mesh_scale, h1,
                   (z - grid_size / 2.0f) * mesh_scale};
        Vec3 v2 = {(x + 1 - grid_size / 2.0f) * mesh_scale, h2,
                   (z - grid_size / 2.0f) * mesh_scale};
        Vec3 v3 = {(x + 1 - grid_size / 2.0f) * mesh_scale, h2,
                   (z + 1 - grid_size / 2.0f) * mesh_scale};
        Vec3 v4 = {(x - grid_size / 2.0f) * mesh_scale, h1,
                   (z + 1 - grid_size / 2.0f) * mesh_scale};

        // Rotate
        rotate_y(&v1, g_viz_state.rotation);
        rotate_y(&v2, g_viz_state.rotation);
        rotate_y(&v3, g_viz_state.rotation);
        rotate_y(&v4, g_viz_state.rotation);

        // Project
        float px1, py1, px2, py2, px3, py3, px4, py4;
        project_3d(&v1, &px1, &py1, 200, canvas_size.x, canvas_size.y);
        project_3d(&v2, &px2, &py2, 200, canvas_size.x, canvas_size.y);
        project_3d(&v3, &px3, &py3, 200, canvas_size.x, canvas_size.y);
        project_3d(&v4, &px4, &py4, 200, canvas_size.x, canvas_size.y);

        px1 += canvas_pos.x;
        py1 += canvas_pos.y;
        px2 += canvas_pos.x;
        py2 += canvas_pos.y;
        px3 += canvas_pos.x;
        py3 += canvas_pos.y;
        px4 += canvas_pos.x;
        py4 += canvas_pos.y;

        // Color based on height
        float intensity = h1 / 50.0f;
        ImU32 color = IM_COL32(cr * 255 * (0.5f + intensity * 0.5f),
                               cg * 255 * (0.5f + intensity * 0.5f),
                               cb * 255 * (0.5f + intensity * 0.5f), 150);

        // Draw wireframe
        draw_list->AddLine(ImVec2(px1, py1), ImVec2(px2, py2), color, 1.0f);
        draw_list->AddLine(ImVec2(px1, py1), ImVec2(px4, py4), color, 1.0f);
      }
    }
    break;
  }

  default:
    break;
  }

  // Invisible button for interaction
  ImGui::SetCursorScreenPos(canvas_pos);
  ImGui::InvisibleButton("viz_canvas", canvas_size);

  // Manual rotation with drag
  if (ImGui::IsItemActive() && ImGui::IsMouseDragging(0)) {
    g_viz_state.rotation += ImGui::GetIO().MouseDelta.x * 0.01f;
  }

  // Bottom controls
  ImGui::SetCursorPosY(ImGui::GetCursorPosY() + canvas_size.y + 5);
  ImGui::SetNextItemWidth(100);
  ImGui::SliderFloat("Smoothing", &g_viz_state.smoothing, 0.0f, 0.99f, "%.2f");

  if (g_viz_state.type == VIZ_PARTICLES) {
    ImGui::SameLine();
    ImGui::SetNextItemWidth(100);
    ImGui::SliderFloat("Spawn Rate", &g_viz_state.particle_spawn_rate, 0.1f,
                       2.0f, "%.1f");
  }

  ImGui::End();
}

#endif // INTUITIVES_DAW_GUI
