#!/usr/bin/env python3
"""
INTUITIVES DAW - Demo Script

Demonstrates all integrated tools and generation capabilities.
Run this to see what Intuitives can do!

"Does this sound cool?" - The only rule.
"""

import numpy as np
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intlib.brand import LOGO_ASCII, APP_NAME, VERSION_STRING
from intlib.integrations import (
    AudioAnalyzer,
    AIGenerator,
    PatternBuilder,
    VisualAnalyzer,
    LIBROSA_AVAILABLE,
)
from intlib.ai_models import (
    MelodyRNN,
    TextToMusic,
    get_available_models,
)


def print_header():
    """Print welcome header"""
    print("\n" + "=" * 60)
    print(f"  {APP_NAME} DAW v{VERSION_STRING} - Demo")
    print("=" * 60)
    print('  "Does this sound cool?" - The only rule.')
    print("=" * 60 + "\n")


def demo_analysis():
    """Demo audio analysis features"""
    print("\n📊 AUDIO ANALYSIS DEMO")
    print("-" * 40)
    
    # Create test audio (440Hz sine wave)
    sr = 44100
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration))
    audio = np.sin(2 * np.pi * 440 * t) * 0.5
    
    analyzer = AudioAnalyzer(sample_rate=sr)
    
    # Basic features
    features = analyzer.analyze(audio)
    print(f"  RMS Level: {features['rms']:.3f}")
    print(f"  Peak: {features['peak']:.3f}")
    print(f"  Spectral Centroid: {features['spectral_centroid']:.0f} Hz")
    print(f"  Spectral Flatness: {features['spectral_flatness']:.3f}")
    
    # Pitch detection
    freq, conf = analyzer.detect_pitch(audio)
    print(f"  Detected Pitch: {freq:.1f} Hz (confidence: {conf:.2f})")
    
    # Tempo
    bpm = analyzer.detect_bpm(audio)
    print(f"  Estimated BPM: {bpm:.1f}")
    
    print("  ✅ Analysis complete")


def demo_markov_generation():
    """Demo Markov melody generation"""
    print("\n🎲 MARKOV MELODY GENERATION")
    print("-" * 40)
    
    gen = AIGenerator()
    
    # Generate with different temperatures
    for temp in [0.3, 0.7, 1.0]:
        melody = gen.generate_melody(
            num_bars=2,
            notes_per_bar=4,
            scale='pentatonic',
            temperature=temp,
            style='markov'
        )
        notes = [n['note'] for n in melody]
        print(f"  Temperature {temp}: {notes}")
    
    print("  ✅ Markov generation complete")


def demo_genetic_generation():
    """Demo genetic algorithm melody"""
    print("\n🧬 GENETIC ALGORITHM EVOLUTION")
    print("-" * 40)
    
    gen = AIGenerator()
    
    melody = gen.generate_melody(
        num_bars=4,
        notes_per_bar=4,
        scale='minor',
        temperature=0.8,
        style='genetic'
    )
    
    print(f"  Evolved {len(melody)} notes over 50 generations")
    notes = [n['note'] for n in melody[:8]]
    print(f"  First 8 notes: {notes}")
    
    print("  ✅ Genetic evolution complete")


def demo_cellular_generation():
    """Demo cellular automata rhythms"""
    print("\n🔲 CELLULAR AUTOMATA RHYTHMS")
    print("-" * 40)
    
    gen = AIGenerator()
    
    drums = gen.generate_drum_pattern(
        num_bars=2,
        steps_per_bar=16,
        style='cellular',
        density=0.4
    )
    
    # Print patterns
    for name, pattern in drums.items():
        visual = ''.join('█' if x else '·' for x in pattern[:16])
        print(f"  {name:6s}: {visual}")
    
    print("  ✅ Cellular generation complete")


def demo_text_to_melody():
    """Demo text-to-melody conversion"""
    print("\n📝 TEXT TO MELODY")
    print("-" * 40)
    
    gen = AIGenerator()
    
    texts = ["Hello", "MUSIC!", "Intuitives"]
    
    for text in texts:
        melody = gen.text_to_melody(text)
        notes = [n['note'] for n in melody]
        print(f"  '{text}' → {notes}")
    
    print("  ✅ Text conversion complete")


def demo_color_to_harmony():
    """Demo color-to-harmony conversion"""
    print("\n🎨 COLOR TO HARMONY")
    print("-" * 40)
    
    gen = AIGenerator()
    
    colors = [
        (255, 0, 0, "Red (C major)"),
        (0, 255, 0, "Green (E major)"),
        (0, 0, 255, "Blue (A major)"),
        (128, 0, 128, "Purple (minor)"),
    ]
    
    for r, g, b, name in colors:
        chord = gen.color_to_harmony(r, g, b)
        print(f"  {name}: MIDI notes {chord}")
    
    print("  ✅ Color conversion complete")


def demo_pattern_builder():
    """Demo pattern string parsing"""
    print("\n🥁 PATTERN BUILDER")
    print("-" * 40)
    
    builder = PatternBuilder(bpm=120)
    
    # Pattern strings
    patterns = [
        ("x-x- x-x-", "Basic 4/4"),
        ("x--x --x-", "Syncopated"),
        ("X-x-X-x-", "Accented"),
        ("[xx]-x-", "Ghost notes"),
    ]
    
    for pattern_str, name in patterns:
        events = builder.from_string(pattern_str)
        hits = len([e for e in events])
        print(f"  {name}: '{pattern_str}' → {hits} hits")
    
    # Euclidean rhythm
    euclidean = builder.euclidean(5, 8)
    visual = ''.join('█' if x else '·' for x in euclidean)
    print(f"  Euclidean(5,8): {visual}")
    
    # Chord progression
    chords = builder.chord_pattern("Cmaj7 Am Dm7 G7")
    print(f"  Chord progression: {len(chords)} notes in 4 chords")
    
    print("  ✅ Pattern building complete")


def demo_visualization():
    """Demo visualization features"""
    print("\n👁️ VISUALIZATION")
    print("-" * 40)
    
    viz = VisualAnalyzer(sample_rate=44100)
    
    # Test audio
    sr = 44100
    t = np.linspace(0, 0.5, sr // 2)
    
    # C major chord
    audio = (
        np.sin(2 * np.pi * 261.63 * t) +   # C4
        np.sin(2 * np.pi * 329.63 * t) +   # E4
        np.sin(2 * np.pi * 392.00 * t)     # G4
    ) * 0.3
    
    # Waveform
    waveform = viz.get_waveform(audio, num_points=20)
    wf_visual = ''.join('█' if w > 0.1 else '▄' if w > 0.05 else '·' 
                        for w in waveform)
    print(f"  Waveform: {wf_visual}")
    
    # Spectrum
    spectrum = viz.get_spectrum(audio, num_bands=16)
    sp_visual = ''.join('█' if s > 0.5 else '▄' if s > 0.2 else '·' 
                        for s in spectrum)
    print(f"  Spectrum: {sp_visual}")
    
    # Chromasynesthesia
    freq, chroma_idx = viz.get_dominant_pitch(audio)
    color = viz.get_chroma_color(chroma_idx)
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                  'F#', 'G', 'G#', 'A', 'A#', 'B']
    print(f"  Dominant note: {note_names[chroma_idx]} ({freq:.1f}Hz)")
    print(f"  Chroma color: RGB{color}")
    
    print("  ✅ Visualization complete")


def demo_ai_models():
    """Demo AI model availability"""
    print("\n🤖 AI MODEL STATUS")
    print("-" * 40)
    
    models = get_available_models()
    
    for name, available in models.items():
        status = "✅ Available" if available else "❌ Not installed"
        print(f"  {name:15s}: {status}")
    
    # Quick MelodyRNN test
    rnn = MelodyRNN()
    seed = [60, 62, 64]  # C D E
    continuation = rnn.continue_melody(seed, num_steps=8)
    notes = [n['note'] for n in continuation]
    print(f"\n  MelodyRNN continuation from [60,62,64]: {notes}")
    
    print("  ✅ AI models checked")


def demo_quick_functions():
    """Demo one-liner convenience functions"""
    print("\n⚡ QUICK FUNCTIONS")
    print("-" * 40)
    
    from intlib.integrations import quick_generate, quick_pattern
    
    # Quick melody
    melody = quick_generate(style='random', bars=2)
    print(f"  quick_generate: {len(melody)} notes")
    
    # Quick pattern
    events = quick_pattern("x-x-x-xx")
    print(f"  quick_pattern: {len(events)} events")
    
    print("  ✅ Quick functions complete")


def main():
    """Run all demos"""
    print_header()
    
    print("Running all Intuitives DAW demos...\n")
    
    try:
        demo_analysis()
        demo_markov_generation()
        demo_genetic_generation()
        demo_cellular_generation()
        demo_text_to_melody()
        demo_color_to_harmony()
        demo_pattern_builder()
        demo_visualization()
        demo_ai_models()
        demo_quick_functions()
        
        print("\n" + "=" * 60)
        print("  🎉 ALL DEMOS COMPLETE!")
        print("=" * 60)
        print("\nIntuitives DAW is ready to create music.")
        print("Remember: 'Does this sound cool?' is the only rule.\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
