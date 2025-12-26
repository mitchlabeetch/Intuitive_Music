"""Local AI models for music generation and analysis

This module provides interfaces to local AI models that run on the user's computer
without requiring cloud API calls. Privacy-first, cost-free, and offline-capable.
"""
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class MIDINote:
    """MIDI note representation"""
    pitch: int  # 0-127
    velocity: int  # 1-127
    start: float  # seconds
    duration: float  # seconds


@dataclass
class MIDIClip:
    """Container for MIDI notes"""
    name: str
    notes: List[MIDINote]
    
    def __init__(self, name: str = "Untitled"):
        self.name = name
        self.notes = []
    
    def add_note(
        self, 
        pitch: int, 
        velocity: int = 100, 
        start: float = 0.0, 
        duration: float = 0.5
    ) -> None:
        """Add a note to the clip"""
        self.notes.append(MIDINote(
            pitch=pitch,
            velocity=velocity,
            start=start,
            duration=duration
        ))
    
    def get_duration(self) -> float:
        """Get total clip duration"""
        if not self.notes:
            return 0.0
        return max(n.start + n.duration for n in self.notes)


class LocalAI:
    """
    Unified interface to local AI models.
    
    Provides easy access to:
    - Magenta MelodyRNN for melody generation
    - AudioCraft MusicGen for audio generation
    - Basic Pitch for audio-to-MIDI
    - Spleeter for stem separation
    """
    
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or os.path.expanduser("~/.intuitive_daw/models")
        self._melody_rnn = None
        self._musicgen = None
        self._pitch_detector = None
        self._separator = None
        
        # Ensure model directory exists
        os.makedirs(self.model_dir, exist_ok=True)
    
    def generate_melody(
        self,
        seed_notes: List[int],
        length: int = 16,
        temperature: float = 1.0
    ) -> MIDIClip:
        """
        Generate a melody from seed notes using Magenta MelodyRNN.
        
        Args:
            seed_notes: List of MIDI note numbers to seed the generation
            length: Number of notes to generate
            temperature: Randomness (0.0=deterministic, 2.0=very random)
        
        Returns:
            MIDIClip containing generated melody
        """
        if self._melody_rnn is None:
            self._melody_rnn = MagentaMelodyRNN(model_dir=self.model_dir)
        
        return self._melody_rnn.generate_melody(
            seed_notes=seed_notes,
            length=length,
            temperature=temperature
        )
    
    def generate_audio(
        self,
        prompt: str,
        duration: float = 10.0,
        temperature: float = 1.0
    ) -> np.ndarray:
        """
        Generate audio from text prompt using AudioCraft MusicGen.
        
        Args:
            prompt: Text description of desired audio
            duration: Duration in seconds
            temperature: Randomness
        
        Returns:
            Audio array (samples, channels)
        """
        if self._musicgen is None:
            self._musicgen = TextToAudio(model_dir=self.model_dir)
        
        return self._musicgen.generate(
            prompt=prompt,
            duration=duration,
            temperature=temperature
        )
    
    def audio_to_midi(
        self,
        audio: np.ndarray,
        sample_rate: int = 48000
    ) -> MIDIClip:
        """
        Convert audio to MIDI notes using Basic Pitch.
        
        Args:
            audio: Audio data
            sample_rate: Sample rate
        
        Returns:
            MIDIClip containing detected notes
        """
        if self._pitch_detector is None:
            self._pitch_detector = AudioToMIDI(model_dir=self.model_dir)
        
        return self._pitch_detector.convert(audio, sample_rate)
    
    def separate_stems(
        self,
        audio: np.ndarray,
        sample_rate: int = 48000,
        stems: int = 4
    ) -> Dict[str, np.ndarray]:
        """
        Separate audio into stems using Spleeter.
        
        Args:
            audio: Mixed audio data
            sample_rate: Sample rate
            stems: Number of stems (2, 4, or 5)
        
        Returns:
            Dictionary of stem name to audio data
        """
        if self._separator is None:
            self._separator = StemSeparator(model_dir=self.model_dir)
        
        return self._separator.separate(audio, sample_rate, stems)


class MagentaMelodyRNN:
    """
    Melody generation using Google Magenta's MelodyRNN.
    
    Uses LSTM models trained on MIDI data to generate or continue melodies
    with high musical coherence.
    """
    
    AVAILABLE_MODELS = ["basic_rnn", "lookback_rnn", "attention_rnn"]
    
    def __init__(
        self,
        model_name: str = "attention_rnn",
        model_dir: Optional[str] = None,
        quantized: bool = False
    ):
        self.model_name = model_name
        self.model_dir = model_dir or os.path.expanduser("~/.intuitive_daw/models")
        self.quantized = quantized
        self._model = None
        self._loaded = False
    
    def _ensure_loaded(self) -> bool:
        """Ensure model is loaded"""
        if self._loaded:
            return True
        
        try:
            # Try to import Magenta
            import note_seq
            from magenta.models.melody_rnn import melody_rnn_sequence_generator
            
            # Get checkpoint
            bundle_file = os.path.join(
                self.model_dir, 
                f"{self.model_name}.mag"
            )
            
            if os.path.exists(bundle_file):
                bundle = note_seq.sequence_generator_bundle.read_bundle_file(bundle_file)
                self._model = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(bundle)
                self._loaded = True
                logger.info(f"Loaded Magenta model: {self.model_name}")
                return True
            else:
                logger.warning(f"Model file not found: {bundle_file}")
                logger.info("Using fallback Markov generator")
                return False
                
        except ImportError:
            logger.warning("Magenta not installed, using fallback generator")
            return False
    
    def generate_melody(
        self,
        seed_notes: List[int],
        length: int = 16,
        temperature: float = 1.0
    ) -> MIDIClip:
        """
        Generate melody from seed notes.
        
        Args:
            seed_notes: Starting MIDI notes
            length: Number of notes to generate
            temperature: Randomness (higher = more random)
        
        Returns:
            MIDIClip with generated melody
        """
        if self._ensure_loaded():
            return self._generate_with_magenta(seed_notes, length, temperature)
        else:
            return self._generate_with_fallback(seed_notes, length, temperature)
    
    def _generate_with_magenta(
        self,
        seed_notes: List[int],
        length: int,
        temperature: float
    ) -> MIDIClip:
        """Generate using Magenta model"""
        import note_seq
        
        # Create seed sequence
        sequence = note_seq.NoteSequence()
        for i, pitch in enumerate(seed_notes):
            sequence.notes.add(
                pitch=pitch,
                start_time=i * 0.5,
                end_time=(i + 1) * 0.5,
                velocity=80
            )
        sequence.total_time = len(seed_notes) * 0.5
        
        # Generate
        generator_options = {
            'temperature': temperature,
            'beam_size': 1,
            'branch_factor': 1
        }
        
        generated = self._model.generate(
            sequence,
            generate_section_spec=length * 0.5,  # Total time
            **generator_options
        )
        
        # Convert to MIDIClip
        clip = MIDIClip(f"Generated Melody ({self.model_name})")
        for note in generated.notes:
            clip.add_note(
                pitch=note.pitch,
                velocity=note.velocity,
                start=note.start_time,
                duration=note.end_time - note.start_time
            )
        
        return clip
    
    def _generate_with_fallback(
        self,
        seed_notes: List[int],
        length: int,
        temperature: float
    ) -> MIDIClip:
        """
        Fallback generator using simple Markov chain.
        Used when Magenta is not available.
        """
        # Define scale intervals based on last note
        major_intervals = [0, 2, 4, 5, 7, 9, 11]
        
        clip = MIDIClip("Generated Melody (Markov)")
        
        # Add seed notes
        current_time = 0.0
        for note in seed_notes:
            clip.add_note(
                pitch=note,
                velocity=80,
                start=current_time,
                duration=0.5
            )
            current_time += 0.5
        
        # Generate new notes
        current_pitch = seed_notes[-1] if seed_notes else 60
        
        for _ in range(length):
            # Simple Markov-like transition
            # Higher temperature = more random jumps
            step = np.random.choice([-2, -1, 0, 1, 2], p=[0.1, 0.2, 0.4, 0.2, 0.1])
            step = int(step * (1 + temperature * 0.5))
            
            # Apply step and constrain to scale
            new_pitch = current_pitch + step
            new_pitch = max(48, min(84, new_pitch))  # Keep in reasonable range
            
            # Snap to nearest scale note
            root = 60  # C
            octave = (new_pitch - root) // 12
            note_in_octave = (new_pitch - root) % 12
            closest_interval = min(major_intervals, key=lambda x: abs(x - note_in_octave))
            new_pitch = root + octave * 12 + closest_interval
            
            clip.add_note(
                pitch=new_pitch,
                velocity=70 + np.random.randint(-10, 10),
                start=current_time,
                duration=0.5
            )
            
            current_pitch = new_pitch
            current_time += 0.5
        
        return clip


class ChordGenerator:
    """
    Generate chord progressions using rule-based and Markov chain approaches.
    """
    
    # Common progressions by style
    PROGRESSIONS = {
        "pop": [
            ["I", "V", "vi", "IV"],  # The "pop punk" progression
            ["I", "IV", "V", "I"],   # Basic
            ["vi", "IV", "I", "V"],  # Axis of Awesome
        ],
        "jazz": [
            ["ii7", "V7", "Imaj7"],  # ii-V-I
            ["Imaj7", "vi7", "ii7", "V7"],  # Rhythm changes
        ],
        "rock": [
            ["I", "IV", "V", "V"],
            ["I", "bVII", "IV", "I"],
        ],
        "classical": [
            ["I", "IV", "V", "I"],
            ["I", "vi", "IV", "V"],
        ],
        "ambient": [
            ["Imaj7", "IVmaj7", "Imaj7", "Vmaj7"],
            ["i", "VI", "III", "VII"],
        ]
    }
    
    # Roman numeral to semitone offset (major key)
    ROMAN_TO_SEMITONE = {
        "I": 0, "i": 0,
        "bII": 1, "II": 2, "ii": 2,
        "bIII": 3, "III": 4, "iii": 4,
        "IV": 5, "iv": 5,
        "bV": 6, "V": 7, "v": 7,
        "bVI": 8, "VI": 9, "vi": 9,
        "bVII": 10, "VII": 11, "vii": 11,
    }
    
    NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    def __init__(self):
        self.name = "Chord Generator"
    
    def suggest_progression(
        self,
        key: str = "C major",
        length: int = 4,
        style: str = "pop"
    ) -> List[str]:
        """
        Suggest a chord progression.
        
        Args:
            key: Musical key (e.g., "C major", "A minor")
            length: Number of chords
            style: Musical style
        
        Returns:
            List of chord symbols
        """
        # Parse key
        parts = key.split()
        root = parts[0] if parts else "C"
        mode = parts[1] if len(parts) > 1 else "major"
        
        # Get root note number
        root_num = self.NOTE_NAMES.index(root) if root in self.NOTE_NAMES else 0
        
        # Get progression template
        templates = self.PROGRESSIONS.get(style, self.PROGRESSIONS["pop"])
        template = templates[np.random.randint(len(templates))]
        
        # Adjust template length
        if len(template) < length:
            template = template * (length // len(template) + 1)
        template = template[:length]
        
        # Convert Roman numerals to chord symbols
        chords = []
        for numeral in template:
            # Extract base numeral and modifiers
            base = numeral.rstrip("7maj")
            modifier = numeral[len(base):]
            
            # Get semitone offset
            offset = self.ROMAN_TO_SEMITONE.get(base, 0)
            
            # Calculate chord root
            chord_root_num = (root_num + offset) % 12
            chord_root = self.NOTE_NAMES[chord_root_num]
            
            # Determine chord type
            if base.islower():
                chord_type = "m"  # Minor
            else:
                chord_type = ""  # Major
            
            # Add modifiers
            chord = f"{chord_root}{chord_type}{modifier}"
            chords.append(chord)
        
        return chords


class RhythmGenerator:
    """
    Generate rhythmic patterns using cellular automata and Euclidean algorithms.
    """
    
    def __init__(self):
        self.name = "Rhythm Generator"
    
    def euclidean(self, length: int, hits: int, rotation: int = 0) -> List[int]:
        """
        Generate Euclidean rhythm (evenly distributed hits).
        
        Args:
            length: Total number of steps
            hits: Number of hits to distribute
            rotation: Rotate pattern by N steps
        
        Returns:
            List of 0s and 1s representing the pattern
        """
        if hits >= length:
            return [1] * length
        if hits == 0:
            return [0] * length
        
        # Bjorklund's algorithm
        groups = [[1]] * hits + [[0]] * (length - hits)
        
        while len(set(len(g) for g in groups)) > 1 and len(groups) > 1:
            # Sort by length descending
            groups.sort(key=len, reverse=True)
            
            # Combine shortest with longest
            while len(groups) > 1:
                shortest = groups.pop()
                groups[0].extend(shortest)
                if len(groups) <= 1 or len(groups[0]) != len(groups[-1]):
                    break
        
        # Flatten
        pattern = [item for group in groups for item in group]
        
        # Rotate
        if rotation:
            pattern = pattern[rotation:] + pattern[:rotation]
        
        return pattern
    
    def cellular_automaton(
        self,
        rule: int = 30,
        steps: int = 16,
        initial_state: Optional[List[int]] = None
    ) -> List[int]:
        """
        Generate rhythm using 1D cellular automaton.
        
        Args:
            rule: Rule number (0-255)
            steps: Number of steps to generate
            initial_state: Starting state (default: single 1 in center)
        
        Returns:
            List of 0s and 1s
        """
        width = steps
        
        # Initialize state
        if initial_state is None:
            state = [0] * width
            state[width // 2] = 1
        else:
            state = initial_state[:width]
            state.extend([0] * (width - len(state)))
        
        # Convert rule to binary lookup
        rule_binary = [(rule >> i) & 1 for i in range(8)]
        
        # Generate next generation
        for _ in range(3):  # Evolve a few generations
            new_state = []
            for i in range(width):
                left = state[(i - 1) % width]
                center = state[i]
                right = state[(i + 1) % width]
                neighborhood = (left << 2) | (center << 1) | right
                new_state.append(rule_binary[neighborhood])
            state = new_state
        
        return state
    
    def generate_pattern(
        self,
        length: int = 16,
        density: float = 0.5,
        algorithm: str = "euclidean"
    ) -> MIDIClip:
        """
        Generate a rhythm pattern as MIDI.
        
        Args:
            length: Pattern length in steps
            density: Hit density (0.0-1.0)
            algorithm: "euclidean" or "cellular"
        
        Returns:
            MIDIClip with rhythm pattern
        """
        hits = int(length * density)
        
        if algorithm == "euclidean":
            pattern = self.euclidean(length, hits)
        else:
            pattern = self.cellular_automaton(30, length)
        
        clip = MIDIClip(f"Rhythm ({algorithm})")
        step_duration = 0.25  # 16th notes at 120 BPM
        
        for step, hit in enumerate(pattern):
            if hit:
                clip.add_note(
                    pitch=36,  # Kick drum
                    velocity=100,
                    start=step * step_duration,
                    duration=step_duration * 0.9
                )
        
        return clip


class TextToAudio:
    """
    Generate audio from text descriptions using AudioCraft MusicGen.
    """
    
    def __init__(
        self,
        model_name: str = "small",
        model_dir: Optional[str] = None
    ):
        self.model_name = model_name
        self.model_dir = model_dir
        self._model = None
        self._loaded = False
    
    def _ensure_loaded(self) -> bool:
        """Ensure model is loaded"""
        if self._loaded:
            return True
        
        try:
            from audiocraft.models import MusicGen
            
            self._model = MusicGen.get_pretrained(self.model_name)
            self._loaded = True
            logger.info(f"Loaded MusicGen model: {self.model_name}")
            return True
            
        except ImportError:
            logger.warning("AudioCraft not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to load MusicGen: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        duration: float = 10.0,
        temperature: float = 1.0
    ) -> np.ndarray:
        """
        Generate audio from text prompt.
        
        Args:
            prompt: Text description
            duration: Audio duration in seconds
            temperature: Randomness
        
        Returns:
            Audio data as numpy array
        """
        if not self._ensure_loaded():
            # Return silence if model not available
            logger.warning("MusicGen not available, returning silence")
            return np.zeros((int(duration * 32000), 2))
        
        # Set generation parameters
        self._model.set_generation_params(
            duration=duration,
            temperature=temperature
        )
        
        # Generate
        wav = self._model.generate([prompt])
        
        # Convert to numpy
        audio = wav[0].cpu().numpy()
        
        # Ensure stereo
        if audio.ndim == 1:
            audio = np.column_stack([audio, audio])
        elif audio.shape[0] < audio.shape[1]:
            audio = audio.T
        
        return audio


class AudioToMIDI:
    """
    Convert audio to MIDI using Spotify's Basic Pitch.
    """
    
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir
        self._model = None
        self._loaded = False
    
    def _ensure_loaded(self) -> bool:
        """Ensure model is loaded"""
        if self._loaded:
            return True
        
        try:
            import basic_pitch
            from basic_pitch.inference import predict
            
            self._predict = predict
            self._loaded = True
            logger.info("Loaded Basic Pitch model")
            return True
            
        except ImportError:
            logger.warning("basic-pitch not installed")
            return False
    
    def convert(
        self,
        audio: np.ndarray,
        sample_rate: int = 48000
    ) -> MIDIClip:
        """
        Convert audio to MIDI notes.
        
        Args:
            audio: Audio data
            sample_rate: Sample rate
        
        Returns:
            MIDIClip with detected notes
        """
        clip = MIDIClip("Audio to MIDI")
        
        if not self._ensure_loaded():
            logger.warning("Basic Pitch not available")
            return clip
        
        # Convert to mono if stereo
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=1)
        else:
            audio_mono = audio
        
        # Run prediction
        model_output, midi_data, note_events = self._predict(
            audio_mono,
            sample_rate
        )
        
        # Convert note events to MIDIClip
        for note in note_events:
            clip.add_note(
                pitch=int(note.pitch),
                velocity=int(note.velocity * 127),
                start=float(note.start_time),
                duration=float(note.end_time - note.start_time)
            )
        
        return clip


class StemSeparator:
    """
    Separate audio into stems using Spleeter.
    """
    
    STEM_CONFIGS = {
        2: ["vocals", "accompaniment"],
        4: ["vocals", "drums", "bass", "other"],
        5: ["vocals", "drums", "bass", "piano", "other"],
    }
    
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir
        self._separator = None
        self._loaded_stems = None
    
    def _ensure_loaded(self, stems: int) -> bool:
        """Ensure separator is loaded"""
        if self._separator is not None and self._loaded_stems == stems:
            return True
        
        try:
            from spleeter.separator import Separator
            
            self._separator = Separator(f"spleeter:{stems}stems")
            self._loaded_stems = stems
            logger.info(f"Loaded Spleeter {stems}-stem model")
            return True
            
        except ImportError:
            logger.warning("Spleeter not installed")
            return False
    
    def separate(
        self,
        audio: np.ndarray,
        sample_rate: int = 48000,
        stems: int = 4
    ) -> Dict[str, np.ndarray]:
        """
        Separate audio into stems.
        
        Args:
            audio: Mixed audio
            sample_rate: Sample rate
            stems: Number of stems (2, 4, or 5)
        
        Returns:
            Dictionary of stem name to audio data
        """
        result = {}
        stem_names = self.STEM_CONFIGS.get(stems, self.STEM_CONFIGS[4])
        
        if not self._ensure_loaded(stems):
            # Return original audio in all stems
            for name in stem_names:
                result[name] = audio.copy()
            return result
        
        # Ensure stereo
        if audio.ndim == 1:
            audio = np.column_stack([audio, audio])
        
        # Run separation
        prediction = self._separator.separate({
            'waveform': audio,
            'sample_rate': sample_rate
        })
        
        # Extract stems
        for name in stem_names:
            if name in prediction:
                result[name] = prediction[name]
            else:
                result[name] = np.zeros_like(audio)
        
        return result


class AudioAnalyzer:
    """
    Analyze audio for features like tempo, key, and spectral content.
    Uses librosa if available, otherwise falls back to basic analysis.
    """
    
    def __init__(self):
        self._librosa_available = False
        try:
            import librosa
            self._librosa = librosa
            self._librosa_available = True
        except ImportError:
            logger.warning("librosa not installed, using basic analysis")
    
    def analyze(
        self,
        audio: np.ndarray,
        sample_rate: int = 48000
    ) -> Dict[str, Any]:
        """
        Analyze audio and return features.
        
        Args:
            audio: Audio data
            sample_rate: Sample rate
        
        Returns:
            Dictionary of analysis results
        """
        # Convert to mono
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=1)
        else:
            audio_mono = audio
        
        if self._librosa_available:
            return self._analyze_with_librosa(audio_mono, sample_rate)
        else:
            return self._analyze_basic(audio_mono, sample_rate)
    
    def _analyze_with_librosa(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> Dict[str, Any]:
        """Full analysis using librosa"""
        # Tempo
        tempo, _ = self._librosa.beat.beat_track(y=audio, sr=sample_rate)
        
        # Key detection using chroma
        chroma = self._librosa.feature.chroma_cqt(y=audio, sr=sample_rate)
        key_index = np.argmax(np.mean(chroma, axis=1))
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Spectral features
        spectral_centroid = np.mean(
            self._librosa.feature.spectral_centroid(y=audio, sr=sample_rate)
        )
        spectral_rolloff = np.mean(
            self._librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)
        )
        
        # RMS energy
        rms = np.mean(self._librosa.feature.rms(y=audio))
        
        return {
            "tempo": float(tempo),
            "key": keys[key_index],
            "duration": len(audio) / sample_rate,
            "spectral_centroid": float(spectral_centroid),
            "spectral_rolloff": float(spectral_rolloff),
            "rms": float(rms),
        }
    
    def _analyze_basic(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> Dict[str, Any]:
        """Basic analysis without librosa"""
        from scipy import signal
        
        # Simple tempo estimation via autocorrelation
        onset_env = np.abs(np.diff(audio))
        autocorr = np.correlate(onset_env, onset_env, mode='same')
        peaks, _ = signal.find_peaks(autocorr, distance=sample_rate // 4)
        
        if len(peaks) >= 2:
            avg_period = np.mean(np.diff(peaks)) / sample_rate
            tempo = 60.0 / avg_period if avg_period > 0 else 120.0
            tempo = max(60, min(200, tempo))  # Constrain
        else:
            tempo = 120.0
        
        # RMS
        rms = np.sqrt(np.mean(audio ** 2))
        
        return {
            "tempo": float(tempo),
            "key": "C",  # Default, no key detection without librosa
            "duration": len(audio) / sample_rate,
            "spectral_centroid": 0.0,
            "spectral_rolloff": 0.0,
            "rms": float(rms),
        }


# Quick access functions
def generate_melody(
    seed_notes: List[int],
    length: int = 16,
    temperature: float = 1.0
) -> MIDIClip:
    """Quick access to melody generation"""
    return MagentaMelodyRNN().generate_melody(seed_notes, length, temperature)


def generate_chords(
    key: str = "C major",
    length: int = 4,
    style: str = "pop"
) -> List[str]:
    """Quick access to chord generation"""
    return ChordGenerator().suggest_progression(key, length, style)


def generate_rhythm(
    length: int = 16,
    hits: int = 4
) -> List[int]:
    """Quick access to rhythm generation"""
    return RhythmGenerator().euclidean(length, hits)
