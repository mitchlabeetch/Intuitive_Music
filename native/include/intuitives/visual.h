/**
 * INTUITIVES - Visual Module
 * Real-time audio analysis for visualization.
 */

#ifndef INTUITIVES_VISUAL_H
#define INTUITIVES_VISUAL_H

#include "core.h"

#ifdef __cplusplus
extern "C" {
#endif

// FEATURE 35: WAVEFORM SCOPE (Oscilloscope view)
#define SCOPE_BUFFER_SIZE 4096

typedef struct {
  Sample buffer_l[SCOPE_BUFFER_SIZE];
  Sample buffer_r[SCOPE_BUFFER_SIZE];
  size_t write_pos;
  size_t trigger_pos;
  float trigger_level;
  bool trigger_rising; // Trigger on rising or falling edge
  bool stereo_mode;
  float time_scale; // Zoom level
  uint32_t sample_rate;
} WaveformScope;

void scope_init(WaveformScope *s, uint32_t sr);
void scope_write(WaveformScope *s, const Sample *l, const Sample *r,
                 size_t frames);
void scope_get_display(WaveformScope *s, float *out_l, float *out_r,
                       size_t points);

// FEATURE 36: SPECTRUM ANALYZER (FFT magnitude)
#define SPECTRUM_FFT_SIZE 2048
#define SPECTRUM_BANDS 128

typedef struct {
  float *fft_buffer;
  float *window;
  float *magnitudes;
  float *smoothed;  // Smoothed magnitudes for display
  float *peaks;     // Peak hold values
  float smoothing;  // Smoothing factor
  float peak_decay; // Peak decay rate
  size_t write_pos;
  bool logarithmic; // Logarithmic frequency scale
  uint32_t sample_rate;
} SpectrumAnalyzer;

IntuitivesResult spectrum_analyzer_init(SpectrumAnalyzer *sa, uint32_t sr);
void spectrum_analyzer_free(SpectrumAnalyzer *sa);
void spectrum_analyzer_write(SpectrumAnalyzer *sa, const Sample *mono,
                             size_t frames);
void spectrum_analyzer_get_bands(SpectrumAnalyzer *sa, float *bands,
                                 size_t num_bands);
void spectrum_analyzer_get_peaks(SpectrumAnalyzer *sa, float *peaks,
                                 size_t num_bands);

// FEATURE 37: STEREO PHASE CORRELATION
typedef struct {
  float correlation; // -1 (out of phase) to +1 (in phase)
  float balance;     // -1 (left) to +1 (right)
  float width;       // Stereo width (0-1)
  float smoothing;
  float sum_lr, sum_ll, sum_rr; // For correlation calculation
  size_t sample_count;
} PhaseCorrelator;

void phase_init(PhaseCorrelator *pc);
void phase_reset(PhaseCorrelator *pc);
void phase_analyze(PhaseCorrelator *pc, const Sample *l, const Sample *r,
                   size_t frames);
float phase_get_correlation(PhaseCorrelator *pc);
void phase_get_goniometer(PhaseCorrelator *pc, float *x, float *y,
                          size_t points);

// FEATURE 38: LEVEL METERS (Peak/RMS with history)
#define METER_HISTORY_SIZE 256

typedef struct {
  float peak_l, peak_r;           // Current peak levels
  float rms_l, rms_r;             // Current RMS levels
  float peak_hold_l, peak_hold_r; // Peak hold
  float history_l[METER_HISTORY_SIZE];
  float history_r[METER_HISTORY_SIZE];
  size_t history_pos;
  float peak_decay; // Peak decay rate
  float hold_time;  // Peak hold time (seconds)
  float hold_counter_l, hold_counter_r;
  uint32_t sample_rate;
  bool clip_l, clip_r; // Clip indicators
} LevelMeter;

void meter_init(LevelMeter *m, uint32_t sr);
void meter_analyze(LevelMeter *m, const Sample *l, const Sample *r,
                   size_t frames);
void meter_get_levels_db(LevelMeter *m, float *peak_l, float *peak_r,
                         float *rms_l, float *rms_r);
void meter_reset_clip(LevelMeter *m);

// FEATURE 39: FLUID SIMULATION AUDIO BRIDGE
typedef struct {
  float amplitude;          // Triggers velocity field strength
  float frequency_centroid; // Affects color/direction
  float spectral_flux;      // Triggers new particles
  float onset_detected;     // Binary onset flag
  float tempo_estimate;     // BPM estimate
} FluidAudioParams;

void fluid_params_from_audio(FluidAudioParams *fp, const Sample *mono,
                             size_t frames, uint32_t sr);

// FEATURE 40: CHROMASYNESTHESIA (Pitch to color mapping)
typedef struct {
  uint8_t r, g, b;
  float brightness;
} SynesthesiaColor;

void chroma_note_to_color(int32_t midi_note, SynesthesiaColor *color);
void chroma_frequency_to_color(float freq, SynesthesiaColor *color);
void chroma_spectrum_to_colors(const float *magnitudes, size_t bins,
                               SynesthesiaColor *colors, uint32_t sr);

#ifdef __cplusplus
}
#endif
#endif
