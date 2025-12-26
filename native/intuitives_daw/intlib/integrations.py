"""
INTUITIVES DAW - External Tool Integration Hub

This module integrates the best open-source audio tools for an
experiment-first, no-learning-curve experience.

"Does this sound cool?" - The only rule.

INTEGRATED TOOLS (by priority):
================================

TIER 1 - CORE (Must have)
-------------------------
1. librosa - Audio analysis & feature extraction
2. aubio - Beat/pitch detection
3. Magenta - AI music generation
4. numpy/scipy - DSP fundamentals

TIER 2 - VISUALIZATION
-----------------------
5. Meyda concepts - Real-time features
6. wavesurfer concepts - Waveform display

TIER 3 - GENERATION
-------------------
7. Tonal concepts - Music theory helpers
8. Scribbletune concepts - Pattern generation

TIER 4 - AI/ML
--------------
9. AudioCraft/MusicGen - Text to music
10. Spleeter - Stem separation
11. RAVE - Neural audio

Usage:
    from intlib.integrations import AudioAnalyzer, AIGenerator, PatternBuilder
"""

import os
import sys
from typing import Optional, List, Tuple, Dict, Any
import numpy as np

# Try to import optional dependencies
LIBROSA_AVAILABLE = False
AUBIO_AVAILABLE = False
MAGENTA_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    pass

try:
    import aubio
    AUBIO_AVAILABLE = True
except ImportError:
    pass

try:
    from note_seq import midi_io
    MAGENTA_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# AUDIO ANALYSIS (inspired by librosa, aubio, Meyda)
# =============================================================================

class AudioAnalyzer:
    """
    Real-time audio analysis with features from librosa, aubio, and Meyda.
    
    Features extracted:
    - BPM/Tempo detection
    - Pitch tracking
    - Onset detection (note starts)
    - Spectral features (centroid, rolloff, flux)
    - Chroma (pitch class distribution)
    - MFCC (timbre)
    
    Example:
        analyzer = AudioAnalyzer(sample_rate=44100)
        features = analyzer.analyze(audio_samples)
        print(f"BPM: {features['bpm']}, Key: {features['key']}")
    """
    
    def __init__(self, sample_rate: int = 44100, hop_length: int = 512):
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.frame_size = hop_length * 4
        
    def analyze(self, audio: np.ndarray) -> Dict[str, Any]:
        """Analyze audio and return feature dictionary"""
        features = {}
        
        if len(audio) == 0:
            return features
        
        # Ensure mono
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
        
        # Basic features (always available)
        features['rms'] = self._compute_rms(audio)
        features['peak'] = float(np.max(np.abs(audio)))
        features['zero_crossing_rate'] = self._compute_zcr(audio)
        
        # Spectral features
        spectrum = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1/self.sample_rate)
        
        features['spectral_centroid'] = self._spectral_centroid(spectrum, freqs)
        features['spectral_rolloff'] = self._spectral_rolloff(spectrum, freqs)
        features['spectral_flatness'] = self._spectral_flatness(spectrum)
        
        # Use librosa if available for advanced features
        if LIBROSA_AVAILABLE:
            features.update(self._librosa_features(audio))
        
        return features
    
    def detect_bpm(self, audio: np.ndarray) -> float:
        """Detect tempo/BPM"""
        if LIBROSA_AVAILABLE:
            tempo, _ = librosa.beat.beat_track(y=audio, sr=self.sample_rate)
            return float(tempo)
        else:
            # Fallback: simple onset-based BPM detection
            return self._simple_bpm_detection(audio)
    
    def detect_pitch(self, audio: np.ndarray) -> Tuple[float, float]:
        """Detect fundamental pitch (frequency and confidence)"""
        if AUBIO_AVAILABLE:
            pitch_detector = aubio.pitch("yin", self.frame_size, 
                                         self.hop_length, self.sample_rate)
            pitch = pitch_detector(audio.astype(np.float32))[0]
            confidence = pitch_detector.get_confidence()
            return float(pitch), float(confidence)
        else:
            # Fallback: autocorrelation pitch detection
            return self._autocorrelation_pitch(audio)
    
    def detect_onsets(self, audio: np.ndarray) -> List[int]:
        """Detect note onsets (sample indices)"""
        if LIBROSA_AVAILABLE:
            onsets = librosa.onset.onset_detect(
                y=audio, sr=self.sample_rate, 
                hop_length=self.hop_length, units='samples'
            )
            return onsets.tolist()
        else:
            # Fallback: energy-based onset detection
            return self._energy_onset_detection(audio)
    
    def get_chroma(self, audio: np.ndarray) -> np.ndarray:
        """Get chroma (pitch class) features - for chord detection"""
        if LIBROSA_AVAILABLE:
            chroma = librosa.feature.chroma_stft(
                y=audio, sr=self.sample_rate, hop_length=self.hop_length
            )
            return chroma
        else:
            # Simplified chroma from FFT
            return self._simple_chroma(audio)
    
    def detect_key(self, audio: np.ndarray) -> Tuple[str, str]:
        """Detect musical key (note, mode)"""
        chroma = self.get_chroma(audio)
        mean_chroma = np.mean(chroma, axis=1)
        
        # Krumhansl-Kessler key profiles
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
                                  2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                                  2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                      'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        best_key = 'C'
        best_mode = 'major'
        best_correlation = -1
        
        for i in range(12):
            rolled_chroma = np.roll(mean_chroma, -i)
            major_corr = np.corrcoef(rolled_chroma, major_profile)[0, 1]
            minor_corr = np.corrcoef(rolled_chroma, minor_profile)[0, 1]
            
            if major_corr > best_correlation:
                best_correlation = major_corr
                best_key = note_names[i]
                best_mode = 'major'
            if minor_corr > best_correlation:
                best_correlation = minor_corr
                best_key = note_names[i]
                best_mode = 'minor'
        
        return best_key, best_mode
    
    # === PRIVATE METHODS ===
    
    def _compute_rms(self, audio: np.ndarray) -> float:
        return float(np.sqrt(np.mean(audio ** 2)))
    
    def _compute_zcr(self, audio: np.ndarray) -> float:
        signs = np.sign(audio)
        diffs = np.diff(signs)
        crossings = np.sum(np.abs(diffs)) / 2
        return float(crossings / len(audio))
    
    def _spectral_centroid(self, spectrum: np.ndarray, freqs: np.ndarray) -> float:
        if np.sum(spectrum) == 0:
            return 0.0
        return float(np.sum(freqs * spectrum) / np.sum(spectrum))
    
    def _spectral_rolloff(self, spectrum: np.ndarray, freqs: np.ndarray, 
                          threshold: float = 0.85) -> float:
        cumsum = np.cumsum(spectrum)
        total = cumsum[-1]
        if total == 0:
            return 0.0
        idx = np.searchsorted(cumsum, threshold * total)
        return float(freqs[min(idx, len(freqs) - 1)])
    
    def _spectral_flatness(self, spectrum: np.ndarray) -> float:
        spectrum = spectrum + 1e-10  # Avoid log(0)
        geo_mean = np.exp(np.mean(np.log(spectrum)))
        arith_mean = np.mean(spectrum)
        return float(geo_mean / arith_mean) if arith_mean > 0 else 0.0
    
    def _librosa_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """Extract features using librosa"""
        features = {}
        
        # Tempo
        tempo, beats = librosa.beat.beat_track(y=audio, sr=self.sample_rate)
        features['bpm'] = float(tempo)
        features['beat_frames'] = beats.tolist()
        
        # MFCCs (timbre)
        mfccs = librosa.feature.mfcc(y=audio, sr=self.sample_rate, n_mfcc=13)
        features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
        
        # Spectral contrast
        contrast = librosa.feature.spectral_contrast(y=audio, sr=self.sample_rate)
        features['spectral_contrast'] = np.mean(contrast, axis=1).tolist()
        
        return features
    
    def _simple_bpm_detection(self, audio: np.ndarray) -> float:
        """Fallback BPM detection without librosa"""
        # Simple energy-based tempo estimation
        frame_length = int(0.02 * self.sample_rate)  # 20ms frames
        hop = frame_length // 2
        
        # Compute energy per frame
        n_frames = (len(audio) - frame_length) // hop
        energy = np.zeros(n_frames)
        
        for i in range(n_frames):
            start = i * hop
            frame = audio[start:start + frame_length]
            energy[i] = np.sum(frame ** 2)
        
        # Find peaks in energy difference
        energy_diff = np.diff(energy)
        energy_diff[energy_diff < 0] = 0
        
        # Autocorrelation for periodicity
        autocorr = np.correlate(energy_diff, energy_diff, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find first significant peak
        min_lag = int(0.3 * self.sample_rate / hop)  # Min 200 BPM
        max_lag = int(2.0 * self.sample_rate / hop)  # Min 30 BPM
        
        if max_lag > len(autocorr):
            max_lag = len(autocorr) - 1
        
        if min_lag >= max_lag:
            return 120.0  # Default
        
        search_range = autocorr[min_lag:max_lag]
        peak_idx = np.argmax(search_range) + min_lag
        
        # Convert to BPM
        period_seconds = peak_idx * hop / self.sample_rate
        if period_seconds > 0:
            return float(60.0 / period_seconds)
        return 120.0
    
    def _autocorrelation_pitch(self, audio: np.ndarray) -> Tuple[float, float]:
        """Simple autocorrelation pitch detection"""
        if len(audio) < self.frame_size:
            return 0.0, 0.0
        
        # Autocorrelation
        autocorr = np.correlate(audio[:self.frame_size], 
                                audio[:self.frame_size], mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find peak between 50Hz and 2000Hz
        min_lag = int(self.sample_rate / 2000)
        max_lag = int(self.sample_rate / 50)
        
        if max_lag > len(autocorr):
            max_lag = len(autocorr) - 1
        
        if min_lag >= max_lag:
            return 0.0, 0.0
        
        search_range = autocorr[min_lag:max_lag]
        peak_idx = np.argmax(search_range) + min_lag
        
        if peak_idx > 0:
            freq = self.sample_rate / peak_idx
            confidence = autocorr[peak_idx] / autocorr[0] if autocorr[0] > 0 else 0
            return float(freq), float(confidence)
        
        return 0.0, 0.0
    
    def _energy_onset_detection(self, audio: np.ndarray) -> List[int]:
        """Simple energy-based onset detection"""
        frame_length = self.hop_length * 4
        hop = self.hop_length
        
        n_frames = (len(audio) - frame_length) // hop
        energy = np.zeros(n_frames)
        
        for i in range(n_frames):
            start = i * hop
            frame = audio[start:start + frame_length]
            energy[i] = np.sum(frame ** 2)
        
        # Find peaks in energy derivative
        energy_diff = np.diff(energy)
        threshold = np.mean(energy_diff) + 2 * np.std(energy_diff)
        
        onsets = []
        for i in range(1, len(energy_diff) - 1):
            if (energy_diff[i] > threshold and 
                energy_diff[i] > energy_diff[i-1] and
                energy_diff[i] > energy_diff[i+1]):
                onsets.append(i * hop)
        
        return onsets
    
    def _simple_chroma(self, audio: np.ndarray) -> np.ndarray:
        """Simplified chroma features"""
        # FFT
        spectrum = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1/self.sample_rate)
        
        # Map to chroma bins
        chroma = np.zeros(12)
        
        for i, freq in enumerate(freqs):
            if freq > 0:
                # Convert frequency to MIDI note
                midi_note = 69 + 12 * np.log2(freq / 440.0)
                pitch_class = int(round(midi_note)) % 12
                chroma[pitch_class] += spectrum[i]
        
        # Normalize
        if np.max(chroma) > 0:
            chroma /= np.max(chroma)
        
        return chroma.reshape(12, 1)


# =============================================================================
# AI MUSIC GENERATION (inspired by Magenta, AudioCraft, Scribbletune)
# =============================================================================

class AIGenerator:
    """
    AI-powered music generation with zero learning curve.
    
    Features:
    - One-click melody generation
    - Style-based generation
    - Continuation from existing music
    - Text-to-music (if AudioCraft available)
    
    Example:
        generator = AIGenerator()
        melody = generator.generate_melody(
            num_bars=4,
            style="jazzy",
            temperature=0.8
        )
    """
    
    # Scale patterns for generation (semitones from root)
    SCALES = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'pentatonic': [0, 2, 4, 7, 9],
        'blues': [0, 3, 5, 6, 7, 10],
        'dorian': [0, 2, 3, 5, 7, 9, 10],
        'mixolydian': [0, 2, 4, 5, 7, 9, 10],
        'chromatic': list(range(12)),
        'whole_tone': [0, 2, 4, 6, 8, 10],
    }
    
    # Chord progressions by style
    PROGRESSIONS = {
        'pop': [[0, 4, 5, 3], [0, 5, 6, 4]],
        'jazz': [[0, 4, 2, 5], [3, 6, 2, 5]],
        'blues': [[0, 0, 0, 0, 3, 3, 0, 0, 4, 3, 0, 4]],
        'rock': [[0, 3, 4, 4], [0, 5, 3, 4]],
        'ambient': [[0, 4, 5, 0], [2, 4, 6, 0]],
    }
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            np.random.seed(seed)
        self.sample_rate = 44100
    
    def generate_melody(
        self,
        num_bars: int = 4,
        notes_per_bar: int = 4,
        root: int = 60,  # Middle C
        scale: str = 'pentatonic',
        temperature: float = 0.7,
        style: str = 'random'
    ) -> List[Dict[str, Any]]:
        """
        Generate a melody with specified parameters.
        
        Returns list of note events:
        [{'note': 60, 'velocity': 100, 'start': 0.0, 'duration': 0.5}, ...]
        """
        notes = []
        scale_intervals = self.SCALES.get(scale, self.SCALES['pentatonic'])
        
        # Build available notes (2 octaves centered on root)
        available_notes = []
        for octave in range(-1, 2):
            for interval in scale_intervals:
                note = root + octave * 12 + interval
                if 36 <= note <= 96:  # Piano range
                    available_notes.append(note)
        
        # Generate based on style
        if style == 'markov':
            notes = self._generate_markov_melody(
                num_bars, notes_per_bar, available_notes, temperature
            )
        elif style == 'genetic':
            notes = self._generate_genetic_melody(
                num_bars, notes_per_bar, available_notes, temperature
            )
        elif style == 'cellular':
            notes = self._generate_cellular_melody(
                num_bars, notes_per_bar, available_notes, temperature
            )
        else:
            # Random walk melody
            notes = self._generate_random_walk_melody(
                num_bars, notes_per_bar, available_notes, temperature
            )
        
        return notes
    
    def generate_chord_progression(
        self,
        num_bars: int = 4,
        style: str = 'pop',
        root: int = 60
    ) -> List[List[int]]:
        """Generate a chord progression"""
        if style in self.PROGRESSIONS:
            progression = self.PROGRESSIONS[style]
            base_prog = progression[np.random.randint(len(progression))]
        else:
            # Random functional progression
            base_prog = [0, np.random.choice([3, 4, 5]), 
                        np.random.choice([2, 4, 5]), 
                        np.random.choice([4, 5])]
        
        # Extend/trim to num_bars
        while len(base_prog) < num_bars:
            base_prog = base_prog + base_prog
        base_prog = base_prog[:num_bars]
        
        # Convert to actual chords
        chords = []
        for degree in base_prog:
            chord_root = root + self.SCALES['major'][degree % 7]
            # Major or minor based on degree
            if degree in [0, 3, 4]:  # I, IV, V are major
                chord = [chord_root, chord_root + 4, chord_root + 7]
            else:  # ii, iii, vi are minor
                chord = [chord_root, chord_root + 3, chord_root + 7]
            chords.append(chord)
        
        return chords
    
    def generate_drum_pattern(
        self,
        num_bars: int = 2,
        steps_per_bar: int = 16,
        style: str = 'rock',
        density: float = 0.5
    ) -> Dict[str, List[int]]:
        """
        Generate a drum pattern.
        
        Returns dict of instrument -> step triggers
        """
        total_steps = num_bars * steps_per_bar
        
        if style == 'rock':
            kick = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
            snare = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
            hihat = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        elif style == 'house':
            kick = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
            snare = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
            hihat = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
        elif style == 'jazz':
            kick = [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0]
            snare = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
            hihat = [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0]
        elif style == 'cellular':
            # Use cellular automata
            return self._generate_cellular_drums(num_bars, steps_per_bar, density)
        else:
            # Random with density control
            kick = [1 if np.random.random() < density * 0.4 else 0 
                    for _ in range(steps_per_bar)]
            snare = [1 if np.random.random() < density * 0.3 else 0 
                     for _ in range(steps_per_bar)]
            hihat = [1 if np.random.random() < density * 0.6 else 0 
                     for _ in range(steps_per_bar)]
        
        # Extend to full length
        pattern = {
            'kick': (kick * num_bars)[:total_steps],
            'snare': (snare * num_bars)[:total_steps],
            'hihat': (hihat * num_bars)[:total_steps],
        }
        
        return pattern
    
    def text_to_melody(self, text: str, root: int = 60) -> List[Dict[str, Any]]:
        """
        Convert text to melody (ASCII mapping).
        
        Each character becomes a note, spaces become rests.
        """
        notes = []
        time = 0.0
        duration = 0.25  # Quarter note
        
        for char in text:
            if char == ' ':
                # Rest
                time += duration
            else:
                # Map ASCII to note (mod 24 for 2 octaves)
                note_offset = ord(char.lower()) % 24 - 12
                note = root + note_offset
                
                # Velocity based on case
                velocity = 100 if char.isupper() else 80
                
                notes.append({
                    'note': note,
                    'velocity': velocity,
                    'start': time,
                    'duration': duration,
                })
                time += duration
        
        return notes
    
    def color_to_harmony(
        self, 
        r: int, g: int, b: int,
        root: int = 60
    ) -> List[int]:
        """
        Convert RGB color to a chord.
        
        - Hue determines root note
        - Saturation determines chord type
        - Brightness determines octave
        """
        import colorsys
        
        # Convert to HSV
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        # Hue -> root note (0-11)
        note_offset = int(h * 12) % 12
        chord_root = root + note_offset
        
        # Adjust octave by brightness
        octave_shift = int((v - 0.5) * 2) * 12  # -12 to +12
        chord_root += octave_shift
        
        # Saturation -> chord type
        if s < 0.3:
            # Power chord (neutral)
            chord = [chord_root, chord_root + 7]
        elif s < 0.5:
            # Minor (sad)
            chord = [chord_root, chord_root + 3, chord_root + 7]
        elif s < 0.7:
            # Major (happy)
            chord = [chord_root, chord_root + 4, chord_root + 7]
        else:
            # Dominant 7th (tension)
            chord = [chord_root, chord_root + 4, chord_root + 7, chord_root + 10]
        
        return chord
    
    # === GENERATION ALGORITHMS ===
    
    def _generate_markov_melody(
        self,
        num_bars: int,
        notes_per_bar: int,
        available_notes: List[int],
        temperature: float
    ) -> List[Dict[str, Any]]:
        """Generate melody using Markov chain"""
        total_notes = num_bars * notes_per_bar
        notes = []
        
        # Build transition probabilities (prefer small intervals)
        n = len(available_notes)
        transition = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                interval = abs(available_notes[i] - available_notes[j])
                # Prefer smaller intervals
                transition[i, j] = np.exp(-interval / (12 * temperature))
            transition[i] /= np.sum(transition[i])
        
        # Generate
        current_idx = np.random.randint(n)
        time = 0.0
        duration = 1.0 / notes_per_bar
        
        for _ in range(total_notes):
            note = available_notes[current_idx]
            velocity = np.random.randint(70, 110)
            
            notes.append({
                'note': note,
                'velocity': velocity,
                'start': time,
                'duration': duration * 0.9,
            })
            
            # Transition
            current_idx = np.random.choice(n, p=transition[current_idx])
            time += duration
        
        return notes
    
    def _generate_genetic_melody(
        self,
        num_bars: int,
        notes_per_bar: int,
        available_notes: List[int],
        temperature: float
    ) -> List[Dict[str, Any]]:
        """Generate melody using genetic algorithm"""
        total_notes = num_bars * notes_per_bar
        n = len(available_notes)
        
        # Population
        pop_size = 16
        generations = 50
        
        def create_individual():
            return [np.random.randint(n) for _ in range(total_notes)]
        
        def fitness(individual):
            # Penalize large jumps
            jump_penalty = sum(
                abs(available_notes[individual[i]] - available_notes[individual[i-1]])
                for i in range(1, len(individual))
            )
            # Reward variety but not too much
            unique = len(set(individual))
            variety_score = unique if unique < total_notes * 0.7 else total_notes - unique
            
            return variety_score * 10 - jump_penalty * 0.5
        
        def crossover(a, b):
            point = np.random.randint(1, total_notes - 1)
            return a[:point] + b[point:]
        
        def mutate(individual, rate=0.1):
            return [
                np.random.randint(n) if np.random.random() < rate else x
                for x in individual
            ]
        
        # Evolution
        population = [create_individual() for _ in range(pop_size)]
        
        for _ in range(generations):
            # Score and sort
            scored = [(fitness(ind), ind) for ind in population]
            scored.sort(reverse=True)
            
            # Selection (keep best half)
            survivors = [ind for _, ind in scored[:pop_size // 2]]
            
            # Reproduction
            new_pop = survivors.copy()
            while len(new_pop) < pop_size:
                p1, p2 = np.random.choice(len(survivors), 2, replace=False)
                child = crossover(survivors[p1], survivors[p2])
                child = mutate(child, rate=temperature * 0.2)
                new_pop.append(child)
            
            population = new_pop
        
        # Use best individual
        best = max(population, key=fitness)
        
        # Convert to notes
        notes = []
        time = 0.0
        duration = 1.0 / notes_per_bar
        
        for idx in best:
            notes.append({
                'note': available_notes[idx],
                'velocity': np.random.randint(70, 110),
                'start': time,
                'duration': duration * 0.9,
            })
            time += duration
        
        return notes
    
    def _generate_cellular_melody(
        self,
        num_bars: int,
        notes_per_bar: int,
        available_notes: List[int],
        temperature: float
    ) -> List[Dict[str, Any]]:
        """Generate melody using cellular automata (Rule 110)"""
        total_notes = num_bars * notes_per_bar
        width = len(available_notes)
        
        # Rule 110 lookup
        rule = {
            (1, 1, 1): 0, (1, 1, 0): 1, (1, 0, 1): 1, (1, 0, 0): 0,
            (0, 1, 1): 1, (0, 1, 0): 1, (0, 0, 1): 1, (0, 0, 0): 0,
        }
        
        # Initialize with random state
        state = [1 if np.random.random() < temperature else 0 for _ in range(width)]
        
        notes = []
        time = 0.0
        duration = 1.0 / notes_per_bar
        
        for _ in range(total_notes):
            # Find active cells
            active = [i for i, cell in enumerate(state) if cell == 1]
            
            if active:
                # Pick note from active cells
                idx = np.random.choice(active)
                notes.append({
                    'note': available_notes[idx],
                    'velocity': 80 + len(active) * 5,
                    'start': time,
                    'duration': duration * 0.9,
                })
            
            # Evolve state
            new_state = []
            for i in range(width):
                left = state[(i - 1) % width]
                center = state[i]
                right = state[(i + 1) % width]
                new_state.append(rule.get((left, center, right), 0))
            state = new_state
            
            time += duration
        
        return notes
    
    def _generate_random_walk_melody(
        self,
        num_bars: int,
        notes_per_bar: int,
        available_notes: List[int],
        temperature: float
    ) -> List[Dict[str, Any]]:
        """Generate melody using random walk"""
        total_notes = num_bars * notes_per_bar
        n = len(available_notes)
        
        notes = []
        current_idx = n // 2  # Start in middle
        time = 0.0
        duration = 1.0 / notes_per_bar
        
        for _ in range(total_notes):
            notes.append({
                'note': available_notes[current_idx],
                'velocity': np.random.randint(70, 100),
                'start': time,
                'duration': duration * 0.9,
            })
            
            # Random walk step
            step = int(np.random.normal(0, temperature * 3))
            current_idx = max(0, min(n - 1, current_idx + step))
            time += duration
        
        return notes
    
    def _generate_cellular_drums(
        self,
        num_bars: int,
        steps_per_bar: int,
        density: float
    ) -> Dict[str, List[int]]:
        """Generate drums using cellular automata"""
        total_steps = num_bars * steps_per_bar
        
        # Initialize 3 rows (kick, snare, hihat)
        state = [
            [1 if np.random.random() < density * 0.3 else 0 
             for _ in range(total_steps)],
            [1 if np.random.random() < density * 0.2 else 0 
             for _ in range(total_steps)],
            [1 if np.random.random() < density * 0.5 else 0 
             for _ in range(total_steps)],
        ]
        
        # Evolve each row with Rule 30
        rule = {
            (1, 1, 1): 0, (1, 1, 0): 0, (1, 0, 1): 0, (1, 0, 0): 1,
            (0, 1, 1): 1, (0, 1, 0): 1, (0, 0, 1): 1, (0, 0, 0): 0,
        }
        
        for _ in range(8):  # 8 generation steps
            new_state = []
            for row in state:
                new_row = []
                for i in range(len(row)):
                    left = row[(i - 1) % len(row)]
                    center = row[i]
                    right = row[(i + 1) % len(row)]
                    new_row.append(rule.get((left, center, right), 0))
                new_state.append(new_row)
            state = new_state
        
        # Ensure kick on 1 and snare on 3
        for bar in range(num_bars):
            state[0][bar * steps_per_bar] = 1  # Kick on 1
            if steps_per_bar >= 8:
                state[1][bar * steps_per_bar + steps_per_bar // 2] = 1  # Snare on 3
        
        return {
            'kick': state[0],
            'snare': state[1],
            'hihat': state[2],
        }


# =============================================================================
# PATTERN BUILDER (inspired by Scribbletune, Tonal)
# =============================================================================

class PatternBuilder:
    """
    Build musical patterns with a simple, expressive syntax.
    Inspired by Scribbletune and TidalCycles.
    
    Example:
        builder = PatternBuilder(bpm=120)
        
        # Simple pattern string
        pattern = builder.from_string("x-x- x-x- x-xx x---")
        
        # Euclidean rhythm
        rhythm = builder.euclidean(5, 8)  # 5 hits in 8 steps
        
        # Chord progression
        chords = builder.chord_pattern("Cmaj7 Am7 Fmaj7 G7")
    """
    
    CHORD_TYPES = {
        'maj': [0, 4, 7],
        'min': [0, 3, 7],
        'm': [0, 3, 7],
        'dim': [0, 3, 6],
        'aug': [0, 4, 8],
        '7': [0, 4, 7, 10],
        'maj7': [0, 4, 7, 11],
        'm7': [0, 3, 7, 10],
        'min7': [0, 3, 7, 10],
        'dim7': [0, 3, 6, 9],
        'sus2': [0, 2, 7],
        'sus4': [0, 5, 7],
        'add9': [0, 4, 7, 14],
    }
    
    NOTE_MAP = {
        'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11,
        'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11,
    }
    
    def __init__(self, bpm: int = 120, time_signature: Tuple[int, int] = (4, 4)):
        self.bpm = bpm
        self.beats_per_bar, self.beat_unit = time_signature
        self.samples_per_beat = 44100 * 60 / bpm
    
    def from_string(self, pattern: str, note: int = 60) -> List[Dict[str, Any]]:
        """
        Parse pattern string to note events.
        
        x = hit
        - = rest
        X = accented hit
        [xx] = two hits in one slot
        """
        events = []
        step = 0
        step_duration = 1.0 / len(pattern.replace(' ', '').replace('[', '').replace(']', ''))
        
        i = 0
        chars = pattern.replace(' ', '')
        
        while i < len(chars):
            char = chars[i]
            
            if char == '[':
                # Group - find closing bracket
                j = chars.index(']', i)
                group = chars[i+1:j]
                group_duration = step_duration / len(group)
                
                for g_char in group:
                    if g_char == 'x':
                        events.append({
                            'note': note,
                            'velocity': 80,
                            'start': step,
                            'duration': group_duration * 0.9,
                        })
                    elif g_char == 'X':
                        events.append({
                            'note': note,
                            'velocity': 110,
                            'start': step,
                            'duration': group_duration * 0.9,
                        })
                    step += group_duration
                
                i = j + 1
            else:
                if char == 'x':
                    events.append({
                        'note': note,
                        'velocity': 80,
                        'start': step,
                        'duration': step_duration * 0.9,
                    })
                elif char == 'X':
                    events.append({
                        'note': note,
                        'velocity': 110,
                        'start': step,
                        'duration': step_duration * 0.9,
                    })
                # '-' is rest, just advance time
                step += step_duration
                i += 1
        
        return events
    
    def euclidean(self, hits: int, steps: int, rotation: int = 0) -> List[int]:
        """
        Generate Euclidean rhythm pattern.
        
        Example: euclidean(5, 8) -> [1, 0, 1, 1, 0, 1, 1, 0]
        """
        if hits >= steps:
            return [1] * steps
        if hits == 0:
            return [0] * steps
        
        # Bresenham's algorithm
        pattern = []
        bucket = 0
        
        for _ in range(steps):
            bucket += hits
            if bucket >= steps:
                bucket -= steps
                pattern.append(1)
            else:
                pattern.append(0)
        
        # Rotate
        if rotation:
            pattern = pattern[rotation:] + pattern[:rotation]
        
        return pattern
    
    def parse_chord(self, chord_str: str, octave: int = 4) -> List[int]:
        """
        Parse chord string to MIDI notes.
        
        Examples: "Cmaj7", "Am", "F#dim", "Bb7"
        """
        if not chord_str:
            return []
        
        # Extract root note
        root_str = chord_str[0].upper()
        i = 1
        
        # Check for accidental
        if i < len(chord_str) and chord_str[i] in '#b':
            if chord_str[i] == '#':
                root_offset = 1
            else:
                root_offset = -1
            i += 1
        else:
            root_offset = 0
        
        # Get root MIDI note
        if root_str not in self.NOTE_MAP:
            return []
        
        root = self.NOTE_MAP[root_str] + root_offset + octave * 12 + 12
        
        # Extract chord type
        chord_type = chord_str[i:].lower() if i < len(chord_str) else 'maj'
        
        # Get intervals
        intervals = self.CHORD_TYPES.get(chord_type, self.CHORD_TYPES['maj'])
        
        return [root + interval for interval in intervals]
    
    def chord_pattern(
        self, 
        progression: str, 
        duration: float = 1.0,
        octave: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Parse chord progression string to events.
        
        Example: "Cmaj7 Am7 Fmaj7 G7"
        """
        chords = progression.split()
        events = []
        time = 0.0
        
        for chord_str in chords:
            notes = self.parse_chord(chord_str, octave)
            
            for note in notes:
                events.append({
                    'note': note,
                    'velocity': 80,
                    'start': time,
                    'duration': duration * 0.95,
                    'chord': chord_str,
                })
            
            time += duration
        
        return events
    
    def arpeggio(
        self,
        chord: List[int],
        pattern: str = 'up',
        steps: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Generate arpeggio from chord.
        
        Patterns: 'up', 'down', 'updown', 'random', 'order'
        """
        if not chord:
            return []
        
        events = []
        step_duration = 1.0 / steps
        
        if pattern == 'up':
            sequence = sorted(chord) * (steps // len(chord) + 1)
        elif pattern == 'down':
            sequence = sorted(chord, reverse=True) * (steps // len(chord) + 1)
        elif pattern == 'updown':
            up = sorted(chord)
            down = sorted(chord, reverse=True)[1:-1] if len(chord) > 2 else []
            cycle = up + down
            sequence = cycle * (steps // len(cycle) + 1)
        elif pattern == 'random':
            sequence = [np.random.choice(chord) for _ in range(steps)]
        else:  # 'order'
            sequence = chord * (steps // len(chord) + 1)
        
        for i in range(steps):
            events.append({
                'note': sequence[i],
                'velocity': 90,
                'start': i * step_duration,
                'duration': step_duration * 0.8,
            })
        
        return events


# =============================================================================
# VISUAL ANALYZER (inspired by Meyda, wavesurfer.js)
# =============================================================================

class VisualAnalyzer:
    """
    Real-time audio visualization features.
    
    Provides data for:
    - Waveform display
    - Spectrum analyzer
    - Chromasynesthesia colors
    - Beat pulse
    """
    
    # Chromasynesthesia color mapping (0-11 semitones)
    CHROMA_COLORS = [
        (255, 92, 92),    # C - Red
        (255, 140, 76),   # C# - Orange-Red
        (255, 184, 76),   # D - Orange
        (255, 224, 76),   # D# - Yellow-Orange
        (232, 255, 76),   # E - Yellow
        (140, 255, 76),   # F - Yellow-Green
        (76, 255, 140),   # F# - Green
        (76, 255, 255),   # G - Cyan
        (76, 140, 255),   # G# - Blue
        (76, 76, 255),    # A - Indigo
        (140, 76, 255),   # A# - Purple
        (255, 76, 255),   # B - Magenta
    ]
    
    def __init__(self, sample_rate: int = 44100, fft_size: int = 2048):
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.smoothing = 0.8
        self.prev_spectrum = None
    
    def get_waveform(self, audio: np.ndarray, num_points: int = 200) -> np.ndarray:
        """Downsample audio for waveform display"""
        if len(audio) == 0:
            return np.zeros(num_points)
        
        if len(audio) < num_points:
            return np.pad(audio, (0, num_points - len(audio)))
        
        # Average into bins
        chunk_size = len(audio) // num_points
        waveform = np.zeros(num_points)
        
        for i in range(num_points):
            start = i * chunk_size
            end = start + chunk_size
            chunk = audio[start:end]
            
            # Use max for peaks
            waveform[i] = np.max(np.abs(chunk))
        
        return waveform
    
    def get_spectrum(self, audio: np.ndarray, num_bands: int = 64) -> np.ndarray:
        """Get frequency spectrum with smoothing"""
        if len(audio) < self.fft_size:
            audio = np.pad(audio, (0, self.fft_size - len(audio)))
        
        # Window and FFT
        windowed = audio[:self.fft_size] * np.hanning(self.fft_size)
        spectrum = np.abs(np.fft.rfft(windowed))
        
        # Log-scale frequency bands
        freq_bins = len(spectrum)
        bands = np.zeros(num_bands)
        
        for i in range(num_bands):
            # Logarithmic distribution
            low = int((freq_bins / num_bands) * i)
            high = int((freq_bins / num_bands) * (i + 1))
            if high <= low:
                high = low + 1
            bands[i] = np.mean(spectrum[low:high])
        
        # Normalize to 0-1
        if np.max(bands) > 0:
            bands = bands / np.max(bands)
        
        # Smoothing
        if self.prev_spectrum is not None and len(self.prev_spectrum) == num_bands:
            bands = self.smoothing * self.prev_spectrum + (1 - self.smoothing) * bands
        
        self.prev_spectrum = bands.copy()
        return bands
    
    def get_dominant_pitch(self, audio: np.ndarray) -> Tuple[float, int]:
        """Get dominant pitch and chromasynesthesia color index"""
        if len(audio) < 512:
            return 0.0, 0
        
        # Autocorrelation for pitch
        autocorr = np.correlate(audio[:1024], audio[:1024], mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find peak between 80Hz and 1000Hz
        min_lag = int(self.sample_rate / 1000)
        max_lag = int(self.sample_rate / 80)
        
        if max_lag > len(autocorr):
            max_lag = len(autocorr) - 1
        
        if min_lag >= max_lag:
            return 0.0, 0
        
        peak_idx = np.argmax(autocorr[min_lag:max_lag]) + min_lag
        
        if peak_idx > 0:
            freq = self.sample_rate / peak_idx
            # Convert to MIDI note
            if freq > 0:
                midi_note = 69 + 12 * np.log2(freq / 440.0)
                chroma_idx = int(round(midi_note)) % 12
                return freq, chroma_idx
        
        return 0.0, 0
    
    def get_chroma_color(self, pitch_class: int) -> Tuple[int, int, int]:
        """Get RGB color for pitch class (0-11)"""
        return self.CHROMA_COLORS[pitch_class % 12]
    
    def midi_to_color(self, midi_note: int) -> Tuple[int, int, int]:
        """Get RGB color for MIDI note"""
        return self.CHROMA_COLORS[midi_note % 12]
    
    def get_beat_pulse(self, audio: np.ndarray, threshold: float = 0.5) -> bool:
        """Detect if current frame is likely a beat"""
        # Simple energy-based detection
        energy = np.sqrt(np.mean(audio ** 2))
        return energy > threshold


# =============================================================================
# CONVENIENCE EXPORTS
# =============================================================================

def quick_analyze(file_path: str) -> Dict[str, Any]:
    """Quick analysis of an audio file"""
    if not LIBROSA_AVAILABLE:
        raise ImportError("librosa required for file analysis")
    
    audio, sr = librosa.load(file_path)
    
    analyzer = AudioAnalyzer(sample_rate=sr)
    features = analyzer.analyze(audio)
    features['key'], features['mode'] = analyzer.detect_key(audio)
    features['bpm'] = analyzer.detect_bpm(audio)
    features['duration'] = len(audio) / sr
    
    return features


def quick_generate(style: str = 'random', bars: int = 4) -> List[Dict[str, Any]]:
    """Quick one-shot melody generation"""
    gen = AIGenerator()
    return gen.generate_melody(num_bars=bars, style=style)


def quick_pattern(pattern_str: str) -> List[Dict[str, Any]]:
    """Quick pattern parsing"""
    builder = PatternBuilder()
    return builder.from_string(pattern_str)


# Export main classes
__all__ = [
    'AudioAnalyzer',
    'AIGenerator', 
    'PatternBuilder',
    'VisualAnalyzer',
    'quick_analyze',
    'quick_generate',
    'quick_pattern',
    'LIBROSA_AVAILABLE',
    'AUBIO_AVAILABLE',
    'MAGENTA_AVAILABLE',
]
