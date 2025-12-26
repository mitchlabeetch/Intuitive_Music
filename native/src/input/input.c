/**
 * INTUITIVES - Input Processing Implementation
 * Convert any media to music.
 */

#include "intuitives/input.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

// ============================================================================
// IMAGE TO SPECTRUM
// ============================================================================

IntuitivesResult image_spectrum_init(ImageToSpectrum *its, uint32_t sr,
                                     size_t bins) {
  if (!its)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(its, 0, sizeof(ImageToSpectrum));
  its->sample_rate = sr;
  its->num_bins = bins;
  its->base_freq = 55.0f; // A1
  its->freq_scale = 8000.0f / bins;
  its->loop = true;

  its->phases = (float *)calloc(bins, sizeof(float));
  if (!its->phases)
    return INTUITIVES_ERROR_OUT_OF_MEMORY;

  return INTUITIVES_OK;
}

void image_spectrum_free(ImageToSpectrum *its) {
  if (its) {
    free(its->spectrum_data);
    free(its->phases);
  }
}

IntuitivesResult image_spectrum_load_rgb(ImageToSpectrum *its,
                                         const uint8_t *rgb, size_t width,
                                         size_t height) {
  if (!its || !rgb)
    return INTUITIVES_ERROR_NULL_POINTER;

  its->num_bins = width;
  its->num_frames = height;
  its->spectrum_data = (float *)malloc(width * height * sizeof(float));
  if (!its->spectrum_data)
    return INTUITIVES_ERROR_OUT_OF_MEMORY;

  // Convert RGB to luminance
  for (size_t y = 0; y < height; y++) {
    for (size_t x = 0; x < width; x++) {
      size_t idx = (y * width + x) * 3;
      float lum =
          (0.299f * rgb[idx] + 0.587f * rgb[idx + 1] + 0.114f * rgb[idx + 2]) /
          255.0f;
      its->spectrum_data[y * width + x] = lum;
    }
  }

  free(its->phases);
  its->phases = (float *)calloc(width, sizeof(float));

  return INTUITIVES_OK;
}

void image_spectrum_set_freq_range(ImageToSpectrum *its, float min_hz,
                                   float max_hz) {
  its->base_freq = min_hz;
  its->freq_scale = (max_hz - min_hz) / its->num_bins;
}

void image_spectrum_process(ImageToSpectrum *its, Sample *buffer,
                            size_t frames) {
  if (!its->spectrum_data || its->num_frames == 0) {
    memset(buffer, 0, frames * sizeof(Sample));
    return;
  }

  float frame_inc =
      (float)its->num_frames / (its->sample_rate * 4.0f); // 4 seconds per image

  for (size_t i = 0; i < frames; i++) {
    Sample out = 0.0f;
    size_t frame = its->current_frame % its->num_frames;

    // Additive synthesis from current row
    for (size_t bin = 0; bin < its->num_bins; bin++) {
      float amp = its->spectrum_data[frame * its->num_bins + bin];
      float freq = its->base_freq + bin * its->freq_scale;

      out += amp * sinf(its->phases[bin]);

      its->phases[bin] += INTUITIVES_TWO_PI * freq / its->sample_rate;
      if (its->phases[bin] > INTUITIVES_TWO_PI) {
        its->phases[bin] -= INTUITIVES_TWO_PI;
      }
    }

    buffer[i] = out / its->num_bins;

    // Advance frame (slowly)
    static float frame_accum = 0;
    frame_accum += frame_inc;
    if (frame_accum >= 1.0f) {
      its->current_frame++;
      if (its->loop && its->current_frame >= its->num_frames) {
        its->current_frame = 0;
      }
      frame_accum -= 1.0f;
    }
  }
}

// ============================================================================
// COLOR TO HARMONY
// ============================================================================

static void rgb_to_hsb(uint8_t r, uint8_t g, uint8_t b, float *h, float *s,
                       float *br) {
  float rf = r / 255.0f;
  float gf = g / 255.0f;
  float bf = b / 255.0f;

  float max = rf > gf ? (rf > bf ? rf : bf) : (gf > bf ? gf : bf);
  float min = rf < gf ? (rf < bf ? rf : bf) : (gf < bf ? gf : bf);
  float delta = max - min;

  *br = max;
  *s = max > 0 ? delta / max : 0;

  if (delta == 0) {
    *h = 0;
  } else if (max == rf) {
    *h = 60.0f * fmodf((gf - bf) / delta, 6.0f);
  } else if (max == gf) {
    *h = 60.0f * ((bf - rf) / delta + 2.0f);
  } else {
    *h = 60.0f * ((rf - gf) / delta + 4.0f);
  }
  if (*h < 0)
    *h += 360.0f;
}

void color_harmony_from_rgb(ColorHarmony *ch, uint8_t r, uint8_t g, uint8_t b,
                            int32_t octave) {
  rgb_to_hsb(r, g, b, &ch->hue, &ch->saturation, &ch->brightness);

  // Hue (0-360) -> root note (0-11)
  ch->root_note = (int32_t)(ch->hue / 30.0f) + octave * 12;

  // Saturation -> chord complexity
  // Low sat = simple (major/minor), high sat = complex (7ths, extensions)
  ch->num_notes = 3;
  ch->chord_notes[0] = ch->root_note;

  if (ch->brightness > 0.5f) {
    // Brighter = major
    ch->chord_notes[1] = ch->root_note + 4; // Major 3rd
    ch->chord_notes[2] = ch->root_note + 7; // Perfect 5th
  } else {
    // Darker = minor
    ch->chord_notes[1] = ch->root_note + 3; // Minor 3rd
    ch->chord_notes[2] = ch->root_note + 7; // Perfect 5th
  }

  if (ch->saturation > 0.5f) {
    // High saturation = add 7th
    ch->chord_notes[ch->num_notes++] =
        ch->root_note + (ch->brightness > 0.5f ? 11 : 10);
  }

  if (ch->saturation > 0.75f) {
    // Very high saturation = add 9th
    ch->chord_notes[ch->num_notes++] = ch->root_note + 14;
  }
}

// ============================================================================
// PIXEL RHYTHM
// ============================================================================

IntuitivesResult pixel_rhythm_init(PixelRhythm *pr, size_t width,
                                   size_t height) {
  if (!pr)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(pr, 0, sizeof(PixelRhythm));

  pr->width = width;
  pr->height = height;
  pr->threshold = 0.5f;
  pr->subdivision = 1;

  pr->pattern = (uint8_t *)calloc(width * height, sizeof(uint8_t));
  if (!pr->pattern)
    return INTUITIVES_ERROR_OUT_OF_MEMORY;

  return INTUITIVES_OK;
}

void pixel_rhythm_free(PixelRhythm *pr) {
  if (pr && pr->pattern) {
    free(pr->pattern);
    pr->pattern = NULL;
  }
}

IntuitivesResult pixel_rhythm_load(PixelRhythm *pr, const uint8_t *luminance) {
  if (!pr || !luminance)
    return INTUITIVES_ERROR_NULL_POINTER;
  memcpy(pr->pattern, luminance, pr->width * pr->height);
  return INTUITIVES_OK;
}

void pixel_rhythm_advance(PixelRhythm *pr) {
  pr->current_step = (pr->current_step + 1) % pr->width;
}

bool pixel_rhythm_get_trigger(PixelRhythm *pr, size_t track, float *velocity) {
  if (track >= pr->height)
    return false;

  uint8_t val = pr->pattern[track * pr->width + pr->current_step];
  float normalized = val / 255.0f;

  if (normalized > pr->threshold) {
    *velocity = normalized;
    return true;
  }
  return false;
}

// ============================================================================
// GESTURE ENVELOPE
// ============================================================================

void gesture_envelope_init(GestureEnvelope *ge, uint32_t sr) {
  memset(ge, 0, sizeof(GestureEnvelope));
  ge->sample_rate = sr;
  ge->attack = 0.01f;
  ge->decay = 0.2f;
  ge->sustain = 0.7f;
  ge->release = 0.3f;
}

void gesture_envelope_update(GestureEnvelope *ge, float x, float y, float z) {
  // Map gesture to ADSR
  ge->x = x;
  ge->y = y;
  ge->z = z;

  // X controls attack (left = fast, right = slow)
  ge->attack = 0.001f + x * 0.5f;

  // Y controls decay and sustain
  ge->decay = 0.05f + (1.0f - y) * 0.5f;
  ge->sustain = y;

  // Z controls release
  ge->release = 0.01f + z * 1.0f;

  // Recalculate coefficients
  ge->attack_coef = expf(-1.0f / (ge->attack * ge->sample_rate));
  ge->decay_coef = expf(-1.0f / (ge->decay * ge->sample_rate));
  ge->release_coef = expf(-1.0f / (ge->release * ge->sample_rate));
}

void gesture_envelope_gate_on(GestureEnvelope *ge) { ge->gate = true; }

void gesture_envelope_gate_off(GestureEnvelope *ge) { ge->gate = false; }

float gesture_envelope_process(GestureEnvelope *ge) {
  if (ge->gate) {
    if (ge->current_level < ge->sustain) {
      // Attack
      ge->current_level = 1.0f - ge->attack_coef * (1.0f - ge->current_level);
      if (ge->current_level >= 0.99f) {
        ge->current_level = 1.0f;
      }
    } else {
      // Decay to sustain
      ge->current_level =
          ge->sustain + ge->decay_coef * (ge->current_level - ge->sustain);
    }
  } else {
    // Release
    ge->current_level *= ge->release_coef;
  }

  return ge->current_level;
}

// ============================================================================
// MOTION FILTER
// ============================================================================

void motion_filter_init(MotionFilter *mf) {
  memset(mf, 0, sizeof(MotionFilter));
  mf->smoothing = 0.9f;
  mf->cutoff_range[0] = 100.0f;
  mf->cutoff_range[1] = 8000.0f;
  mf->resonance_range[0] = 0.1f;
  mf->resonance_range[1] = 0.9f;
}

void motion_filter_update(MotionFilter *mf, float x, float y) {
  // Smooth the input
  mf->x = mf->smoothing * mf->last_x + (1.0f - mf->smoothing) * x;
  mf->y = mf->smoothing * mf->last_y + (1.0f - mf->smoothing) * y;
  mf->last_x = mf->x;
  mf->last_y = mf->y;
}

void motion_filter_get_params(MotionFilter *mf, float *cutoff,
                              float *resonance) {
  // Logarithmic mapping for cutoff
  float log_min = logf(mf->cutoff_range[0]);
  float log_max = logf(mf->cutoff_range[1]);
  *cutoff = expf(log_min + mf->x * (log_max - log_min));

  // Linear mapping for resonance
  *resonance = mf->resonance_range[0] +
               mf->y * (mf->resonance_range[1] - mf->resonance_range[0]);
}

// ============================================================================
// TEXT TO MELODY
// ============================================================================

void text_melody_init(TextMelody *tm, const char *text) {
  memset(tm, 0, sizeof(TextMelody));
  tm->text = text;
  tm->length = strlen(text);
  tm->octave_base = 4;
  tm->use_modulo_mapping = true;

  // Default: major scale
  static const int32_t major[] = {0, 2, 4, 5, 7, 9, 11};
  memcpy(tm->scale, major, 7 * sizeof(int32_t));
  tm->scale_size = 7;
}

void text_melody_set_scale(TextMelody *tm, const int32_t *scale, size_t size) {
  tm->scale_size = size > 12 ? 12 : size;
  memcpy(tm->scale, scale, tm->scale_size * sizeof(int32_t));
}

int32_t text_melody_next_note(TextMelody *tm) {
  if (tm->position >= tm->length) {
    tm->position = 0;
  }

  char c = tm->text[tm->position++];

  if (tm->use_modulo_mapping) {
    // Map to scale
    int32_t degree = ((int32_t)c) % tm->scale_size;
    int32_t octave = tm->octave_base + (((int32_t)c) / tm->scale_size) % 3 - 1;
    return octave * 12 + tm->scale[degree];
  } else {
    // Direct ASCII mapping
    return 36 + (c % 48); // 4 octave range
  }
}

void text_melody_get_sequence(TextMelody *tm, int32_t *notes, size_t *count,
                              size_t max) {
  tm->position = 0;
  *count = 0;

  while (tm->position < tm->length && *count < max) {
    notes[(*count)++] = text_melody_next_note(tm);
  }
}

// ============================================================================
// RANDOM WALK
// ============================================================================

static inline uint32_t xorshift32(uint32_t *state) {
  uint32_t x = *state;
  x ^= x << 13;
  x ^= x >> 17;
  x ^= x << 5;
  *state = x;
  return x;
}

static inline float random_float(uint32_t *state) {
  return (float)xorshift32(state) / (float)UINT32_MAX;
}

IntuitivesResult random_walk_init(RandomWalk *rw, int32_t start, int32_t min,
                                  int32_t max, uint32_t seed) {
  if (!rw)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(rw, 0, sizeof(RandomWalk));

  rw->current_note = start;
  rw->min_note = min;
  rw->max_note = max;
  rw->max_step = 5;
  rw->step_bias = 0.0f;
  rw->random_state = seed ? seed : 12345;

  // Default pentatonic scale
  static const int32_t penta[] = {0, 2, 4, 7, 9};
  memcpy(rw->scale, penta, 5 * sizeof(int32_t));
  rw->scale_size = 5;
  rw->quantize_to_scale = true;

  return INTUITIVES_OK;
}

void random_walk_set_scale(RandomWalk *rw, const int32_t *scale, size_t size) {
  rw->scale_size = size > 12 ? 12 : size;
  memcpy(rw->scale, scale, rw->scale_size * sizeof(int32_t));
}

static int32_t quantize_to_scale(int32_t note, const int32_t *scale,
                                 size_t size) {
  int32_t octave = note / 12;
  int32_t degree = note % 12;

  // Find closest scale degree
  int32_t closest = scale[0];
  int32_t min_dist = 12;

  for (size_t i = 0; i < size; i++) {
    int32_t dist = abs(scale[i] - degree);
    if (dist < min_dist) {
      min_dist = dist;
      closest = scale[i];
    }
  }

  return octave * 12 + closest;
}

int32_t random_walk_next(RandomWalk *rw) {
  // Random step
  float r = random_float(&rw->random_state);
  int32_t step =
      (int32_t)((r - 0.5f + rw->step_bias * 0.5f) * 2.0f * rw->max_step);

  rw->current_note += step;

  // Clamp to range
  if (rw->current_note < rw->min_note)
    rw->current_note = rw->min_note;
  if (rw->current_note > rw->max_note)
    rw->current_note = rw->max_note;

  // Quantize if needed
  if (rw->quantize_to_scale && rw->scale_size > 0) {
    return quantize_to_scale(rw->current_note, rw->scale, rw->scale_size);
  }

  return rw->current_note;
}

void random_walk_sequence(RandomWalk *rw, int32_t *notes, size_t count) {
  for (size_t i = 0; i < count; i++) {
    notes[i] = random_walk_next(rw);
  }
}

// ============================================================================
// EMOJI DRUMS
// ============================================================================

void emoji_drums_init(EmojiDrums *ed) { memset(ed, 0, sizeof(EmojiDrums)); }

void emoji_drums_set_default_mappings(EmojiDrums *ed) {
  // Common emoji codepoints for drums
  // These are simplified mappings - real emoji handling is more complex

  // Faces -> Kick
  for (int i = 0; i < 20; i++) {
    ed->emoji_map[i] = DRUM_KICK;
  }

  // Hands -> Snare
  for (int i = 20; i < 40; i++) {
    ed->emoji_map[i] = DRUM_SNARE;
  }

  // Objects -> Hi-hat
  for (int i = 40; i < 60; i++) {
    ed->emoji_map[i] = DRUM_HIHAT;
  }

  // Nature -> Toms
  for (int i = 60; i < 80; i++) {
    ed->emoji_map[i] = DRUM_TOM_MID;
  }

  // Symbols -> Crash/Ride
  for (int i = 80; i < 100; i++) {
    ed->emoji_map[i] = DRUM_CRASH;
  }
}

DrumType emoji_drums_get(EmojiDrums *ed, uint32_t codepoint) {
  // Simple hash to bucket
  uint32_t bucket = codepoint % 128;
  return (DrumType)ed->emoji_map[bucket];
}

void emoji_drums_parse_sequence(EmojiDrums *ed, const char *utf8,
                                DrumType *drums, size_t *count, size_t max) {
  *count = 0;
  const uint8_t *p = (const uint8_t *)utf8;

  while (*p && *count < max) {
    uint32_t codepoint;

    // Simplified UTF-8 decoding
    if ((*p & 0x80) == 0) {
      codepoint = *p++;
    } else if ((*p & 0xE0) == 0xC0) {
      codepoint = (*p++ & 0x1F) << 6;
      codepoint |= (*p++ & 0x3F);
    } else if ((*p & 0xF0) == 0xE0) {
      codepoint = (*p++ & 0x0F) << 12;
      codepoint |= (*p++ & 0x3F) << 6;
      codepoint |= (*p++ & 0x3F);
    } else if ((*p & 0xF8) == 0xF0) {
      codepoint = (*p++ & 0x07) << 18;
      codepoint |= (*p++ & 0x3F) << 12;
      codepoint |= (*p++ & 0x3F) << 6;
      codepoint |= (*p++ & 0x3F);
    } else {
      p++;
      continue;
    }

    drums[(*count)++] = emoji_drums_get(ed, codepoint);
  }
}
