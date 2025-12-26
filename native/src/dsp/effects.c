/**
 * INTUITIVES - Effects Implementations
 * Professional audio effects with experimental features.
 */

#include "intuitives/effects.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

// ============================================================================
// STATE VARIABLE FILTER
// ============================================================================

IntuitivesResult svf_init(StateVariableFilter *filter, uint32_t sample_rate) {
  if (!filter)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(filter, 0, sizeof(StateVariableFilter));
  filter->sample_rate = sample_rate;
  filter->type = FILTER_LOWPASS;
  filter->cutoff = 1000.0f;
  filter->resonance = 0.5f;
  svf_set_cutoff(filter, filter->cutoff);
  return INTUITIVES_OK;
}

void svf_set_cutoff(StateVariableFilter *filter, float cutoff) {
  filter->cutoff = INTUITIVES_CLAMP(cutoff, 20.0f, filter->sample_rate * 0.49f);
  filter->g = tanf(INTUITIVES_PI * filter->cutoff / filter->sample_rate);
  filter->k = 2.0f - 2.0f * filter->resonance;
}

void svf_set_resonance(StateVariableFilter *filter, float resonance) {
  filter->resonance = INTUITIVES_CLAMP(resonance, 0.0f, 1.0f);
  filter->k = 2.0f - 2.0f * filter->resonance;
}

Sample svf_process(StateVariableFilter *filter, Sample input) {
  float v0 = input;
  float v1 = filter->ic1eq;
  float v2 = filter->ic2eq;
  float g = filter->g;
  float k = filter->k;

  float v3 = v0 - v2;
  float v1_new = g * v3 + v1;
  v1_new = v1_new / (1.0f + g * (g + k));
  v1_new = g * v3 / (1.0f + g * (g + k)) + v1;

  float hp = (v0 - k * v1_new - v2) / (1.0f + g * (g + k));
  float bp = g * hp + v1;
  float lp = g * bp + v2;

  filter->ic1eq = 2.0f * bp - v1;
  filter->ic2eq = 2.0f * lp - v2;

  filter->lowpass = lp;
  filter->highpass = hp;
  filter->bandpass = bp;
  filter->notch = hp + lp;

  switch (filter->type) {
  case FILTER_LOWPASS:
    return lp;
  case FILTER_HIGHPASS:
    return hp;
  case FILTER_BANDPASS:
    return bp;
  case FILTER_NOTCH:
    return filter->notch;
  default:
    return lp;
  }
}

void svf_process_block(StateVariableFilter *filter, Sample *buffer,
                       size_t frames) {
  for (size_t i = 0; i < frames; i++) {
    buffer[i] = svf_process(filter, buffer[i]);
  }
}

// ============================================================================
// MOOG LADDER FILTER
// ============================================================================

IntuitivesResult moog_init(MoogFilter *filter, uint32_t sample_rate) {
  if (!filter)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(filter, 0, sizeof(MoogFilter));
  filter->sample_rate = sample_rate;
  filter->cutoff = 1000.0f;
  filter->resonance = 0.0f;
  filter->saturate = true;
  moog_set_cutoff(filter, filter->cutoff);
  return INTUITIVES_OK;
}

void moog_set_cutoff(MoogFilter *filter, float cutoff) {
  filter->cutoff = INTUITIVES_CLAMP(cutoff, 20.0f, filter->sample_rate * 0.45f);
  float fc = filter->cutoff / filter->sample_rate;
  filter->tune = 1.16f * fc;
}

void moog_set_resonance(MoogFilter *filter, float resonance) {
  filter->resonance = INTUITIVES_CLAMP(resonance, 0.0f, 1.0f);
  filter->res_quad = 4.0f * filter->resonance * (1.0f + 0.22f * filter->tune);
}

Sample moog_process(MoogFilter *filter, Sample input) {
  float in = input - filter->res_quad * filter->delay[3];

  if (filter->saturate) {
    in = intuitives_fast_tanh(in);
  }

  filter->stage[0] =
      in * filter->tune + filter->delay[0] * (1.0f - filter->tune);
  filter->delay[0] = filter->stage[0];

  for (int i = 1; i < 4; i++) {
    filter->stage[i] = filter->stage[i - 1] * filter->tune +
                       filter->delay[i] * (1.0f - filter->tune);
    filter->delay[i] = filter->stage[i];
  }

  return filter->stage[3];
}

// ============================================================================
// FORMANT FILTER (Vowel shaping)
// ============================================================================

// Vowel formant frequencies: A, E, I, O, U
static const float VOWEL_FORMANTS[5][3] = {
    {800.0f, 1150.0f, 2900.0f}, // A
    {350.0f, 2000.0f, 2800.0f}, // E
    {270.0f, 2140.0f, 2950.0f}, // I
    {450.0f, 800.0f, 2830.0f},  // O
    {325.0f, 700.0f, 2700.0f}   // U
};

IntuitivesResult formant_init(FormantFilter *filter, uint32_t sample_rate) {
  if (!filter)
    return INTUITIVES_ERROR_NULL_POINTER;
  filter->sample_rate = sample_rate;
  filter->vowel_blend = 0.0f;

  for (int i = 0; i < 5; i++) {
    for (int j = 0; j < 3; j++) {
      filter->formants[i][j] = VOWEL_FORMANTS[i][j];
    }
  }

  for (int i = 0; i < 3; i++) {
    svf_init(&filter->filters[i], sample_rate);
    filter->filters[i].type = FILTER_BANDPASS;
    filter->filter_gains[i] = 1.0f / 3.0f;
  }

  formant_set_vowel(filter, 0.0f);
  return INTUITIVES_OK;
}

void formant_set_vowel(FormantFilter *filter, float vowel) {
  filter->vowel_blend = INTUITIVES_CLAMP(vowel, 0.0f, 4.0f);

  int v1 = (int)filter->vowel_blend;
  int v2 = v1 + 1;
  if (v2 > 4)
    v2 = 4;
  float frac = filter->vowel_blend - (float)v1;

  for (int i = 0; i < 3; i++) {
    float f =
        INTUITIVES_LERP(filter->formants[v1][i], filter->formants[v2][i], frac);
    svf_set_cutoff(&filter->filters[i], f);
    svf_set_resonance(&filter->filters[i], 0.8f);
  }
}

Sample formant_process(FormantFilter *filter, Sample input) {
  Sample out = 0.0f;
  for (int i = 0; i < 3; i++) {
    out += svf_process(&filter->filters[i], input) * filter->filter_gains[i];
  }
  return out;
}

// ============================================================================
// DELAY LINE
// ============================================================================

IntuitivesResult delay_init(DelayLine *delay, uint32_t sample_rate,
                            float max_time) {
  if (!delay)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(delay, 0, sizeof(DelayLine));

  delay->sample_rate = sample_rate;
  delay->buffer_size = (size_t)(max_time * sample_rate) + 1;
  delay->buffer = (Sample *)calloc(delay->buffer_size, sizeof(Sample));
  if (!delay->buffer)
    return INTUITIVES_ERROR_OUT_OF_MEMORY;

  delay->mix = 0.5f;
  svf_init(&delay->feedback_filter, sample_rate);
  delay->feedback_cutoff = 5000.0f;
  svf_set_cutoff(&delay->feedback_filter, delay->feedback_cutoff);

  return INTUITIVES_OK;
}

void delay_free(DelayLine *delay) {
  if (delay && delay->buffer) {
    free(delay->buffer);
    delay->buffer = NULL;
  }
}

void delay_add_tap(DelayLine *delay, float time, float feedback, float pan) {
  if (delay->num_taps >= MAX_DELAY_TAPS)
    return;

  delay->taps[delay->num_taps].time = time;
  delay->taps[delay->num_taps].feedback = feedback;
  delay->taps[delay->num_taps].pan = pan;
  delay->taps[delay->num_taps].active = true;
  delay->num_taps++;
}

void delay_process_stereo(DelayLine *delay, Sample *left, Sample *right,
                          size_t frames) {
  for (size_t i = 0; i < frames; i++) {
    Sample mono_in = (left[i] + right[i]) * 0.5f;

    // Write to buffer
    delay->buffer[delay->write_pos] = mono_in;

    // Read from taps
    Sample delayed_l = 0.0f;
    Sample delayed_r = 0.0f;

    for (uint32_t t = 0; t < delay->num_taps; t++) {
      if (!delay->taps[t].active)
        continue;

      size_t delay_samples = (size_t)(delay->taps[t].time * delay->sample_rate);
      size_t read_pos =
          (delay->write_pos + delay->buffer_size - delay_samples) %
          delay->buffer_size;

      Sample tap_out = delay->buffer[read_pos] * delay->taps[t].feedback;
      tap_out = svf_process(&delay->feedback_filter, tap_out);

      delayed_l += tap_out * (1.0f - delay->taps[t].pan);
      delayed_r += tap_out * delay->taps[t].pan;
    }

    // Mix
    left[i] = INTUITIVES_LERP(left[i], delayed_l, delay->mix);
    right[i] = INTUITIVES_LERP(right[i], delayed_r, delay->mix);

    // Add feedback to buffer
    delay->buffer[delay->write_pos] += (delayed_l + delayed_r) * 0.5f;

    delay->write_pos = (delay->write_pos + 1) % delay->buffer_size;
  }
}

// ============================================================================
// REVERB (Schroeder/Moorer algorithm)
// ============================================================================

static const size_t COMB_LENGTHS[] = {1557, 1617, 1491, 1422,
                                      1277, 1356, 1188, 1116};
static const size_t ALLPASS_LENGTHS[] = {225, 556, 441, 341};

IntuitivesResult reverb_init(Reverb *rev, uint32_t sample_rate) {
  if (!rev)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(rev, 0, sizeof(Reverb));
  rev->sample_rate = sample_rate;

  float scale = (float)sample_rate / 44100.0f;

  // Initialize comb filters
  for (int i = 0; i < REVERB_NUM_COMBS; i++) {
    size_t size = (size_t)(COMB_LENGTHS[i] * scale);
    rev->combs_l[i].buffer = (Sample *)calloc(size, sizeof(Sample));
    rev->combs_r[i].buffer = (Sample *)calloc(size, sizeof(Sample));
    rev->combs_l[i].size = size;
    rev->combs_r[i].size = size;
    rev->comb_feedback[i] = 0.84f;
  }

  // Initialize allpass filters
  for (int i = 0; i < REVERB_NUM_ALLPASS; i++) {
    size_t size = (size_t)(ALLPASS_LENGTHS[i] * scale);
    rev->allpass_l[i].buffer = (Sample *)calloc(size, sizeof(Sample));
    rev->allpass_r[i].buffer = (Sample *)calloc(size, sizeof(Sample));
    rev->allpass_l[i].size = size;
    rev->allpass_r[i].size = size;
    rev->allpass_l[i].gain = 0.5f;
    rev->allpass_r[i].gain = 0.5f;
  }

  rev->room_size = 0.5f;
  rev->damping = 0.5f;
  rev->width = 1.0f;
  rev->mix = 0.3f;

  svf_init(&rev->damping_filter_l, sample_rate);
  svf_init(&rev->damping_filter_r, sample_rate);
  svf_set_cutoff(&rev->damping_filter_l, 4000.0f);
  svf_set_cutoff(&rev->damping_filter_r, 4000.0f);

  return INTUITIVES_OK;
}

void reverb_free(Reverb *rev) {
  if (!rev)
    return;
  for (int i = 0; i < REVERB_NUM_COMBS; i++) {
    free(rev->combs_l[i].buffer);
    free(rev->combs_r[i].buffer);
  }
  for (int i = 0; i < REVERB_NUM_ALLPASS; i++) {
    free(rev->allpass_l[i].buffer);
    free(rev->allpass_r[i].buffer);
  }
  free(rev->predelay_buffer);
}

static inline Sample comb_process(CombFilter *comb, Sample input,
                                  float feedback, StateVariableFilter *damp) {
  Sample delayed = comb->buffer[comb->pos];
  Sample filtered = svf_process(damp, delayed);
  comb->buffer[comb->pos] = input + filtered * feedback;
  comb->pos = (comb->pos + 1) % comb->size;
  return delayed;
}

static inline Sample allpass_process(AllpassFilter *ap, Sample input) {
  Sample delayed = ap->buffer[ap->pos];
  Sample out = -input + delayed;
  ap->buffer[ap->pos] = input + delayed * ap->gain;
  ap->pos = (ap->pos + 1) % ap->size;
  return out;
}

void reverb_process_stereo(Reverb *rev, Sample *left, Sample *right,
                           size_t frames) {
  float feedback = 0.7f + rev->room_size * 0.28f;

  for (size_t i = 0; i < frames; i++) {
    Sample in_l = left[i];
    Sample in_r = right[i];
    Sample mono = (in_l + in_r) * 0.5f;

    // Parallel comb filters
    Sample comb_out_l = 0.0f;
    Sample comb_out_r = 0.0f;

    for (int c = 0; c < REVERB_NUM_COMBS; c++) {
      comb_out_l += comb_process(&rev->combs_l[c], mono, feedback,
                                 &rev->damping_filter_l);
      comb_out_r += comb_process(&rev->combs_r[c], mono, feedback,
                                 &rev->damping_filter_r);
    }

    comb_out_l /= REVERB_NUM_COMBS;
    comb_out_r /= REVERB_NUM_COMBS;

    // Series allpass filters
    Sample ap_out_l = comb_out_l;
    Sample ap_out_r = comb_out_r;

    for (int a = 0; a < REVERB_NUM_ALLPASS; a++) {
      ap_out_l = allpass_process(&rev->allpass_l[a], ap_out_l);
      ap_out_r = allpass_process(&rev->allpass_r[a], ap_out_r);
    }

    // Stereo width
    Sample wet_l = ap_out_l + ap_out_r * (1.0f - rev->width);
    Sample wet_r = ap_out_r + ap_out_l * (1.0f - rev->width);

    // Mix
    left[i] = INTUITIVES_LERP(in_l, wet_l, rev->mix);
    right[i] = INTUITIVES_LERP(in_r, wet_r, rev->mix);
  }
}

// ============================================================================
// DISTORTION
// ============================================================================

IntuitivesResult distortion_init(Distortion *dist, uint32_t sample_rate) {
  if (!dist)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(dist, 0, sizeof(Distortion));
  dist->sample_rate = sample_rate;
  dist->type = DISTORT_SOFT_CLIP;
  dist->drive = 1.0f;
  dist->mix = 1.0f;
  dist->bit_depth = 8;
  dist->order = 3;
  svf_init(&dist->tone_filter, sample_rate);
  svf_set_cutoff(&dist->tone_filter, 8000.0f);
  return INTUITIVES_OK;
}

static Sample chebyshev(Sample x, int order) {
  switch (order) {
  case 1:
    return x;
  case 2:
    return 2 * x * x - 1;
  case 3:
    return 4 * x * x * x - 3 * x;
  case 4:
    return 8 * x * x * x * x - 8 * x * x + 1;
  case 5:
    return 16 * x * x * x * x * x - 20 * x * x * x + 5 * x;
  default:
    return x;
  }
}

Sample distortion_process(Distortion *dist, Sample input) {
  Sample in = input * dist->drive;
  Sample out;

  switch (dist->type) {
  case DISTORT_SOFT_CLIP:
    out = intuitives_fast_tanh(in);
    break;

  case DISTORT_HARD_CLIP:
    out = INTUITIVES_CLAMP(in, -1.0f, 1.0f);
    break;

  case DISTORT_TUBE:
    // Soft asymmetric tube saturation
    if (in >= 0) {
      out = 1.0f - expf(-in);
    } else {
      out = -1.0f + expf(in);
    }
    out = out * 0.9f + in * 0.1f;
    break;

  case DISTORT_FOLDBACK: {
    // Wave folding
    float threshold = 1.0f;
    while (in > threshold || in < -threshold) {
      if (in > threshold)
        in = 2 * threshold - in;
      if (in < -threshold)
        in = -2 * threshold - in;
    }
    out = in;
    break;
  }

  case DISTORT_BITCRUSH: {
    float quant = powf(2.0f, (float)dist->bit_depth - 1);
    out = roundf(in * quant) / quant;
    break;
  }

  case DISTORT_RECTIFY:
    out = fabsf(in);
    break;

  case DISTORT_CHEBYSHEV:
    out = chebyshev(INTUITIVES_CLAMP(in, -1.0f, 1.0f), dist->order);
    break;

  case DISTORT_ASYMMETRIC:
    out = intuitives_fast_tanh(in + dist->bias) -
          intuitives_fast_tanh(dist->bias);
    break;

  default:
    out = in;
  }

  // Tone control
  out = svf_process(&dist->tone_filter, out);

  return INTUITIVES_LERP(input, out, dist->mix);
}

// ============================================================================
// COMPRESSOR
// ============================================================================

IntuitivesResult compressor_init(Compressor *comp, uint32_t sample_rate) {
  if (!comp)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(comp, 0, sizeof(Compressor));
  comp->sample_rate = sample_rate;
  comp->threshold = -20.0f;
  comp->ratio = 4.0f;
  comp->attack = 10.0f;
  comp->release = 100.0f;
  comp->knee = 6.0f;
  comp->makeup = 0.0f;
  compressor_set_attack(comp, comp->attack);
  compressor_set_release(comp, comp->release);
  return INTUITIVES_OK;
}

void compressor_set_attack(Compressor *comp, float attack_ms) {
  comp->attack = attack_ms;
  comp->attack_coef = expf(-1.0f / (comp->attack * 0.001f * comp->sample_rate));
}

void compressor_set_release(Compressor *comp, float release_ms) {
  comp->release = release_ms;
  comp->release_coef =
      expf(-1.0f / (comp->release * 0.001f * comp->sample_rate));
}

Sample compressor_process(Compressor *comp, Sample input, Sample sidechain) {
  // Detect level
  float level_db = INTUITIVES_LINEAR_TO_DB(fabsf(sidechain));

  // Calculate gain reduction
  float gain_db = 0.0f;
  float over_db = level_db - comp->threshold;

  if (over_db > 0.0f) {
    // Soft knee
    if (over_db < comp->knee) {
      over_db = over_db * over_db / (2.0f * comp->knee);
    }
    gain_db = over_db * (1.0f - 1.0f / comp->ratio);
  }

  // Envelope follower
  float target = gain_db;
  if (target > comp->envelope) {
    comp->envelope = comp->attack_coef * (comp->envelope - target) + target;
  } else {
    comp->envelope = comp->release_coef * (comp->envelope - target) + target;
  }

  // Apply gain
  float gain = INTUITIVES_DB_TO_LINEAR(-comp->envelope + comp->makeup);
  return input * gain;
}

// ============================================================================
// CHORUS
// ============================================================================

IntuitivesResult chorus_init(Chorus *chorus, uint32_t sample_rate,
                             uint32_t num_voices) {
  if (!chorus)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(chorus, 0, sizeof(Chorus));

  chorus->sample_rate = sample_rate;
  chorus->buffer_size = (size_t)(sample_rate * 0.1f); // 100ms max delay
  chorus->buffer = (Sample *)calloc(chorus->buffer_size, sizeof(Sample));
  if (!chorus->buffer)
    return INTUITIVES_ERROR_OUT_OF_MEMORY;

  chorus->num_voices =
      num_voices > CHORUS_MAX_VOICES ? CHORUS_MAX_VOICES : num_voices;
  chorus->rate = 0.5f;
  chorus->depth = 0.003f; // 3ms modulation
  chorus->mix = 0.5f;

  // Distribute phases and pans
  for (uint32_t i = 0; i < chorus->num_voices; i++) {
    chorus->phases[i] = (float)i / (float)chorus->num_voices;
    chorus->voice_pan[i] = (float)i / (float)(chorus->num_voices - 1);
  }

  return INTUITIVES_OK;
}

void chorus_free(Chorus *chorus) {
  if (chorus && chorus->buffer) {
    free(chorus->buffer);
    chorus->buffer = NULL;
  }
}

void chorus_process_stereo(Chorus *chorus, Sample *left, Sample *right,
                           size_t frames) {
  float phase_inc = chorus->rate / (float)chorus->sample_rate;

  for (size_t i = 0; i < frames; i++) {
    Sample in = (left[i] + right[i]) * 0.5f;

    // Write to buffer
    chorus->buffer[chorus->write_pos] = in;

    Sample out_l = 0.0f;
    Sample out_r = 0.0f;

    for (uint32_t v = 0; v < chorus->num_voices; v++) {
      // LFO modulation
      float lfo = 0.5f + 0.5f * sinf(chorus->phases[v] * INTUITIVES_TWO_PI);
      float delay_time = 0.005f + chorus->depth * lfo; // Base + modulated delay

      // Read from buffer with interpolation
      float delay_samples = delay_time * chorus->sample_rate;
      size_t delay_int = (size_t)delay_samples;
      float delay_frac = delay_samples - (float)delay_int;

      size_t pos1 = (chorus->write_pos + chorus->buffer_size - delay_int) %
                    chorus->buffer_size;
      size_t pos2 = (pos1 + chorus->buffer_size - 1) % chorus->buffer_size;

      Sample delayed = INTUITIVES_LERP(chorus->buffer[pos1],
                                       chorus->buffer[pos2], delay_frac);

      out_l += delayed * (1.0f - chorus->voice_pan[v]);
      out_r += delayed * chorus->voice_pan[v];

      // Advance phase
      chorus->phases[v] += phase_inc;
      if (chorus->phases[v] >= 1.0f)
        chorus->phases[v] -= 1.0f;
    }

    out_l /= chorus->num_voices;
    out_r /= chorus->num_voices;

    // Mix
    left[i] = INTUITIVES_LERP(left[i], out_l, chorus->mix);
    right[i] = INTUITIVES_LERP(right[i], out_r, chorus->mix);

    chorus->write_pos = (chorus->write_pos + 1) % chorus->buffer_size;
  }
}

// ============================================================================
// PHASER
// ============================================================================

IntuitivesResult phaser_init(Phaser *phaser, uint32_t sample_rate,
                             uint32_t num_stages) {
  if (!phaser)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(phaser, 0, sizeof(Phaser));

  phaser->sample_rate = sample_rate;
  phaser->num_stages =
      num_stages > PHASER_MAX_STAGES ? PHASER_MAX_STAGES : num_stages;
  phaser->rate = 0.3f;
  phaser->depth = 0.6f;
  phaser->feedback = 0.7f;
  phaser->min_freq = 200.0f;
  phaser->max_freq = 4000.0f;
  phaser->mix = 0.5f;

  return INTUITIVES_OK;
}

Sample phaser_process(Phaser *phaser, Sample input) {
  // LFO
  float lfo = 0.5f + 0.5f * sinf(phaser->lfo_phase * INTUITIVES_TWO_PI);
  phaser->lfo_phase += phaser->rate / (float)phaser->sample_rate;
  if (phaser->lfo_phase >= 1.0f)
    phaser->lfo_phase -= 1.0f;

  // Calculate frequency
  float freq = phaser->min_freq +
               lfo * phaser->depth * (phaser->max_freq - phaser->min_freq);

  // Update allpass coefficients
  float w = INTUITIVES_TWO_PI * freq / (float)phaser->sample_rate;
  float a1 = (1.0f - w) / (1.0f + w);

  for (uint32_t i = 0; i < phaser->num_stages; i++) {
    phaser->a1[i] = a1;
  }

  // Process through allpass stages
  Sample y = input + phaser->zm1[phaser->num_stages - 1] * phaser->feedback;

  for (uint32_t i = 0; i < phaser->num_stages; i++) {
    Sample x = y;
    y = phaser->a1[i] * (x - phaser->zm1[i]) + phaser->zm1[i];
    phaser->zm1[i] = INTUITIVES_LERP(phaser->zm1[i], y, 0.9f);
    y = x - phaser->a1[i] * y;
  }

  return INTUITIVES_LERP(input, y, phaser->mix);
}

// ============================================================================
// BITCRUSHER
// ============================================================================

IntuitivesResult bitcrusher_init(Bitcrusher *bc, uint32_t sample_rate) {
  if (!bc)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(bc, 0, sizeof(Bitcrusher));
  bc->original_sample_rate = sample_rate;
  bc->bit_depth = 12;
  bc->sample_rate_reduction = 1;
  bc->mix = 1.0f;
  bc->dither = 0.0f;
  return INTUITIVES_OK;
}

Sample bitcrusher_process(Bitcrusher *bc, Sample input) {
  // Sample rate reduction (sample & hold)
  bc->hold_counter++;
  if (bc->hold_counter >= bc->sample_rate_reduction) {
    bc->hold_sample = input;
    bc->hold_counter = 0;
  }

  // Bit depth reduction
  float quant = powf(2.0f, (float)bc->bit_depth - 1);
  Sample crushed = roundf(bc->hold_sample * quant) / quant;

  return INTUITIVES_LERP(input, crushed, bc->mix);
}

// ============================================================================
// EFFECT CHAIN
// ============================================================================

IntuitivesResult effect_chain_init(EffectChain *chain, uint32_t sample_rate) {
  if (!chain)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(chain, 0, sizeof(EffectChain));
  chain->sample_rate = sample_rate;
  return INTUITIVES_OK;
}

void effect_chain_process(EffectChain *chain, Sample *left, Sample *right,
                          size_t frames) {
  for (uint32_t e = 0; e < chain->num_effects; e++) {
    if (chain->slots[e].bypass)
      continue;

    EffectSlot *slot = &chain->slots[e];

    switch (slot->type) {
    case EFFECT_FILTER:
      for (size_t i = 0; i < frames; i++) {
        left[i] = svf_process(&slot->effect.filter, left[i]);
        right[i] = svf_process(&slot->effect.filter, right[i]);
      }
      break;
    case EFFECT_REVERB:
      reverb_process_stereo(&slot->effect.reverb, left, right, frames);
      break;
    case EFFECT_DELAY:
      delay_process_stereo(&slot->effect.delay, left, right, frames);
      break;
    case EFFECT_DISTORTION:
      for (size_t i = 0; i < frames; i++) {
        left[i] = distortion_process(&slot->effect.distortion, left[i]);
        right[i] = distortion_process(&slot->effect.distortion, right[i]);
      }
      break;
    case EFFECT_COMPRESSOR:
      for (size_t i = 0; i < frames; i++) {
        Sample sc = (left[i] + right[i]) * 0.5f;
        left[i] = compressor_process(&slot->effect.compressor, left[i], sc);
        right[i] = compressor_process(&slot->effect.compressor, right[i], sc);
      }
      break;
    case EFFECT_CHORUS:
      chorus_process_stereo(&slot->effect.chorus, left, right, frames);
      break;
    case EFFECT_PHASER:
      for (size_t i = 0; i < frames; i++) {
        left[i] = phaser_process(&slot->effect.phaser, left[i]);
        right[i] = phaser_process(&slot->effect.phaser, right[i]);
      }
      break;
    case EFFECT_BITCRUSHER:
      for (size_t i = 0; i < frames; i++) {
        left[i] = bitcrusher_process(&slot->effect.bitcrusher, left[i]);
        right[i] = bitcrusher_process(&slot->effect.bitcrusher, right[i]);
      }
      break;
    default:
      break;
    }
  }
}
