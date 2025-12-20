"""Audio processing utilities and effects"""
from typing import Optional, Tuple
import numpy as np
from scipy import signal
from dataclasses import dataclass


@dataclass
class AudioClip:
    """Audio clip containing audio data"""
    name: str
    data: np.ndarray
    sample_rate: int
    position: float = 0.0  # Position in seconds
    
    def get_duration(self) -> float:
        """Get clip duration in seconds"""
        return len(self.data) / self.sample_rate
    
    def get_end_time(self) -> float:
        """Get clip end time"""
        return self.position + self.get_duration()
    
    def get_audio(
        self,
        position: int,
        frames: int,
        sample_rate: int
    ) -> Optional[np.ndarray]:
        """Get audio data at position"""
        # Calculate position in clip
        clip_start_samples = int(self.position * sample_rate)
        relative_position = position - clip_start_samples
        
        # Check if position is within clip bounds
        if relative_position < 0 or relative_position >= len(self.data):
            return None
        
        # Extract audio chunk
        end_position = min(relative_position + frames, len(self.data))
        chunk = self.data[relative_position:end_position]
        
        # Pad if necessary
        if len(chunk) < frames:
            padding = np.zeros((frames - len(chunk), chunk.shape[1]))
            chunk = np.vstack([chunk, padding])
        
        return chunk


class AudioEffect:
    """Base class for audio effects"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_enabled = True
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Process audio through effect"""
        if not self.is_enabled:
            return audio
        return self._process_impl(audio)
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        """Implementation of audio processing"""
        return audio


class GainEffect(AudioEffect):
    """Simple gain/volume effect"""
    
    def __init__(self, gain_db: float = 0.0):
        super().__init__("Gain")
        self.gain_db = gain_db
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        """Apply gain"""
        gain_linear = 10.0 ** (self.gain_db / 20.0)
        return audio * gain_linear


class EQEffect(AudioEffect):
    """Parametric EQ effect"""
    
    def __init__(
        self,
        sample_rate: int = 48000,
        low_freq: float = 100.0,
        low_gain: float = 0.0,
        mid_freq: float = 1000.0,
        mid_gain: float = 0.0,
        high_freq: float = 10000.0,
        high_gain: float = 0.0
    ):
        super().__init__("EQ")
        self.sample_rate = sample_rate
        self.low_freq = low_freq
        self.low_gain = low_gain
        self.mid_freq = mid_freq
        self.mid_gain = mid_gain
        self.high_freq = high_freq
        self.high_gain = high_gain
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        """Apply EQ (simplified implementation)"""
        # This is a simplified EQ implementation
        # In production, use proper biquad filters
        result = audio.copy()
        
        # Apply low shelf
        if abs(self.low_gain) > 0.1:
            sos = signal.butter(
                2, 
                self.low_freq, 
                btype='low',
                fs=self.sample_rate,
                output='sos'
            )
            gain = 10.0 ** (self.low_gain / 20.0)
            for ch in range(result.shape[1]):
                filtered = signal.sosfilt(sos, result[:, ch])
                result[:, ch] = result[:, ch] + (filtered - result[:, ch]) * (gain - 1)
        
        return result


class CompressorEffect(AudioEffect):
    """Dynamic range compressor"""
    
    def __init__(
        self,
        threshold_db: float = -20.0,
        ratio: float = 4.0,
        attack_ms: float = 10.0,
        release_ms: float = 100.0,
        sample_rate: int = 48000
    ):
        super().__init__("Compressor")
        self.threshold_db = threshold_db
        self.ratio = ratio
        self.attack_ms = attack_ms
        self.release_ms = release_ms
        self.sample_rate = sample_rate
        
        # Calculate envelope coefficients
        self.attack_coef = np.exp(-1.0 / (sample_rate * attack_ms / 1000.0))
        self.release_coef = np.exp(-1.0 / (sample_rate * release_ms / 1000.0))
        self.envelope = 0.0
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        """Apply compression"""
        threshold_linear = 10.0 ** (self.threshold_db / 20.0)
        
        result = audio.copy()
        
        for i in range(len(result)):
            # Get peak level
            peak = np.max(np.abs(result[i]))
            
            # Update envelope
            if peak > self.envelope:
                self.envelope = self.attack_coef * self.envelope + \
                               (1 - self.attack_coef) * peak
            else:
                self.envelope = self.release_coef * self.envelope + \
                               (1 - self.release_coef) * peak
            
            # Calculate gain reduction
            if self.envelope > threshold_linear:
                gain_reduction = (
                    threshold_linear + 
                    (self.envelope - threshold_linear) / self.ratio
                ) / self.envelope
                result[i] *= gain_reduction
        
        return result


class ReverbEffect(AudioEffect):
    """Simple reverb effect"""
    
    def __init__(
        self,
        room_size: float = 0.5,
        damping: float = 0.5,
        wet_level: float = 0.3,
        sample_rate: int = 48000
    ):
        super().__init__("Reverb")
        self.room_size = room_size
        self.damping = damping
        self.wet_level = wet_level
        self.sample_rate = sample_rate
        self.dry_level = 1.0 - wet_level
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        """Apply reverb (simplified implementation)"""
        # Simplified reverb using convolution with impulse response
        # In production, use proper reverb algorithm
        
        # Create simple impulse response
        decay = 0.3 + self.room_size * 0.6
        ir_length = int(self.sample_rate * 0.5)  # 0.5 second IR
        t = np.linspace(0, 1, ir_length)
        ir = np.exp(-t * (1.0 / decay)) * np.random.randn(ir_length)
        
        # Convolve each channel
        result = audio * self.dry_level
        
        for ch in range(audio.shape[1]):
            wet = signal.fftconvolve(audio[:, ch], ir, mode='same')
            wet = wet * self.wet_level
            result[:, ch] += wet[:len(result)]
        
        return result


class DelayEffect(AudioEffect):
    """Delay/echo effect"""
    
    def __init__(
        self,
        delay_time: float = 0.5,
        feedback: float = 0.4,
        mix: float = 0.3,
        sample_rate: int = 48000
    ):
        super().__init__("Delay")
        self.delay_time = delay_time
        self.feedback = feedback
        self.mix = mix
        self.sample_rate = sample_rate
        self.buffer = None
    
    def _process_impl(self, audio: np.ndarray) -> np.ndarray:
        """Apply delay"""
        delay_samples = int(self.delay_time * self.sample_rate)
        
        # Initialize buffer
        if self.buffer is None or len(self.buffer) != delay_samples:
            self.buffer = np.zeros((delay_samples, audio.shape[1]))
        
        result = audio.copy()
        
        # Process each sample
        for i in range(len(result)):
            # Add delayed signal
            delayed = self.buffer[0]
            result[i] = audio[i] * (1 - self.mix) + delayed * self.mix
            
            # Update buffer
            self.buffer = np.roll(self.buffer, -1, axis=0)
            self.buffer[-1] = audio[i] + delayed * self.feedback
        
        return result


class AudioAnalyzer:
    """Analyze audio signals"""
    
    @staticmethod
    def get_rms(audio: np.ndarray) -> float:
        """Calculate RMS level"""
        return np.sqrt(np.mean(audio ** 2))
    
    @staticmethod
    def get_peak(audio: np.ndarray) -> float:
        """Calculate peak level"""
        return np.max(np.abs(audio))
    
    @staticmethod
    def get_lufs(audio: np.ndarray, sample_rate: int) -> float:
        """
        Calculate LUFS (simplified)
        
        Note: This is a simplified implementation.
        For accurate LUFS measurement, use pyloudnorm library.
        """
        # Apply K-weighting filter (simplified)
        # Stage 1: High-shelf filter
        sos1 = signal.butter(
            1, 
            1500,
            btype='high',
            fs=sample_rate,
            output='sos'
        )
        
        filtered = audio.copy()
        for ch in range(audio.shape[1]):
            filtered[:, ch] = signal.sosfilt(sos1, audio[:, ch])
        
        # Calculate mean square
        mean_square = np.mean(filtered ** 2)
        
        # Convert to LUFS
        lufs = -0.691 + 10.0 * np.log10(mean_square)
        
        return lufs
    
    @staticmethod
    def detect_tempo(audio: np.ndarray, sample_rate: int) -> float:
        """
        Detect tempo using onset detection
        
        Returns estimated BPM
        """
        # Simplified tempo detection
        # In production, use librosa.beat.tempo
        
        # Calculate onset strength
        hop_length = 512
        onset_env = np.abs(np.diff(audio[:, 0]))
        
        # Autocorrelation
        autocorr = np.correlate(onset_env, onset_env, mode='full')
        autocorr = autocorr[len(autocorr) // 2:]
        
        # Find peaks
        peaks = signal.find_peaks(autocorr, distance=sample_rate // hop_length)[0]
        
        if len(peaks) > 0:
            # Estimate tempo from first peak
            period = peaks[0] * hop_length / sample_rate
            bpm = 60.0 / period
            
            # Constrain to reasonable range
            while bpm < 60:
                bpm *= 2
            while bpm > 180:
                bpm /= 2
            
            return bpm
        
        return 120.0  # Default tempo
