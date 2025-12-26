"""Image-to-Sound Processor for Intuitives DAW

Converts images to audio using various mapping strategies:
- Pixel brightness to amplitude
- Color hue to frequency
- Image rows as spectral frames
- Chromasynesthesia-inspired color-to-harmony mapping
"""
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
import math
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import image libraries
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.warning("PIL not available: pip install Pillow")

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.warning("NumPy not available: pip install numpy")


@dataclass
class ImageToSoundConfig:
    """Configuration for image-to-sound conversion"""
    # Frequency mapping
    min_freq: float = 80.0       # Lowest frequency (Hz)
    max_freq: float = 8000.0     # Highest frequency (Hz)
    
    # Time mapping
    duration: float = 10.0       # Total duration (seconds)
    sample_rate: int = 44100     # Output sample rate
    
    # Mapping mode
    mode: str = "spectral"       # spectral, melodic, harmonic, drone
    
    # Image processing
    width: int = 256             # Resample width
    height: int = 128            # Resample height (frequency bins)
    
    # Synthesis
    num_oscillators: int = 32    # Number of simultaneous oscillators
    attack: float = 0.01         # Attack time (seconds)
    release: float = 0.05        # Release time (seconds)


@dataclass
class SynthNote:
    """A synthesized note from image data"""
    frequency: float
    amplitude: float
    start_time: float
    duration: float
    color: Tuple[int, int, int]  # Original RGB


class ChromaSynesthesia:
    """
    Maps colors to musical elements using synesthesia-inspired mappings.
    
    Color wheel mapping:
    - Red (0°): C
    - Orange (30°): D
    - Yellow (60°): E
    - Green (120°): G
    - Cyan (180°): A
    - Blue (240°): C (octave)
    - Purple (270°): D (octave)
    - Magenta (300°): E (octave)
    """
    
    # Hue to note mapping (chromatic scale)
    HUE_TO_NOTE = {
        0: 0,    # Red -> C
        30: 2,   # Orange -> D
        60: 4,   # Yellow -> E
        90: 5,   # Yellow-Green -> F
        120: 7,  # Green -> G
        150: 9,  # Cyan-Green -> A
        180: 11, # Cyan -> B
        210: 12, # Cyan-Blue -> C+
        240: 14, # Blue -> D+
        270: 16, # Purple -> E+
        300: 17, # Magenta -> F+
        330: 19, # Red-Magenta -> G+
    }
    
    @staticmethod
    def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Convert RGB (0-255) to HSL (0-360, 0-1, 0-1)"""
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0
        
        max_c = max(r_norm, g_norm, b_norm)
        min_c = min(r_norm, g_norm, b_norm)
        l = (max_c + min_c) / 2.0
        
        if max_c == min_c:
            h = s = 0.0
        else:
            d = max_c - min_c
            s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
            
            if max_c == r_norm:
                h = (g_norm - b_norm) / d + (6.0 if g_norm < b_norm else 0.0)
            elif max_c == g_norm:
                h = (b_norm - r_norm) / d + 2.0
            else:
                h = (r_norm - g_norm) / d + 4.0
            
            h *= 60.0
        
        return (h, s, l)
    
    @classmethod
    def color_to_note(cls, r: int, g: int, b: int, base_note: int = 60) -> int:
        """Convert RGB color to MIDI note number"""
        h, s, l = cls.rgb_to_hsl(r, g, b)
        
        # Find closest hue in mapping
        hue_keys = sorted(cls.HUE_TO_NOTE.keys())
        closest_hue = min(hue_keys, key=lambda x: min(abs(x - h), 360 - abs(x - h)))
        
        note_offset = cls.HUE_TO_NOTE[closest_hue]
        
        # Lightness affects octave
        octave_offset = int((l - 0.5) * 2) * 12  # -12 to +12
        
        return base_note + note_offset + octave_offset
    
    @classmethod
    def color_to_freq(cls, r: int, g: int, b: int, base_freq: float = 261.63) -> float:
        """Convert RGB color to frequency (Hz)"""
        note = cls.color_to_note(r, g, b, base_note=60)
        # MIDI note to frequency: f = 440 * 2^((n-69)/12)
        return 440.0 * (2.0 ** ((note - 69) / 12.0))
    
    @classmethod
    def color_to_chord(cls, r: int, g: int, b: int) -> List[int]:
        """Convert color to chord (root + harmony based on saturation)"""
        h, s, l = cls.rgb_to_hsl(r, g, b)
        root = cls.color_to_note(r, g, b)
        
        if s < 0.2:
            # Low saturation: single note or octave
            return [root]
        elif s < 0.5:
            # Medium saturation: power chord (root + 5th)
            return [root, root + 7]
        elif s < 0.8:
            # High saturation: major/minor triad based on hue
            third = 4 if h < 180 else 3  # Warm = major, cool = minor
            return [root, root + third, root + 7]
        else:
            # Very high saturation: 7th chord
            third = 4 if h < 180 else 3
            return [root, root + third, root + 7, root + 10]


class ImageToSound:
    """
    Main image-to-sound converter.
    
    Usage:
        converter = ImageToSound()
        
        # Load image and convert to audio
        audio = converter.process("image.jpg", duration=10.0)
        
        # Get MIDI notes instead
        notes = converter.to_midi("image.jpg")
        
        # Get synthesis parameters
        synth_data = converter.analyze("image.jpg")
    """
    
    def __init__(self, config: Optional[ImageToSoundConfig] = None):
        self.config = config or ImageToSoundConfig()
        self.chroma = ChromaSynesthesia()
    
    def load_image(self, path: Union[str, Path]) -> Optional[List[List[Tuple[int, int, int]]]]:
        """
        Load and resize image, return as 2D array of RGB tuples.
        
        Args:
            path: Path to image file
        
        Returns:
            2D list of (R, G, B) tuples, or None if loading failed
        """
        if not HAS_PIL:
            logger.error("PIL required for image loading")
            return None
        
        try:
            img = Image.open(path).convert('RGB')
            img = img.resize((self.config.width, self.config.height))
            
            pixels = []
            for y in range(self.config.height):
                row = []
                for x in range(self.config.width):
                    row.append(img.getpixel((x, y)))
                pixels.append(row)
            
            return pixels
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None
    
    def analyze(self, path: Union[str, Path]) -> Dict:
        """
        Analyze image and return synthesis parameters.
        
        Returns dict with:
            - frames: List of spectral frames
            - notes: List of SynthNote objects
            - dominant_colors: Top colors in image
            - suggested_key: Musical key based on colors
        """
        pixels = self.load_image(path)
        if not pixels:
            return {}
        
        frames = []
        notes = []
        color_counts = {}
        
        time_per_column = self.config.duration / self.config.width
        
        for x in range(self.config.width):
            frame = []
            for y in range(self.config.height):
                r, g, b = pixels[y][x]
                
                # Calculate frequency for this row
                freq_ratio = (self.config.height - 1 - y) / (self.config.height - 1)
                freq = self.config.min_freq * (
                    (self.config.max_freq / self.config.min_freq) ** freq_ratio
                )
                
                # Calculate amplitude from brightness
                brightness = (r + g + b) / (3 * 255)
                
                frame.append({
                    'frequency': freq,
                    'amplitude': brightness,
                    'color': (r, g, b)
                })
                
                # Track colors
                color_key = (r // 32, g // 32, b // 32)
                color_counts[color_key] = color_counts.get(color_key, 0) + 1
            
            frames.append(frame)
            
            # Generate melodic notes for this column
            if self.config.mode == "melodic":
                # Find brightest pixel
                brightest = max(frame, key=lambda f: f['amplitude'])
                if brightest['amplitude'] > 0.1:
                    notes.append(SynthNote(
                        frequency=self.chroma.color_to_freq(*brightest['color']),
                        amplitude=brightest['amplitude'],
                        start_time=x * time_per_column,
                        duration=time_per_column * 1.5,  # Slight overlap
                        color=brightest['color']
                    ))
        
        # Find dominant colors
        sorted_colors = sorted(color_counts.items(), key=lambda x: -x[1])[:5]
        dominant = [(c[0] * 32, c[1] * 32, c[2] * 32) for c, _ in sorted_colors]
        
        # Suggest key based on dominant color
        if dominant:
            main_color = dominant[0]
            suggested_note = self.chroma.color_to_note(*main_color)
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            suggested_key = note_names[suggested_note % 12]
        else:
            suggested_key = 'C'
        
        return {
            'frames': frames,
            'notes': notes,
            'dominant_colors': dominant,
            'suggested_key': suggested_key,
            'duration': self.config.duration,
            'num_frames': len(frames),
        }
    
    def to_midi(self, path: Union[str, Path]) -> List[Dict]:
        """
        Convert image to MIDI note data.
        
        Returns list of dicts with: note, velocity, start, duration
        """
        analysis = self.analyze(path)
        
        midi_notes = []
        for synth_note in analysis.get('notes', []):
            # Frequency to MIDI note
            midi_num = 69 + 12 * math.log2(synth_note.frequency / 440.0)
            midi_num = max(0, min(127, int(round(midi_num))))
            
            midi_notes.append({
                'note': midi_num,
                'velocity': int(synth_note.amplitude * 127),
                'start': synth_note.start_time,
                'duration': synth_note.duration,
                'color': synth_note.color,
            })
        
        return midi_notes
    
    def process(self, path: Union[str, Path]) -> Optional[List[float]]:
        """
        Process image and generate audio samples.
        
        Returns list of audio samples (mono, -1 to 1 range).
        """
        if not HAS_NUMPY:
            logger.error("NumPy required for audio synthesis")
            return None
        
        analysis = self.analyze(path)
        if not analysis:
            return None
        
        frames = analysis['frames']
        num_samples = int(self.config.duration * self.config.sample_rate)
        audio = np.zeros(num_samples)
        
        # Additive synthesis from spectral frames
        samples_per_frame = num_samples / len(frames)
        
        for frame_idx, frame in enumerate(frames):
            frame_start = int(frame_idx * samples_per_frame)
            frame_end = min(num_samples, int((frame_idx + 1) * samples_per_frame))
            frame_len = frame_end - frame_start
            
            if frame_len <= 0:
                continue
            
            # Select top N oscillators by amplitude
            sorted_bins = sorted(frame, key=lambda x: -x['amplitude'])
            top_bins = sorted_bins[:self.config.num_oscillators]
            
            t = np.linspace(0, frame_len / self.config.sample_rate, frame_len)
            
            for bin_data in top_bins:
                if bin_data['amplitude'] < 0.01:
                    continue
                
                freq = bin_data['frequency']
                amp = bin_data['amplitude'] * 0.5 / self.config.num_oscillators
                
                # Simple sine oscillator with envelope
                envelope = np.ones(frame_len)
                attack_samples = int(self.config.attack * self.config.sample_rate)
                release_samples = int(self.config.release * self.config.sample_rate)
                
                if attack_samples > 0 and attack_samples < frame_len:
                    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
                if release_samples > 0 and release_samples < frame_len:
                    envelope[-release_samples:] = np.linspace(1, 0, release_samples)
                
                audio[frame_start:frame_end] += amp * envelope * np.sin(2 * np.pi * freq * t)
        
        # Normalize
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.9
        
        return audio.tolist()
    
    def save_wav(self, audio: List[float], path: Union[str, Path]) -> bool:
        """Save audio to WAV file"""
        if not HAS_NUMPY:
            return False
        
        try:
            import wave
            import struct
            
            audio_array = np.array(audio)
            audio_int16 = (audio_array * 32767).astype(np.int16)
            
            with wave.open(str(path), 'w') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(self.config.sample_rate)
                wav.writeframes(audio_int16.tobytes())
            
            logger.info(f"Saved WAV: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save WAV: {e}")
            return False


# Row-based spectral sonification (like spectrograms)
class SpectralSonifier:
    """
    Treats image rows as frequency bins and columns as time.
    Similar to ARSS or photosounder.
    """
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def sonify(
        self,
        image_path: Union[str, Path],
        duration: float = 10.0,
        min_freq: float = 55.0,
        max_freq: float = 14080.0
    ) -> Optional[List[float]]:
        """
        Sonify image using spectral representation.
        
        Args:
            image_path: Path to image
            duration: Output duration in seconds
            min_freq: Lowest frequency (bottom of image)
            max_freq: Highest frequency (top of image)
        
        Returns:
            Audio samples or None
        """
        if not HAS_PIL or not HAS_NUMPY:
            return None
        
        # Load grayscale image
        img = Image.open(image_path).convert('L')
        width, height = img.size
        
        # Get pixel data as 2D array
        pixels = np.array(img) / 255.0
        
        # Calculate synthesis parameters
        num_samples = int(duration * self.sample_rate)
        samples_per_column = num_samples / width
        
        # Output buffer
        audio = np.zeros(num_samples)
        
        # Frequency array (logarithmic scale)
        freqs = min_freq * (max_freq / min_freq) ** (np.arange(height) / (height - 1))
        freqs = freqs[::-1]  # Flip so low frequencies at bottom
        
        # Phase accumulators
        phases = np.zeros(height)
        
        # Process each column
        for col in range(width):
            col_start = int(col * samples_per_column)
            col_end = min(num_samples, int((col + 1) * samples_per_column))
            col_len = col_end - col_start
            
            if col_len <= 0:
                continue
            
            # Get amplitudes for this column
            amplitudes = pixels[:, col]
            
            # Synthesize
            t = np.arange(col_len) / self.sample_rate
            
            for i, (freq, amp) in enumerate(zip(freqs, amplitudes)):
                if amp < 0.01:
                    continue
                
                phase_inc = 2 * np.pi * freq * t + phases[i]
                audio[col_start:col_end] += amp * 0.1 / height * np.sin(phase_inc)
                
                # Update phase for continuity
                phases[i] = phase_inc[-1] if len(phase_inc) > 0 else phases[i]
        
        # Normalize
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.9
        
        return audio.tolist()


# Convenience functions
def image_to_midi(image_path: str, duration: float = 10.0) -> List[Dict]:
    """Quick image to MIDI conversion"""
    converter = ImageToSound(ImageToSoundConfig(duration=duration))
    return converter.to_midi(image_path)


def image_to_audio(image_path: str, duration: float = 10.0) -> Optional[List[float]]:
    """Quick image to audio conversion"""
    converter = ImageToSound(ImageToSoundConfig(duration=duration))
    return converter.process(image_path)


def color_to_note(r: int, g: int, b: int) -> int:
    """Quick color to MIDI note"""
    return ChromaSynesthesia.color_to_note(r, g, b)


def color_to_freq(r: int, g: int, b: int) -> float:
    """Quick color to frequency"""
    return ChromaSynesthesia.color_to_freq(r, g, b)
