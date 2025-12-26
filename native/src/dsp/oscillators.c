/**
 * INTUITIVES - Oscillator Implementations
 * High-performance DSP oscillators with SIMD optimization.
 */

#include "intuitives/oscillators.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

// ============================================================================
// UTILITY FUNCTIONS
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

// ============================================================================
// QUANTUM OSCILLATOR (Multi-waveform with morphing)
// ============================================================================

static inline Sample generate_waveform(WaveformType type, Phase phase,
                                       float pulse_width) {
  switch (type) {
  case WAVE_SINE:
    return sinf(phase * INTUITIVES_TWO_PI);
  case WAVE_SAW:
    return 2.0f * phase - 1.0f;
  case WAVE_SQUARE:
    return phase < 0.5f ? 1.0f : -1.0f;
  case WAVE_TRIANGLE:
    return phase < 0.5f ? (4.0f * phase - 1.0f) : (3.0f - 4.0f * phase);
  case WAVE_PULSE:
    return phase < pulse_width ? 1.0f : -1.0f;
  default:
    return 0.0f;
  }
}

IntuitivesResult quantum_osc_init(QuantumOscillator *osc,
                                  uint32_t sample_rate) {
  if (!osc)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(osc, 0, sizeof(QuantumOscillator));
  osc->waveform_a = WAVE_SINE;
  osc->waveform_b = WAVE_SAW;
  osc->morph = 0.0f;
  osc->pulse_width = 0.5f;
  osc->sample_rate = sample_rate;
  osc->frequency = 440.0f;
  osc->phase_increment = osc->frequency / (float)sample_rate;
  return INTUITIVES_OK;
}

void quantum_osc_set_frequency(QuantumOscillator *osc, Frequency freq) {
  osc->frequency = freq;
  float detune_ratio = powf(2.0f, osc->detune / 1200.0f);
  osc->phase_increment = (freq * detune_ratio) / (float)osc->sample_rate;
}

void quantum_osc_set_morph(QuantumOscillator *osc, float morph) {
  osc->morph = INTUITIVES_CLAMP(morph, 0.0f, 1.0f);
}

Sample quantum_osc_process(QuantumOscillator *osc) {
  Sample a = generate_waveform(osc->waveform_a, osc->phase, osc->pulse_width);
  Sample b = generate_waveform(osc->waveform_b, osc->phase, osc->pulse_width);
  Sample out = INTUITIVES_LERP(a, b, osc->morph);

  osc->phase += osc->phase_increment;
  if (osc->phase >= 1.0f)
    osc->phase -= 1.0f;

  return out;
}

void quantum_osc_process_block(QuantumOscillator *osc, Sample *buffer,
                               size_t frames) {
  for (size_t i = 0; i < frames; i++) {
    buffer[i] = quantum_osc_process(osc);
  }
}

// ============================================================================
// CHAOS OSCILLATOR (Lorenz Attractor)
// ============================================================================

IntuitivesResult chaos_osc_init(ChaosOscillator *osc, uint32_t sample_rate) {
  if (!osc)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(osc, 0, sizeof(ChaosOscillator));

  // Classic Lorenz parameters
  osc->sigma = 10.0;
  osc->rho = 28.0;
  osc->beta = 8.0 / 3.0;
  osc->dt = 0.01;

  // Initial conditions
  osc->x = 0.1;
  osc->y = 0.0;
  osc->z = 0.0;

  osc->output_scale = 0.05f;
  osc->output_axis = 0;
  osc->sample_rate = sample_rate;

  return INTUITIVES_OK;
}

void chaos_osc_set_params(ChaosOscillator *osc, double sigma, double rho,
                          double beta) {
  osc->sigma = sigma;
  osc->rho = rho;
  osc->beta = beta;
}

void chaos_osc_reset(ChaosOscillator *osc) {
  osc->x = 0.1;
  osc->y = 0.0;
  osc->z = 0.0;
}

Sample chaos_osc_process(ChaosOscillator *osc) {
  // Lorenz system differential equations
  double dx = osc->sigma * (osc->y - osc->x);
  double dy = osc->x * (osc->rho - osc->z) - osc->y;
  double dz = osc->x * osc->y - osc->beta * osc->z;

  osc->x += dx * osc->dt;
  osc->y += dy * osc->dt;
  osc->z += dz * osc->dt;

  // Select output axis
  double output;
  switch (osc->output_axis) {
  case 0:
    output = osc->x;
    break;
  case 1:
    output = osc->y;
    break;
  case 2:
    output = osc->z;
    break;
  default:
    output = osc->x;
    break;
  }

  return (Sample)(output * osc->output_scale);
}

void chaos_osc_process_block(ChaosOscillator *osc, Sample *buffer,
                             size_t frames) {
  for (size_t i = 0; i < frames; i++) {
    buffer[i] = chaos_osc_process(osc);
  }
}

// ============================================================================
// WAVETABLE OSCILLATOR
// ============================================================================

IntuitivesResult wavetable_osc_init(WavetableOscillator *osc,
                                    uint32_t sample_rate) {
  if (!osc)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(osc, 0, sizeof(WavetableOscillator));
  osc->sample_rate = sample_rate;
  osc->frequency = 440.0f;
  osc->phase_increment = osc->frequency / (float)sample_rate;
  wavetable_osc_generate_basic(osc);
  return INTUITIVES_OK;
}

void wavetable_osc_generate_basic(WavetableOscillator *osc) {
  // Table 0: Sine
  for (size_t i = 0; i < WAVETABLE_SIZE; i++) {
    float phase = (float)i / (float)WAVETABLE_SIZE;
    osc->tables[0][i] = sinf(phase * INTUITIVES_TWO_PI);
  }

  // Table 1: Saw (band-limited)
  for (size_t i = 0; i < WAVETABLE_SIZE; i++) {
    float phase = (float)i / (float)WAVETABLE_SIZE;
    float saw = 0.0f;
    for (int h = 1; h <= 16; h++) {
      saw += (1.0f / h) * sinf(h * phase * INTUITIVES_TWO_PI);
    }
    osc->tables[1][i] = saw * 0.5f;
  }

  // Table 2: Square (band-limited)
  for (size_t i = 0; i < WAVETABLE_SIZE; i++) {
    float phase = (float)i / (float)WAVETABLE_SIZE;
    float sq = 0.0f;
    for (int h = 1; h <= 16; h += 2) {
      sq += (1.0f / h) * sinf(h * phase * INTUITIVES_TWO_PI);
    }
    osc->tables[2][i] = sq * 0.8f;
  }

  // Table 3: Triangle
  for (size_t i = 0; i < WAVETABLE_SIZE; i++) {
    float phase = (float)i / (float)WAVETABLE_SIZE;
    float tri = 0.0f;
    for (int h = 1; h <= 16; h += 2) {
      tri += (1.0f / (h * h)) * sinf(h * phase * INTUITIVES_TWO_PI) *
             ((h - 1) / 2 % 2 ? -1 : 1);
    }
    osc->tables[3][i] = tri * 0.8f;
  }

  osc->num_tables = 4;
}

void wavetable_osc_set_frequency(WavetableOscillator *osc, Frequency freq) {
  osc->frequency = freq;
  osc->phase_increment = freq / (float)osc->sample_rate;
}

void wavetable_osc_set_position(WavetableOscillator *osc, float position) {
  osc->table_position =
      INTUITIVES_CLAMP(position, 0.0f, (float)(osc->num_tables - 1));
}

Sample wavetable_osc_process(WavetableOscillator *osc) {
  // Interpolate between tables
  uint32_t table_a = (uint32_t)osc->table_position;
  uint32_t table_b = table_a + 1;
  if (table_b >= osc->num_tables)
    table_b = table_a;
  float table_frac = osc->table_position - (float)table_a;

  // Interpolate within table
  float index = osc->phase * (float)WAVETABLE_SIZE;
  uint32_t idx_a = (uint32_t)index;
  uint32_t idx_b = (idx_a + 1) % WAVETABLE_SIZE;
  float frac = index - (float)idx_a;

  // Bilinear interpolation
  Sample val_a = INTUITIVES_LERP(osc->tables[table_a][idx_a],
                                 osc->tables[table_a][idx_b], frac);
  Sample val_b = INTUITIVES_LERP(osc->tables[table_b][idx_a],
                                 osc->tables[table_b][idx_b], frac);
  Sample out = INTUITIVES_LERP(val_a, val_b, table_frac);

  osc->phase += osc->phase_increment;
  if (osc->phase >= 1.0f)
    osc->phase -= 1.0f;

  return out;
}

// ============================================================================
// FM OSCILLATOR
// ============================================================================

IntuitivesResult fm_osc_init(FMOscillator *osc, uint32_t sample_rate,
                             uint32_t num_ops) {
  if (!osc)
    return INTUITIVES_ERROR_NULL_POINTER;
  if (num_ops > FM_MAX_OPERATORS)
    num_ops = FM_MAX_OPERATORS;

  memset(osc, 0, sizeof(FMOscillator));
  osc->sample_rate = sample_rate;
  osc->num_operators = num_ops;
  osc->base_frequency = 440.0f;

  // Default: all carriers with 1:1 ratio
  for (uint32_t i = 0; i < num_ops; i++) {
    osc->operators[i].frequency = osc->base_frequency;
    osc->operators[i].ratio = 1.0f;
    osc->operators[i].amplitude = 1.0f / num_ops;
  }

  return INTUITIVES_OK;
}

void fm_osc_set_frequency(FMOscillator *osc, Frequency freq) {
  osc->base_frequency = freq;
  for (uint32_t i = 0; i < osc->num_operators; i++) {
    osc->operators[i].frequency =
        freq * osc->operators[i].ratio + osc->operators[i].detune;
  }
}

void fm_osc_set_modulation(FMOscillator *osc, uint32_t mod, uint32_t carrier,
                           float amount) {
  if (mod < FM_MAX_OPERATORS && carrier < FM_MAX_OPERATORS) {
    osc->modulation_matrix[mod][carrier] = amount;
  }
}

Sample fm_osc_process(FMOscillator *osc) {
  float outputs[FM_MAX_OPERATORS] = {0};
  float phase_inc = INTUITIVES_TWO_PI / (float)osc->sample_rate;

  // Calculate each operator output (with modulation from previous operators)
  for (uint32_t i = 0; i < osc->num_operators; i++) {
    FMOperator *op = &osc->operators[i];

    // Sum modulation inputs
    float mod_sum = 0.0f;
    for (uint32_t m = 0; m < osc->num_operators; m++) {
      mod_sum += outputs[m] * osc->modulation_matrix[m][i];
    }

    // Add feedback
    mod_sum += op->last_output * op->feedback;

    // Calculate output
    float phase = op->phase + mod_sum;
    op->last_output = sinf(phase) * op->amplitude;
    outputs[i] = op->last_output;

    // Advance phase
    op->phase += op->frequency * phase_inc;
    if (op->phase >= INTUITIVES_TWO_PI)
      op->phase -= INTUITIVES_TWO_PI;
  }

  // Sum all operators as carriers (simplified)
  Sample out = 0.0f;
  for (uint32_t i = 0; i < osc->num_operators; i++) {
    out += outputs[i];
  }

  return out;
}

// ============================================================================
// ADDITIVE OSCILLATOR
// ============================================================================

IntuitivesResult additive_osc_init(AdditiveOscillator *osc,
                                   uint32_t sample_rate) {
  if (!osc)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(osc, 0, sizeof(AdditiveOscillator));
  osc->sample_rate = sample_rate;
  osc->base_frequency = 440.0f;
  osc->num_partials = 8;

  // Default harmonic series with 1/n rolloff
  for (uint32_t i = 0; i < 8; i++) {
    osc->frequencies[i] = (float)(i + 1);
    osc->amplitudes[i] = 1.0f / (float)(i + 1);
  }

  return INTUITIVES_OK;
}

void additive_osc_set_frequency(AdditiveOscillator *osc, Frequency freq) {
  osc->base_frequency = freq;
}

void additive_osc_set_harmonic_series(AdditiveOscillator *osc,
                                      uint32_t num_harmonics, float rolloff) {
  if (num_harmonics > ADDITIVE_MAX_PARTIALS)
    num_harmonics = ADDITIVE_MAX_PARTIALS;
  osc->num_partials = num_harmonics;

  for (uint32_t i = 0; i < num_harmonics; i++) {
    osc->frequencies[i] = (float)(i + 1);
    osc->amplitudes[i] = powf(1.0f / (float)(i + 1), rolloff);
  }
}

Sample additive_osc_process(AdditiveOscillator *osc) {
  Sample out = 0.0f;
  float base_inc = osc->base_frequency / (float)osc->sample_rate;

  for (uint32_t i = 0; i < osc->num_partials; i++) {
    float freq_ratio = osc->frequencies[i];
    float phase_inc = base_inc * freq_ratio;

    out += osc->amplitudes[i] * sinf(osc->phases[i] * INTUITIVES_TWO_PI);

    osc->phases[i] += phase_inc;
    if (osc->phases[i] >= 1.0f)
      osc->phases[i] -= 1.0f;
  }

  return out;
}

// ============================================================================
// NOISE GENERATOR
// ============================================================================

IntuitivesResult noise_gen_init(NoiseGenerator *gen, NoiseType type,
                                uint32_t seed) {
  if (!gen)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(gen, 0, sizeof(NoiseGenerator));
  gen->type = type;
  gen->seed = seed;
  gen->state = seed ? seed : 12345;
  gen->amplitude = 1.0f;
  return INTUITIVES_OK;
}

Sample noise_gen_process(NoiseGenerator *gen) {
  float white = 2.0f * random_float(&gen->state) - 1.0f;

  switch (gen->type) {
  case NOISE_WHITE:
    return white * gen->amplitude;

  case NOISE_PINK: {
    // Voss-McCartney algorithm (simplified)
    gen->pink_b0 = 0.99886f * gen->pink_b0 + white * 0.0555179f;
    gen->pink_b1 = 0.99332f * gen->pink_b1 + white * 0.0750759f;
    gen->pink_b2 = 0.96900f * gen->pink_b2 + white * 0.1538520f;
    float pink = gen->pink_b0 + gen->pink_b1 + gen->pink_b2 + white * 0.5362f;
    return pink * 0.11f * gen->amplitude;
  }

  case NOISE_BROWN: {
    gen->brown_last += white * 0.02f;
    gen->brown_last = INTUITIVES_CLAMP(gen->brown_last, -1.0f, 1.0f);
    return gen->brown_last * gen->amplitude;
  }

  case NOISE_VELVET: {
    // Sparse impulse noise
    if (random_float(&gen->state) < 0.01f) {
      return (random_float(&gen->state) < 0.5f ? 1.0f : -1.0f) * gen->amplitude;
    }
    return 0.0f;
  }

  default:
    return white * gen->amplitude;
  }
}

void noise_gen_process_block(NoiseGenerator *gen, Sample *buffer,
                             size_t frames) {
  for (size_t i = 0; i < frames; i++) {
    buffer[i] = noise_gen_process(gen);
  }
}

// ============================================================================
// FRACTAL OSCILLATOR (Mandelbrot-derived harmonics)
// ============================================================================

IntuitivesResult fractal_osc_init(FractalOscillator *osc,
                                  uint32_t sample_rate) {
  if (!osc)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(osc, 0, sizeof(FractalOscillator));

  osc->sample_rate = sample_rate;
  osc->base_frequency = 220.0f;
  osc->real_c = -0.7f;
  osc->imag_c = 0.27015f;
  osc->max_iterations = 32;
  osc->num_harmonics = 16;
  osc->needs_recalc = true;

  osc->harmonic_weights = (float *)calloc(64, sizeof(float));

  return INTUITIVES_OK;
}

void fractal_osc_set_coordinates(FractalOscillator *osc, double real,
                                 double imag) {
  osc->real_c = real;
  osc->imag_c = imag;
  osc->needs_recalc = true;
}

void fractal_osc_recalculate(FractalOscillator *osc) {
  // Generate harmonic weights from Julia set escape times
  for (uint32_t i = 0; i < osc->num_harmonics; i++) {
    double zr = (double)i / (double)osc->num_harmonics * 2.0 - 1.0;
    double zi = 0.0;

    uint32_t iter = 0;
    while (zr * zr + zi * zi < 4.0 && iter < osc->max_iterations) {
      double tmp = zr * zr - zi * zi + osc->real_c;
      zi = 2.0 * zr * zi + osc->imag_c;
      zr = tmp;
      iter++;
    }

    osc->harmonic_weights[i] = (float)iter / (float)osc->max_iterations;
  }
  osc->needs_recalc = false;
}

Sample fractal_osc_process(FractalOscillator *osc) {
  if (osc->needs_recalc) {
    fractal_osc_recalculate(osc);
  }

  Sample out = 0.0f;
  float base_inc = osc->base_frequency / (float)osc->sample_rate;

  for (uint32_t i = 0; i < osc->num_harmonics; i++) {
    float freq_ratio = (float)(i + 1);
    out += osc->harmonic_weights[i] * sinf(osc->phases[i] * INTUITIVES_TWO_PI);

    osc->phases[i] += base_inc * freq_ratio;
    if (osc->phases[i] >= 1.0f)
      osc->phases[i] -= 1.0f;
  }

  return out * 0.5f;
}

// ============================================================================
// OSCILLATOR BANK
// ============================================================================

IntuitivesResult osc_bank_init(OscillatorBank *bank, uint32_t sample_rate) {
  if (!bank)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(bank, 0, sizeof(OscillatorBank));
  bank->sample_rate = sample_rate;
  return INTUITIVES_OK;
}

int32_t osc_bank_add(OscillatorBank *bank, OscillatorType type) {
  for (uint32_t i = 0; i < INTUITIVES_MAX_OSCILLATORS; i++) {
    if (!bank->slots[i].active) {
      bank->slots[i].type = type;
      bank->slots[i].gain = 1.0f;
      bank->slots[i].pan = 0.5f;
      bank->slots[i].active = true;

      switch (type) {
      case OSC_TYPE_QUANTUM:
        quantum_osc_init(&bank->slots[i].osc.quantum, bank->sample_rate);
        break;
      case OSC_TYPE_CHAOS:
        chaos_osc_init(&bank->slots[i].osc.chaos, bank->sample_rate);
        break;
      case OSC_TYPE_WAVETABLE:
        wavetable_osc_init(&bank->slots[i].osc.wavetable, bank->sample_rate);
        break;
      case OSC_TYPE_FM:
        fm_osc_init(&bank->slots[i].osc.fm, bank->sample_rate, 4);
        break;
      case OSC_TYPE_ADDITIVE:
        additive_osc_init(&bank->slots[i].osc.additive, bank->sample_rate);
        break;
      case OSC_TYPE_NOISE:
        noise_gen_init(&bank->slots[i].osc.noise, NOISE_WHITE, 0);
        break;
      case OSC_TYPE_FRACTAL:
        fractal_osc_init(&bank->slots[i].osc.fractal, bank->sample_rate);
        break;
      }

      bank->num_active++;
      return (int32_t)i;
    }
  }
  return -1;
}

void osc_bank_process(OscillatorBank *bank, Sample *left, Sample *right,
                      size_t frames) {
  memset(left, 0, frames * sizeof(Sample));
  memset(right, 0, frames * sizeof(Sample));

  for (uint32_t slot = 0; slot < INTUITIVES_MAX_OSCILLATORS; slot++) {
    if (!bank->slots[slot].active)
      continue;

    OscillatorSlot *s = &bank->slots[slot];
    float gain_l = s->gain * (1.0f - s->pan);
    float gain_r = s->gain * s->pan;

    for (size_t i = 0; i < frames; i++) {
      Sample sample = 0.0f;

      switch (s->type) {
      case OSC_TYPE_QUANTUM:
        sample = quantum_osc_process(&s->osc.quantum);
        break;
      case OSC_TYPE_CHAOS:
        sample = chaos_osc_process(&s->osc.chaos);
        break;
      case OSC_TYPE_WAVETABLE:
        sample = wavetable_osc_process(&s->osc.wavetable);
        break;
      case OSC_TYPE_FM:
        sample = fm_osc_process(&s->osc.fm);
        break;
      case OSC_TYPE_ADDITIVE:
        sample = additive_osc_process(&s->osc.additive);
        break;
      case OSC_TYPE_NOISE:
        sample = noise_gen_process(&s->osc.noise);
        break;
      case OSC_TYPE_FRACTAL:
        sample = fractal_osc_process(&s->osc.fractal);
        break;
      }

      left[i] += sample * gain_l;
      right[i] += sample * gain_r;
    }
  }
}
