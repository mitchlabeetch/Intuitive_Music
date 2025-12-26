"""External integrations hub

This module provides unified access to external audio analysis and processing
libraries including librosa, aubio, and Meyda-like spectral features.
"""
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
from scipy import signal
from scipy.fftpack import fft
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Container for audio analysis results"""
    tempo: float = 120.0
    key: str = "C"
    mode: str = "major"
    duration: float = 0.0
    rms: float = 0.0
    peak: float = 0.0
    spectral_centroid: float = 0.0
    spectral_rolloff: float = 0.0
    spectral_flatness: float = 0.0
    zero_crossing_rate: float = 0.0
    onsets: Optional[List[float]] = None
    beats: Optional[List[float]] = None
    chroma: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tempo": self.tempo,
            "key": self.key,
            "mode": self.mode,
            "duration": self.duration,
            "rms": self.rms,
            "peak": self.peak,
            "spectral_centroid": self.spectral_centroid,
            "spectral_rolloff": self.spectral_rolloff,
            "spectral_flatness": self.spectral_flatness,
            "zero_crossing_rate": self.zero_crossing_rate,
            "num_onsets": len(self.onsets) if self.onsets else 0,
            "num_beats": len(self.beats) if self.beats else 0,
        }


class AudioAnalyzer:
    """
    Unified audio analysis with librosa fallback.
    
    Provides professional-grade analysis including:
    - Tempo and beat detection
    - Key and mode detection
    - Spectral features
    - Onset detection
    """
    
    def __init__(self):
        self._librosa = None
        self._aubio = None
        self._load_backends()
    
    def _load_backends(self) -> None:
        """Load available analysis backends"""
        try:
            import librosa
            self._librosa = librosa
            logger.info("librosa backend loaded")
        except ImportError:
            logger.warning("librosa not available, using scipy fallback")
        
        try:
            import aubio
            self._aubio = aubio
            logger.info("aubio backend loaded")
        except ImportError:
            logger.debug("aubio not available")
    
    def analyze(
        self,
        audio: np.ndarray,
        sample_rate: int = 48000,
        features: Optional[List[str]] = None
    ) -> AnalysisResult:
        """
        Perform comprehensive audio analysis.
        
        Args:
            audio: Audio data (samples,) or (samples, channels)
            sample_rate: Sample rate in Hz
            features: List of features to compute (None = all)
        
        Returns:
            AnalysisResult with computed features
        """
        # Convert to mono
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=1)
        else:
            audio_mono = audio
        
        # Normalize
        audio_mono = audio_mono.astype(np.float32)
        if np.max(np.abs(audio_mono)) > 0:
            audio_mono = audio_mono / np.max(np.abs(audio_mono))
        
        result = AnalysisResult()
        result.duration = len(audio_mono) / sample_rate
        
        # Select features to compute
        if features is None:
            features = [
                "tempo", "key", "rms", "peak",
                "spectral_centroid", "spectral_rolloff",
                "spectral_flatness", "zero_crossing_rate",
                "onsets", "beats"
            ]
        
        # Compute requested features
        if "rms" in features:
            result.rms = self._compute_rms(audio_mono)
        
        if "peak" in features:
            result.peak = np.max(np.abs(audio_mono))
        
        if "zero_crossing_rate" in features:
            result.zero_crossing_rate = self._compute_zcr(audio_mono)
        
        if "spectral_centroid" in features:
            result.spectral_centroid = self._compute_spectral_centroid(
                audio_mono, sample_rate
            )
        
        if "spectral_rolloff" in features:
            result.spectral_rolloff = self._compute_spectral_rolloff(
                audio_mono, sample_rate
            )
        
        if "spectral_flatness" in features:
            result.spectral_flatness = self._compute_spectral_flatness(audio_mono)
        
        if "onsets" in features:
            result.onsets = self._detect_onsets(audio_mono, sample_rate)
        
        if "tempo" in features or "beats" in features:
            tempo, beats = self._detect_tempo_and_beats(audio_mono, sample_rate)
            result.tempo = tempo
            result.beats = beats
        
        if "key" in features:
            key, mode = self._detect_key(audio_mono, sample_rate)
            result.key = key
            result.mode = mode
        
        return result
    
    def _compute_rms(self, audio: np.ndarray) -> float:
        """Compute RMS level"""
        return float(np.sqrt(np.mean(audio ** 2)))
    
    def _compute_zcr(self, audio: np.ndarray) -> float:
        """Compute zero crossing rate"""
        signs = np.sign(audio)
        signs[signs == 0] = 1  # Handle zeros
        crossings = np.where(np.diff(signs))[0]
        return len(crossings) / len(audio)
    
    def _compute_spectral_centroid(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> float:
        """Compute spectral centroid (brightness)"""
        if self._librosa:
            centroid = self._librosa.feature.spectral_centroid(
                y=audio, sr=sample_rate
            )
            return float(np.mean(centroid))
        
        # Fallback implementation
        n_fft = 2048
        hop_length = 512
        
        # Compute magnitude spectrum
        spectrum = np.abs(fft(audio[:n_fft]))[:n_fft // 2]
        freqs = np.linspace(0, sample_rate / 2, len(spectrum))
        
        # Compute centroid
        magnitude_sum = np.sum(spectrum)
        if magnitude_sum > 0:
            centroid = np.sum(freqs * spectrum) / magnitude_sum
        else:
            centroid = 0.0
        
        return float(centroid)
    
    def _compute_spectral_rolloff(
        self,
        audio: np.ndarray,
        sample_rate: int,
        rolloff_percent: float = 0.85
    ) -> float:
        """Compute spectral rolloff frequency"""
        if self._librosa:
            rolloff = self._librosa.feature.spectral_rolloff(
                y=audio, sr=sample_rate, roll_percent=rolloff_percent
            )
            return float(np.mean(rolloff))
        
        # Fallback implementation
        n_fft = 2048
        spectrum = np.abs(fft(audio[:n_fft]))[:n_fft // 2]
        freqs = np.linspace(0, sample_rate / 2, len(spectrum))
        
        total_energy = np.sum(spectrum)
        if total_energy == 0:
            return 0.0
        
        cumsum = np.cumsum(spectrum)
        threshold = rolloff_percent * total_energy
        rolloff_idx = np.searchsorted(cumsum, threshold)
        
        if rolloff_idx < len(freqs):
            return float(freqs[rolloff_idx])
        return float(sample_rate / 2)
    
    def _compute_spectral_flatness(self, audio: np.ndarray) -> float:
        """Compute spectral flatness (noisiness)"""
        if self._librosa:
            flatness = self._librosa.feature.spectral_flatness(y=audio)
            return float(np.mean(flatness))
        
        # Fallback implementation
        n_fft = 2048
        spectrum = np.abs(fft(audio[:n_fft]))[:n_fft // 2]
        spectrum = spectrum + 1e-10  # Avoid log(0)
        
        geometric_mean = np.exp(np.mean(np.log(spectrum)))
        arithmetic_mean = np.mean(spectrum)
        
        if arithmetic_mean > 0:
            return float(geometric_mean / arithmetic_mean)
        return 0.0
    
    def _detect_onsets(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> List[float]:
        """Detect note onsets"""
        if self._librosa:
            onset_frames = self._librosa.onset.onset_detect(
                y=audio, sr=sample_rate
            )
            onset_times = self._librosa.frames_to_time(onset_frames, sr=sample_rate)
            return onset_times.tolist()
        
        # Fallback using energy-based detection
        hop_length = 512
        n_frames = len(audio) // hop_length
        
        energy = np.array([
            np.sum(audio[i * hop_length:(i + 1) * hop_length] ** 2)
            for i in range(n_frames)
        ])
        
        # Compute onset envelope (difference of energy)
        onset_env = np.diff(energy)
        onset_env = np.maximum(0, onset_env)  # Half-wave rectifier
        
        # Peak picking
        peaks, _ = signal.find_peaks(onset_env, height=np.mean(onset_env) * 2)
        
        # Convert to time
        onset_times = peaks * hop_length / sample_rate
        return onset_times.tolist()
    
    def _detect_tempo_and_beats(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> Tuple[float, List[float]]:
        """Detect tempo and beat positions"""
        if self._librosa:
            tempo, beat_frames = self._librosa.beat.beat_track(
                y=audio, sr=sample_rate
            )
            beat_times = self._librosa.frames_to_time(beat_frames, sr=sample_rate)
            return float(tempo), beat_times.tolist()
        
        # Fallback implementation using autocorrelation
        hop_length = 512
        
        # Compute onset envelope
        n_frames = len(audio) // hop_length
        onset_env = np.array([
            np.sum(np.abs(audio[i * hop_length:(i + 1) * hop_length]))
            for i in range(n_frames)
        ])
        
        # Autocorrelation
        autocorr = np.correlate(onset_env, onset_env, mode='full')
        autocorr = autocorr[len(autocorr) // 2:]
        
        # Find peaks in autocorrelation
        min_lag = int(60 / 200 * sample_rate / hop_length)  # 200 BPM max
        max_lag = int(60 / 60 * sample_rate / hop_length)   # 60 BPM min
        
        peaks, _ = signal.find_peaks(autocorr[min_lag:max_lag])
        
        if len(peaks) > 0:
            # Find strongest peak
            peak_idx = peaks[np.argmax(autocorr[min_lag:max_lag][peaks])]
            period_frames = min_lag + peak_idx
            tempo = 60 * sample_rate / hop_length / period_frames
        else:
            tempo = 120.0  # Default tempo
        
        # Generate beat times
        beat_period = 60.0 / tempo
        duration = len(audio) / sample_rate
        beats = np.arange(0, duration, beat_period).tolist()
        
        return float(tempo), beats
    
    def _detect_key(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> Tuple[str, str]:
        """Detect musical key and mode"""
        if self._librosa:
            chroma = self._librosa.feature.chroma_cqt(y=audio, sr=sample_rate)
            chroma_mean = np.mean(chroma, axis=1)
        else:
            # Simple FFT-based chroma
            chroma_mean = self._compute_simple_chroma(audio, sample_rate)
        
        # Key profiles (Krumhansl-Kessler)
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 
                                  2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 
                                  2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                      'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        best_corr = -1
        best_key = 'C'
        best_mode = 'major'
        
        # Try all keys and modes
        for i in range(12):
            # Rotate chroma to start from this key
            rotated = np.roll(chroma_mean, -i)
            
            # Correlate with profiles
            major_corr = np.corrcoef(rotated, major_profile)[0, 1]
            minor_corr = np.corrcoef(rotated, minor_profile)[0, 1]
            
            if major_corr > best_corr:
                best_corr = major_corr
                best_key = note_names[i]
                best_mode = 'major'
            
            if minor_corr > best_corr:
                best_corr = minor_corr
                best_key = note_names[i]
                best_mode = 'minor'
        
        return best_key, best_mode
    
    def _compute_simple_chroma(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> np.ndarray:
        """Simple FFT-based chroma computation"""
        n_fft = 4096
        spectrum = np.abs(fft(audio[:n_fft]))[:n_fft // 2]
        freqs = np.linspace(0, sample_rate / 2, len(spectrum))
        
        # Map frequencies to pitch classes
        chroma = np.zeros(12)
        for i, (freq, mag) in enumerate(zip(freqs, spectrum)):
            if freq > 0:
                # Convert frequency to MIDI note
                midi_note = 12 * np.log2(freq / 440) + 69
                pitch_class = int(midi_note) % 12
                if 0 <= pitch_class < 12:
                    chroma[pitch_class] += mag
        
        # Normalize
        if np.max(chroma) > 0:
            chroma = chroma / np.max(chroma)
        
        return chroma


class PatternBuilder:
    """
    Build musical patterns using expressive syntax.
    
    Supports:
    - String-based patterns like "[xx]-X-"
    - Euclidean rhythms
    - Probability-based generation
    """
    
    def __init__(self, step_duration: float = 0.125):
        self.step_duration = step_duration  # Default: 32nd notes at 120 BPM
    
    def from_string(
        self,
        pattern: str,
        note: int = 36,
        velocity: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Parse string pattern to note events.
        
        Pattern syntax:
        - 'x' or 'X': Hit (lowercase = soft, uppercase = hard)
        - '-': Rest
        - '[' ']': Group (notes in group share the step)
        - ' ': Separator (ignored)
        
        Args:
            pattern: Pattern string
            note: MIDI note number
            velocity: Base velocity
        
        Returns:
            List of note events
        """
        events = []
        time = 0.0
        in_group = False
        group_notes = []
        
        for char in pattern:
            if char == ' ':
                continue
            elif char == '[':
                in_group = True
                group_notes = []
            elif char == ']':
                in_group = False
                if group_notes:
                    group_duration = self.step_duration / len(group_notes)
                    for i, (n, v) in enumerate(group_notes):
                        events.append({
                            'note': n,
                            'velocity': v,
                            'start': time + i * group_duration,
                            'duration': group_duration * 0.9
                        })
                time += self.step_duration
            elif char.lower() == 'x':
                vel = velocity if char.isupper() else int(velocity * 0.6)
                if in_group:
                    group_notes.append((note, vel))
                else:
                    events.append({
                        'note': note,
                        'velocity': vel,
                        'start': time,
                        'duration': self.step_duration * 0.9
                    })
                    time += self.step_duration
            elif char == '-':
                if not in_group:
                    time += self.step_duration
        
        return events
    
    def euclidean(
        self,
        steps: int,
        hits: int,
        rotation: int = 0,
        note: int = 36,
        velocity: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Generate Euclidean rhythm.
        
        Args:
            steps: Total number of steps
            hits: Number of hits to distribute
            rotation: Rotate pattern
            note: MIDI note
            velocity: Note velocity
        
        Returns:
            List of note events
        """
        # Bjorklund's algorithm
        if hits >= steps:
            pattern = [1] * steps
        elif hits == 0:
            pattern = [0] * steps
        else:
            groups = [[1]] * hits + [[0]] * (steps - hits)
            
            while len(set(len(g) for g in groups)) > 1 and len(groups) > 1:
                groups.sort(key=len, reverse=True)
                while len(groups) > 1:
                    shortest = groups.pop()
                    groups[0].extend(shortest)
                    if len(groups) <= 1 or len(groups[0]) != len(groups[-1]):
                        break
            
            pattern = [item for group in groups for item in group]
        
        # Rotate
        if rotation:
            pattern = pattern[rotation:] + pattern[:rotation]
        
        # Convert to events
        events = []
        for i, hit in enumerate(pattern):
            if hit:
                events.append({
                    'note': note,
                    'velocity': velocity,
                    'start': i * self.step_duration,
                    'duration': self.step_duration * 0.9
                })
        
        return events
    
    def probabilistic(
        self,
        steps: int,
        probability: float = 0.5,
        note: int = 36,
        velocity: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Generate pattern with probability per step.
        
        Args:
            steps: Number of steps
            probability: Hit probability (0.0-1.0)
            note: MIDI note
            velocity: Note velocity
        
        Returns:
            List of note events
        """
        events = []
        for i in range(steps):
            if np.random.random() < probability:
                events.append({
                    'note': note,
                    'velocity': velocity + np.random.randint(-10, 10),
                    'start': i * self.step_duration,
                    'duration': self.step_duration * 0.9
                })
        return events


class ScaleHelper:
    """
    Music theory utilities for scales and chords.
    """
    
    SCALES = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
        'melodic_minor': [0, 2, 3, 5, 7, 9, 11],
        'dorian': [0, 2, 3, 5, 7, 9, 10],
        'phrygian': [0, 1, 3, 5, 7, 8, 10],
        'lydian': [0, 2, 4, 6, 7, 9, 11],
        'mixolydian': [0, 2, 4, 5, 7, 9, 10],
        'locrian': [0, 1, 3, 5, 6, 8, 10],
        'pentatonic_major': [0, 2, 4, 7, 9],
        'pentatonic_minor': [0, 3, 5, 7, 10],
        'blues': [0, 3, 5, 6, 7, 10],
        'chromatic': list(range(12)),
        'whole_tone': [0, 2, 4, 6, 8, 10],
    }
    
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                  'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    @classmethod
    def get_scale_notes(
        cls,
        root: str,
        scale_type: str,
        octave: int = 4
    ) -> List[int]:
        """
        Get MIDI notes for a scale.
        
        Args:
            root: Root note name (e.g., "C", "F#")
            scale_type: Scale type
            octave: Starting octave
        
        Returns:
            List of MIDI note numbers
        """
        root_idx = cls.NOTE_NAMES.index(root) if root in cls.NOTE_NAMES else 0
        root_midi = root_idx + (octave + 1) * 12
        
        intervals = cls.SCALES.get(scale_type, cls.SCALES['major'])
        return [root_midi + interval for interval in intervals]
    
    @classmethod
    def snap_to_scale(
        cls,
        note: int,
        root: str,
        scale_type: str
    ) -> int:
        """
        Snap a note to the nearest scale degree.
        
        Args:
            note: MIDI note number
            root: Root note name
            scale_type: Scale type
        
        Returns:
            Snapped MIDI note number
        """
        root_idx = cls.NOTE_NAMES.index(root) if root in cls.NOTE_NAMES else 0
        intervals = cls.SCALES.get(scale_type, cls.SCALES['major'])
        
        # Get pitch class
        pitch_class = (note - root_idx) % 12
        
        # Find nearest scale degree
        nearest = min(intervals, key=lambda x: min(abs(x - pitch_class), 
                                                   12 - abs(x - pitch_class)))
        
        # Reconstruct note
        octave = (note - root_idx) // 12
        return root_idx + octave * 12 + nearest
    
    @classmethod
    def get_chord_notes(
        cls,
        root: str,
        chord_type: str,
        octave: int = 4
    ) -> List[int]:
        """
        Get MIDI notes for a chord.
        
        Args:
            root: Root note name
            chord_type: Chord type
            octave: Starting octave
        
        Returns:
            List of MIDI note numbers
        """
        CHORD_INTERVALS = {
            'major': [0, 4, 7],
            'minor': [0, 3, 7],
            'dim': [0, 3, 6],
            'aug': [0, 4, 8],
            'sus2': [0, 2, 7],
            'sus4': [0, 5, 7],
            'maj7': [0, 4, 7, 11],
            'min7': [0, 3, 7, 10],
            'dom7': [0, 4, 7, 10],
            '7': [0, 4, 7, 10],
            'dim7': [0, 3, 6, 9],
            'm7b5': [0, 3, 6, 10],
            'add9': [0, 4, 7, 14],
            'add11': [0, 4, 7, 17],
            'power': [0, 7],
            '5': [0, 7],
        }
        
        root_idx = cls.NOTE_NAMES.index(root) if root in cls.NOTE_NAMES else 0
        root_midi = root_idx + (octave + 1) * 12
        
        intervals = CHORD_INTERVALS.get(chord_type, CHORD_INTERVALS['major'])
        return [root_midi + interval for interval in intervals]


# Convenience functions
def analyze_audio(
    audio: np.ndarray,
    sample_rate: int = 48000
) -> AnalysisResult:
    """Quick audio analysis"""
    return AudioAnalyzer().analyze(audio, sample_rate)


def detect_tempo(
    audio: np.ndarray,
    sample_rate: int = 48000
) -> float:
    """Quick tempo detection"""
    result = AudioAnalyzer().analyze(audio, sample_rate, features=["tempo"])
    return result.tempo


def detect_key(
    audio: np.ndarray,
    sample_rate: int = 48000
) -> str:
    """Quick key detection"""
    result = AudioAnalyzer().analyze(audio, sample_rate, features=["key"])
    return f"{result.key} {result.mode}"
