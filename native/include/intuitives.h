/**
 * INTUITIVES - Main Header
 * Include this single header to access all features.
 */

#ifndef INTUITIVES_H
#define INTUITIVES_H

#include "intuitives/core.h"
#include "intuitives/effects.h"
#include "intuitives/engine.h"
#include "intuitives/generators.h"
#include "intuitives/input.h"
#include "intuitives/oscillators.h"
#include "intuitives/visual.h"

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// INTUITIVES LIBRARY VERSION AND INFO
// ============================================================================

typedef struct {
  int major;
  int minor;
  int patch;
  const char *build_date;
  const char *features[64];
  size_t num_features;
  bool simd_enabled;
  const char *platform;
} IntuitivesInfo;

void intuitives_get_info(IntuitivesInfo *info);
const char *intuitives_version_string(void);

// ============================================================================
// QUICK-START CONVENIENCE FUNCTIONS
// ============================================================================

// Create a fully initialized engine with default settings
AudioEngine *intuitives_create_default_engine(void);

// Create a basic synth with oscillator + filter + envelope
typedef struct {
  QuantumOscillator osc1;
  QuantumOscillator osc2;
  NoiseGenerator noise;
  StateVariableFilter filter;
  float osc1_level, osc2_level, noise_level;
  float filter_env_amount;
  float amp_attack, amp_decay, amp_sustain, amp_release;
  float filter_attack, filter_decay, filter_sustain, filter_release;
  float amp_env_level, filter_env_level;
  bool gate;
  uint32_t sample_rate;
} BasicSynth;

IntuitivesResult synth_init(BasicSynth *synth, uint32_t sample_rate);
void synth_note_on(BasicSynth *synth, int32_t note, float velocity);
void synth_note_off(BasicSynth *synth);
Sample synth_process(BasicSynth *synth);
void synth_process_block(BasicSynth *synth, Sample *buffer, size_t frames);

// Quick melody generation from text/image
int32_t *intuitives_melody_from_text(const char *text, size_t *out_length);
int32_t *intuitives_melody_from_image(const uint8_t *rgb, size_t width,
                                      size_t height, size_t *out_length);

// Quick rhythm generation
bool *intuitives_rhythm_from_image(const uint8_t *lum, size_t width,
                                   size_t height, size_t *out_steps,
                                   size_t *out_tracks);

#ifdef __cplusplus
}
#endif
#endif
