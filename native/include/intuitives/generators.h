/**
 * INTUITIVES - Generators Module
 * Procedural and AI-driven music generation.
 */

#ifndef INTUITIVES_GENERATORS_H
#define INTUITIVES_GENERATORS_H

#include "core.h"

#ifdef __cplusplus
extern "C" {
#endif

// FEATURE 18: GRANULAR SYNTHESIS ENGINE
#define GRAIN_MAX_COUNT 128

typedef enum {
  GRAIN_ENV_GAUSSIAN = 0,
  GRAIN_ENV_HANN,
  GRAIN_ENV_TRAPEZOID
} GrainEnvelope;

typedef struct {
  size_t start_pos, current_pos, length;
  float phase, pitch_ratio, pan, amplitude;
  GrainEnvelope env_type;
  bool active;
} Grain;

typedef struct {
  Sample *source_buffer;
  size_t source_length;
  Grain grains[GRAIN_MAX_COUNT];
  uint32_t active_grain_count;
  float position, position_spread, grain_size, grain_size_spread;
  float density, pitch, pitch_spread, pan_spread;
  GrainEnvelope envelope;
  float spawn_timer;
  uint32_t sample_rate, random_state;
} GranularEngine;

IntuitivesResult granular_init(GranularEngine *e, uint32_t sr);
void granular_free(GranularEngine *e);
IntuitivesResult granular_load_buffer(GranularEngine *e, const Sample *data,
                                      size_t length);
void granular_process_stereo(GranularEngine *e, Sample *l, Sample *r,
                             size_t frames);

// FEATURE 19: SPECTRAL PROCESSOR
typedef enum {
  SPECTRAL_FREEZE = 0,
  SPECTRAL_BLUR,
  SPECTRAL_SHIFT,
  SPECTRAL_ROBOTIZE
} SpectralMode;

typedef struct {
  float *window, *fft_in, *fft_out, *magnitude, *phase, *output_buffer;
  SpectralMode mode;
  float freeze_mix, blur_amount, shift_hz, mix;
  uint32_t sample_rate;
  bool frozen;
} SpectralProcessor;

IntuitivesResult spectral_init(SpectralProcessor *p, uint32_t sr);
void spectral_free(SpectralProcessor *p);
void spectral_process(SpectralProcessor *p, Sample *buf, size_t frames);

// FEATURE 20: MARKOV CHAIN MELODY
typedef struct {
  float transitions[12][12];
  int32_t current_state, octave;
  float octave_jump_prob, rest_prob, temperature;
  uint32_t random_state;
} MarkovMelodyGenerator;

IntuitivesResult markov_init(MarkovMelodyGenerator *g, uint32_t seed);
int32_t markov_next_note(MarkovMelodyGenerator *g);

// FEATURE 21: CELLULAR AUTOMATA RHYTHM
#define CELLULAR_MAX_WIDTH 64
typedef struct {
  uint8_t cells[CELLULAR_MAX_WIDTH], next_cells[CELLULAR_MAX_WIDTH];
  uint32_t width, rule, step, random_state;
  float density;
} CellularAutomata;

IntuitivesResult cellular_init(CellularAutomata *ca, uint32_t width,
                               uint32_t rule);
void cellular_randomize(CellularAutomata *ca, float density);
void cellular_step(CellularAutomata *ca);
void cellular_get_triggers(CellularAutomata *ca, bool *triggers, size_t n);

// FEATURE 22: GENETIC ALGORITHM MELODY
#define GENETIC_POP 32
#define GENETIC_LEN 16
typedef struct {
  int32_t notes[GENETIC_LEN];
  float fitness;
} Genome;
typedef struct {
  Genome pop[GENETIC_POP], best;
  float mutation_rate, crossover_rate;
  uint32_t generation, random_state;
  int32_t scale[12], root_note;
  uint32_t scale_size;
} GeneticMelody;

IntuitivesResult genetic_init(GeneticMelody *g, uint32_t seed);
void genetic_evolve(GeneticMelody *g);
void genetic_get_best(GeneticMelody *g, int32_t *melody);

// FEATURE 23: L-SYSTEM MELODY
#define LSYSTEM_MAX_STR 4096
typedef struct {
  char pred;
  char succ[64];
} LSystemRule;
typedef struct {
  char axiom[256], current[LSYSTEM_MAX_STR];
  LSystemRule rules[10];
  uint32_t num_rules, iteration;
  size_t str_len;
  int32_t current_note, note_step;
} LSystemGenerator;

IntuitivesResult lsystem_init(LSystemGenerator *g, const char *axiom);
void lsystem_add_rule(LSystemGenerator *g, char pred, const char *succ);
void lsystem_iterate(LSystemGenerator *g);
void lsystem_to_melody(LSystemGenerator *g, int32_t *notes, size_t *count,
                       size_t max);

// FEATURE 24: BROWNIAN MOTION
typedef struct {
  float position, min_val, max_val, step_size, momentum, velocity, target,
      attraction;
  uint32_t random_state;
} BrownianMotion;

IntuitivesResult brownian_init(BrownianMotion *b, float min, float max,
                               uint32_t seed);
float brownian_next(BrownianMotion *b);

// FEATURE 25: STOCHASTIC SEQUENCER
#define STOCHASTIC_MAX 64
typedef struct {
  float prob, vel, dur;
  int32_t note;
} StochasticStep;
typedef struct {
  StochasticStep steps[STOCHASTIC_MAX];
  uint32_t num_steps, current_step, random_state;
  float density, vel_variance;
} StochasticSequencer;

IntuitivesResult stochastic_init(StochasticSequencer *s, uint32_t n,
                                 uint32_t seed);
bool stochastic_advance(StochasticSequencer *s, int32_t *note, float *vel,
                        float *dur);

// FEATURE 26: CHORD PROGRESSION
typedef enum {
  CHORD_MAJ = 0,
  CHORD_MIN,
  CHORD_DIM,
  CHORD_MAJ7,
  CHORD_MIN7,
  CHORD_DOM7
} ChordType;
typedef struct {
  int32_t current_degree, key_root;
  ChordType current_type;
  bool is_minor;
  uint32_t random_state;
} ChordGenerator;

IntuitivesResult chord_gen_init(ChordGenerator *g, int32_t root, bool minor,
                                uint32_t seed);
int32_t chord_gen_next(ChordGenerator *g, int32_t *notes, size_t *num,
                       size_t max);

#ifdef __cplusplus
}
#endif
#endif
