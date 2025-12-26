/**
 * INTUITIVES - Generators Implementation
 * AI-driven and procedural music generation.
 */

#include "intuitives/generators.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

// ============================================================================
// UTILITY
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

static inline int32_t random_int(uint32_t *state, int32_t min, int32_t max) {
  return min + (int32_t)(random_float(state) * (max - min + 1));
}

// Grain envelope functions
static float grain_envelope(GrainEnvelope type, float phase) {
  switch (type) {
  case GRAIN_ENV_GAUSSIAN:
    return expf(-8.0f * (phase - 0.5f) * (phase - 0.5f));
  case GRAIN_ENV_HANN:
    return 0.5f * (1.0f - cosf(INTUITIVES_TWO_PI * phase));
  case GRAIN_ENV_TRAPEZOID: {
    if (phase < 0.1f)
      return phase / 0.1f;
    if (phase > 0.9f)
      return (1.0f - phase) / 0.1f;
    return 1.0f;
  }
  default:
    return 1.0f;
  }
}

// ============================================================================
// GRANULAR SYNTHESIS ENGINE
// ============================================================================

IntuitivesResult granular_init(GranularEngine *e, uint32_t sr) {
  if (!e)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(e, 0, sizeof(GranularEngine));
  e->sample_rate = sr;
  e->random_state = 12345;
  e->position = 0.5f;
  e->position_spread = 0.1f;
  e->grain_size = 0.05f;
  e->grain_size_spread = 0.02f;
  e->density = 20.0f;
  e->pitch = 1.0f;
  e->pitch_spread = 0.0f;
  e->pan_spread = 0.5f;
  e->envelope = GRAIN_ENV_HANN;
  return INTUITIVES_OK;
}

void granular_free(GranularEngine *e) {
  if (e && e->source_buffer) {
    free(e->source_buffer);
    e->source_buffer = NULL;
  }
}

IntuitivesResult granular_load_buffer(GranularEngine *e, const Sample *data,
                                      size_t length) {
  if (!e || !data)
    return INTUITIVES_ERROR_NULL_POINTER;

  e->source_buffer = (Sample *)malloc(length * sizeof(Sample));
  if (!e->source_buffer)
    return INTUITIVES_ERROR_OUT_OF_MEMORY;

  memcpy(e->source_buffer, data, length * sizeof(Sample));
  e->source_length = length;
  return INTUITIVES_OK;
}

static void spawn_grain(GranularEngine *e) {
  // Find inactive grain slot
  Grain *grain = NULL;
  for (uint32_t i = 0; i < GRAIN_MAX_COUNT; i++) {
    if (!e->grains[i].active) {
      grain = &e->grains[i];
      break;
    }
  }
  if (!grain)
    return;

  // Randomize parameters
  float pos = e->position +
              (random_float(&e->random_state) - 0.5f) * e->position_spread;
  pos = INTUITIVES_CLAMP(pos, 0.0f, 1.0f);

  float size = e->grain_size +
               (random_float(&e->random_state) - 0.5f) * e->grain_size_spread;
  size = INTUITIVES_MAX(size, 0.001f);

  float pitch =
      e->pitch + (random_float(&e->random_state) - 0.5f) * e->pitch_spread;

  grain->start_pos = (size_t)(pos * e->source_length);
  grain->current_pos = 0;
  grain->length = (size_t)(size * e->sample_rate);
  grain->phase = 0.0f;
  grain->pitch_ratio = pitch;
  grain->pan = 0.5f + (random_float(&e->random_state) - 0.5f) * e->pan_spread;
  grain->amplitude = 0.8f + random_float(&e->random_state) * 0.2f;
  grain->env_type = e->envelope;
  grain->active = true;

  e->active_grain_count++;
}

void granular_process_stereo(GranularEngine *e, Sample *l, Sample *r,
                             size_t frames) {
  if (!e->source_buffer || e->source_length == 0) {
    memset(l, 0, frames * sizeof(Sample));
    memset(r, 0, frames * sizeof(Sample));
    return;
  }

  float spawn_interval = e->sample_rate / e->density;

  for (size_t i = 0; i < frames; i++) {
    Sample out_l = 0.0f;
    Sample out_r = 0.0f;

    // Spawn new grains
    e->spawn_timer += 1.0f;
    if (e->spawn_timer >= spawn_interval) {
      spawn_grain(e);
      e->spawn_timer -= spawn_interval;
    }

    // Process active grains
    for (uint32_t g = 0; g < GRAIN_MAX_COUNT; g++) {
      Grain *grain = &e->grains[g];
      if (!grain->active)
        continue;

      // Read from source with pitch
      float read_pos = (float)grain->start_pos +
                       (float)grain->current_pos * grain->pitch_ratio;
      size_t idx = (size_t)read_pos % e->source_length;

      Sample sample = e->source_buffer[idx];

      // Apply envelope
      float env = grain_envelope(grain->env_type, grain->phase);
      sample *= env * grain->amplitude;

      // Pan
      out_l += sample * (1.0f - grain->pan);
      out_r += sample * grain->pan;

      // Advance
      grain->current_pos++;
      grain->phase = (float)grain->current_pos / (float)grain->length;

      // Check if done
      if (grain->current_pos >= grain->length) {
        grain->active = false;
        e->active_grain_count--;
      }
    }

    l[i] = out_l;
    r[i] = out_r;
  }
}

// ============================================================================
// MARKOV MELODY GENERATOR
// ============================================================================

IntuitivesResult markov_init(MarkovMelodyGenerator *g, uint32_t seed) {
  if (!g)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(g, 0, sizeof(MarkovMelodyGenerator));
  g->random_state = seed ? seed : 12345;
  g->octave = 4;
  g->octave_jump_prob = 0.1f;
  g->rest_prob = 0.05f;
  g->temperature = 0.5f;

  // Default major scale probabilities
  float scale[12] = {1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1}; // Major scale
  for (int from = 0; from < 12; from++) {
    float sum = 0;
    for (int to = 0; to < 12; to++) {
      int interval = (to - from + 12) % 12;
      // Prefer small intervals
      float prob = scale[to] * expf(-interval * 0.3f);
      g->transitions[from][to] = prob;
      sum += prob;
    }
    // Normalize
    for (int to = 0; to < 12; to++) {
      g->transitions[from][to] /= sum;
    }
  }

  return INTUITIVES_OK;
}

int32_t markov_next_note(MarkovMelodyGenerator *g) {
  // Rest?
  if (random_float(&g->random_state) < g->rest_prob) {
    return -1;
  }

  // Octave jump?
  if (random_float(&g->random_state) < g->octave_jump_prob) {
    g->octave += random_float(&g->random_state) < 0.5f ? -1 : 1;
    g->octave = INTUITIVES_CLAMP(g->octave, 2, 6);
  }

  // Select next note based on transition probabilities
  float r = random_float(&g->random_state);
  float temp = g->temperature;

  // Apply temperature
  float probs[12];
  float sum = 0;
  for (int i = 0; i < 12; i++) {
    probs[i] = powf(g->transitions[g->current_state][i], 1.0f / temp);
    sum += probs[i];
  }

  // Sample
  float cumulative = 0;
  for (int i = 0; i < 12; i++) {
    cumulative += probs[i] / sum;
    if (r < cumulative) {
      g->current_state = i;
      return g->octave * 12 + i;
    }
  }

  return g->octave * 12 + g->current_state;
}

// ============================================================================
// CELLULAR AUTOMATA RHYTHM
// ============================================================================

IntuitivesResult cellular_init(CellularAutomata *ca, uint32_t width,
                               uint32_t rule) {
  if (!ca)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(ca, 0, sizeof(CellularAutomata));
  ca->width = width > CELLULAR_MAX_WIDTH ? CELLULAR_MAX_WIDTH : width;
  ca->rule = rule;
  ca->random_state = 12345;
  ca->density = 0.5f;

  // Initialize with single cell in center
  memset(ca->cells, 0, CELLULAR_MAX_WIDTH);
  ca->cells[ca->width / 2] = 1;

  return INTUITIVES_OK;
}

void cellular_randomize(CellularAutomata *ca, float density) {
  ca->density = density;
  for (uint32_t i = 0; i < ca->width; i++) {
    ca->cells[i] = random_float(&ca->random_state) < density ? 1 : 0;
  }
}

void cellular_step(CellularAutomata *ca) {
  for (uint32_t i = 0; i < ca->width; i++) {
    uint32_t left = (i > 0) ? ca->cells[i - 1] : ca->cells[ca->width - 1];
    uint32_t center = ca->cells[i];
    uint32_t right = (i < ca->width - 1) ? ca->cells[i + 1] : ca->cells[0];

    uint32_t pattern = (left << 2) | (center << 1) | right;
    ca->next_cells[i] = (ca->rule >> pattern) & 1;
  }

  memcpy(ca->cells, ca->next_cells, ca->width);
  ca->step++;
}

void cellular_get_triggers(CellularAutomata *ca, bool *triggers, size_t n) {
  for (size_t i = 0; i < n && i < ca->width; i++) {
    triggers[i] = ca->cells[i] != 0;
  }
}

// ============================================================================
// GENETIC ALGORITHM MELODY
// ============================================================================

IntuitivesResult genetic_init(GeneticMelody *g, uint32_t seed) {
  if (!g)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(g, 0, sizeof(GeneticMelody));
  g->random_state = seed ? seed : 12345;
  g->mutation_rate = 0.1f;
  g->crossover_rate = 0.7f;
  g->root_note = 60; // Middle C

  // Major scale
  int32_t major[] = {0, 2, 4, 5, 7, 9, 11};
  memcpy(g->scale, major, 7 * sizeof(int32_t));
  g->scale_size = 7;

  // Initialize random population
  for (int p = 0; p < GENETIC_POP; p++) {
    for (int n = 0; n < GENETIC_LEN; n++) {
      int32_t degree = random_int(&g->random_state, 0, g->scale_size - 1);
      int32_t octave = random_int(&g->random_state, -1, 1);
      g->pop[p].notes[n] = g->root_note + g->scale[degree] + octave * 12;
    }
    g->pop[p].fitness = 0;
  }

  return INTUITIVES_OK;
}

static float evaluate_melody(GeneticMelody *g, Genome *genome) {
  float fitness = 100.0f;

  // Penalize large jumps
  for (int i = 1; i < GENETIC_LEN; i++) {
    int32_t interval = abs(genome->notes[i] - genome->notes[i - 1]);
    if (interval > 12)
      fitness -= 5.0f;
    else if (interval > 7)
      fitness -= 2.0f;
    else if (interval <= 2)
      fitness += 1.0f; // Reward stepwise motion
  }

  // Reward resolving to tonic
  if (genome->notes[GENETIC_LEN - 1] % 12 == g->root_note % 12) {
    fitness += 10.0f;
  }

  // Penalize notes outside range
  for (int i = 0; i < GENETIC_LEN; i++) {
    if (genome->notes[i] < 48 || genome->notes[i] > 84) {
      fitness -= 3.0f;
    }
  }

  return INTUITIVES_MAX(fitness, 0.0f);
}

void genetic_evolve(GeneticMelody *g) {
  // Evaluate fitness
  for (int p = 0; p < GENETIC_POP; p++) {
    g->pop[p].fitness = evaluate_melody(g, &g->pop[p]);
    if (g->pop[p].fitness > g->best.fitness) {
      memcpy(&g->best, &g->pop[p], sizeof(Genome));
    }
  }

  // Selection and reproduction
  Genome new_pop[GENETIC_POP];

  for (int p = 0; p < GENETIC_POP; p++) {
    // Tournament selection
    int a = random_int(&g->random_state, 0, GENETIC_POP - 1);
    int b = random_int(&g->random_state, 0, GENETIC_POP - 1);
    Genome *parent1 =
        g->pop[a].fitness > g->pop[b].fitness ? &g->pop[a] : &g->pop[b];

    a = random_int(&g->random_state, 0, GENETIC_POP - 1);
    b = random_int(&g->random_state, 0, GENETIC_POP - 1);
    Genome *parent2 =
        g->pop[a].fitness > g->pop[b].fitness ? &g->pop[a] : &g->pop[b];

    // Crossover
    if (random_float(&g->random_state) < g->crossover_rate) {
      int point = random_int(&g->random_state, 1, GENETIC_LEN - 2);
      for (int n = 0; n < GENETIC_LEN; n++) {
        new_pop[p].notes[n] = n < point ? parent1->notes[n] : parent2->notes[n];
      }
    } else {
      memcpy(&new_pop[p], parent1, sizeof(Genome));
    }

    // Mutation
    for (int n = 0; n < GENETIC_LEN; n++) {
      if (random_float(&g->random_state) < g->mutation_rate) {
        int32_t step = random_int(&g->random_state, -3, 3);
        new_pop[p].notes[n] += step;
      }
    }
  }

  memcpy(g->pop, new_pop, sizeof(new_pop));
  g->generation++;
}

void genetic_get_best(GeneticMelody *g, int32_t *melody) {
  memcpy(melody, g->best.notes, GENETIC_LEN * sizeof(int32_t));
}

// ============================================================================
// L-SYSTEM MELODY
// ============================================================================

IntuitivesResult lsystem_init(LSystemGenerator *g, const char *axiom) {
  if (!g || !axiom)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(g, 0, sizeof(LSystemGenerator));
  strncpy(g->axiom, axiom, 255);
  strncpy(g->current, axiom, LSYSTEM_MAX_STR - 1);
  g->str_len = strlen(axiom);
  g->current_note = 60;
  g->note_step = 2;
  return INTUITIVES_OK;
}

void lsystem_add_rule(LSystemGenerator *g, char pred, const char *succ) {
  if (g->num_rules >= 10)
    return;
  g->rules[g->num_rules].pred = pred;
  strncpy(g->rules[g->num_rules].succ, succ, 63);
  g->num_rules++;
}

void lsystem_iterate(LSystemGenerator *g) {
  char new_str[LSYSTEM_MAX_STR] = {0};
  size_t new_len = 0;

  for (size_t i = 0; i < g->str_len && new_len < LSYSTEM_MAX_STR - 64; i++) {
    char c = g->current[i];
    bool found = false;

    for (uint32_t r = 0; r < g->num_rules; r++) {
      if (g->rules[r].pred == c) {
        size_t succ_len = strlen(g->rules[r].succ);
        strcat(new_str, g->rules[r].succ);
        new_len += succ_len;
        found = true;
        break;
      }
    }

    if (!found) {
      new_str[new_len++] = c;
    }
  }

  strcpy(g->current, new_str);
  g->str_len = new_len;
  g->iteration++;
}

void lsystem_to_melody(LSystemGenerator *g, int32_t *notes, size_t *count,
                       size_t max) {
  *count = 0;
  g->current_note = 60;

  for (size_t i = 0; i < g->str_len && *count < max; i++) {
    char c = g->current[i];

    switch (c) {
    case 'F':
    case 'G':
      notes[(*count)++] = g->current_note;
      g->current_note += g->note_step;
      break;
    case '+':
      g->note_step = abs(g->note_step);
      break;
    case '-':
      g->note_step = -abs(g->note_step);
      break;
    case '[':
      g->current_note -= 12;
      break;
    case ']':
      g->current_note += 12;
      break;
    }
  }
}

// ============================================================================
// BROWNIAN MOTION
// ============================================================================

IntuitivesResult brownian_init(BrownianMotion *b, float min, float max,
                               uint32_t seed) {
  if (!b)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(b, 0, sizeof(BrownianMotion));
  b->min_val = min;
  b->max_val = max;
  b->position = (min + max) * 0.5f;
  b->step_size = (max - min) * 0.1f;
  b->momentum = 0.5f;
  b->random_state = seed ? seed : 12345;
  return INTUITIVES_OK;
}

float brownian_next(BrownianMotion *b) {
  // Random acceleration
  float accel = (random_float(&b->random_state) - 0.5f) * 2.0f * b->step_size;

  // Attraction to target
  if (b->attraction > 0) {
    accel += (b->target - b->position) * b->attraction;
  }

  // Apply momentum
  b->velocity = b->velocity * b->momentum + accel * (1.0f - b->momentum);

  // Update position
  b->position += b->velocity;

  // Bounce at boundaries
  if (b->position < b->min_val) {
    b->position = b->min_val;
    b->velocity = -b->velocity * 0.5f;
  }
  if (b->position > b->max_val) {
    b->position = b->max_val;
    b->velocity = -b->velocity * 0.5f;
  }

  return b->position;
}

// ============================================================================
// STOCHASTIC SEQUENCER
// ============================================================================

IntuitivesResult stochastic_init(StochasticSequencer *s, uint32_t n,
                                 uint32_t seed) {
  if (!s)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(s, 0, sizeof(StochasticSequencer));
  s->num_steps = n > STOCHASTIC_MAX ? STOCHASTIC_MAX : n;
  s->random_state = seed ? seed : 12345;
  s->density = 1.0f;
  s->vel_variance = 0.1f;

  // Default: all steps equal probability
  for (uint32_t i = 0; i < s->num_steps; i++) {
    s->steps[i].prob = 0.5f;
    s->steps[i].note = 60;
    s->steps[i].vel = 0.8f;
    s->steps[i].dur = 1.0f;
  }

  return INTUITIVES_OK;
}

bool stochastic_advance(StochasticSequencer *s, int32_t *note, float *vel,
                        float *dur) {
  StochasticStep *step = &s->steps[s->current_step];

  s->current_step = (s->current_step + 1) % s->num_steps;

  // Check probability
  float adjusted_prob = step->prob * s->density;
  if (random_float(&s->random_state) > adjusted_prob) {
    return false; // No trigger
  }

  // Output with variance
  *note = step->note;
  *vel = step->vel + (random_float(&s->random_state) - 0.5f) * s->vel_variance;
  *vel = INTUITIVES_CLAMP(*vel, 0.0f, 1.0f);
  *dur = step->dur;

  return true;
}

// ============================================================================
// CHORD GENERATOR
// ============================================================================

static const int32_t CHORD_INTERVALS[][4] = {
    {0, 4, 7, -1}, // Major
    {0, 3, 7, -1}, // Minor
    {0, 3, 6, -1}, // Dim
    {0, 4, 7, 11}, // Maj7
    {0, 3, 7, 10}, // Min7
    {0, 4, 7, 10}  // Dom7
};

IntuitivesResult chord_gen_init(ChordGenerator *g, int32_t root, bool minor,
                                uint32_t seed) {
  if (!g)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(g, 0, sizeof(ChordGenerator));
  g->key_root = root;
  g->is_minor = minor;
  g->current_degree = 0;
  g->current_type = minor ? CHORD_MIN : CHORD_MAJ;
  g->random_state = seed ? seed : 12345;
  return INTUITIVES_OK;
}

int32_t chord_gen_next(ChordGenerator *g, int32_t *notes, size_t *num,
                       size_t max) {
  // Simple progression: I -> IV -> V -> I
  static const int32_t prog_major[] = {0, 5, 7, 0, 4, 5, 7, 0};
  static const ChordType types_major[] = {CHORD_MAJ, CHORD_MAJ, CHORD_MAJ,
                                          CHORD_MAJ, CHORD_MIN, CHORD_MAJ,
                                          CHORD_MAJ, CHORD_MAJ};

  int32_t step = random_int(&g->random_state, 0, 7);
  int32_t root = g->key_root + prog_major[step];
  ChordType type = types_major[step];

  const int32_t *intervals = CHORD_INTERVALS[type];
  *num = 0;

  for (int i = 0; i < 4 && intervals[i] >= 0 && *num < max; i++) {
    notes[(*num)++] = root + intervals[i];
  }

  g->current_degree = step;
  g->current_type = type;

  return root;
}
