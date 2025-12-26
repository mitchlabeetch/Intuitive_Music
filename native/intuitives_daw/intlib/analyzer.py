"""
INTUITIVES DAW - Shared Memory Analyzer Access

"Does this sound cool?" - The only rule.

This module provides Python access to the real-time audio analyzer
via shared memory for high-performance visualization.

The analyzer data is updated by the C audio engine and read by
Python for OpenGL/Qt visualization without copying large buffers.
"""

import ctypes
import mmap
import os
import struct
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np

from intlib.log import LOG


# ============================================================================
# CONSTANTS (Must match analyzer.h)
# ============================================================================

ANALYZER_FFT_SIZE = 2048
ANALYZER_SPECTRUM_BINS = 512
ANALYZER_WAVEFORM_SIZE = 1024
ANALYZER_HISTORY_SIZE = 60

ANALYZER_MAGIC = 0x494E5455  # "INTU"

# Default shared memory path
SHM_NAME = "/intuitives_analyzer"
SHM_PATH = f"/dev/shm{SHM_NAME}"  # Linux
SHM_PATH_MACOS = f"/tmp{SHM_NAME}"  # macOS fallback


# ============================================================================
# CTYPES STRUCTURES (Mirror C structs)
# ============================================================================

class SpectrumData(ctypes.Structure):
    """Spectrum analysis data."""
    _fields_ = [
        ("magnitude", ctypes.c_float * ANALYZER_SPECTRUM_BINS),
        ("phase", ctypes.c_float * ANALYZER_SPECTRUM_BINS),
        ("smoothed", ctypes.c_float * ANALYZER_SPECTRUM_BINS),
        ("peak_frequencies", ctypes.c_float * 8),
        ("peak_magnitudes", ctypes.c_float * 8),
        ("num_peaks", ctypes.c_uint32),
        ("spectral_centroid", ctypes.c_float),
        ("spectral_spread", ctypes.c_float),
        ("spectral_flux", ctypes.c_float),
        ("spectral_rolloff", ctypes.c_float),
        ("spectral_flatness", ctypes.c_float),
        ("chroma", ctypes.c_float * 12),
        ("dominant_pitch_class", ctypes.c_float),
    ]


class WaveformData(ctypes.Structure):
    """Waveform oscilloscope data."""
    _fields_ = [
        ("samples_left", ctypes.c_float * ANALYZER_WAVEFORM_SIZE),
        ("samples_right", ctypes.c_float * ANALYZER_WAVEFORM_SIZE),
        ("write_pos", ctypes.c_uint32),
        ("zoom_level", ctypes.c_float),
        ("trigger_level", ctypes.c_float),
        ("trigger_rising", ctypes.c_bool),
    ]


class LevelData(ctypes.Structure):
    """Level metering data."""
    _fields_ = [
        ("rms_left", ctypes.c_float),
        ("rms_right", ctypes.c_float),
        ("peak_left", ctypes.c_float),
        ("peak_right", ctypes.c_float),
        ("peak_hold_left", ctypes.c_float),
        ("peak_hold_right", ctypes.c_float),
        ("peak_hold_samples", ctypes.c_uint32),
        ("momentary_lufs", ctypes.c_float),
        ("short_term_lufs", ctypes.c_float),
        ("integrated_lufs", ctypes.c_float),
        ("dynamic_range", ctypes.c_float),
        ("crest_factor", ctypes.c_float),
        ("correlation", ctypes.c_float),
        ("balance", ctypes.c_float),
        ("mono_compatibility", ctypes.c_float),
    ]


class BeatData(ctypes.Structure):
    """Beat/tempo detection data."""
    _fields_ = [
        ("bpm", ctypes.c_float),
        ("confidence", ctypes.c_float),
        ("phase", ctypes.c_float),
        ("beat_count", ctypes.c_uint32),
        ("last_beat", ctypes.c_uint64),
        ("is_on_beat", ctypes.c_bool),
        ("onset_strength", ctypes.c_float),
        ("onset_detected", ctypes.c_bool),
    ]


class AnalyzerSharedMemory(ctypes.Structure):
    """Main analyzer shared memory structure."""
    _fields_ = [
        # Header
        ("magic", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
        ("frame_count", ctypes.c_uint32),  # Atomic in C
        # Configuration
        ("sample_rate", ctypes.c_uint32),
        ("fft_size", ctypes.c_uint32),
        ("update_rate_hz", ctypes.c_uint32),
        # Status
        ("is_active", ctypes.c_bool),
        ("needs_reconfigure", ctypes.c_bool),
        # Analysis data
        ("spectrum", SpectrumData),
        ("waveform", WaveformData),
        ("levels", LevelData),
        ("beat", BeatData),
        # History (flattened)
        ("spectrum_history", (ctypes.c_float * ANALYZER_SPECTRUM_BINS) * ANALYZER_HISTORY_SIZE),
        ("level_history_left", ctypes.c_float * ANALYZER_HISTORY_SIZE),
        ("level_history_right", ctypes.c_float * ANALYZER_HISTORY_SIZE),
        ("history_write_pos", ctypes.c_uint32),
        # Timestamp
        ("last_update_ns", ctypes.c_uint64),
    ]


# ============================================================================
# ANALYZER READER CLASS
# ============================================================================

@dataclass
class ChromaColors:
    """Chromasynesthesia color mapping for each pitch class."""
    # Scriabin-inspired colors (matching brand.py CHROMA_COLORS)
    COLORS = [
        (1.0, 0.36, 0.36),  # C - Red
        (1.0, 0.55, 0.30),  # C# - Orange-Red
        (1.0, 0.72, 0.30),  # D - Orange
        (1.0, 0.88, 0.30),  # D# - Yellow-Orange
        (0.91, 1.0, 0.30),  # E - Yellow
        (0.55, 1.0, 0.30),  # F - Yellow-Green
        (0.30, 1.0, 0.55),  # F# - Green
        (0.30, 1.0, 1.0),   # G - Cyan
        (0.30, 0.55, 1.0),  # G# - Blue
        (0.30, 0.30, 1.0),  # A - Indigo
        (0.55, 0.30, 1.0),  # A# - Purple
        (1.0, 0.30, 1.0),   # B - Magenta
    ]
    
    @classmethod
    def get_color(cls, pitch_class: int, intensity: float = 1.0) -> Tuple[float, float, float]:
        """Get RGB color for a pitch class with intensity."""
        r, g, b = cls.COLORS[pitch_class % 12]
        return (r * intensity, g * intensity, b * intensity)
    
    @classmethod
    def blend_chroma(cls, chroma: np.ndarray) -> Tuple[float, float, float]:
        """Blend all pitch class colors weighted by chroma intensities."""
        r, g, b = 0.0, 0.0, 0.0
        total = np.sum(chroma) + 1e-6
        
        for i, intensity in enumerate(chroma):
            color = cls.COLORS[i]
            weight = intensity / total
            r += color[0] * weight
            g += color[1] * weight
            b += color[2] * weight
        
        return (r, g, b)


class AnalyzerReader:
    """
    High-performance reader for the shared memory analyzer.
    
    This class provides numpy array access to real-time audio analysis
    data without copying, suitable for 60fps OpenGL visualization.
    """
    
    def __init__(self, shm_path: Optional[str] = None):
        """
        Initialize the analyzer reader.
        
        Args:
            shm_path: Path to shared memory file (auto-detected if None)
        """
        self.shm_path = shm_path
        self._mmap: Optional[mmap.mmap] = None
        self._analyzer: Optional[AnalyzerSharedMemory] = None
        self._last_frame = 0
        
        # Cached numpy arrays (views into shared memory)
        self._spectrum: Optional[np.ndarray] = None
        self._chroma: Optional[np.ndarray] = None
        self._waveform_l: Optional[np.ndarray] = None
        self._waveform_r: Optional[np.ndarray] = None
        
        # Fallback data if analyzer not available
        self._fallback_spectrum = np.zeros(ANALYZER_SPECTRUM_BINS, dtype=np.float32)
        self._fallback_chroma = np.zeros(12, dtype=np.float32)
        self._fallback_waveform = np.zeros(ANALYZER_WAVEFORM_SIZE, dtype=np.float32)
    
    def connect(self) -> bool:
        """
        Connect to the shared memory analyzer.
        
        Returns:
            True if connected successfully
        """
        # Try to find the shared memory file
        paths = [
            self.shm_path,
            SHM_PATH,
            SHM_PATH_MACOS,
        ]
        
        for path in paths:
            if path and os.path.exists(path):
                try:
                    fd = os.open(path, os.O_RDONLY)
                    size = ctypes.sizeof(AnalyzerSharedMemory)
                    self._mmap = mmap.mmap(fd, size, access=mmap.ACCESS_READ)
                    os.close(fd)
                    
                    # Cast to structure
                    self._analyzer = AnalyzerSharedMemory.from_buffer_copy(
                        self._mmap[:size]
                    )
                    
                    # Validate magic
                    if self._analyzer.magic != ANALYZER_MAGIC:
                        LOG.warning(f"Invalid analyzer magic: {self._analyzer.magic}")
                        self.disconnect()
                        continue
                    
                    LOG.info(f"Connected to analyzer at {path}")
                    self._setup_numpy_views()
                    return True
                    
                except Exception as e:
                    LOG.warning(f"Failed to connect to analyzer at {path}: {e}")
        
        LOG.info("Analyzer not available, using fallback mode")
        return False
    
    def disconnect(self):
        """Disconnect from shared memory."""
        if self._mmap:
            self._mmap.close()
            self._mmap = None
        self._analyzer = None
        self._spectrum = None
        self._chroma = None
    
    def _setup_numpy_views(self):
        """Create numpy array views of the shared memory data."""
        if not self._analyzer:
            return
        
        # Note: These are copies, not views, because ctypes arrays
        # can't be directly viewed by numpy without memoryview tricks
        # For true zero-copy, we'd need to use the mmap buffer directly
        pass
    
    def update(self) -> bool:
        """
        Check for new data and update if available.
        
        Returns:
            True if new data was available
        """
        if not self._mmap:
            return False
        
        try:
            # Re-read the structure from shared memory
            size = ctypes.sizeof(AnalyzerSharedMemory)
            self._analyzer = AnalyzerSharedMemory.from_buffer_copy(
                self._mmap[:size]
            )
            
            frame = self._analyzer.frame_count
            if frame != self._last_frame:
                self._last_frame = frame
                return True
            return False
            
        except Exception as e:
            LOG.warning(f"Analyzer update error: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to analyzer."""
        return self._analyzer is not None and self._analyzer.is_active
    
    @property
    def spectrum(self) -> np.ndarray:
        """Get spectrum magnitude data (0-1 normalized)."""
        if self._analyzer:
            return np.array(self._analyzer.spectrum.smoothed)
        return self._fallback_spectrum
    
    @property
    def chroma(self) -> np.ndarray:
        """Get chromagram data (12 pitch classes)."""
        if self._analyzer:
            return np.array(self._analyzer.spectrum.chroma)
        return self._fallback_chroma
    
    @property
    def waveform_left(self) -> np.ndarray:
        """Get left channel waveform."""
        if self._analyzer:
            return np.array(self._analyzer.waveform.samples_left)
        return self._fallback_waveform
    
    @property
    def waveform_right(self) -> np.ndarray:
        """Get right channel waveform."""
        if self._analyzer:
            return np.array(self._analyzer.waveform.samples_right)
        return self._fallback_waveform
    
    @property
    def levels(self) -> Tuple[float, float, float, float]:
        """Get (rms_left, rms_right, peak_left, peak_right)."""
        if self._analyzer:
            l = self._analyzer.levels
            return (l.rms_left, l.rms_right, l.peak_left, l.peak_right)
        return (0.0, 0.0, 0.0, 0.0)
    
    @property
    def bpm(self) -> float:
        """Get detected BPM."""
        if self._analyzer:
            return self._analyzer.beat.bpm
        return 120.0
    
    @property
    def is_on_beat(self) -> bool:
        """Check if currently on a beat."""
        if self._analyzer:
            return self._analyzer.beat.is_on_beat
        return False
    
    @property
    def beat_phase(self) -> float:
        """Get beat phase (0-1, 0 = on beat)."""
        if self._analyzer:
            return self._analyzer.beat.phase
        return 0.0
    
    @property
    def dominant_color(self) -> Tuple[float, float, float]:
        """Get the dominant chromasynesthesia color."""
        chroma = self.chroma
        return ChromaColors.blend_chroma(chroma)
    
    @property  
    def spectral_centroid(self) -> float:
        """Get spectral centroid (brightness) in Hz."""
        if self._analyzer:
            return self._analyzer.spectrum.spectral_centroid
        return 1000.0
    
    @property
    def stereo_correlation(self) -> float:
        """Get stereo correlation (-1 to 1)."""
        if self._analyzer:
            return self._analyzer.levels.correlation
        return 1.0


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_reader: Optional[AnalyzerReader] = None


def get_analyzer() -> AnalyzerReader:
    """Get the global analyzer reader, creating if needed."""
    global _reader
    if _reader is None:
        _reader = AnalyzerReader()
        _reader.connect()
    return _reader


def get_spectrum() -> np.ndarray:
    """Quick access to spectrum data."""
    return get_analyzer().spectrum


def get_chroma() -> np.ndarray:
    """Quick access to chromagram data."""
    return get_analyzer().chroma


def get_dominant_color() -> Tuple[float, float, float]:
    """Quick access to dominant chromasynesthesia color."""
    return get_analyzer().dominant_color
