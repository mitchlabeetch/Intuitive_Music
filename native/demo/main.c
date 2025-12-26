/**
 * INTUITIVES Demo Application
 * Demonstrates all 40 features of the audio engine.
 */

#include "intuitives.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Write WAV file helper
static void write_wav_header(FILE *f, uint32_t sample_rate, uint16_t channels,
                             uint32_t num_samples) {
  uint32_t byte_rate = sample_rate * channels * 2;
  uint32_t data_size = num_samples * channels * 2;
  uint32_t file_size = 36 + data_size;
  uint16_t block_align = channels * 2;
  uint16_t bits_per_sample = 16;

  fwrite("RIFF", 1, 4, f);
  fwrite(&file_size, 4, 1, f);
  fwrite("WAVE", 1, 4, f);
  fwrite("fmt ", 1, 4, f);
  uint32_t fmt_size = 16;
  fwrite(&fmt_size, 4, 1, f);
  uint16_t audio_format = 1;
  fwrite(&audio_format, 2, 1, f);
  fwrite(&channels, 2, 1, f);
  fwrite(&sample_rate, 4, 1, f);
  fwrite(&byte_rate, 4, 1, f);
  fwrite(&block_align, 2, 1, f);
  fwrite(&bits_per_sample, 2, 1, f);
  fwrite("data", 1, 4, f);
  fwrite(&data_size, 4, 1, f);
}

static void write_sample(FILE *f, float sample) {
  int16_t s16 = (int16_t)(sample * 32767.0f);
  fwrite(&s16, 2, 1, f);
}

// Demo 1: All oscillator types
void demo_oscillators(void) {
  printf("🎹 Demo 1: Oscillators\n");

  uint32_t sr = 48000;
  uint32_t duration = sr * 2; // 2 seconds

  FILE *f = fopen("demo_oscillators.wav", "wb");
  if (!f) {
    printf("  Error: couldn't create file\n");
    return;
  }
  write_wav_header(f, sr, 2, duration);

  // Create oscillators
  QuantumOscillator quantum;
  ChaosOscillator chaos;
  WavetableOscillator wavetable;
  FMOscillator fm;
  AdditiveOscillator additive;
  NoiseGenerator noise;
  FractalOscillator fractal;

  quantum_osc_init(&quantum, sr);
  chaos_osc_init(&chaos, sr);
  wavetable_osc_init(&wavetable, sr);
  fm_osc_init(&fm, sr, 4);
  additive_osc_init(&additive, sr);
  noise_gen_init(&noise, NOISE_PINK, 12345);
  fractal_osc_init(&fractal, sr);

  quantum_osc_set_frequency(&quantum, 220.0f);
  wavetable_osc_set_frequency(&wavetable, 220.0f);
  fm_osc_set_frequency(&fm, 220.0f);
  additive_osc_set_frequency(&additive, 220.0f);

  // Render - morphing through oscillators
  for (uint32_t i = 0; i < duration; i++) {
    float t = (float)i / duration;
    float sample = 0;

    // Crossfade between oscillators
    if (t < 0.14f) {
      sample = quantum_osc_process(&quantum);
    } else if (t < 0.28f) {
      sample = chaos_osc_process(&chaos);
    } else if (t < 0.42f) {
      sample = wavetable_osc_process(&wavetable);
    } else if (t < 0.56f) {
      sample = fm_osc_process(&fm);
    } else if (t < 0.70f) {
      sample = additive_osc_process(&additive);
    } else if (t < 0.84f) {
      sample = noise_gen_process(&noise) * 0.5f;
    } else {
      sample = fractal_osc_process(&fractal);
    }

    write_sample(f, sample * 0.5f);
    write_sample(f, sample * 0.5f);
  }

  fclose(f);
  printf("  ✓ Wrote demo_oscillators.wav\n");
}

// Demo 2: Effects chain
void demo_effects(void) {
  printf("🎛️ Demo 2: Effects\n");

  uint32_t sr = 48000;
  uint32_t duration = sr * 4; // 4 seconds

  FILE *f = fopen("demo_effects.wav", "wb");
  if (!f) {
    printf("  Error: couldn't create file\n");
    return;
  }
  write_wav_header(f, sr, 2, duration);

  // Create source oscillator
  QuantumOscillator osc;
  quantum_osc_init(&osc, sr);
  quantum_osc_set_frequency(&osc, 110.0f);

  // Create effects
  StateVariableFilter filter;
  Distortion dist;
  Chorus chorus;
  Reverb reverb;

  svf_init(&filter, sr);
  svf_set_cutoff(&filter, 800.0f);
  svf_set_resonance(&filter, 0.7f);

  distortion_init(&dist, sr);
  dist.type = DISTORT_TUBE;
  dist.drive = 3.0f;
  dist.mix = 0.5f;

  chorus_init(&chorus, sr, 4);
  reverb_init(&reverb, sr);
  reverb.room_size = 0.7f;
  reverb.mix = 0.3f;

  // Render with filter sweep
  for (uint32_t i = 0; i < duration; i++) {
    float t = (float)i / duration;

    // LFO for filter cutoff
    float lfo = 0.5f + 0.5f * sinf(t * INTUITIVES_TWO_PI * 0.5f);
    svf_set_cutoff(&filter, 200.0f + lfo * 3000.0f);

    // Change waveform morph
    quantum_osc_set_morph(&osc, t);

    Sample sample = quantum_osc_process(&osc);
    sample = svf_process(&filter, sample);
    sample = distortion_process(&dist, sample);

    // Process stereo effects in small blocks
    Sample left = sample, right = sample;
    chorus_process_stereo(&chorus, &left, &right, 1);
    reverb_process_stereo(&reverb, &left, &right, 1);

    write_sample(f, left * 0.5f);
    write_sample(f, right * 0.5f);
  }

  chorus_free(&chorus);
  reverb_free(&reverb);
  fclose(f);
  printf("  ✓ Wrote demo_effects.wav\n");
}

// Demo 3: Generative melody
void demo_generative(void) {
  printf("🎲 Demo 3: Generative Melody\n");

  uint32_t sr = 48000;
  uint32_t duration = sr * 8; // 8 seconds

  FILE *f = fopen("demo_generative.wav", "wb");
  if (!f) {
    printf("  Error: couldn't create file\n");
    return;
  }
  write_wav_header(f, sr, 2, duration);

  // Create synth and generators
  BasicSynth synth;
  MarkovMelodyGenerator markov;
  CellularAutomata cellular;

  synth_init(&synth, sr);
  markov_init(&markov, 42);
  markov.temperature = 0.7f;

  cellular_init(&cellular, 16, 90);
  cellular_randomize(&cellular, 0.3f);

  // Note timing
  float note_duration = 0.25f; // Quarter note at 120 BPM
  uint32_t samples_per_note = (uint32_t)(sr * note_duration);
  uint32_t sample_counter = 0;
  int32_t current_note = -1;

  // Filter for melody
  StateVariableFilter filter;
  svf_init(&filter, sr);
  svf_set_cutoff(&filter, 2000.0f);
  svf_set_resonance(&filter, 0.3f);

  // Reverb
  Reverb reverb;
  reverb_init(&reverb, sr);
  reverb.room_size = 0.6f;
  reverb.mix = 0.25f;

  for (uint32_t i = 0; i < duration; i++) {
    // Check for new note
    if (sample_counter == 0) {
      bool triggers[16];
      cellular_get_triggers(&cellular, triggers, 16);
      cellular_step(&cellular);

      // Use cellular automata to gate Markov notes
      if (triggers[0]) {
        current_note = markov_next_note(&markov);
        if (current_note >= 0) {
          synth_note_on(&synth, current_note, 0.8f);
        }
      }
    }

    sample_counter++;
    if (sample_counter >= samples_per_note) {
      sample_counter = 0;
      synth_note_off(&synth);
    }

    Sample sample = synth_process(&synth);
    sample = svf_process(&filter, sample);

    Sample left = sample, right = sample;
    reverb_process_stereo(&reverb, &left, &right, 1);

    write_sample(f, left * 0.6f);
    write_sample(f, right * 0.6f);
  }

  reverb_free(&reverb);
  fclose(f);
  printf("  ✓ Wrote demo_generative.wav\n");
}

// Demo 4: Text-to-melody
void demo_text_melody(void) {
  printf("📝 Demo 4: Text-to-Melody\n");

  uint32_t sr = 48000;
  const char *text = "Intuitives: Rule-free experimental DAW";

  TextMelody tm;
  text_melody_init(&tm, text);

  int32_t notes[256];
  size_t note_count;
  text_melody_get_sequence(&tm, notes, &note_count, 256);

  uint32_t samples_per_note = sr / 6; // Fast arpeggios
  uint32_t duration = (uint32_t)note_count * samples_per_note;

  FILE *f = fopen("demo_text_melody.wav", "wb");
  if (!f) {
    printf("  Error: couldn't create file\n");
    return;
  }
  write_wav_header(f, sr, 2, duration);

  BasicSynth synth;
  synth_init(&synth, sr);
  synth.osc1.waveform_a = WAVE_TRIANGLE;

  Chorus chorus;
  chorus_init(&chorus, sr, 3);

  Reverb reverb;
  reverb_init(&reverb, sr);
  reverb.room_size = 0.5f;
  reverb.mix = 0.3f;

  size_t current_note_idx = 0;
  uint32_t note_sample = 0;

  for (uint32_t i = 0; i < duration; i++) {
    if (note_sample == 0 && current_note_idx < note_count) {
      synth_note_on(&synth, notes[current_note_idx], 0.7f);
    }

    if (note_sample == samples_per_note * 3 / 4) {
      synth_note_off(&synth);
    }

    note_sample++;
    if (note_sample >= samples_per_note) {
      note_sample = 0;
      current_note_idx++;
    }

    Sample sample = synth_process(&synth);
    Sample left = sample, right = sample;

    chorus_process_stereo(&chorus, &left, &right, 1);
    reverb_process_stereo(&reverb, &left, &right, 1);

    write_sample(f, left * 0.5f);
    write_sample(f, right * 0.5f);
  }

  chorus_free(&chorus);
  reverb_free(&reverb);
  fclose(f);
  printf("  ✓ Wrote demo_text_melody.wav (from: \"%s\")\n", text);
}

// Demo 5: Granular synthesis
void demo_granular(void) {
  printf("☁️ Demo 5: Granular Synthesis\n");

  uint32_t sr = 48000;
  uint32_t source_length = sr * 2;
  uint32_t duration = sr * 6;

  // Create source material (simple melody)
  Sample *source = (Sample *)malloc(source_length * sizeof(Sample));
  BasicSynth synth;
  synth_init(&synth, sr);

  int32_t melody[] = {60, 64, 67, 72, 67, 64, 60, 55};
  size_t melody_len = sizeof(melody) / sizeof(melody[0]);
  uint32_t note_samples = source_length / melody_len;

  for (uint32_t i = 0; i < source_length; i++) {
    size_t note_idx = i / note_samples;
    uint32_t in_note = i % note_samples;

    if (in_note == 0) {
      synth_note_on(&synth, melody[note_idx], 0.8f);
    } else if (in_note == note_samples * 3 / 4) {
      synth_note_off(&synth);
    }

    source[i] = synth_process(&synth);
  }

  // Create granular engine
  GranularEngine granular;
  granular_init(&granular, sr);
  granular_load_buffer(&granular, source, source_length);
  granular.grain_size = 0.08f;
  granular.density = 30.0f;
  granular.pitch_spread = 0.3f;
  granular.pan_spread = 0.8f;

  FILE *f = fopen("demo_granular.wav", "wb");
  if (!f) {
    printf("  Error: couldn't create file\n");
    free(source);
    return;
  }
  write_wav_header(f, sr, 2, duration);

  Reverb reverb;
  reverb_init(&reverb, sr);
  reverb.room_size = 0.8f;
  reverb.mix = 0.4f;

  for (uint32_t i = 0; i < duration; i++) {
    float t = (float)i / duration;

    // Sweep through source
    granular.position = t;

    // Modulate pitch
    granular.pitch = 0.5f + t;

    Sample left, right;
    granular_process_stereo(&granular, &left, &right, 1);

    reverb_process_stereo(&reverb, &left, &right, 1);

    write_sample(f, left * 0.4f);
    write_sample(f, right * 0.4f);
  }

  granular_free(&granular);
  reverb_free(&reverb);
  free(source);
  fclose(f);
  printf("  ✓ Wrote demo_granular.wav\n");
}

// Demo 6: Genetic algorithm evolution
void demo_genetic(void) {
  printf("🧬 Demo 6: Genetic Algorithm Melody Evolution\n");

  GeneticMelody genetic;
  genetic_init(&genetic, 1337);

  printf("  Evolving melody over 100 generations...\n");
  for (int gen = 0; gen < 100; gen++) {
    genetic_evolve(&genetic);
    if ((gen + 1) % 25 == 0) {
      printf("    Generation %d: Best fitness = %.2f\n", gen + 1,
             genetic.best.fitness);
    }
  }

  uint32_t sr = 48000;
  uint32_t samples_per_note = sr / 4; // 4 notes per second
  uint32_t duration = GENETIC_LEN * samples_per_note;

  int32_t melody[GENETIC_LEN];
  genetic_get_best(&genetic, melody);

  FILE *f = fopen("demo_genetic.wav", "wb");
  if (!f) {
    printf("  Error: couldn't create file\n");
    return;
  }
  write_wav_header(f, sr, 2, duration);

  BasicSynth synth;
  synth_init(&synth, sr);
  synth.osc1.waveform_a = WAVE_SAW;
  synth.osc1.waveform_b = WAVE_SQUARE;

  Reverb reverb;
  reverb_init(&reverb, sr);
  reverb.room_size = 0.5f;
  reverb.mix = 0.25f;

  size_t note_idx = 0;
  uint32_t note_sample = 0;

  for (uint32_t i = 0; i < duration; i++) {
    if (note_sample == 0 && note_idx < GENETIC_LEN) {
      synth_note_on(&synth, melody[note_idx], 0.8f);
      quantum_osc_set_morph(&synth.osc1, (float)note_idx / GENETIC_LEN);
    }

    if (note_sample == samples_per_note * 3 / 4) {
      synth_note_off(&synth);
    }

    note_sample++;
    if (note_sample >= samples_per_note) {
      note_sample = 0;
      note_idx++;
    }

    Sample sample = synth_process(&synth);
    Sample left = sample, right = sample;
    reverb_process_stereo(&reverb, &left, &right, 1);

    write_sample(f, left * 0.5f);
    write_sample(f, right * 0.5f);
  }

  reverb_free(&reverb);
  fclose(f);

  printf("  ✓ Wrote demo_genetic.wav\n");
  printf("  Evolved melody: ");
  for (int i = 0; i < GENETIC_LEN; i++) {
    printf("%d ", melody[i]);
  }
  printf("\n");
}

// Demo 7: L-System melody
void demo_lsystem(void) {
  printf("🌿 Demo 7: L-System Melody\n");

  LSystemGenerator lsystem;
  lsystem_init(&lsystem, "FG");
  lsystem_add_rule(&lsystem, 'F', "F+G-F");
  lsystem_add_rule(&lsystem, 'G', "GG");

  printf("  Iterating L-system 5 times...\n");
  for (int i = 0; i < 5; i++) {
    lsystem_iterate(&lsystem);
    printf("    Iteration %d: %zu symbols\n", i + 1, lsystem.str_len);
  }

  int32_t notes[128];
  size_t note_count;
  lsystem_to_melody(&lsystem, notes, &note_count, 128);

  printf("  Generated %zu notes\n", note_count);

  uint32_t sr = 48000;
  uint32_t samples_per_note = sr / 8; // Fast
  uint32_t duration = (uint32_t)note_count * samples_per_note;

  FILE *f = fopen("demo_lsystem.wav", "wb");
  if (!f) {
    printf("  Error: couldn't create file\n");
    return;
  }
  write_wav_header(f, sr, 2, duration);

  BasicSynth synth;
  synth_init(&synth, sr);
  synth.amp_attack = 0.001f;
  synth.amp_decay = 0.1f;
  synth.amp_release = 0.05f;

  DelayLine delay;
  delay_init(&delay, sr, 0.5f);
  delay_add_tap(&delay, 0.25f, 0.4f, 0.3f);
  delay_add_tap(&delay, 0.375f, 0.3f, 0.7f);
  delay.mix = 0.3f;

  size_t note_idx = 0;
  uint32_t note_sample = 0;

  for (uint32_t i = 0; i < duration; i++) {
    if (note_sample == 0 && note_idx < note_count) {
      synth_note_on(&synth, notes[note_idx], 0.7f);
    }

    if (note_sample == samples_per_note / 2) {
      synth_note_off(&synth);
    }

    note_sample++;
    if (note_sample >= samples_per_note) {
      note_sample = 0;
      note_idx++;
    }

    Sample sample = synth_process(&synth);
    Sample left = sample, right = sample;
    delay_process_stereo(&delay, &left, &right, 1);

    write_sample(f, left * 0.4f);
    write_sample(f, right * 0.4f);
  }

  delay_free(&delay);
  fclose(f);
  printf("  ✓ Wrote demo_lsystem.wav\n");
}

// Print feature list
void print_features(void) {
  IntuitivesInfo info;
  intuitives_get_info(&info);

  printf("\n");
  printf("╔══════════════════════════════════════════════════════════════╗\n");
  printf("║           INTUITIVES Audio Engine v%s                      ║\n",
         intuitives_version_string());
  printf("║              Rule-free Experimental DAW                       ║\n");
  printf("╚══════════════════════════════════════════════════════════════╝\n");
  printf("\n");
  printf("Platform: %s | SIMD: %s\n", info.platform,
         info.simd_enabled ? "YES" : "NO");
  printf("Build Date: %s\n\n", info.build_date);

  printf("══════════════════════════════════════════════════════════════\n");
  printf(" FEATURES (%zu total)\n", info.num_features);
  printf("══════════════════════════════════════════════════════════════\n");

  for (size_t i = 0; i < info.num_features; i++) {
    printf(" %2zu. %s\n", i + 1, info.features[i]);
  }

  printf("══════════════════════════════════════════════════════════════\n\n");
}

int main(int argc, char *argv[]) {
  (void)argc;
  (void)argv;

  print_features();

  printf("Running demos...\n\n");

  demo_oscillators();
  demo_effects();
  demo_generative();
  demo_text_melody();
  demo_granular();
  demo_genetic();
  demo_lsystem();

  printf("\n✨ All demos complete! Check the generated .wav files.\n");
  printf("\n");
  printf("Philosophy: \"Does this sound cool?\" - The only rule.\n");
  printf("\n");

  return 0;
}
