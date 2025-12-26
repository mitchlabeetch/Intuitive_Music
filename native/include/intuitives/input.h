/**
 * INTUITIVES - Input Module
 * Convert ANY media into music - images, gestures, text.
 */

#ifndef INTUITIVES_INPUT_H
#define INTUITIVES_INPUT_H

#include "core.h"

#ifdef __cplusplus
extern "C" {
#endif

// FEATURE 27: IMAGE TO SPECTRUM (Additive synthesis from image rows)
typedef struct {
  float *spectrum_data; // Amplitude data per frequency bin
  size_t num_bins;      // Number of frequency bins (image width)
  size_t num_frames;    // Number of time frames (image height)
  size_t current_frame;
  float *phases;    // Oscillator phases
  float base_freq;  // Lowest frequency bin
  float freq_scale; // Hz per bin
  uint32_t sample_rate;
  bool loop;
} ImageToSpectrum;

IntuitivesResult image_spectrum_init(ImageToSpectrum *its, uint32_t sr,
                                     size_t bins);
void image_spectrum_free(ImageToSpectrum *its);
IntuitivesResult image_spectrum_load_rgb(ImageToSpectrum *its,
                                         const uint8_t *rgb, size_t width,
                                         size_t height);
IntuitivesResult image_spectrum_load_luminance(ImageToSpectrum *its,
                                               const float *lum, size_t width,
                                               size_t height);
void image_spectrum_set_freq_range(ImageToSpectrum *its, float min_hz,
                                   float max_hz);
void image_spectrum_process(ImageToSpectrum *its, Sample *buffer,
                            size_t frames);

// FEATURE 28: COLOR TO HARMONY (RGB values to chord intervals)
typedef struct {
  float hue, saturation, brightness;
  int32_t root_note;
  int32_t chord_notes[8];
  size_t num_notes;
} ColorHarmony;

void color_harmony_from_rgb(ColorHarmony *ch, uint8_t r, uint8_t g, uint8_t b,
                            int32_t octave);
void color_harmony_from_hsb(ColorHarmony *ch, float h, float s, float b,
                            int32_t octave);
// Hue -> root note, Saturation -> chord complexity, Brightness -> octave

// FEATURE 29: PIXEL RHYTHM (Image brightness to trigger patterns)
typedef struct {
  uint8_t *pattern; // Brightness values as velocity triggers
  size_t width;     // Steps per bar
  size_t height;    // Number of tracks/voices
  size_t current_step;
  float threshold;      // Brightness threshold for trigger
  uint32_t subdivision; // Ticks per step
} PixelRhythm;

IntuitivesResult pixel_rhythm_init(PixelRhythm *pr, size_t width,
                                   size_t height);
void pixel_rhythm_free(PixelRhythm *pr);
IntuitivesResult pixel_rhythm_load(PixelRhythm *pr, const uint8_t *luminance);
void pixel_rhythm_advance(PixelRhythm *pr);
bool pixel_rhythm_get_trigger(PixelRhythm *pr, size_t track, float *velocity);

// FEATURE 30: GESTURE ENVELOPE (Hand position to ADSR)
typedef struct {
  float x, y, z; // Normalized position (0-1)
  float attack, decay, sustain, release;
  float current_level;
  bool gate;
  uint32_t sample_rate;
  float attack_coef, decay_coef, release_coef;
} GestureEnvelope;

void gesture_envelope_init(GestureEnvelope *ge, uint32_t sr);
void gesture_envelope_update(GestureEnvelope *ge, float x, float y, float z);
// X -> attack, Y -> decay/sustain, Z -> release
void gesture_envelope_gate_on(GestureEnvelope *ge);
void gesture_envelope_gate_off(GestureEnvelope *ge);
float gesture_envelope_process(GestureEnvelope *ge);

// FEATURE 31: MOTION FILTER (Head/hand tracking to filter)
typedef struct {
  float x, y;               // Normalized position (0-1)
  float smoothing;          // Position smoothing
  float cutoff_range[2];    // Min/max cutoff
  float resonance_range[2]; // Min/max resonance
  float last_x, last_y;
} MotionFilter;

void motion_filter_init(MotionFilter *mf);
void motion_filter_update(MotionFilter *mf, float x, float y);
void motion_filter_get_params(MotionFilter *mf, float *cutoff,
                              float *resonance);

// FEATURE 32: TEXT TO MELODY (ASCII values to MIDI notes)
typedef struct {
  const char *text;
  size_t length;
  size_t position;
  int32_t scale[12];
  size_t scale_size;
  int32_t octave_base;
  bool use_modulo_mapping; // Wrap to scale or use raw values
} TextMelody;

void text_melody_init(TextMelody *tm, const char *text);
void text_melody_set_scale(TextMelody *tm, const int32_t *scale, size_t size);
int32_t text_melody_next_note(TextMelody *tm);
void text_melody_get_sequence(TextMelody *tm, int32_t *notes, size_t *count,
                              size_t max);

// FEATURE 33: RANDOM WALK GENERATOR (Bounded random walk)
typedef struct {
  int32_t current_note;
  int32_t min_note, max_note;
  int32_t max_step; // Maximum interval
  float step_bias;  // Tendency up (+) or down (-)
  int32_t scale[12];
  size_t scale_size;
  bool quantize_to_scale;
  uint32_t random_state;
} RandomWalk;

IntuitivesResult random_walk_init(RandomWalk *rw, int32_t start, int32_t min,
                                  int32_t max, uint32_t seed);
void random_walk_set_scale(RandomWalk *rw, const int32_t *scale, size_t size);
int32_t random_walk_next(RandomWalk *rw);
void random_walk_sequence(RandomWalk *rw, int32_t *notes, size_t count);

// FEATURE 34: EMOJI DRUMS (Emoji characters to drum sounds)
typedef enum {
  DRUM_KICK = 0,
  DRUM_SNARE,
  DRUM_HIHAT,
  DRUM_CLAP,
  DRUM_TOM_LOW,
  DRUM_TOM_MID,
  DRUM_TOM_HIGH,
  DRUM_CRASH,
  DRUM_RIDE,
  DRUM_PERC,
  DRUM_COUNT
} DrumType;

typedef struct {
  uint32_t emoji_map[128]; // Map emoji codepoints to drum type
} EmojiDrums;

void emoji_drums_init(EmojiDrums *ed);
void emoji_drums_set_default_mappings(EmojiDrums *ed);
DrumType emoji_drums_get(EmojiDrums *ed, uint32_t codepoint);
void emoji_drums_parse_sequence(EmojiDrums *ed, const char *utf8,
                                DrumType *drums, size_t *count, size_t max);

#ifdef __cplusplus
}
#endif
#endif
