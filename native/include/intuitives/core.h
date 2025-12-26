/**
 * INTUITIVES - Native Audio Engine Core
 *
 * Rule-free, experimental DAW core types and constants.
 * "Does this sound cool?" - The only rule.
 *
 * (C) 2024 - MIT License
 */

#ifndef INTUITIVES_CORE_H
#define INTUITIVES_CORE_H

#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// CORE CONSTANTS
// ============================================================================

#define INTUITIVES_VERSION_MAJOR 1
#define INTUITIVES_VERSION_MINOR 0
#define INTUITIVES_VERSION_PATCH 0

#define INTUITIVES_DEFAULT_SAMPLE_RATE 48000
#define INTUITIVES_DEFAULT_BUFFER_SIZE 256
#define INTUITIVES_DEFAULT_CHANNELS 2

#define INTUITIVES_MAX_TRACKS 64
#define INTUITIVES_MAX_EFFECTS_PER_TRACK 16
#define INTUITIVES_MAX_OSCILLATORS 32
#define INTUITIVES_MAX_GENERATORS 16

#define INTUITIVES_PI 3.14159265358979323846
#define INTUITIVES_TWO_PI 6.28318530717958647692
#define INTUITIVES_EPSILON 1e-7f

// SIMD alignment for optimal performance
#define INTUITIVES_SIMD_ALIGN 32

// ============================================================================
// PLATFORM DETECTION
// ============================================================================

#if defined(__APPLE__)
#define INTUITIVES_MACOS 1
#elif defined(_WIN32) || defined(_WIN64)
#define INTUITIVES_WINDOWS 1
#elif defined(__linux__)
#define INTUITIVES_LINUX 1
#elif defined(__EMSCRIPTEN__)
#define INTUITIVES_WASM 1
#endif

// SIMD detection
#if defined(__AVX2__)
#define INTUITIVES_HAS_AVX2 1
#endif
#if defined(__AVX__)
#define INTUITIVES_HAS_AVX 1
#endif
#if defined(__SSE4_1__)
#define INTUITIVES_HAS_SSE4 1
#endif
#if defined(__ARM_NEON)
#define INTUITIVES_HAS_NEON 1
#endif

// ============================================================================
// CORE TYPES
// ============================================================================

typedef float Sample;         // Audio sample type (32-bit float)
typedef double PreciseSample; // For precision operations
typedef int32_t MIDINote;     // MIDI note number (0-127)
typedef int32_t MIDIVelocity; // MIDI velocity (0-127)
typedef uint64_t SampleTime;  // Sample-accurate timing
typedef float Phase;          // Oscillator phase (0-1)
typedef float Frequency;      // Frequency in Hz
typedef float Amplitude;      // Amplitude (0-1)
typedef float Parameter;      // Normalized parameter (0-1)

// Result codes
typedef enum {
  INTUITIVES_OK = 0,
  INTUITIVES_ERROR_NULL_POINTER,
  INTUITIVES_ERROR_INVALID_PARAM,
  INTUITIVES_ERROR_BUFFER_OVERFLOW,
  INTUITIVES_ERROR_NOT_INITIALIZED,
  INTUITIVES_ERROR_ALREADY_RUNNING,
  INTUITIVES_ERROR_AUDIO_DEVICE,
  INTUITIVES_ERROR_OUT_OF_MEMORY
} IntuitivesResult;

// Transport state
typedef enum {
  TRANSPORT_STOPPED = 0,
  TRANSPORT_PLAYING,
  TRANSPORT_RECORDING,
  TRANSPORT_PAUSED
} TransportState;

// Waveform types for oscillators
typedef enum {
  WAVE_SINE = 0,
  WAVE_SAW,
  WAVE_SQUARE,
  WAVE_TRIANGLE,
  WAVE_NOISE,
  WAVE_PULSE,
  WAVE_CHAOS,   // Lorenz attractor
  WAVE_FRACTAL, // Mandelbrot-derived
  WAVE_WAVETABLE,
  WAVE_MORPHING // Blend between waveforms
} WaveformType;

// Effect types
typedef enum {
  EFFECT_NONE = 0,
  EFFECT_FILTER,
  EFFECT_REVERB,
  EFFECT_DELAY,
  EFFECT_DISTORTION,
  EFFECT_COMPRESSOR,
  EFFECT_CHORUS,
  EFFECT_PHASER,
  EFFECT_BITCRUSHER,
  EFFECT_GRANULAR,
  EFFECT_SPECTRAL,
  EFFECT_CONVOLUTION
} EffectType;

// Filter types
typedef enum {
  FILTER_LOWPASS = 0,
  FILTER_HIGHPASS,
  FILTER_BANDPASS,
  FILTER_NOTCH,
  FILTER_ALLPASS,
  FILTER_PEAK,
  FILTER_LOWSHELF,
  FILTER_HIGHSHELF,
  FILTER_FORMANT,
  FILTER_MOOG,     // Moog ladder filter
  FILTER_STATE_VAR // State variable filter
} FilterType;

// Generator types (for procedural/AI-driven generation)
typedef enum {
  GEN_MARKOV = 0,
  GEN_CELLULAR,
  GEN_GENETIC,
  GEN_LSYSTEM,
  GEN_BROWNIAN,
  GEN_STOCHASTIC,
  GEN_FRACTAL,
  GEN_CHAOS
} GeneratorType;

// ============================================================================
// CORE STRUCTURES
// ============================================================================

// Stereo sample pair
typedef struct {
  Sample left;
  Sample right;
} StereoSample;

// Audio buffer (interleaved stereo) - prefixed to avoid CoreAudio conflict
typedef struct {
  Sample *data;
  size_t size;   // Total samples (frames * channels)
  size_t frames; // Number of frames
  uint32_t channels;
  uint32_t sample_rate;
} IntuitivesAudioBuffer;

// MIDI note event
typedef struct {
  MIDINote note;
  MIDIVelocity velocity;
  SampleTime start;    // Sample-accurate start time
  SampleTime duration; // Duration in samples
  bool is_active;
} MIDINoteEvent;

// Parameter automation point
typedef struct {
  SampleTime time;
  Parameter value;
  float curve; // Curve factor (-1 to 1, 0 = linear)
} AutomationPoint;

// Engine configuration
typedef struct {
  uint32_t sample_rate;
  uint32_t buffer_size;
  uint32_t channels;
  uint32_t bit_depth;
  bool realtime_priority;
  bool simd_enabled;
} EngineConfig;

// Audio analysis results (for visualization)
typedef struct {
  float rms_left;
  float rms_right;
  float peak_left;
  float peak_right;
  float lufs;         // Integrated loudness (LUFS)
  float correlation;  // Stereo correlation (-1 to 1)
  float crest_factor; // Peak to RMS ratio
  float *spectrum;    // FFT magnitude bins (if computed)
  size_t spectrum_size;
} AudioAnalysis;

// ============================================================================
// UTILITY MACROS
// ============================================================================

#define INTUITIVES_MIN(a, b) ((a) < (b) ? (a) : (b))
#define INTUITIVES_MAX(a, b) ((a) > (b) ? (a) : (b))
#define INTUITIVES_CLAMP(x, lo, hi) INTUITIVES_MIN(INTUITIVES_MAX(x, lo), hi)
#define INTUITIVES_LERP(a, b, t) ((a) + ((b) - (a)) * (t))
#define INTUITIVES_DB_TO_LINEAR(db) powf(10.0f, (db) / 20.0f)
#define INTUITIVES_LINEAR_TO_DB(lin)                                           \
  (20.0f * log10f(INTUITIVES_MAX(lin, INTUITIVES_EPSILON)))
#define INTUITIVES_FREQ_TO_MIDI(freq) (69.0f + 12.0f * log2f((freq) / 440.0f))
#define INTUITIVES_MIDI_TO_FREQ(midi)                                          \
  (440.0f * powf(2.0f, ((midi) - 69.0f) / 12.0f))

// Fast approximations
static inline float intuitives_fast_sin(float x) {
  // Polynomial approximation (valid for -π to π)
  const float B = 4.0f / INTUITIVES_PI;
  const float C = -4.0f / (INTUITIVES_PI * INTUITIVES_PI);
  float y = B * x + C * x * fabsf(x);
  const float P = 0.225f;
  return P * (y * fabsf(y) - y) + y;
}

static inline float intuitives_fast_tanh(float x) {
  // Fast hyperbolic tangent approximation
  if (x < -3.0f)
    return -1.0f;
  if (x > 3.0f)
    return 1.0f;
  float x2 = x * x;
  return x * (27.0f + x2) / (27.0f + 9.0f * x2);
}

static inline float intuitives_soft_clip(float x) {
  // Soft clipping using fast tanh
  return intuitives_fast_tanh(x);
}

#ifdef __cplusplus
}
#endif

#endif // INTUITIVES_CORE_H
