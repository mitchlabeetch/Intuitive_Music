/**
 * INTUITIVES - Audio Analyzer with Shared Memory
 *
 * Real-time audio analysis with memory-mapped buffers for
 * high-performance visualization in the Python UI.
 *
 * "Does this sound cool?" - The only rule.
 *
 * (C) 2024 - MIT License
 */

#ifndef INTUITIVES_ANALYZER_H
#define INTUITIVES_ANALYZER_H

#include "core.h"
#include <stdatomic.h>

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// ANALYZER CONFIGURATION
// ============================================================================

#define ANALYZER_FFT_SIZE 2048
#define ANALYZER_SPECTRUM_BINS 512
#define ANALYZER_WAVEFORM_SIZE 1024
#define ANALYZER_HISTORY_SIZE 60 // ~1 second at 60fps

// ============================================================================
// ANALYZER DATA STRUCTURES (Shared Memory Layout)
// ============================================================================

/**
 * Real-time spectrum data for visualization.
 * This struct is designed for memory-mapping to Python.
 */
typedef struct {
  // Spectrum analysis
  float magnitude[ANALYZER_SPECTRUM_BINS]; // FFT magnitude (0-1 normalized)
  float phase[ANALYZER_SPECTRUM_BINS];     // FFT phase (-π to π)
  float smoothed[ANALYZER_SPECTRUM_BINS];  // Smoothed magnitude for display

  // Peak detection
  float peak_frequencies[8]; // Top 8 peak frequencies (Hz)
  float peak_magnitudes[8];  // Magnitudes of peaks
  uint32_t num_peaks;        // Number of valid peaks

  // Spectral features
  float spectral_centroid; // Brightness (Hz)
  float spectral_spread;   // Width of spectrum
  float spectral_flux;     // Rate of spectral change
  float spectral_rolloff;  // Frequency below which 85% of energy
  float spectral_flatness; // Tonality vs noise (0-1)

  // Chromagram (12 pitch classes for Chromasynesthesia)
  float chroma[12];           // Energy per pitch class (C, C#, D, ...)
  float dominant_pitch_class; // Most prominent pitch (0-11)

} SpectrumData;

/**
 * Waveform data for oscilloscope display.
 */
typedef struct {
  float samples_left[ANALYZER_WAVEFORM_SIZE];
  float samples_right[ANALYZER_WAVEFORM_SIZE];
  uint32_t write_pos;  // Current write position
  float zoom_level;    // Display zoom (1.0 = full buffer)
  float trigger_level; // Oscilloscope trigger level
  bool trigger_rising; // Trigger on rising edge
} WaveformData;

/**
 * Level metering data.
 */
typedef struct {
  // Current levels
  float rms_left;
  float rms_right;
  float peak_left;
  float peak_right;

  // Peak hold
  float peak_hold_left;
  float peak_hold_right;
  uint32_t peak_hold_samples; // Samples since peak

  // Loudness (ITU-R BS.1770)
  float momentary_lufs;  // 400ms window
  float short_term_lufs; // 3s window
  float integrated_lufs; // From start

  // Dynamics
  float dynamic_range; // Peak to average ratio (dB)
  float crest_factor;  // Peak to RMS ratio

  // Stereo analysis
  float correlation;        // Stereo correlation (-1 to 1)
  float balance;            // L/R balance (-1 to 1)
  float mono_compatibility; // How well it sums to mono (0-1)

} LevelData;

/**
 * Beat/tempo detection data.
 */
typedef struct {
  float bpm;            // Detected tempo
  float confidence;     // Detection confidence (0-1)
  float phase;          // Beat phase (0-1, 0 = on beat)
  uint32_t beat_count;  // Total beats detected
  SampleTime last_beat; // Sample time of last beat
  bool is_on_beat;      // Currently on a beat

  // Onset detection
  float onset_strength; // Current onset strength
  bool onset_detected;  // Onset in this frame
} BeatData;

/**
 * Main analyzer shared memory structure.
 * This entire struct can be memory-mapped for Python access.
 */
typedef struct {
  // Header
  uint32_t magic;   // Magic number for validation (0x494E5455 = "INTU")
  uint32_t version; // Structure version
  uint32_t size;    // Total size in bytes
  _Atomic uint32_t frame_count; // Increments each update (for sync)

  // Configuration
  uint32_t sample_rate;
  uint32_t fft_size;
  uint32_t update_rate_hz; // Target update rate

  // Status
  _Atomic bool is_active;
  _Atomic bool needs_reconfigure;

  // Analysis data
  SpectrumData spectrum;
  WaveformData waveform;
  LevelData levels;
  BeatData beat;

  // History for animation (ring buffers)
  float spectrum_history[ANALYZER_HISTORY_SIZE][ANALYZER_SPECTRUM_BINS];
  float level_history_left[ANALYZER_HISTORY_SIZE];
  float level_history_right[ANALYZER_HISTORY_SIZE];
  uint32_t history_write_pos;

  // Timestamp
  uint64_t last_update_ns; // Nanoseconds since epoch

} AnalyzerSharedMemory;

#define ANALYZER_MAGIC 0x494E5455 // "INTU" in ASCII

// ============================================================================
// ANALYZER FUNCTIONS
// ============================================================================

/**
 * Initialize the analyzer with shared memory.
 * Creates a memory-mapped file that Python can access.
 *
 * @param sample_rate Audio sample rate
 * @param shm_name Name for shared memory (e.g., "/intuitives_analyzer")
 * @return Pointer to shared memory, or NULL on failure
 */
AnalyzerSharedMemory *analyzer_init(uint32_t sample_rate, const char *shm_name);

/**
 * Free the analyzer and unmap shared memory.
 */
void analyzer_free(AnalyzerSharedMemory *analyzer);

/**
 * Process a block of audio samples.
 * Updates spectrum, waveform, and level data.
 *
 * @param analyzer Analyzer instance
 * @param left Left channel samples
 * @param right Right channel samples
 * @param frames Number of frames
 */
void analyzer_process(AnalyzerSharedMemory *analyzer, const float *left,
                      const float *right, uint32_t frames);

/**
 * Get the shared memory path for Python access.
 */
const char *analyzer_get_shm_path(void);

/**
 * Compute chromagram from spectrum for Chromasynesthesia visualization.
 */
void analyzer_compute_chroma(AnalyzerSharedMemory *analyzer);

/**
 * Detect beats and update tempo estimation.
 */
void analyzer_detect_beat(AnalyzerSharedMemory *analyzer);

/**
 * Apply smoothing to spectrum data.
 * @param attack Attack time in ms (how fast values rise)
 * @param release Release time in ms (how fast values fall)
 */
void analyzer_smooth_spectrum(AnalyzerSharedMemory *analyzer, float attack_ms,
                              float release_ms);

// ============================================================================
// PYTHON BINDING HELPERS
// ============================================================================

/**
 * Get a pointer to the raw spectrum magnitude buffer.
 * For ctypes/numpy access from Python.
 */
static inline float *analyzer_get_spectrum_ptr(AnalyzerSharedMemory *a) {
  return a ? a->spectrum.magnitude : NULL;
}

/**
 * Get a pointer to the chromagram for Chromasynesthesia.
 */
static inline float *analyzer_get_chroma_ptr(AnalyzerSharedMemory *a) {
  return a ? a->spectrum.chroma : NULL;
}

/**
 * Get a pointer to the waveform samples.
 */
static inline float *analyzer_get_waveform_left_ptr(AnalyzerSharedMemory *a) {
  return a ? a->waveform.samples_left : NULL;
}

static inline float *analyzer_get_waveform_right_ptr(AnalyzerSharedMemory *a) {
  return a ? a->waveform.samples_right : NULL;
}

/**
 * Check if the analyzer data is valid and current.
 */
static inline bool analyzer_is_valid(const AnalyzerSharedMemory *a) {
  return a && a->magic == ANALYZER_MAGIC && atomic_load(&a->is_active);
}

/**
 * Get the current frame count for synchronization.
 */
static inline uint32_t analyzer_get_frame(const AnalyzerSharedMemory *a) {
  return a ? atomic_load(&a->frame_count) : 0;
}

#ifdef __cplusplus
}
#endif

#endif // INTUITIVES_ANALYZER_H
