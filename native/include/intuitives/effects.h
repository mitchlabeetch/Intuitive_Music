/**
 * INTUITIVES - Effects Module
 *
 * Professional audio effects with experimental twists.
 * Everything is permissible if it sounds cool.
 */

#ifndef INTUITIVES_EFFECTS_H
#define INTUITIVES_EFFECTS_H

#include "core.h"

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// FEATURE 8: STATE VARIABLE FILTER (Multi-mode filter)
// ============================================================================

typedef struct {
  FilterType type;
  float cutoff;                             // Cutoff frequency (Hz)
  float resonance;                          // Resonance (0-1)
  float lowpass, highpass, bandpass, notch; // Outputs
  float ic1eq, ic2eq;                       // Integrator states
  uint32_t sample_rate;
  float g, k; // Coefficients
} StateVariableFilter;

IntuitivesResult svf_init(StateVariableFilter *filter, uint32_t sample_rate);
void svf_set_cutoff(StateVariableFilter *filter, float cutoff);
void svf_set_resonance(StateVariableFilter *filter, float resonance);
void svf_set_type(StateVariableFilter *filter, FilterType type);
Sample svf_process(StateVariableFilter *filter, Sample input);
void svf_process_block(StateVariableFilter *filter, Sample *buffer,
                       size_t frames);

// ============================================================================
// FEATURE 9: MOOG LADDER FILTER
// ============================================================================

typedef struct {
  float cutoff;
  float resonance;
  float stage[4]; // 4-pole states
  float delay[4]; // Delay elements
  float tune;     // Tuning coefficient
  float res_quad; // Resonance coefficient
  uint32_t sample_rate;
  bool saturate; // Enable nonlinear saturation
} MoogFilter;

IntuitivesResult moog_init(MoogFilter *filter, uint32_t sample_rate);
void moog_set_cutoff(MoogFilter *filter, float cutoff);
void moog_set_resonance(MoogFilter *filter, float resonance);
Sample moog_process(MoogFilter *filter, Sample input);

// ============================================================================
// FEATURE 10: FORMANT FILTER (Vowel shaping)
// ============================================================================

typedef struct {
  float formants[5][3];           // 5 vowels, 3 formant frequencies each
  float vowel_blend;              // Current vowel position (0-4)
  StateVariableFilter filters[3]; // 3 parallel bandpass filters
  float filter_gains[3];
  uint32_t sample_rate;
} FormantFilter;

IntuitivesResult formant_init(FormantFilter *filter, uint32_t sample_rate);
void formant_set_vowel(FormantFilter *filter,
                       float vowel); // 0=A, 1=E, 2=I, 3=O, 4=U
void formant_set_custom(FormantFilter *filter, float f1, float f2, float f3);
Sample formant_process(FormantFilter *filter, Sample input);

// ============================================================================
// FEATURE 11: DELAY LINE (Multi-tap with feedback)
// ============================================================================

#define MAX_DELAY_TAPS 8
#define MAX_DELAY_SAMPLES (48000 * 5) // 5 seconds at 48kHz

typedef struct {
  float time;     // Delay time in seconds
  float feedback; // Feedback amount
  float pan;      // Stereo pan position
  bool active;
} DelayTap;

typedef struct {
  Sample *buffer;
  size_t buffer_size;
  size_t write_pos;
  DelayTap taps[MAX_DELAY_TAPS];
  uint32_t num_taps;
  float mix; // Dry/wet mix
  StateVariableFilter feedback_filter;
  float feedback_cutoff;
  uint32_t sample_rate;
  bool ping_pong; // Stereo ping-pong mode
} DelayLine;

IntuitivesResult delay_init(DelayLine *delay, uint32_t sample_rate,
                            float max_time);
void delay_free(DelayLine *delay);
void delay_add_tap(DelayLine *delay, float time, float feedback, float pan);
void delay_clear_taps(DelayLine *delay);
void delay_set_mix(DelayLine *delay, float mix);
void delay_process_stereo(DelayLine *delay, Sample *left, Sample *right,
                          size_t frames);

// ============================================================================
// FEATURE 12: ALGORITHMIC REVERB (Schroeder/Moorer)
// ============================================================================

#define REVERB_NUM_COMBS 8
#define REVERB_NUM_ALLPASS 4

typedef struct {
  Sample *buffer;
  size_t size;
  size_t pos;
} CombFilter;

typedef struct {
  Sample *buffer;
  size_t size;
  size_t pos;
  float gain;
} AllpassFilter;

typedef struct {
  CombFilter combs_l[REVERB_NUM_COMBS];
  CombFilter combs_r[REVERB_NUM_COMBS];
  AllpassFilter allpass_l[REVERB_NUM_ALLPASS];
  AllpassFilter allpass_r[REVERB_NUM_ALLPASS];
  float comb_feedback[REVERB_NUM_COMBS];
  float room_size;
  float damping;
  float width;
  float mix;
  float predelay;
  Sample *predelay_buffer;
  size_t predelay_size;
  size_t predelay_pos;
  StateVariableFilter damping_filter_l, damping_filter_r;
  uint32_t sample_rate;
} Reverb;

IntuitivesResult reverb_init(Reverb *rev, uint32_t sample_rate);
void reverb_free(Reverb *rev);
void reverb_set_room_size(Reverb *rev, float size);
void reverb_set_damping(Reverb *rev, float damping);
void reverb_set_width(Reverb *rev, float width);
void reverb_set_mix(Reverb *rev, float mix);
void reverb_process_stereo(Reverb *rev, Sample *left, Sample *right,
                           size_t frames);

// ============================================================================
// FEATURE 13: WAVESHAPER DISTORTION (Multiple algorithms)
// ============================================================================

typedef enum {
  DISTORT_SOFT_CLIP = 0,
  DISTORT_HARD_CLIP,
  DISTORT_TUBE,      // Valve simulation
  DISTORT_FOLDBACK,  // Wave folding
  DISTORT_BITCRUSH,  // Bit reduction
  DISTORT_RECTIFY,   // Full/half wave rectification
  DISTORT_CHEBYSHEV, // Polynomial waveshaping
  DISTORT_ASYMMETRIC // Asymmetric soft clip
} DistortionType;

typedef struct {
  DistortionType type;
  float drive;        // Input gain
  float mix;          // Dry/wet
  float tone;         // Post-distortion tone control
  float bias;         // DC offset for asymmetric distortion
  uint32_t bit_depth; // For bitcrusher (1-24)
  uint32_t order;     // For Chebyshev (1-8)
  StateVariableFilter tone_filter;
  uint32_t sample_rate;
} Distortion;

IntuitivesResult distortion_init(Distortion *dist, uint32_t sample_rate);
void distortion_set_type(Distortion *dist, DistortionType type);
void distortion_set_drive(Distortion *dist, float drive);
Sample distortion_process(Distortion *dist, Sample input);
void distortion_process_block(Distortion *dist, Sample *buffer, size_t frames);

// ============================================================================
// FEATURE 14: COMPRESSOR/LIMITER (with sidechain)
// ============================================================================

typedef enum {
  COMP_DOWNWARD = 0,
  COMP_UPWARD,
  COMP_PARALLEL,
  COMP_MULTIBAND
} CompressorType;

typedef struct {
  float threshold;    // Threshold in dB
  float ratio;        // Compression ratio
  float attack;       // Attack time (ms)
  float release;      // Release time (ms)
  float knee;         // Soft knee width (dB)
  float makeup;       // Makeup gain (dB)
  float envelope;     // Current envelope level
  float attack_coef;  // Calculated coefficient
  float release_coef; // Calculated coefficient
  CompressorType type;
  bool sidechain_enabled;
  StateVariableFilter sidechain_filter;
  float sidechain_cutoff;
  uint32_t sample_rate;
} Compressor;

IntuitivesResult compressor_init(Compressor *comp, uint32_t sample_rate);
void compressor_set_threshold(Compressor *comp, float threshold_db);
void compressor_set_ratio(Compressor *comp, float ratio);
void compressor_set_attack(Compressor *comp, float attack_ms);
void compressor_set_release(Compressor *comp, float release_ms);
Sample compressor_process(Compressor *comp, Sample input, Sample sidechain);
float compressor_get_gain_reduction(const Compressor *comp);

// ============================================================================
// FEATURE 15: CHORUS (Multi-voice modulation)
// ============================================================================

#define CHORUS_MAX_VOICES 8

typedef struct {
  Sample *buffer;
  size_t buffer_size;
  size_t write_pos;
  float rate;  // LFO rate (Hz)
  float depth; // Modulation depth (ms)
  float mix;   // Dry/wet
  float feedback;
  float phases[CHORUS_MAX_VOICES];
  float voice_pan[CHORUS_MAX_VOICES];
  uint32_t num_voices;
  uint32_t sample_rate;
} Chorus;

IntuitivesResult chorus_init(Chorus *chorus, uint32_t sample_rate,
                             uint32_t num_voices);
void chorus_free(Chorus *chorus);
void chorus_set_rate(Chorus *chorus, float rate);
void chorus_set_depth(Chorus *chorus, float depth);
void chorus_process_stereo(Chorus *chorus, Sample *left, Sample *right,
                           size_t frames);

// ============================================================================
// FEATURE 16: PHASER (All-pass cascade)
// ============================================================================

#define PHASER_MAX_STAGES 12

typedef struct {
  float a1[PHASER_MAX_STAGES];
  float zm1[PHASER_MAX_STAGES];
  float lfo_phase;
  float rate;  // LFO rate
  float depth; // Modulation depth
  float feedback;
  float min_freq, max_freq;
  uint32_t num_stages;
  float mix;
  uint32_t sample_rate;
} Phaser;

IntuitivesResult phaser_init(Phaser *phaser, uint32_t sample_rate,
                             uint32_t num_stages);
void phaser_set_rate(Phaser *phaser, float rate);
void phaser_set_depth(Phaser *phaser, float depth);
void phaser_set_feedback(Phaser *phaser, float feedback);
Sample phaser_process(Phaser *phaser, Sample input);

// ============================================================================
// FEATURE 17: BITCRUSHER (Lo-fi destruction)
// ============================================================================

typedef struct {
  uint32_t bit_depth;             // Target bit depth (1-24)
  uint32_t sample_rate_reduction; // Divide sample rate
  float mix;
  float dither;       // Dither amount
  Sample hold_sample; // S&H for rate reduction
  uint32_t hold_counter;
  uint32_t original_sample_rate;
} Bitcrusher;

IntuitivesResult bitcrusher_init(Bitcrusher *bc, uint32_t sample_rate);
void bitcrusher_set_bits(Bitcrusher *bc, uint32_t bits);
void bitcrusher_set_rate_reduction(Bitcrusher *bc, uint32_t factor);
Sample bitcrusher_process(Bitcrusher *bc, Sample input);

// ============================================================================
// EFFECT CHAIN
// ============================================================================

typedef union {
  StateVariableFilter filter;
  MoogFilter moog;
  FormantFilter formant;
  DelayLine delay;
  Reverb reverb;
  Distortion distortion;
  Compressor compressor;
  Chorus chorus;
  Phaser phaser;
  Bitcrusher bitcrusher;
} EffectUnion;

typedef struct {
  EffectType type;
  EffectUnion effect;
  bool bypass;
  float mix;
} EffectSlot;

typedef struct {
  EffectSlot slots[INTUITIVES_MAX_EFFECTS_PER_TRACK];
  uint32_t num_effects;
  uint32_t sample_rate;
} EffectChain;

IntuitivesResult effect_chain_init(EffectChain *chain, uint32_t sample_rate);
int32_t effect_chain_add(EffectChain *chain, EffectType type);
void effect_chain_remove(EffectChain *chain, uint32_t index);
void effect_chain_process(EffectChain *chain, Sample *left, Sample *right,
                          size_t frames);

#ifdef __cplusplus
}
#endif

#endif // INTUITIVES_EFFECTS_H
