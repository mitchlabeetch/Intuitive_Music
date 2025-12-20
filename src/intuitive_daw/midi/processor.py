"""MIDI processing and manipulation"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np


class MIDIMessageType(Enum):
    """MIDI message types"""
    NOTE_ON = "note_on"
    NOTE_OFF = "note_off"
    CONTROL_CHANGE = "control_change"
    PROGRAM_CHANGE = "program_change"
    PITCH_BEND = "pitch_bend"
    AFTERTOUCH = "aftertouch"


@dataclass
class MIDINote:
    """MIDI note representation"""
    pitch: int  # 0-127
    velocity: int  # 0-127
    start_time: float  # in seconds or beats
    duration: float  # in seconds or beats
    channel: int = 0


@dataclass
class MIDIEvent:
    """Generic MIDI event"""
    type: MIDIMessageType
    time: float
    channel: int = 0
    data: Dict[str, Any] = None


class MIDIClip:
    """
    Container for MIDI notes and events
    """
    
    def __init__(self, name: str = "MIDI Clip"):
        self.name = name
        self.notes: List[MIDINote] = []
        self.events: List[MIDIEvent] = []
        self.position = 0.0  # Start position in beats
        self.length = 4.0  # Length in beats
        
    def add_note(
        self,
        pitch: int,
        velocity: int,
        start: float,
        duration: float,
        channel: int = 0
    ) -> None:
        """Add a note to the clip"""
        note = MIDINote(
            pitch=pitch,
            velocity=velocity,
            start_time=start,
            duration=duration,
            channel=channel
        )
        self.notes.append(note)
        self._sort_notes()
    
    def remove_note(self, note: MIDINote) -> None:
        """Remove a note from the clip"""
        if note in self.notes:
            self.notes.remove(note)
    
    def _sort_notes(self) -> None:
        """Sort notes by start time"""
        self.notes.sort(key=lambda n: n.start_time)
    
    def transpose(self, semitones: int) -> None:
        """Transpose all notes by semitones"""
        for note in self.notes:
            note.pitch = max(0, min(127, note.pitch + semitones))
    
    def quantize(self, grid: float) -> None:
        """
        Quantize note positions to grid
        
        Args:
            grid: Grid size in beats (e.g., 0.25 for 16th notes)
        """
        for note in self.notes:
            note.start_time = round(note.start_time / grid) * grid
    
    def scale_velocity(self, factor: float) -> None:
        """Scale all velocities by factor"""
        for note in self.notes:
            note.velocity = int(max(1, min(127, note.velocity * factor)))
    
    def get_notes_in_range(
        self,
        start: float,
        end: float
    ) -> List[MIDINote]:
        """Get notes within time range"""
        return [
            note for note in self.notes
            if note.start_time < end and 
               note.start_time + note.duration > start
        ]


class MIDIProcessor:
    """
    Process and manipulate MIDI data
    """
    
    @staticmethod
    def create_chord(
        root: int,
        chord_type: str,
        velocity: int = 80,
        start_time: float = 0.0,
        duration: float = 1.0
    ) -> List[MIDINote]:
        """
        Create a chord
        
        Args:
            root: Root note (MIDI number)
            chord_type: Chord type (major, minor, dim, aug, etc.)
            velocity: Note velocity
            start_time: Start time
            duration: Duration
            
        Returns:
            List of MIDI notes
        """
        intervals = MIDIProcessor._get_chord_intervals(chord_type)
        
        notes = []
        for interval in intervals:
            note = MIDINote(
                pitch=root + interval,
                velocity=velocity,
                start_time=start_time,
                duration=duration
            )
            notes.append(note)
        
        return notes
    
    @staticmethod
    def _get_chord_intervals(chord_type: str) -> List[int]:
        """Get intervals for chord type"""
        chord_intervals = {
            "major": [0, 4, 7],
            "minor": [0, 3, 7],
            "dim": [0, 3, 6],
            "aug": [0, 4, 8],
            "sus2": [0, 2, 7],
            "sus4": [0, 5, 7],
            "maj7": [0, 4, 7, 11],
            "min7": [0, 3, 7, 10],
            "dom7": [0, 4, 7, 10],
            "dim7": [0, 3, 6, 9],
        }
        return chord_intervals.get(chord_type.lower(), [0, 4, 7])
    
    @staticmethod
    def create_arpeggio(
        notes: List[int],
        pattern: str = "up",
        velocity: int = 80,
        note_duration: float = 0.25,
        start_time: float = 0.0,
        num_repeats: int = 1
    ) -> List[MIDINote]:
        """
        Create an arpeggio pattern
        
        Args:
            notes: List of MIDI note numbers
            pattern: Pattern type (up, down, up-down, random)
            velocity: Note velocity
            note_duration: Duration of each note
            start_time: Start time
            num_repeats: Number of pattern repeats
            
        Returns:
            List of MIDI notes
        """
        arp_notes = []
        
        patterns = {
            "up": notes,
            "down": list(reversed(notes)),
            "up-down": notes + list(reversed(notes[1:-1])),
        }
        
        sequence = patterns.get(pattern, notes) * num_repeats
        
        for i, pitch in enumerate(sequence):
            note = MIDINote(
                pitch=pitch,
                velocity=velocity,
                start_time=start_time + i * note_duration,
                duration=note_duration * 0.9  # Slight gap
            )
            arp_notes.append(note)
        
        return arp_notes
    
    @staticmethod
    def humanize(
        notes: List[MIDINote],
        timing_variance: float = 0.02,
        velocity_variance: int = 10
    ) -> None:
        """
        Add human feel to MIDI notes
        
        Args:
            notes: List of MIDI notes to humanize
            timing_variance: Maximum timing offset in beats
            velocity_variance: Maximum velocity variation
        """
        for note in notes:
            # Randomize timing slightly
            timing_offset = np.random.uniform(
                -timing_variance, 
                timing_variance
            )
            note.start_time += timing_offset
            
            # Randomize velocity
            velocity_offset = np.random.randint(
                -velocity_variance,
                velocity_variance + 1
            )
            note.velocity = max(1, min(127, note.velocity + velocity_offset))


class MIDIUtilities:
    """Utility functions for MIDI processing"""
    
    @staticmethod
    def note_name_to_number(note_name: str) -> int:
        """
        Convert note name to MIDI number
        
        Args:
            note_name: Note name (e.g., "C4", "A#3")
            
        Returns:
            MIDI note number
        """
        notes = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
        
        # Parse note name
        note = note_name[0].upper()
        octave = int(note_name[-1])
        
        # Handle sharps and flats
        accidental = 0
        if len(note_name) > 2:
            if "#" in note_name:
                accidental = 1
            elif "b" in note_name:
                accidental = -1
        
        midi_number = notes[note] + accidental + (octave + 1) * 12
        return max(0, min(127, midi_number))
    
    @staticmethod
    def note_number_to_name(note_number: int) -> str:
        """
        Convert MIDI number to note name
        
        Args:
            note_number: MIDI note number (0-127)
            
        Returns:
            Note name
        """
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (note_number // 12) - 1
        note = notes[note_number % 12]
        return f"{note}{octave}"
    
    @staticmethod
    def beats_to_seconds(beats: float, tempo: float) -> float:
        """Convert beats to seconds"""
        return (beats / tempo) * 60.0
    
    @staticmethod
    def seconds_to_beats(seconds: float, tempo: float) -> float:
        """Convert seconds to beats"""
        return (seconds * tempo) / 60.0
