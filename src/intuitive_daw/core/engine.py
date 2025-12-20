"""Core audio engine for the DAW"""
import threading
from typing import List, Optional, Dict, Any
import numpy as np
import soundfile as sf
import sounddevice as sd
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AudioConfig:
    """Audio configuration settings"""
    sample_rate: int = 48000
    buffer_size: int = 512
    channels: int = 2
    bit_depth: int = 24
    

class AudioEngine:
    """
    Main audio engine that handles real-time audio processing,
    playback, and recording.
    """
    
    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        self.is_playing = False
        self.is_recording = False
        self.current_position = 0  # in samples
        self.tracks: List[Any] = []
        self.master_bus = None
        self._lock = threading.Lock()
        self._stream = None
        
    def initialize(self) -> bool:
        """Initialize the audio engine"""
        try:
            # Query available devices
            devices = sd.query_devices()
            print(f"Available audio devices: {len(devices)}")
            return True
        except Exception as e:
            print(f"Failed to initialize audio engine: {e}")
            return False
    
    def start_playback(self) -> None:
        """Start audio playback"""
        with self._lock:
            if self.is_playing:
                return
            self.is_playing = True
            self._start_audio_stream()
    
    def stop_playback(self) -> None:
        """Stop audio playback"""
        with self._lock:
            if not self.is_playing:
                return
            self.is_playing = False
            self._stop_audio_stream()
    
    def start_recording(self) -> None:
        """Start audio recording"""
        with self._lock:
            self.is_recording = True
    
    def stop_recording(self) -> None:
        """Stop audio recording"""
        with self._lock:
            self.is_recording = False
    
    def add_track(self, track: Any) -> None:
        """Add a track to the engine"""
        with self._lock:
            self.tracks.append(track)
    
    def remove_track(self, track: Any) -> None:
        """Remove a track from the engine"""
        with self._lock:
            if track in self.tracks:
                self.tracks.remove(track)
    
    def set_position(self, position: int) -> None:
        """Set playback position in samples"""
        with self._lock:
            self.current_position = max(0, position)
    
    def get_position(self) -> int:
        """Get current playback position in samples"""
        return self.current_position
    
    def _start_audio_stream(self) -> None:
        """Internal method to start audio stream"""
        # This would be implemented with actual audio callback
        pass
    
    def _stop_audio_stream(self) -> None:
        """Internal method to stop audio stream"""
        if self._stream:
            self._stream.stop()
            self._stream = None
    
    def process_audio(self, frames: int) -> np.ndarray:
        """
        Process audio for the given number of frames
        
        Args:
            frames: Number of frames to process
            
        Returns:
            Processed audio buffer
        """
        buffer = np.zeros((frames, self.config.channels))
        
        # Mix all tracks
        for track in self.tracks:
            if hasattr(track, 'get_audio') and track.is_enabled:
                track_audio = track.get_audio(
                    self.current_position, 
                    frames,
                    self.config.sample_rate
                )
                if track_audio is not None:
                    buffer += track_audio
        
        # Apply master effects
        if self.master_bus:
            buffer = self.master_bus.process(buffer)
        
        self.current_position += frames
        return buffer
    
    def render(self, output_path: str, duration: float) -> bool:
        """
        Render the project to an audio file
        
        Args:
            output_path: Path to output file
            duration: Duration in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            total_frames = int(duration * self.config.sample_rate)
            frames_per_chunk = self.config.buffer_size
            
            audio_data = []
            processed_frames = 0
            
            while processed_frames < total_frames:
                frames_to_process = min(
                    frames_per_chunk,
                    total_frames - processed_frames
                )
                chunk = self.process_audio(frames_to_process)
                audio_data.append(chunk)
                processed_frames += frames_to_process
            
            # Concatenate all chunks
            final_audio = np.vstack(audio_data)
            
            # Write to file
            sf.write(
                output_path,
                final_audio,
                self.config.sample_rate,
                subtype=f'PCM_{self.config.bit_depth}'
            )
            
            return True
        except Exception as e:
            print(f"Render failed: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown the audio engine"""
        self.stop_playback()
        self.stop_recording()
        if self._stream:
            self._stream.close()
