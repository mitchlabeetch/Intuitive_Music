/**
 * INTUITIVES - Visual Analysis Implementation
 * Real-time audio analysis for visualization.
 */

#include "intuitives/visual.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

// ============================================================================
// WAVEFORM SCOPE
// ============================================================================

void scope_init(WaveformScope *s, uint32_t sr) {
  memset(s, 0, sizeof(WaveformScope));
  s->sample_rate = sr;
  s->trigger_level = 0.0f;
  s->trigger_rising = true;
  s->stereo_mode = true;
  s->time_scale = 1.0f;
}

void scope_write(WaveformScope *s, const Sample *l, const Sample *r,
                 size_t frames) {
  for (size_t i = 0; i < frames; i++) {
    s->buffer_l[s->write_pos] = l[i];
    s->buffer_r[s->write_pos] = r ? r[i] : l[i];

    // Trigger detection
    if (s->trigger_rising) {
      if (s->buffer_l[(s->write_pos + SCOPE_BUFFER_SIZE - 1) %
                      SCOPE_BUFFER_SIZE] < s->trigger_level &&
          l[i] >= s->trigger_level) {
        s->trigger_pos = s->write_pos;
      }
    } else {
      if (s->buffer_l[(s->write_pos + SCOPE_BUFFER_SIZE - 1) %
                      SCOPE_BUFFER_SIZE] > s->trigger_level &&
          l[i] <= s->trigger_level) {
        s->trigger_pos = s->write_pos;
      }
    }

    s->write_pos = (s->write_pos + 1) % SCOPE_BUFFER_SIZE;
  }
}

void scope_get_display(WaveformScope *s, float *out_l, float *out_r,
                       size_t points) {
  float step = (SCOPE_BUFFER_SIZE / s->time_scale) / (float)points;
  size_t start = s->trigger_pos;

  for (size_t i = 0; i < points; i++) {
    size_t idx = (start + (size_t)(i * step)) % SCOPE_BUFFER_SIZE;
    out_l[i] = s->buffer_l[idx];
    if (out_r)
      out_r[i] = s->buffer_r[idx];
  }
}

// ============================================================================
// SPECTRUM ANALYZER
// ============================================================================

IntuitivesResult spectrum_analyzer_init(SpectrumAnalyzer *sa, uint32_t sr) {
  if (!sa)
    return INTUITIVES_ERROR_NULL_POINTER;
  memset(sa, 0, sizeof(SpectrumAnalyzer));

  sa->sample_rate = sr;
  sa->smoothing = 0.8f;
  sa->peak_decay = 0.99f;
  sa->logarithmic = true;

  sa->fft_buffer = (float *)calloc(SPECTRUM_FFT_SIZE, sizeof(float));
  sa->window = (float *)calloc(SPECTRUM_FFT_SIZE, sizeof(float));
  sa->magnitudes = (float *)calloc(SPECTRUM_FFT_SIZE / 2, sizeof(float));
  sa->smoothed = (float *)calloc(SPECTRUM_FFT_SIZE / 2, sizeof(float));
  sa->peaks = (float *)calloc(SPECTRUM_FFT_SIZE / 2, sizeof(float));

  if (!sa->fft_buffer || !sa->window || !sa->magnitudes || !sa->smoothed ||
      !sa->peaks) {
    spectrum_analyzer_free(sa);
    return INTUITIVES_ERROR_OUT_OF_MEMORY;
  }

  // Hann window
  for (size_t i = 0; i < SPECTRUM_FFT_SIZE; i++) {
    sa->window[i] =
        0.5f * (1.0f - cosf(INTUITIVES_TWO_PI * i / (SPECTRUM_FFT_SIZE - 1)));
  }

  return INTUITIVES_OK;
}

void spectrum_analyzer_free(SpectrumAnalyzer *sa) {
  if (!sa)
    return;
  free(sa->fft_buffer);
  free(sa->window);
  free(sa->magnitudes);
  free(sa->smoothed);
  free(sa->peaks);
}

// Simple DFT (not FFT) for demonstration - use FFTW or similar in production
static void compute_dft(const float *input, float *output, size_t n) {
  for (size_t k = 0; k < n / 2; k++) {
    float real = 0, imag = 0;
    for (size_t t = 0; t < n; t++) {
      float angle = INTUITIVES_TWO_PI * k * t / n;
      real += input[t] * cosf(angle);
      imag -= input[t] * sinf(angle);
    }
    output[k] = sqrtf(real * real + imag * imag) / n;
  }
}

void spectrum_analyzer_write(SpectrumAnalyzer *sa, const Sample *mono,
                             size_t frames) {
  // Fill buffer with windowed samples
  for (size_t i = 0; i < frames && i < SPECTRUM_FFT_SIZE; i++) {
    size_t idx = (sa->write_pos + i) % SPECTRUM_FFT_SIZE;
    sa->fft_buffer[idx] = mono[i] * sa->window[idx];
  }
  sa->write_pos = (sa->write_pos + frames) % SPECTRUM_FFT_SIZE;

  // Compute DFT
  compute_dft(sa->fft_buffer, sa->magnitudes, SPECTRUM_FFT_SIZE);

  // Smooth and update peaks
  for (size_t i = 0; i < SPECTRUM_FFT_SIZE / 2; i++) {
    sa->smoothed[i] = sa->smoothing * sa->smoothed[i] +
                      (1.0f - sa->smoothing) * sa->magnitudes[i];

    if (sa->magnitudes[i] > sa->peaks[i]) {
      sa->peaks[i] = sa->magnitudes[i];
    } else {
      sa->peaks[i] *= sa->peak_decay;
    }
  }
}

void spectrum_analyzer_get_bands(SpectrumAnalyzer *sa, float *bands,
                                 size_t num_bands) {
  size_t bins_per_band = (SPECTRUM_FFT_SIZE / 2) / num_bands;

  if (sa->logarithmic) {
    // Logarithmic frequency distribution
    float log_max = logf(SPECTRUM_FFT_SIZE / 2.0f);

    for (size_t b = 0; b < num_bands; b++) {
      float start_log = b * log_max / num_bands;
      float end_log = (b + 1) * log_max / num_bands;
      size_t start_bin = (size_t)expf(start_log);
      size_t end_bin = (size_t)expf(end_log);

      if (start_bin >= SPECTRUM_FFT_SIZE / 2)
        start_bin = SPECTRUM_FFT_SIZE / 2 - 1;
      if (end_bin >= SPECTRUM_FFT_SIZE / 2)
        end_bin = SPECTRUM_FFT_SIZE / 2;
      if (end_bin <= start_bin)
        end_bin = start_bin + 1;

      float sum = 0;
      for (size_t i = start_bin; i < end_bin; i++) {
        sum += sa->smoothed[i];
      }
      bands[b] = sum / (end_bin - start_bin);
    }
  } else {
    // Linear frequency distribution
    for (size_t b = 0; b < num_bands; b++) {
      float sum = 0;
      for (size_t i = 0; i < bins_per_band; i++) {
        sum += sa->smoothed[b * bins_per_band + i];
      }
      bands[b] = sum / bins_per_band;
    }
  }
}

void spectrum_analyzer_get_peaks(SpectrumAnalyzer *sa, float *peaks,
                                 size_t num_bands) {
  size_t bins_per_band = (SPECTRUM_FFT_SIZE / 2) / num_bands;

  for (size_t b = 0; b < num_bands; b++) {
    float max = 0;
    for (size_t i = 0; i < bins_per_band; i++) {
      size_t idx = b * bins_per_band + i;
      if (idx < SPECTRUM_FFT_SIZE / 2 && sa->peaks[idx] > max) {
        max = sa->peaks[idx];
      }
    }
    peaks[b] = max;
  }
}

// ============================================================================
// PHASE CORRELATOR
// ============================================================================

void phase_init(PhaseCorrelator *pc) {
  memset(pc, 0, sizeof(PhaseCorrelator));
  pc->smoothing = 0.95f;
}

void phase_reset(PhaseCorrelator *pc) {
  pc->sum_lr = 0;
  pc->sum_ll = 0;
  pc->sum_rr = 0;
  pc->sample_count = 0;
}

void phase_analyze(PhaseCorrelator *pc, const Sample *l, const Sample *r,
                   size_t frames) {
  for (size_t i = 0; i < frames; i++) {
    pc->sum_lr += l[i] * r[i];
    pc->sum_ll += l[i] * l[i];
    pc->sum_rr += r[i] * r[i];
    pc->sample_count++;
  }

  // Calculate correlation
  float denom = sqrtf(pc->sum_ll * pc->sum_rr);
  float new_corr = denom > 0 ? pc->sum_lr / denom : 0;

  // Smooth
  pc->correlation =
      pc->smoothing * pc->correlation + (1.0f - pc->smoothing) * new_corr;

  // Calculate balance
  float energy_l = pc->sum_ll / pc->sample_count;
  float energy_r = pc->sum_rr / pc->sample_count;
  float total = energy_l + energy_r;
  if (total > 0) {
    pc->balance = (energy_r - energy_l) / total;
  }

  // Calculate width (correlation-based)
  pc->width = 1.0f - fabsf(pc->correlation);

  // Reset accumulators periodically
  if (pc->sample_count > 4096) {
    phase_reset(pc);
  }
}

float phase_get_correlation(PhaseCorrelator *pc) { return pc->correlation; }

void phase_get_goniometer(PhaseCorrelator *pc, float *x, float *y,
                          size_t points) {
  // Generate Lissajous-like points
  // In practice, you'd use the actual audio buffer here
  for (size_t i = 0; i < points; i++) {
    float t = (float)i / points * INTUITIVES_TWO_PI;
    x[i] = cosf(t) * (0.5f + 0.5f * pc->correlation);
    y[i] = sinf(t) * (0.5f + 0.5f * pc->width);
  }
}

// ============================================================================
// LEVEL METERS
// ============================================================================

void meter_init(LevelMeter *m, uint32_t sr) {
  memset(m, 0, sizeof(LevelMeter));
  m->sample_rate = sr;
  m->peak_decay = 0.9995f;
  m->hold_time = 2.0f;
}

void meter_analyze(LevelMeter *m, const Sample *l, const Sample *r,
                   size_t frames) {
  float sum_l = 0, sum_r = 0;
  float peak_l = 0, peak_r = 0;

  for (size_t i = 0; i < frames; i++) {
    float abs_l = fabsf(l[i]);
    float abs_r = fabsf(r[i]);

    sum_l += l[i] * l[i];
    sum_r += r[i] * r[i];

    if (abs_l > peak_l)
      peak_l = abs_l;
    if (abs_r > peak_r)
      peak_r = abs_r;

    // Clip detection
    if (abs_l >= 1.0f)
      m->clip_l = true;
    if (abs_r >= 1.0f)
      m->clip_r = true;
  }

  // Update RMS
  m->rms_l = sqrtf(sum_l / frames);
  m->rms_r = sqrtf(sum_r / frames);

  // Update peaks with decay
  if (peak_l > m->peak_l) {
    m->peak_l = peak_l;
  } else {
    m->peak_l *= m->peak_decay;
  }

  if (peak_r > m->peak_r) {
    m->peak_r = peak_r;
  } else {
    m->peak_r *= m->peak_decay;
  }

  // Peak hold
  if (peak_l > m->peak_hold_l) {
    m->peak_hold_l = peak_l;
    m->hold_counter_l = m->hold_time * m->sample_rate;
  } else if (m->hold_counter_l > 0) {
    m->hold_counter_l -= frames;
  } else {
    m->peak_hold_l *= m->peak_decay;
  }

  if (peak_r > m->peak_hold_r) {
    m->peak_hold_r = peak_r;
    m->hold_counter_r = m->hold_time * m->sample_rate;
  } else if (m->hold_counter_r > 0) {
    m->hold_counter_r -= frames;
  } else {
    m->peak_hold_r *= m->peak_decay;
  }

  // History
  m->history_l[m->history_pos] = m->peak_l;
  m->history_r[m->history_pos] = m->peak_r;
  m->history_pos = (m->history_pos + 1) % METER_HISTORY_SIZE;
}

void meter_get_levels_db(LevelMeter *m, float *peak_l, float *peak_r,
                         float *rms_l, float *rms_r) {
  *peak_l = INTUITIVES_LINEAR_TO_DB(m->peak_l);
  *peak_r = INTUITIVES_LINEAR_TO_DB(m->peak_r);
  *rms_l = INTUITIVES_LINEAR_TO_DB(m->rms_l);
  *rms_r = INTUITIVES_LINEAR_TO_DB(m->rms_r);
}

void meter_reset_clip(LevelMeter *m) {
  m->clip_l = false;
  m->clip_r = false;
}

// ============================================================================
// FLUID SIMULATION AUDIO BRIDGE
// ============================================================================

void fluid_params_from_audio(FluidAudioParams *fp, const Sample *mono,
                             size_t frames, uint32_t sr) {
  float sum = 0;
  float peak = 0;
  static float prev_energy = 0;

  for (size_t i = 0; i < frames; i++) {
    float abs_val = fabsf(mono[i]);
    sum += abs_val * abs_val;
    if (abs_val > peak)
      peak = abs_val;
  }

  float energy = sqrtf(sum / frames);

  // Amplitude for velocity field
  fp->amplitude = energy;

  // Spectral flux for particle emission
  float flux = fabsf(energy - prev_energy);
  fp->spectral_flux = flux;
  prev_energy = energy;

  // Onset detection (simple threshold)
  fp->onset_detected = flux > 0.1f ? 1.0f : 0.0f;

  // Naive frequency centroid estimation
  // In practice, use FFT-based spectral centroid
  fp->frequency_centroid = 1000.0f + energy * 3000.0f;

  // Tempo estimation would require beat tracking - placeholder
  fp->tempo_estimate = 120.0f;
}

// ============================================================================
// CHROMASYNESTHESIA (Pitch to color)
// ============================================================================

// Spectral hue mapping: C = Red, E = Yellow, G = Cyan, etc.
static const float NOTE_HUES[12] = {
    0.0f,   // C - Red
    30.0f,  // C# - Orange-red
    60.0f,  // D - Orange
    90.0f,  // D# - Yellow-orange
    120.0f, // E - Yellow
    150.0f, // F - Yellow-green
    180.0f, // F# - Green
    210.0f, // G - Cyan-green
    240.0f, // G# - Cyan
    270.0f, // A - Blue
    300.0f, // A# - Violet
    330.0f  // B - Magenta
};

static void hsb_to_rgb(float h, float s, float b, uint8_t *r, uint8_t *g,
                       uint8_t *bl) {
  h = fmodf(h, 360.0f);
  if (h < 0)
    h += 360.0f;

  float c = b * s;
  float x = c * (1.0f - fabsf(fmodf(h / 60.0f, 2.0f) - 1.0f));
  float m = b - c;

  float rf, gf, bf;

  if (h < 60) {
    rf = c;
    gf = x;
    bf = 0;
  } else if (h < 120) {
    rf = x;
    gf = c;
    bf = 0;
  } else if (h < 180) {
    rf = 0;
    gf = c;
    bf = x;
  } else if (h < 240) {
    rf = 0;
    gf = x;
    bf = c;
  } else if (h < 300) {
    rf = x;
    gf = 0;
    bf = c;
  } else {
    rf = c;
    gf = 0;
    bf = x;
  }

  *r = (uint8_t)((rf + m) * 255);
  *g = (uint8_t)((gf + m) * 255);
  *bl = (uint8_t)((bf + m) * 255);
}

void chroma_note_to_color(int32_t midi_note, SynesthesiaColor *color) {
  int32_t pitch_class = midi_note % 12;
  int32_t octave = midi_note / 12;

  float hue = NOTE_HUES[pitch_class];
  float saturation = 0.8f;

  // Higher octaves -> brighter
  float brightness = 0.3f + (octave / 10.0f) * 0.7f;
  brightness = INTUITIVES_CLAMP(brightness, 0.0f, 1.0f);

  hsb_to_rgb(hue, saturation, brightness, &color->r, &color->g, &color->b);
  color->brightness = brightness;
}

void chroma_frequency_to_color(float freq, SynesthesiaColor *color) {
  // Convert frequency to MIDI note
  float midi_float = INTUITIVES_FREQ_TO_MIDI(freq);
  int32_t midi_note = (int32_t)roundf(midi_float);

  chroma_note_to_color(midi_note, color);

  // Adjust brightness by amplitude (if needed)
}

void chroma_spectrum_to_colors(const float *magnitudes, size_t bins,
                               SynesthesiaColor *colors, uint32_t sr) {
  // Map frequency bins to chromatic colors
  float bin_freq = (float)sr / (bins * 2);

  for (size_t i = 0; i < bins; i++) {
    float freq = i * bin_freq;

    if (freq < 20.0f) {
      // Sub-audio: dark gray
      colors[i].r = colors[i].g = colors[i].b = 30;
      colors[i].brightness = magnitudes[i];
    } else if (freq > 20000.0f) {
      // Ultrasonic: white
      colors[i].r = colors[i].g = colors[i].b = 255;
      colors[i].brightness = magnitudes[i];
    } else {
      chroma_frequency_to_color(freq, &colors[i]);
      // Modulate brightness by magnitude
      colors[i].brightness = magnitudes[i];

      uint8_t r = colors[i].r, g = colors[i].g, b = colors[i].b;
      float mag = INTUITIVES_CLAMP(magnitudes[i] * 10.0f, 0.0f, 1.0f);
      colors[i].r = (uint8_t)(r * mag);
      colors[i].g = (uint8_t)(g * mag);
      colors[i].b = (uint8_t)(b * mag);
    }
  }
}
