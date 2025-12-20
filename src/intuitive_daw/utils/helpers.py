"""Utility functions for the DAW"""
import os
import json
import yaml
from typing import Any, Dict, Optional
from pathlib import Path


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        return {}
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def save_config(config: Dict[str, Any], config_path: str = 'config.yaml') -> bool:
    """
    Save configuration to YAML file
    
    Args:
        config: Configuration dictionary
        config_path: Path to config file
        
    Returns:
        True if successful
    """
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        print(f"Failed to save config: {e}")
        return False


def ensure_directories(directories: list) -> None:
    """
    Ensure directories exist, create if they don't
    
    Args:
        directories: List of directory paths
    """
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def format_time(seconds: float) -> str:
    """
    Format time in seconds to MM:SS.mmm
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"


def format_db(value: float) -> str:
    """
    Format dB value for display
    
    Args:
        value: dB value
        
    Returns:
        Formatted string
    """
    if value <= -60:
        return "-∞ dB"
    return f"{value:+.1f} dB"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between min and max
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation
    
    Args:
        a: Start value
        b: End value
        t: Interpolation factor (0-1)
        
    Returns:
        Interpolated value
    """
    return a + (b - a) * t


def db_to_linear(db: float) -> float:
    """Convert dB to linear gain"""
    return 10.0 ** (db / 20.0)


def linear_to_db(linear: float) -> float:
    """Convert linear gain to dB"""
    if linear <= 0:
        return -60.0
    return 20.0 * (linear ** 0.05)  # log10


def midi_to_freq(midi_note: int) -> float:
    """
    Convert MIDI note number to frequency in Hz
    
    Args:
        midi_note: MIDI note number (0-127)
        
    Returns:
        Frequency in Hz
    """
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def freq_to_midi(freq: float) -> int:
    """
    Convert frequency to MIDI note number
    
    Args:
        freq: Frequency in Hz
        
    Returns:
        MIDI note number
    """
    import math
    return int(round(69 + 12 * math.log2(freq / 440.0)))


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system use
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized


def get_file_extension(format: str) -> str:
    """
    Get file extension for audio format
    
    Args:
        format: Audio format name
        
    Returns:
        File extension
    """
    extensions = {
        'wav': '.wav',
        'mp3': '.mp3',
        'ogg': '.ogg',
        'flac': '.flac',
        'aiff': '.aiff',
        'aif': '.aif'
    }
    return extensions.get(format.lower(), '.wav')


class Logger:
    """Simple logger for the DAW"""
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        self.name = name
        self.log_file = log_file
    
    def _write(self, level: str, message: str) -> None:
        """Write log message"""
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] [{self.name}] {message}"
        
        print(log_message)
        
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(log_message + '\n')
    
    def info(self, message: str) -> None:
        """Log info message"""
        self._write('INFO', message)
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        self._write('WARNING', message)
    
    def error(self, message: str) -> None:
        """Log error message"""
        self._write('ERROR', message)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        self._write('DEBUG', message)
