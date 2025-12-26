/**
 * INTUITIVES - Audio Engine
 * Lock-free, real-time audio processing engine.
 */

#ifndef INTUITIVES_ENGINE_H
#define INTUITIVES_ENGINE_H

#include "core.h"
#include "effects.h"
#include "generators.h"
#include "oscillators.h"
#include "visual.h"

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// AUDIO ENGINE (Main processing hub)
// ============================================================================

typedef struct {
  uint32_t id;
  char name[64];
  OscillatorBank oscillators;
  EffectChain effects;
  float volume;
  float pan;
  bool mute;
  bool solo;
  bool armed;            // Armed for recording
  Sample *output_buffer; // Per-track output buffer
  size_t buffer_size;
} Track;

typedef struct {
  Sample *data;
  size_t size;
  size_t capacity;
  size_t head;
  size_t tail;
  _Atomic uint32_t read_pos; // Atomic for lock-free
  _Atomic uint32_t write_pos;
} LockFreeRingBuffer;

typedef struct {
  EngineConfig config;
  TransportState transport;
  Track tracks[INTUITIVES_MAX_TRACKS];
  uint32_t num_tracks;

  // Master section
  EffectChain master_effects;
  float master_volume;
  LevelMeter master_meter;

  // Timing
  float tempo; // BPM
  float time_signature_num;
  float time_signature_denom;
  SampleTime current_sample;
  float beat_position;

  // Output buffers
  Sample *mix_buffer_l;
  Sample *mix_buffer_r;
  LockFreeRingBuffer output_ring;

  // Visualization
  WaveformScope scope;
  SpectrumAnalyzer analyzer;

  bool initialized;
  bool running;
} AudioEngine;

// Engine lifecycle
IntuitivesResult engine_init(AudioEngine *engine, const EngineConfig *config);
void engine_free(AudioEngine *engine);
IntuitivesResult engine_start(AudioEngine *engine);
void engine_stop(AudioEngine *engine);

// Transport
void engine_play(AudioEngine *engine);
void engine_pause(AudioEngine *engine);
void engine_stop_transport(AudioEngine *engine);
void engine_set_tempo(AudioEngine *engine, float bpm);
void engine_set_position(AudioEngine *engine, SampleTime sample);

// Track management
int32_t engine_add_track(AudioEngine *engine, const char *name);
void engine_remove_track(AudioEngine *engine, uint32_t track_id);
Track *engine_get_track(AudioEngine *engine, uint32_t track_id);
void engine_set_track_volume(AudioEngine *engine, uint32_t track_id,
                             float volume);
void engine_set_track_pan(AudioEngine *engine, uint32_t track_id, float pan);

// Processing (called from audio thread)
void engine_process_block(AudioEngine *engine, Sample *output_l,
                          Sample *output_r, size_t frames);

// Ring buffer for audio output (lock-free)
IntuitivesResult ring_buffer_init(LockFreeRingBuffer *rb, size_t capacity);
void ring_buffer_free(LockFreeRingBuffer *rb);
size_t ring_buffer_write(LockFreeRingBuffer *rb, const Sample *data,
                         size_t count);
size_t ring_buffer_read(LockFreeRingBuffer *rb, Sample *data, size_t count);
size_t ring_buffer_available(const LockFreeRingBuffer *rb);

#ifdef __cplusplus
}
#endif
#endif
