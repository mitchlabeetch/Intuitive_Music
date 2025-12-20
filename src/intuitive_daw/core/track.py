"""Track management for the DAW"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class TrackType(Enum):
    """Types of tracks"""
    AUDIO = "audio"
    MIDI = "midi"
    INSTRUMENT = "instrument"
    AUX = "aux"
    MASTER = "master"


@dataclass
class TrackSettings:
    """Track settings"""
    volume: float = 0.0  # in dB
    pan: float = 0.0  # -1.0 to 1.0
    mute: bool = False
    solo: bool = False
    record_enabled: bool = False
    monitoring: bool = False


class Track:
    """
    Base track class for audio and MIDI tracks
    """
    
    def __init__(
        self, 
        name: str, 
        track_type: TrackType = TrackType.AUDIO,
        index: int = 0
    ):
        self.name = name
        self.track_type = track_type
        self.index = index
        self.settings = TrackSettings()
        self.clips: List[Any] = []
        self.effects: List[Any] = []
        self.automation: Dict[str, List[tuple]] = {}
        self.color: str = "#3498db"
        self.is_enabled = True
        
    def add_clip(self, clip: Any) -> None:
        """Add a clip to the track"""
        self.clips.append(clip)
        # Sort clips by position
        self.clips.sort(key=lambda c: getattr(c, 'position', 0))
    
    def remove_clip(self, clip: Any) -> None:
        """Remove a clip from the track"""
        if clip in self.clips:
            self.clips.remove(clip)
    
    def add_effect(self, effect: Any, position: Optional[int] = None) -> None:
        """Add an effect to the track's effect chain"""
        if position is None:
            self.effects.append(effect)
        else:
            self.effects.insert(position, effect)
    
    def remove_effect(self, effect: Any) -> None:
        """Remove an effect from the track"""
        if effect in self.effects:
            self.effects.remove(effect)
    
    def set_volume(self, volume_db: float) -> None:
        """Set track volume in dB"""
        self.settings.volume = max(-60.0, min(12.0, volume_db))
    
    def set_pan(self, pan: float) -> None:
        """Set track pan (-1.0 = left, 1.0 = right)"""
        self.settings.pan = max(-1.0, min(1.0, pan))
    
    def toggle_mute(self) -> None:
        """Toggle mute state"""
        self.settings.mute = not self.settings.mute
    
    def toggle_solo(self) -> None:
        """Toggle solo state"""
        self.settings.solo = not self.settings.solo
    
    def get_audio(
        self, 
        position: int, 
        frames: int, 
        sample_rate: int
    ) -> Optional[np.ndarray]:
        """
        Get audio for this track at the given position
        
        Args:
            position: Starting position in samples
            frames: Number of frames to retrieve
            sample_rate: Sample rate
            
        Returns:
            Audio buffer or None
        """
        if self.settings.mute or not self.is_enabled:
            return None
        
        # Initialize buffer
        buffer = np.zeros((frames, 2))
        
        # Get audio from active clips
        for clip in self.clips:
            if hasattr(clip, 'get_audio'):
                clip_audio = clip.get_audio(position, frames, sample_rate)
                if clip_audio is not None:
                    buffer += clip_audio
        
        # Apply effects chain
        for effect in self.effects:
            if hasattr(effect, 'process') and getattr(effect, 'is_enabled', True):
                buffer = effect.process(buffer)
        
        # Apply volume
        volume_linear = self._db_to_linear(self.settings.volume)
        buffer *= volume_linear
        
        # Apply pan
        if self.settings.pan != 0.0:
            buffer = self._apply_pan(buffer, self.settings.pan)
        
        return buffer
    
    def get_duration(self) -> float:
        """Get track duration in seconds"""
        if not self.clips:
            return 0.0
        max_end = 0.0
        for clip in self.clips:
            if hasattr(clip, 'get_end_time'):
                max_end = max(max_end, clip.get_end_time())
        return max_end
    
    def add_automation(
        self, 
        parameter: str, 
        points: List[tuple]
    ) -> None:
        """
        Add automation for a parameter
        
        Args:
            parameter: Parameter name (e.g., 'volume', 'pan')
            points: List of (time, value) tuples
        """
        self.automation[parameter] = sorted(points, key=lambda x: x[0])
    
    def get_automation_value(
        self, 
        parameter: str, 
        time: float
    ) -> Optional[float]:
        """Get interpolated automation value at given time"""
        if parameter not in self.automation:
            return None
        
        points = self.automation[parameter]
        if not points:
            return None
        
        # Find surrounding points
        for i in range(len(points) - 1):
            if points[i][0] <= time <= points[i + 1][0]:
                # Linear interpolation
                t1, v1 = points[i]
                t2, v2 = points[i + 1]
                ratio = (time - t1) / (t2 - t1)
                return v1 + (v2 - v1) * ratio
        
        # Return first or last value if outside range
        if time < points[0][0]:
            return points[0][1]
        return points[-1][1]
    
    @staticmethod
    def _db_to_linear(db: float) -> float:
        """Convert dB to linear gain"""
        return 10.0 ** (db / 20.0)
    
    @staticmethod
    def _apply_pan(buffer: np.ndarray, pan: float) -> np.ndarray:
        """Apply pan to stereo buffer"""
        result = buffer.copy()
        if pan < 0:  # Pan left
            result[:, 1] *= (1.0 + pan)
        elif pan > 0:  # Pan right
            result[:, 0] *= (1.0 - pan)
        return result


class AudioTrack(Track):
    """Audio track for recorded or imported audio"""
    
    def __init__(self, name: str, index: int = 0):
        super().__init__(name, TrackType.AUDIO, index)
        self.input_device: Optional[str] = None
        self.input_channel: int = 0


class MIDITrack(Track):
    """MIDI track for MIDI events and virtual instruments"""
    
    def __init__(self, name: str, index: int = 0):
        super().__init__(name, TrackType.MIDI, index)
        self.midi_channel: int = 0
        self.instrument: Optional[Any] = None
        self.midi_events: List[Any] = []
    
    def add_midi_event(self, event: Any) -> None:
        """Add a MIDI event to the track"""
        self.midi_events.append(event)
        self.midi_events.sort(key=lambda e: getattr(e, 'time', 0))


class InstrumentTrack(MIDITrack):
    """Instrument track with built-in virtual instrument"""
    
    def __init__(self, name: str, index: int = 0):
        super().__init__(name, index)
        self.track_type = TrackType.INSTRUMENT
        self.preset: Optional[str] = None
