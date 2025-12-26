"""
INTUITIVES DAW - AI Music Models

Neural network-based music generation integrating:
- Magenta (MelodyRNN, MusicVAE, GrooVAE)
- AudioCraft (MusicGen for text-to-music)
- Spleeter (Stem separation)
- RAVE (Real-time neural audio)

These are OPTIONAL dependencies - the DAW works without them,
but they enable powerful AI features when available.

Usage:
    from intlib.ai_models import MelodyRNN, StemSeparator, TextToMusic
    
    # Generate melody continuation
    rnn = MelodyRNN()
    notes = rnn.continue_melody(seed_notes, num_steps=32)
    
    # Separate stems
    separator = StemSeparator()
    stems = separator.separate('song.mp3')
    
    # Text to music
    generator = TextToMusic()
    audio = generator.generate("upbeat electronic with synth lead")
"""

import os
import sys
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import tempfile

# =============================================================================
# FEATURE FLAGS - Check available models
# =============================================================================

MAGENTA_AVAILABLE = False
AUDIOCRAFT_AVAILABLE = False
SPLEETER_AVAILABLE = False
RAVE_AVAILABLE = False
BASIC_PITCH_AVAILABLE = False

try:
    from note_seq import midi_io, music_pb2
    from note_seq.protobuf import generator_pb2
    MAGENTA_AVAILABLE = True
except ImportError:
    pass

try:
    from audiocraft.models import MusicGen
    AUDIOCRAFT_AVAILABLE = True
except ImportError:
    pass

try:
    from spleeter.separator import Separator
    SPLEETER_AVAILABLE = True
except ImportError:
    pass

try:
    import torch
    # RAVE requires torch
    RAVE_AVAILABLE = torch.cuda.is_available() or True  # CPU works too
except ImportError:
    pass

try:
    import basic_pitch
    BASIC_PITCH_AVAILABLE = True
except ImportError:
    pass


def get_available_models() -> Dict[str, bool]:
    """Return dict of available AI models"""
    return {
        'magenta': MAGENTA_AVAILABLE,
        'audiocraft': AUDIOCRAFT_AVAILABLE,
        'spleeter': SPLEETER_AVAILABLE,
        'rave': RAVE_AVAILABLE,
        'basic_pitch': BASIC_PITCH_AVAILABLE,
    }


# =============================================================================
# MELODY RNN (from Magenta)
# =============================================================================

class MelodyRNN:
    """
    Neural network melody generation using Magenta's MelodyRNN.
    
    Generates melodies note-by-note using an LSTM trained on
    thousands of MIDI files.
    
    Example:
        rnn = MelodyRNN()
        
        # Generate from scratch
        melody = rnn.generate(num_steps=64, temperature=1.0)
        
        # Continue from seed
        seed = [60, 62, 64, 65, 67]  # C D E F G
        continuation = rnn.continue_melody(seed, num_steps=32)
    """
    
    def __init__(self, model_name: str = 'attention_rnn'):
        """
        Initialize MelodyRNN.
        
        model_name: 'basic_rnn', 'lookback_rnn', 'attention_rnn'
        """
        self.model_name = model_name
        self._model = None
        self._initialized = False
        
        if not MAGENTA_AVAILABLE:
            print("Warning: Magenta not available. Using fallback generator.")
    
    def _ensure_initialized(self):
        """Lazy initialization of model"""
        if self._initialized:
            return
        
        if not MAGENTA_AVAILABLE:
            self._initialized = True
            return
        
        try:
            from magenta.models.melody_rnn import melody_rnn_sequence_generator
            from magenta.models.shared import sequence_generator_bundle
            
            # Load pre-trained model
            bundle_file = f'{self.model_name}.mag'
            
            # Try to find bundle
            bundle = sequence_generator_bundle.read_bundle_file(bundle_file)
            self._model = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(
                bundle=bundle
            )
            self._initialized = True
            
        except Exception as e:
            print(f"Could not load MelodyRNN model: {e}")
            self._initialized = True
    
    def generate(
        self,
        num_steps: int = 64,
        temperature: float = 1.0,
        primer_melody: Optional[List[int]] = None,
        qpm: float = 120.0
    ) -> List[Dict[str, Any]]:
        """
        Generate a melody.
        
        Returns list of note events with 'note', 'velocity', 'start', 'duration'.
        """
        self._ensure_initialized()
        
        if self._model and MAGENTA_AVAILABLE:
            return self._generate_with_magenta(
                num_steps, temperature, primer_melody, qpm
            )
        else:
            return self._generate_fallback(
                num_steps, temperature, primer_melody, qpm
            )
    
    def continue_melody(
        self,
        seed_notes: List[int],
        num_steps: int = 32,
        temperature: float = 1.0
    ) -> List[Dict[str, Any]]:
        """Continue from a seed melody"""
        return self.generate(
            num_steps=num_steps,
            temperature=temperature,
            primer_melody=seed_notes
        )
    
    def _generate_with_magenta(
        self,
        num_steps: int,
        temperature: float,
        primer_melody: Optional[List[int]],
        qpm: float
    ) -> List[Dict[str, Any]]:
        """Generate using actual Magenta model"""
        from note_seq.protobuf import generator_pb2
        from note_seq import sequences_lib
        
        # Create primer sequence
        if primer_melody:
            primer_sequence = music_pb2.NoteSequence()
            primer_sequence.tempos.add(qpm=qpm)
            
            for i, note in enumerate(primer_melody):
                primer_sequence.notes.add(
                    pitch=note,
                    velocity=80,
                    start_time=i * 0.5,
                    end_time=(i + 1) * 0.5 - 0.1
                )
            primer_sequence.total_time = len(primer_melody) * 0.5
        else:
            primer_sequence = None
        
        # Generate
        generator_options = generator_pb2.GeneratorOptions()
        generator_options.args['temperature'].float_value = temperature
        
        if primer_sequence:
            generator_options.generate_sections.add(
                start_time=primer_sequence.total_time,
                end_time=primer_sequence.total_time + num_steps * 0.5
            )
        else:
            generator_options.generate_sections.add(
                start_time=0,
                end_time=num_steps * 0.5
            )
        
        generated = self._model.generate(primer_sequence, generator_options)
        
        # Convert to our format
        notes = []
        for note in generated.notes:
            notes.append({
                'note': note.pitch,
                'velocity': note.velocity,
                'start': note.start_time,
                'duration': note.end_time - note.start_time,
            })
        
        return notes
    
    def _generate_fallback(
        self,
        num_steps: int,
        temperature: float,
        primer_melody: Optional[List[int]],
        qpm: float
    ) -> List[Dict[str, Any]]:
        """Fallback generation without Magenta (Markov chain)"""
        from intlib.integrations import AIGenerator
        
        gen = AIGenerator()
        bars = max(1, num_steps // 16)
        
        if primer_melody:
            # Use primer to influence generation
            root = primer_melody[0] if primer_melody else 60
            scale = 'pentatonic'
            
            # Detect scale from primer
            intervals = set()
            for note in primer_melody:
                intervals.add((note - root) % 12)
            
            if intervals <= {0, 2, 4, 5, 7, 9, 11}:
                scale = 'major'
            elif intervals <= {0, 2, 3, 5, 7, 8, 10}:
                scale = 'minor'
        else:
            root = 60
            scale = 'pentatonic'
        
        return gen.generate_melody(
            num_bars=bars,
            notes_per_bar=4,
            root=root,
            scale=scale,
            temperature=temperature,
            style='markov'
        )


# =============================================================================
# STEM SEPARATOR (from Spleeter/Demucs)
# =============================================================================

class StemSeparator:
    """
    Separate audio into stems (vocals, drums, bass, other).
    
    Uses Spleeter (Deezer) or Demucs (Facebook) when available.
    
    Example:
        separator = StemSeparator()
        stems = separator.separate('song.mp3')
        
        # Access individual stems
        vocals = stems['vocals']
        drums = stems['drums']
        bass = stems['bass']
        other = stems['other']
    """
    
    def __init__(self, num_stems: int = 4):
        """
        Initialize separator.
        
        num_stems: 2 (vocals/accompaniment) or 4 (vocals/drums/bass/other)
                   or 5 (adds piano)
        """
        self.num_stems = num_stems
        self._separator = None
        
        if not SPLEETER_AVAILABLE:
            print("Warning: Spleeter not available. Stem separation disabled.")
    
    def separate(
        self,
        audio_path: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, np.ndarray]:
        """
        Separate audio file into stems.
        
        Returns dict of stem_name -> audio_array
        """
        if not SPLEETER_AVAILABLE:
            print("Spleeter not installed. Run: pip install spleeter")
            return {}
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Create output directory
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
        # Initialize separator
        if self._separator is None:
            model = f'spleeter:{self.num_stems}stems'
            self._separator = Separator(model)
        
        # Separate
        self._separator.separate_to_file(
            audio_path,
            output_dir,
            codec='wav'
        )
        
        # Load results
        stems = {}
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        stem_dir = os.path.join(output_dir, base_name)
        
        stem_names = ['vocals', 'drums', 'bass', 'other', 'piano'][:self.num_stems]
        if self.num_stems == 2:
            stem_names = ['vocals', 'accompaniment']
        
        for stem_name in stem_names:
            stem_path = os.path.join(stem_dir, f'{stem_name}.wav')
            if os.path.exists(stem_path):
                try:
                    import librosa
                    stems[stem_name], _ = librosa.load(stem_path, sr=44100)
                except ImportError:
                    # Use scipy if librosa not available
                    from scipy.io import wavfile
                    sr, audio = wavfile.read(stem_path)
                    stems[stem_name] = audio.astype(np.float32) / 32768.0
        
        return stems
    
    def isolate_vocals(self, audio_path: str) -> np.ndarray:
        """Quick helper to just get vocals"""
        stems = self.separate(audio_path)
        return stems.get('vocals', np.array([]))
    
    def remove_vocals(self, audio_path: str) -> np.ndarray:
        """Quick helper to get instrumental (no vocals)"""
        stems = self.separate(audio_path)
        
        # Sum non-vocal stems
        non_vocal = None
        for name, audio in stems.items():
            if name != 'vocals':
                if non_vocal is None:
                    non_vocal = audio.copy()
                else:
                    min_len = min(len(non_vocal), len(audio))
                    non_vocal[:min_len] += audio[:min_len]
        
        return non_vocal if non_vocal is not None else np.array([])


# =============================================================================
# TEXT TO MUSIC (from AudioCraft/MusicGen)
# =============================================================================

class TextToMusic:
    """
    Generate music from text descriptions using Meta's AudioCraft.
    
    This is the MOST EXPERIMENTAL feature - generates audio directly
    from text prompts like "upbeat electronic dance music".
    
    Example:
        generator = TextToMusic()
        
        # Generate 10 seconds of music
        audio = generator.generate(
            prompt="chill lofi hip hop beat with piano",
            duration=10.0
        )
    """
    
    MODEL_SIZES = ['small', 'medium', 'large', 'melody']
    
    def __init__(self, model_size: str = 'small'):
        """
        Initialize TextToMusic.
        
        model_size: 'small' (300M), 'medium' (1.5B), 'large' (3.3B), 'melody'
        """
        self.model_size = model_size
        self._model = None
        
        if not AUDIOCRAFT_AVAILABLE:
            print("Warning: AudioCraft not available.")
            print("Install with: pip install audiocraft")
    
    def _ensure_loaded(self):
        """Lazy load model"""
        if self._model is not None:
            return True
        
        if not AUDIOCRAFT_AVAILABLE:
            return False
        
        try:
            self._model = MusicGen.get_pretrained(self.model_size)
            self._model.set_generation_params(duration=10)
            return True
        except Exception as e:
            print(f"Could not load MusicGen model: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        duration: float = 10.0,
        temperature: float = 1.0,
        top_k: int = 250
    ) -> Optional[np.ndarray]:
        """
        Generate music from text prompt.
        
        prompt: Text description of desired music
        duration: Length in seconds (max 30 with small model)
        
        Returns numpy array of audio samples (32kHz)
        """
        if not self._ensure_loaded():
            print("TextToMusic not available.")
            return self._generate_fallback(prompt, duration)
        
        try:
            self._model.set_generation_params(
                duration=min(duration, 30),
                temperature=temperature,
                top_k=top_k
            )
            
            # Generate
            wav = self._model.generate([prompt])
            
            # Convert to numpy
            audio = wav[0, 0].cpu().numpy()
            return audio
            
        except Exception as e:
            print(f"Generation failed: {e}")
            return None
    
    def generate_continuation(
        self,
        audio: np.ndarray,
        prompt: str,
        duration: float = 10.0
    ) -> Optional[np.ndarray]:
        """Continue from existing audio with text prompt guidance"""
        if not self._ensure_loaded():
            return None
        
        if self.model_size != 'melody':
            print("Continuation requires 'melody' model")
            return None
        
        try:
            import torch
            
            self._model.set_generation_params(duration=duration)
            
            # Convert to tensor
            audio_tensor = torch.from_numpy(audio).unsqueeze(0).unsqueeze(0)
            
            # Generate continuation
            wav = self._model.generate_continuation(audio_tensor, [prompt])
            
            return wav[0, 0].cpu().numpy()
            
        except Exception as e:
            print(f"Continuation failed: {e}")
            return None
    
    def _generate_fallback(
        self,
        prompt: str,
        duration: float
    ) -> np.ndarray:
        """Fallback when AudioCraft not available - generate simple tone"""
        print("Generating fallback audio (AudioCraft not installed)")
        
        sr = 44100
        num_samples = int(duration * sr)
        
        # Parse prompt for simple keywords
        prompt_lower = prompt.lower()
        
        # Base frequency from mood keywords
        if any(w in prompt_lower for w in ['happy', 'upbeat', 'bright']):
            base_freq = 440.0  # A4
        elif any(w in prompt_lower for w in ['sad', 'dark', 'minor']):
            base_freq = 392.0  # G4
        else:
            base_freq = 261.63  # C4
        
        # Generate simple ambient texture
        t = np.linspace(0, duration, num_samples)
        
        # Multiple detuned oscillators
        audio = np.zeros(num_samples)
        
        for i, mult in enumerate([1.0, 1.5, 2.0, 0.5]):
            freq = base_freq * mult * (1 + 0.01 * np.sin(2 * np.pi * 0.1 * t))
            phase = np.cumsum(2 * np.pi * freq / sr)
            audio += 0.25 * np.sin(phase) * np.exp(-t * 0.5)
        
        # Apply envelope
        attack = int(0.1 * sr)
        release = int(0.5 * sr)
        envelope = np.ones(num_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        audio *= envelope
        
        # Normalize
        audio = audio / np.max(np.abs(audio)) * 0.8
        
        return audio


# =============================================================================
# AUDIO TO MIDI (from basic-pitch/Spotify)
# =============================================================================

class AudioToMIDI:
    """
    Convert audio to MIDI notes using Spotify's basic-pitch.
    
    This is perfect for the experiment-first philosophy - 
    record anything and get notes!
    
    Example:
        converter = AudioToMIDI()
        notes = converter.transcribe('recording.wav')
        
        # notes is a list of {'note': 60, 'start': 0.0, 'end': 0.5, 'velocity': 80}
    """
    
    def __init__(self):
        if not BASIC_PITCH_AVAILABLE:
            print("Warning: basic-pitch not available.")
            print("Install with: pip install basic-pitch")
    
    def transcribe(
        self,
        audio_path: str,
        onset_threshold: float = 0.5,
        frame_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Transcribe audio file to MIDI notes.
        
        Returns list of note events with pitch, start, end, velocity.
        """
        if not BASIC_PITCH_AVAILABLE:
            return self._transcribe_fallback(audio_path)
        
        try:
            from basic_pitch.inference import predict
            from basic_pitch import ICASSP_2022_MODEL_PATH
            
            # Run inference
            model_output, midi_data, note_events = predict(
                audio_path,
                onset_threshold=onset_threshold,
                frame_threshold=frame_threshold,
            )
            
            # Convert note events to our format
            notes = []
            for note in note_events:
                notes.append({
                    'note': int(note[2]),
                    'start': float(note[0]),
                    'end': float(note[1]),
                    'duration': float(note[1] - note[0]),
                    'velocity': int(note[3] * 127),
                })
            
            return notes
            
        except Exception as e:
            print(f"Transcription failed: {e}")
            return []
    
    def transcribe_array(
        self,
        audio: np.ndarray,
        sample_rate: int = 44100
    ) -> List[Dict[str, Any]]:
        """Transcribe audio array directly"""
        if not BASIC_PITCH_AVAILABLE:
            return self._transcribe_fallback_array(audio, sample_rate)
        
        try:
            from basic_pitch.inference import predict
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_path = f.name
                
                from scipy.io import wavfile
                wavfile.write(temp_path, sample_rate, 
                             (audio * 32767).astype(np.int16))
            
            notes = self.transcribe(temp_path)
            
            os.unlink(temp_path)
            return notes
            
        except Exception as e:
            print(f"Transcription failed: {e}")
            return []
    
    def _transcribe_fallback(self, audio_path: str) -> List[Dict[str, Any]]:
        """Fallback using simple pitch detection"""
        try:
            import librosa
            audio, sr = librosa.load(audio_path)
        except:
            return []
        
        return self._transcribe_fallback_array(audio, sr)
    
    def _transcribe_fallback_array(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> List[Dict[str, Any]]:
        """Simple pitch detection fallback"""
        from intlib.integrations import AudioAnalyzer
        
        analyzer = AudioAnalyzer(sample_rate=sample_rate)
        
        # Split into frames
        frame_size = int(0.1 * sample_rate)  # 100ms frames
        hop = frame_size // 2
        
        notes = []
        current_note = None
        current_start = None
        
        for i in range(0, len(audio) - frame_size, hop):
            frame = audio[i:i + frame_size]
            freq, conf = analyzer.detect_pitch(frame)
            
            time = i / sample_rate
            
            if freq > 50 and conf > 0.5:
                # Convert frequency to MIDI
                midi_note = int(round(69 + 12 * np.log2(freq / 440)))
                
                if current_note is None:
                    # Start new note
                    current_note = midi_note
                    current_start = time
                elif abs(midi_note - current_note) > 1:
                    # Note changed
                    notes.append({
                        'note': current_note,
                        'start': current_start,
                        'end': time,
                        'duration': time - current_start,
                        'velocity': 80,
                    })
                    current_note = midi_note
                    current_start = time
            else:
                # Silence - end current note
                if current_note is not None:
                    notes.append({
                        'note': current_note,
                        'start': current_start,
                        'end': time,
                        'duration': time - current_start,
                        'velocity': 80,
                    })
                    current_note = None
        
        return notes


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def quick_generate_from_text(prompt: str, duration: float = 10.0) -> np.ndarray:
    """One-liner text to music"""
    generator = TextToMusic()
    return generator.generate(prompt, duration)


def quick_separate_stems(audio_path: str) -> Dict[str, np.ndarray]:
    """One-liner stem separation"""
    separator = StemSeparator()
    return separator.separate(audio_path)


def quick_transcribe(audio_path: str) -> List[Dict[str, Any]]:
    """One-liner audio to MIDI"""
    converter = AudioToMIDI()
    return converter.transcribe(audio_path)


def quick_continue_melody(seed: List[int], num_steps: int = 32) -> List[Dict[str, Any]]:
    """One-liner melody continuation"""
    rnn = MelodyRNN()
    return rnn.continue_melody(seed, num_steps)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Classes
    'MelodyRNN',
    'StemSeparator',
    'TextToMusic',
    'AudioToMIDI',
    
    # Quick functions
    'quick_generate_from_text',
    'quick_separate_stems',
    'quick_transcribe',
    'quick_continue_melody',
    
    # Utility
    'get_available_models',
    
    # Feature flags
    'MAGENTA_AVAILABLE',
    'AUDIOCRAFT_AVAILABLE',
    'SPLEETER_AVAILABLE',
    'RAVE_AVAILABLE',
    'BASIC_PITCH_AVAILABLE',
]
