/**
 * INTUITIVES - Main Audio Engine Implementation
 */

#include "intuitives.h"
#include <math.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ============================================================================
// LOCK-FREE RING BUFFER
// ============================================================================

IntuitivesResult ring_buffer_init(LockFreeRingBuffer *rb, size_t capacity) {
  if (!rb)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(rb, 0, sizeof(LockFreeRingBuffer));

  rb->data = (Sample *)calloc(capacity, sizeof(Sample));
  if (!rb->data)
    return INTUITIVES_ERROR_OUT_OF_MEMORY;

  rb->capacity = capacity;
  atomic_store(&rb->read_pos, 0);
  atomic_store(&rb->write_pos, 0);

  return INTUITIVES_OK;
}

void ring_buffer_free(LockFreeRingBuffer *rb) {
  if (rb && rb->data) {
    free(rb->data);
    rb->data = NULL;
  }
}

size_t ring_buffer_write(LockFreeRingBuffer *rb, const Sample *data,
                         size_t count) {
  uint32_t write_pos = atomic_load(&rb->write_pos);
  uint32_t read_pos = atomic_load(&rb->read_pos);

  size_t available = (read_pos - write_pos - 1 + rb->capacity) % rb->capacity;
  size_t to_write = count < available ? count : available;

  for (size_t i = 0; i < to_write; i++) {
    rb->data[(write_pos + i) % rb->capacity] = data[i];
  }

  atomic_store(&rb->write_pos, (write_pos + to_write) % rb->capacity);
  return to_write;
}

size_t ring_buffer_read(LockFreeRingBuffer *rb, Sample *data, size_t count) {
  uint32_t write_pos = atomic_load(&rb->write_pos);
  uint32_t read_pos = atomic_load(&rb->read_pos);

  size_t available = (write_pos - read_pos + rb->capacity) % rb->capacity;
  size_t to_read = count < available ? count : available;

  for (size_t i = 0; i < to_read; i++) {
    data[i] = rb->data[(read_pos + i) % rb->capacity];
  }

  atomic_store(&rb->read_pos, (read_pos + to_read) % rb->capacity);
  return to_read;
}

size_t ring_buffer_available(const LockFreeRingBuffer *rb) {
  uint32_t write_pos = atomic_load(&rb->write_pos);
  uint32_t read_pos = atomic_load(&rb->read_pos);
  return (write_pos - read_pos + rb->capacity) % rb->capacity;
}

// ============================================================================
// AUDIO ENGINE
// ============================================================================

IntuitivesResult engine_init(AudioEngine *engine, const EngineConfig *config) {
  if (!engine)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(engine, 0, sizeof(AudioEngine));

  if (config) {
    engine->config = *config;
  } else {
    engine->config.sample_rate = INTUITIVES_DEFAULT_SAMPLE_RATE;
    engine->config.buffer_size = INTUITIVES_DEFAULT_BUFFER_SIZE;
    engine->config.channels = INTUITIVES_DEFAULT_CHANNELS;
    engine->config.bit_depth = 24;
    engine->config.realtime_priority = true;
    engine->config.simd_enabled = true;
  }

  engine->tempo = 120.0f;
  engine->time_signature_num = 4;
  engine->time_signature_denom = 4;
  engine->master_volume = 1.0f;
  engine->transport = TRANSPORT_STOPPED;

  // Allocate mix buffers
  size_t buf_size = engine->config.buffer_size * sizeof(Sample);
  engine->mix_buffer_l =
      (Sample *)calloc(engine->config.buffer_size, sizeof(Sample));
  engine->mix_buffer_r =
      (Sample *)calloc(engine->config.buffer_size, sizeof(Sample));

  if (!engine->mix_buffer_l || !engine->mix_buffer_r) {
    engine_free(engine);
    return INTUITIVES_ERROR_OUT_OF_MEMORY;
  }

  // Initialize output ring buffer (2 seconds)
  IntuitivesResult res =
      ring_buffer_init(&engine->output_ring, engine->config.sample_rate * 2 *
                                                 engine->config.channels);
  if (res != INTUITIVES_OK) {
    engine_free(engine);
    return res;
  }

  // Initialize master effects
  effect_chain_init(&engine->master_effects, engine->config.sample_rate);

  // Initialize visualization
  scope_init(&engine->scope, engine->config.sample_rate);
  spectrum_analyzer_init(&engine->analyzer, engine->config.sample_rate);
  meter_init(&engine->master_meter, engine->config.sample_rate);

  engine->initialized = true;
  return INTUITIVES_OK;
}

void engine_free(AudioEngine *engine) {
  if (!engine)
    return;

  engine->running = false;

  free(engine->mix_buffer_l);
  free(engine->mix_buffer_r);
  ring_buffer_free(&engine->output_ring);
  spectrum_analyzer_free(&engine->analyzer);

  // Free track buffers
  for (uint32_t i = 0; i < engine->num_tracks; i++) {
    free(engine->tracks[i].output_buffer);
  }

  engine->initialized = false;
}

IntuitivesResult engine_start(AudioEngine *engine) {
  if (!engine || !engine->initialized)
    return INTUITIVES_ERROR_NOT_INITIALIZED;
  if (engine->running)
    return INTUITIVES_ERROR_ALREADY_RUNNING;

  engine->running = true;
  return INTUITIVES_OK;
}

void engine_stop(AudioEngine *engine) {
  if (engine) {
    engine->running = false;
  }
}

// ============================================================================
// TRANSPORT CONTROL
// ============================================================================

void engine_play(AudioEngine *engine) {
  if (engine)
    engine->transport = TRANSPORT_PLAYING;
}

void engine_pause(AudioEngine *engine) {
  if (engine)
    engine->transport = TRANSPORT_PAUSED;
}

void engine_stop_transport(AudioEngine *engine) {
  if (engine) {
    engine->transport = TRANSPORT_STOPPED;
    engine->current_sample = 0;
    engine->beat_position = 0;
  }
}

void engine_set_tempo(AudioEngine *engine, float bpm) {
  if (engine) {
    engine->tempo = INTUITIVES_CLAMP(bpm, 20.0f, 300.0f);
  }
}

void engine_set_position(AudioEngine *engine, SampleTime sample) {
  if (engine) {
    engine->current_sample = sample;
    // Calculate beat position
    float samples_per_beat =
        (60.0f / engine->tempo) * engine->config.sample_rate;
    engine->beat_position = (float)sample / samples_per_beat;
  }
}

// ============================================================================
// TRACK MANAGEMENT
// ============================================================================

int32_t engine_add_track(AudioEngine *engine, const char *name) {
  if (!engine || engine->num_tracks >= INTUITIVES_MAX_TRACKS)
    return -1;

  uint32_t id = engine->num_tracks;
  Track *track = &engine->tracks[id];

  memset(track, 0, sizeof(Track));
  track->id = id;
  strncpy(track->name, name, 63);
  track->volume = 1.0f;
  track->pan = 0.5f;

  // Initialize track components
  osc_bank_init(&track->oscillators, engine->config.sample_rate);
  effect_chain_init(&track->effects, engine->config.sample_rate);

  // Allocate track buffer
  track->buffer_size = engine->config.buffer_size;
  track->output_buffer =
      (Sample *)calloc(track->buffer_size * 2, sizeof(Sample));

  engine->num_tracks++;
  return (int32_t)id;
}

void engine_remove_track(AudioEngine *engine, uint32_t track_id) {
  if (!engine || track_id >= engine->num_tracks)
    return;

  Track *track = &engine->tracks[track_id];
  free(track->output_buffer);

  // Shift remaining tracks
  for (uint32_t i = track_id; i < engine->num_tracks - 1; i++) {
    engine->tracks[i] = engine->tracks[i + 1];
    engine->tracks[i].id = i;
  }

  engine->num_tracks--;
}

Track *engine_get_track(AudioEngine *engine, uint32_t track_id) {
  if (!engine || track_id >= engine->num_tracks)
    return NULL;
  return &engine->tracks[track_id];
}

void engine_set_track_volume(AudioEngine *engine, uint32_t track_id,
                             float volume) {
  Track *track = engine_get_track(engine, track_id);
  if (track)
    track->volume = INTUITIVES_CLAMP(volume, 0.0f, 2.0f);
}

void engine_set_track_pan(AudioEngine *engine, uint32_t track_id, float pan) {
  Track *track = engine_get_track(engine, track_id);
  if (track)
    track->pan = INTUITIVES_CLAMP(pan, 0.0f, 1.0f);
}

// ============================================================================
// AUDIO PROCESSING
// ============================================================================

void engine_process_block(AudioEngine *engine, Sample *output_l,
                          Sample *output_r, size_t frames) {
  if (!engine || !engine->initialized) {
    memset(output_l, 0, frames * sizeof(Sample));
    memset(output_r, 0, frames * sizeof(Sample));
    return;
  }

  // Clear mix buffers
  memset(engine->mix_buffer_l, 0, frames * sizeof(Sample));
  memset(engine->mix_buffer_r, 0, frames * sizeof(Sample));

  // Process each track
  if (engine->transport == TRANSPORT_PLAYING) {
    // Temporary buffers for track processing
    Sample *track_l = (Sample *)alloca(frames * sizeof(Sample));
    Sample *track_r = (Sample *)alloca(frames * sizeof(Sample));

    for (uint32_t t = 0; t < engine->num_tracks; t++) {
      Track *track = &engine->tracks[t];

      if (track->mute)
        continue;

      // Process oscillators
      memset(track_l, 0, frames * sizeof(Sample));
      memset(track_r, 0, frames * sizeof(Sample));
      osc_bank_process(&track->oscillators, track_l, track_r, frames);

      // Process effects chain
      effect_chain_process(&track->effects, track_l, track_r, frames);

      // Apply track volume and pan, mix to master
      float vol = track->volume;
      float pan_l = 1.0f - track->pan;
      float pan_r = track->pan;

      // Check solo
      bool any_solo = false;
      for (uint32_t s = 0; s < engine->num_tracks; s++) {
        if (engine->tracks[s].solo) {
          any_solo = true;
          break;
        }
      }

      if (any_solo && !track->solo)
        continue;

      for (size_t i = 0; i < frames; i++) {
        engine->mix_buffer_l[i] += track_l[i] * vol * pan_l;
        engine->mix_buffer_r[i] += track_r[i] * vol * pan_r;
      }
    }

    // Advance transport
    engine->current_sample += frames;
    float samples_per_beat =
        (60.0f / engine->tempo) * engine->config.sample_rate;
    engine->beat_position = (float)engine->current_sample / samples_per_beat;
  }

  // Process master effects
  effect_chain_process(&engine->master_effects, engine->mix_buffer_l,
                       engine->mix_buffer_r, frames);

  // Apply master volume
  for (size_t i = 0; i < frames; i++) {
    engine->mix_buffer_l[i] *= engine->master_volume;
    engine->mix_buffer_r[i] *= engine->master_volume;
  }

  // Soft clip master output
  for (size_t i = 0; i < frames; i++) {
    engine->mix_buffer_l[i] = intuitives_soft_clip(engine->mix_buffer_l[i]);
    engine->mix_buffer_r[i] = intuitives_soft_clip(engine->mix_buffer_r[i]);
  }

  // Update visualization
  scope_write(&engine->scope, engine->mix_buffer_l, engine->mix_buffer_r,
              frames);

  Sample mono[256];
  size_t mono_frames = frames > 256 ? 256 : frames;
  for (size_t i = 0; i < mono_frames; i++) {
    mono[i] = (engine->mix_buffer_l[i] + engine->mix_buffer_r[i]) * 0.5f;
  }
  spectrum_analyzer_write(&engine->analyzer, mono, mono_frames);
  meter_analyze(&engine->master_meter, engine->mix_buffer_l,
                engine->mix_buffer_r, frames);

  // Write to output
  memcpy(output_l, engine->mix_buffer_l, frames * sizeof(Sample));
  memcpy(output_r, engine->mix_buffer_r, frames * sizeof(Sample));
}

// ============================================================================
// CONVENIENCE FUNCTIONS
// ============================================================================

AudioEngine *intuitives_create_default_engine(void) {
  AudioEngine *engine = (AudioEngine *)calloc(1, sizeof(AudioEngine));
  if (!engine)
    return NULL;

  if (engine_init(engine, NULL) != INTUITIVES_OK) {
    free(engine);
    return NULL;
  }

  return engine;
}

// ============================================================================
// BASIC SYNTH
// ============================================================================

IntuitivesResult synth_init(BasicSynth *synth, uint32_t sample_rate) {
  if (!synth)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(synth, 0, sizeof(BasicSynth));

  synth->sample_rate = sample_rate;

  quantum_osc_init(&synth->osc1, sample_rate);
  quantum_osc_init(&synth->osc2, sample_rate);
  noise_gen_init(&synth->noise, NOISE_WHITE, 0);
  svf_init(&synth->filter, sample_rate);

  synth->osc1_level = 0.5f;
  synth->osc2_level = 0.3f;
  synth->noise_level = 0.0f;

  synth->amp_attack = 0.01f;
  synth->amp_decay = 0.2f;
  synth->amp_sustain = 0.7f;
  synth->amp_release = 0.3f;

  synth->filter_attack = 0.05f;
  synth->filter_decay = 0.3f;
  synth->filter_sustain = 0.5f;
  synth->filter_release = 0.4f;
  synth->filter_env_amount = 2000.0f;

  svf_set_cutoff(&synth->filter, 1000.0f);
  svf_set_resonance(&synth->filter, 0.5f);

  return INTUITIVES_OK;
}

void synth_note_on(BasicSynth *synth, int32_t note, float velocity) {
  float freq = INTUITIVES_MIDI_TO_FREQ((float)note);

  quantum_osc_set_frequency(&synth->osc1, freq);
  quantum_osc_set_frequency(&synth->osc2, freq * 1.005f); // Slight detune

  synth->gate = true;
  synth->amp_env_level = 0.0f;
  synth->filter_env_level = 0.0f;
}

void synth_note_off(BasicSynth *synth) { synth->gate = false; }

Sample synth_process(BasicSynth *synth) {
  // Oscillators
  Sample osc = synth->osc1_level * quantum_osc_process(&synth->osc1);
  osc += synth->osc2_level * quantum_osc_process(&synth->osc2);
  osc += synth->noise_level * noise_gen_process(&synth->noise);

  // Simple ADSR envelope
  float amp_target, filter_target;
  float amp_coef, filter_coef;

  if (synth->gate) {
    if (synth->amp_env_level < 0.99f) {
      amp_target = 1.0f;
      amp_coef = expf(-1.0f / (synth->amp_attack * synth->sample_rate));
    } else {
      amp_target = synth->amp_sustain;
      amp_coef = expf(-1.0f / (synth->amp_decay * synth->sample_rate));
    }

    if (synth->filter_env_level < 0.99f) {
      filter_target = 1.0f;
      filter_coef = expf(-1.0f / (synth->filter_attack * synth->sample_rate));
    } else {
      filter_target = synth->filter_sustain;
      filter_coef = expf(-1.0f / (synth->filter_decay * synth->sample_rate));
    }
  } else {
    amp_target = 0.0f;
    amp_coef = expf(-1.0f / (synth->amp_release * synth->sample_rate));
    filter_target = 0.0f;
    filter_coef = expf(-1.0f / (synth->filter_release * synth->sample_rate));
  }

  synth->amp_env_level =
      amp_coef * (synth->amp_env_level - amp_target) + amp_target;
  synth->filter_env_level =
      filter_coef * (synth->filter_env_level - filter_target) + filter_target;

  // Apply filter with envelope modulation
  float cutoff = 500.0f + synth->filter_env_level * synth->filter_env_amount;
  svf_set_cutoff(&synth->filter, cutoff);

  Sample filtered = svf_process(&synth->filter, osc);

  return filtered * synth->amp_env_level;
}

void synth_process_block(BasicSynth *synth, Sample *buffer, size_t frames) {
  for (size_t i = 0; i < frames; i++) {
    buffer[i] = synth_process(synth);
  }
}

// ============================================================================
// LIBRARY INFO
// ============================================================================

void intuitives_get_info(IntuitivesInfo *info) {
  if (!info)
    return;

  info->major = INTUITIVES_VERSION_MAJOR;
  info->minor = INTUITIVES_VERSION_MINOR;
  info->patch = INTUITIVES_VERSION_PATCH;
  info->build_date = __DATE__;

#if defined(INTUITIVES_MACOS)
  info->platform = "macOS";
#elif defined(INTUITIVES_WINDOWS)
  info->platform = "Windows";
#elif defined(INTUITIVES_LINUX)
  info->platform = "Linux";
#elif defined(INTUITIVES_WASM)
  info->platform = "WebAssembly";
#else
  info->platform = "Unknown";
#endif

#if defined(INTUITIVES_HAS_AVX2)
  info->simd_enabled = true;
#elif defined(INTUITIVES_HAS_AVX)
  info->simd_enabled = true;
#elif defined(INTUITIVES_HAS_NEON)
  info->simd_enabled = true;
#else
  info->simd_enabled = false;
#endif

  // Feature list
  info->num_features = 0;
  info->features[info->num_features++] = "Quantum Oscillator";
  info->features[info->num_features++] = "Chaos Oscillator (Lorenz)";
  info->features[info->num_features++] = "Wavetable Oscillator";
  info->features[info->num_features++] = "FM Synthesis";
  info->features[info->num_features++] = "Additive Synthesis";
  info->features[info->num_features++] = "Noise Generator (6 types)";
  info->features[info->num_features++] = "Fractal Oscillator (Mandelbrot)";
  info->features[info->num_features++] = "State Variable Filter";
  info->features[info->num_features++] = "Moog Ladder Filter";
  info->features[info->num_features++] = "Formant Filter";
  info->features[info->num_features++] = "Multi-tap Delay";
  info->features[info->num_features++] = "Schroeder Reverb";
  info->features[info->num_features++] = "Waveshaper Distortion (8 types)";
  info->features[info->num_features++] = "Compressor/Limiter";
  info->features[info->num_features++] = "Chorus";
  info->features[info->num_features++] = "Phaser";
  info->features[info->num_features++] = "Bitcrusher";
  info->features[info->num_features++] = "Granular Synthesis";
  info->features[info->num_features++] = "Spectral Processing";
  info->features[info->num_features++] = "Markov Melody Generator";
  info->features[info->num_features++] = "Cellular Automata Rhythm";
  info->features[info->num_features++] = "Genetic Algorithm Melody";
  info->features[info->num_features++] = "L-System Generator";
  info->features[info->num_features++] = "Brownian Motion Generator";
  info->features[info->num_features++] = "Stochastic Sequencer";
  info->features[info->num_features++] = "Chord Progression Generator";
  info->features[info->num_features++] = "Image-to-Spectrum Synthesis";
  info->features[info->num_features++] = "Color-to-Harmony Mapping";
  info->features[info->num_features++] = "Pixel Rhythm";
  info->features[info->num_features++] = "Gesture Envelope";
  info->features[info->num_features++] = "Motion Filter";
  info->features[info->num_features++] = "Text-to-Melody";
  info->features[info->num_features++] = "Random Walk Generator";
  info->features[info->num_features++] = "Emoji Drums";
  info->features[info->num_features++] = "Waveform Scope";
  info->features[info->num_features++] = "Spectrum Analyzer";
  info->features[info->num_features++] = "Phase Correlator";
  info->features[info->num_features++] = "Level Meters";
  info->features[info->num_features++] = "Fluid Simulation Bridge";
  info->features[info->num_features++] = "Chromasynesthesia";
}

const char *intuitives_version_string(void) {
  static char version[32];
  snprintf(version, sizeof(version), "%d.%d.%d", INTUITIVES_VERSION_MAJOR,
           INTUITIVES_VERSION_MINOR, INTUITIVES_VERSION_PATCH);
  return version;
}
