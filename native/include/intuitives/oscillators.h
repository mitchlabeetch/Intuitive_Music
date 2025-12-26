/**
 * INTUITIVES - Oscillator Module
 *
 * Advanced oscillators including chaos, fractal, and morphing types.
 * Rule-free sound generation.
 */

#ifndef INTUITIVES_OSCILLATORS_H
#define INTUITIVES_OSCILLATORS_H

#include "core.h"

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// FEATURE 1: QUANTUM OSCILLATOR (Multi-waveform with morphing)
// ============================================================================

typedef struct {
  WaveformType waveform_a;
  WaveformType waveform_b;
  float morph; // 0.0 = waveform_a, 1.0 = waveform_b
  Phase phase;
  Frequency frequency;
  float detune;      // Detune in cents
  float pulse_width; // For pulse wave (0-1)
  uint32_t sample_rate;
  float phase_increment;
} QuantumOscillator;

IntuitivesResult quantum_osc_init(QuantumOscillator *osc, uint32_t sample_rate);
void quantum_osc_set_frequency(QuantumOscillator *osc, Frequency freq);
void quantum_osc_set_morph(QuantumOscillator *osc, float morph);
Sample quantum_osc_process(QuantumOscillator *osc);
void quantum_osc_process_block(QuantumOscillator *osc, Sample *buffer,
                               size_t frames);

// ============================================================================
// FEATURE 2: CHAOS OSCILLATOR (Lorenz/Rössler attractor)
// ============================================================================

typedef struct {
  double x, y, z;          // System state
  double sigma, rho, beta; // Lorenz parameters (default: 10, 28, 8/3)
  double dt;               // Time step
  float output_scale;
  uint32_t output_axis; // 0=x, 1=y, 2=z for output
  uint32_t sample_rate;
} ChaosOscillator;

IntuitivesResult chaos_osc_init(ChaosOscillator *osc, uint32_t sample_rate);
void chaos_osc_set_params(ChaosOscillator *osc, double sigma, double rho,
                          double beta);
void chaos_osc_reset(ChaosOscillator *osc);
Sample chaos_osc_process(ChaosOscillator *osc);
void chaos_osc_process_block(ChaosOscillator *osc, Sample *buffer,
                             size_t frames);

// ============================================================================
// FEATURE 3: WAVETABLE OSCILLATOR
// ============================================================================

#define WAVETABLE_SIZE 2048
#define MAX_WAVETABLES 16

typedef struct {
  Sample tables[MAX_WAVETABLES][WAVETABLE_SIZE];
  uint32_t num_tables;
  float table_position; // Interpolate between tables
  Phase phase;
  Frequency frequency;
  uint32_t sample_rate;
  float phase_increment;
} WavetableOscillator;

IntuitivesResult wavetable_osc_init(WavetableOscillator *osc,
                                    uint32_t sample_rate);
void wavetable_osc_load_table(WavetableOscillator *osc, uint32_t index,
                              const Sample *data);
void wavetable_osc_generate_basic(
    WavetableOscillator *osc); // Generate sine, saw, square, tri
void wavetable_osc_set_frequency(WavetableOscillator *osc, Frequency freq);
void wavetable_osc_set_position(WavetableOscillator *osc, float position);
Sample wavetable_osc_process(WavetableOscillator *osc);

// ============================================================================
// FEATURE 4: FM SYNTHESIS OSCILLATOR
// ============================================================================

#define FM_MAX_OPERATORS 6

typedef struct {
  Frequency frequency;
  float ratio;  // Frequency ratio relative to carrier
  float detune; // Detune in Hz
  Amplitude amplitude;
  Phase phase;
  float feedback;    // Self-modulation amount
  float last_output; // For feedback
} FMOperator;

typedef struct {
  FMOperator operators[FM_MAX_OPERATORS];
  float modulation_matrix[FM_MAX_OPERATORS]
                         [FM_MAX_OPERATORS]; // Who modulates whom
  uint32_t num_operators;
  uint32_t algorithm; // Preset routing algorithm
  Frequency base_frequency;
  uint32_t sample_rate;
} FMOscillator;

IntuitivesResult fm_osc_init(FMOscillator *osc, uint32_t sample_rate,
                             uint32_t num_ops);
void fm_osc_set_frequency(FMOscillator *osc, Frequency freq);
void fm_osc_set_algorithm(FMOscillator *osc, uint32_t algorithm);
void fm_osc_set_modulation(FMOscillator *osc, uint32_t mod, uint32_t carrier,
                           float amount);
Sample fm_osc_process(FMOscillator *osc);
void fm_osc_process_block(FMOscillator *osc, Sample *buffer, size_t frames);

// ============================================================================
// FEATURE 5: ADDITIVE SYNTHESIS OSCILLATOR
// ============================================================================

#define ADDITIVE_MAX_PARTIALS 64

typedef struct {
  float amplitudes[ADDITIVE_MAX_PARTIALS];  // Partial amplitudes
  float frequencies[ADDITIVE_MAX_PARTIALS]; // Frequency ratios
  Phase phases[ADDITIVE_MAX_PARTIALS];
  uint32_t num_partials;
  Frequency base_frequency;
  uint32_t sample_rate;
} AdditiveOscillator;

IntuitivesResult additive_osc_init(AdditiveOscillator *osc,
                                   uint32_t sample_rate);
void additive_osc_set_frequency(AdditiveOscillator *osc, Frequency freq);
void additive_osc_set_partial(AdditiveOscillator *osc, uint32_t index,
                              float freq_ratio, float amp);
void additive_osc_set_harmonic_series(AdditiveOscillator *osc,
                                      uint32_t num_harmonics, float rolloff);
void additive_osc_set_spectral_shape(AdditiveOscillator *osc,
                                     const float *spectrum, size_t bins);
Sample additive_osc_process(AdditiveOscillator *osc);

// ============================================================================
// FEATURE 6: NOISE GENERATOR (Multiple noise types)
// ============================================================================

typedef enum {
  NOISE_WHITE = 0,
  NOISE_PINK,
  NOISE_BROWN,
  NOISE_BLUE,
  NOISE_VIOLET,
  NOISE_VELVET, // Sparse impulse noise
  NOISE_CRACKLE // Vinyl-style crackle
} NoiseType;

typedef struct {
  NoiseType type;
  uint32_t seed;
  uint32_t state;                  // PRNG state
  float pink_b0, pink_b1, pink_b2; // Pink noise filter state
  float brown_last;                // Brown noise integration
  float amplitude;
} NoiseGenerator;

IntuitivesResult noise_gen_init(NoiseGenerator *gen, NoiseType type,
                                uint32_t seed);
void noise_gen_set_type(NoiseGenerator *gen, NoiseType type);
Sample noise_gen_process(NoiseGenerator *gen);
void noise_gen_process_block(NoiseGenerator *gen, Sample *buffer,
                             size_t frames);

// ============================================================================
// FEATURE 7: FRACTAL OSCILLATOR (Mandelbrot-derived harmonics)
// ============================================================================

typedef struct {
  double real_c, imag_c; // Complex constant for iteration
  uint32_t max_iterations;
  float *harmonic_weights; // Weights derived from fractal
  uint32_t num_harmonics;
  Phase phases[ADDITIVE_MAX_PARTIALS];
  Frequency base_frequency;
  uint32_t sample_rate;
  bool needs_recalc;
} FractalOscillator;

IntuitivesResult fractal_osc_init(FractalOscillator *osc, uint32_t sample_rate);
void fractal_osc_set_coordinates(FractalOscillator *osc, double real,
                                 double imag);
void fractal_osc_set_frequency(FractalOscillator *osc, Frequency freq);
void fractal_osc_recalculate(
    FractalOscillator *osc); // Recompute harmonics from fractal
Sample fractal_osc_process(FractalOscillator *osc);

// ============================================================================
// OSCILLATOR BANK (Manage multiple oscillators)
// ============================================================================

typedef enum {
  OSC_TYPE_QUANTUM = 0,
  OSC_TYPE_CHAOS,
  OSC_TYPE_WAVETABLE,
  OSC_TYPE_FM,
  OSC_TYPE_ADDITIVE,
  OSC_TYPE_NOISE,
  OSC_TYPE_FRACTAL
} OscillatorType;

typedef union {
  QuantumOscillator quantum;
  ChaosOscillator chaos;
  WavetableOscillator wavetable;
  FMOscillator fm;
  AdditiveOscillator additive;
  NoiseGenerator noise;
  FractalOscillator fractal;
} OscillatorUnion;

typedef struct {
  OscillatorType type;
  OscillatorUnion osc;
  float gain;
  float pan;
  bool active;
} OscillatorSlot;

typedef struct {
  OscillatorSlot slots[INTUITIVES_MAX_OSCILLATORS];
  uint32_t num_active;
  uint32_t sample_rate;
} OscillatorBank;

IntuitivesResult osc_bank_init(OscillatorBank *bank, uint32_t sample_rate);
int32_t osc_bank_add(OscillatorBank *bank,
                     OscillatorType type); // Returns slot index
void osc_bank_remove(OscillatorBank *bank, uint32_t slot);
void osc_bank_process(OscillatorBank *bank, Sample *left, Sample *right,
                      size_t frames);

#ifdef __cplusplus
}
#endif

#endif // INTUITIVES_OSCILLATORS_H
