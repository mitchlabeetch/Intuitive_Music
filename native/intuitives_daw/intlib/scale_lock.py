"""
INTUITIVES DAW - Scale Lock / No-Theory Mode

"Does this sound cool?" - The only rule.

This module provides automatic scale correction for MIDI input,
enabling users to play music without knowing theory. Wrong notes
are automatically corrected to the nearest note in the selected scale.

Features:
- Scale Lock: Auto-correct notes to selected scale
- Visual Feedback: Flash UI when corrections occur
- Learning Mode: Gradual reduction of correction strength
- Smart Detection: Suggest scales based on played notes
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set, Tuple, Callable
import random

from intlib.log import LOG


# ============================================================================
# MUSICAL SCALES
# ============================================================================

class ScaleType(Enum):
    """Available musical scales."""
    # Common scales
    MAJOR = "major"
    MINOR = "minor"
    HARMONIC_MINOR = "harmonic_minor"
    MELODIC_MINOR = "melodic_minor"
    
    # Modes
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    AEOLIAN = "aeolian"
    LOCRIAN = "locrian"
    
    # Pentatonic
    PENTATONIC_MAJOR = "pentatonic_major"
    PENTATONIC_MINOR = "pentatonic_minor"
    
    # Blues & Jazz
    BLUES = "blues"
    BEBOP = "bebop"
    WHOLE_TONE = "whole_tone"
    
    # World scales
    JAPANESE = "japanese"
    ARABIC = "arabic"
    HUNGARIAN = "hungarian"
    
    # Experimental - for "rule-free" exploration
    CHROMATIC = "chromatic"  # No correction
    RANDOM = "random"  # Random selection per note


# Scale intervals (semitones from root)
SCALE_INTERVALS = {
    ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11],
    ScaleType.MINOR: [0, 2, 3, 5, 7, 8, 10],
    ScaleType.HARMONIC_MINOR: [0, 2, 3, 5, 7, 8, 11],
    ScaleType.MELODIC_MINOR: [0, 2, 3, 5, 7, 9, 11],
    
    ScaleType.DORIAN: [0, 2, 3, 5, 7, 9, 10],
    ScaleType.PHRYGIAN: [0, 1, 3, 5, 7, 8, 10],
    ScaleType.LYDIAN: [0, 2, 4, 6, 7, 9, 11],
    ScaleType.MIXOLYDIAN: [0, 2, 4, 5, 7, 9, 10],
    ScaleType.AEOLIAN: [0, 2, 3, 5, 7, 8, 10],
    ScaleType.LOCRIAN: [0, 1, 3, 5, 6, 8, 10],
    
    ScaleType.PENTATONIC_MAJOR: [0, 2, 4, 7, 9],
    ScaleType.PENTATONIC_MINOR: [0, 3, 5, 7, 10],
    
    ScaleType.BLUES: [0, 3, 5, 6, 7, 10],
    ScaleType.BEBOP: [0, 2, 4, 5, 7, 9, 10, 11],
    ScaleType.WHOLE_TONE: [0, 2, 4, 6, 8, 10],
    
    ScaleType.JAPANESE: [0, 1, 5, 7, 8],
    ScaleType.ARABIC: [0, 1, 4, 5, 7, 8, 11],
    ScaleType.HUNGARIAN: [0, 2, 3, 6, 7, 8, 11],
    
    ScaleType.CHROMATIC: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    ScaleType.RANDOM: [0, 2, 4, 5, 7, 9, 11],  # Falls back to major
}

# Note names for display
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


# ============================================================================
# SCALE LOCK PROCESSOR
# ============================================================================

@dataclass
class CorrectionEvent:
    """Record of a note correction."""
    original_note: int
    corrected_note: int
    timestamp: float
    was_corrected: bool


class ScaleLock:
    """
    Scale Lock - Automatic note correction for No-Theory Mode.
    
    This class intercepts MIDI notes and corrects them to the nearest
    note in the selected scale, enabling anyone to play "correct" music.
    """
    
    def __init__(
        self,
        root_note: int = 0,  # C
        scale_type: ScaleType = ScaleType.PENTATONIC_MINOR,
        enabled: bool = True,
        correction_strength: float = 1.0,
        learning_mode: bool = False,
        on_correction: Optional[Callable[[int, int], None]] = None,
    ):
        """
        PURPOSE: Initializes the ScaleLock processor with specific musical and behavioral parameters.
        ACTION: Sets the root note, scale type, and correction logic, then initializes internal counters and caches.
        MECHANISM: 
            1. Assigns initial state variables.
            2. Calls _update_scale_cache() to generate valid note sets.
            3. Sets up history and learning mode trackers.
        """
        self.root_note = root_note
        self.scale_type = scale_type
        self.enabled = enabled
        self.correction_strength = correction_strength
        self.learning_mode = learning_mode
        self.on_correction = on_correction
        
        # Learning mode state
        self._correct_streak = 0
        self._learning_progress = 0.0
        
        # Statistics
        self.total_notes = 0
        self.corrected_notes = 0
        self.correction_history: List[CorrectionEvent] = []
        
        # Cache the current scale notes
        self._scale_notes: Set[int] = set()
        self._update_scale_cache()
        
        LOG.info(
            f"ScaleLock initialized: {NOTE_NAMES[root_note]} "
            f"{scale_type.value}, enabled={enabled}"
        )
    
    def _update_scale_cache(self):
        """
        PURPOSE: Pre-calculates all valid MIDI notes for the current scale configuration.
        ACTION: Populates the internal _scale_notes set with every valid semitone across all 11 MIDI octaves.
        MECHANISM: Iterates through 11 octaves and applies scale intervals relative to the root note, filtering for the 0-127 range.
        """
        intervals = SCALE_INTERVALS.get(self.scale_type, SCALE_INTERVALS[ScaleType.MAJOR])
        self._scale_notes = set()
        
        # Generate all valid notes across all octaves
        for octave in range(11):  # MIDI octaves
            for interval in intervals:
                note = (octave * 12) + self.root_note + interval
                if 0 <= note <= 127:
                    self._scale_notes.add(note)
    
    def set_scale(self, root_note: int, scale_type: ScaleType):
        """
        PURPOSE: Updates the active musical scale and refreshes the correction logic.
        ACTION: Updates internal root and scale parameters and rebuilds the valid note cache.
        MECHANISM: Sets root_note and scale_type, then invokes _update_scale_cache().
        """
        self.root_note = root_note % 12
        self.scale_type = scale_type
        self._update_scale_cache()
        LOG.info(f"Scale changed to: {NOTE_NAMES[self.root_note]} {scale_type.value}")
    
    def is_in_scale(self, note: int) -> bool:
        """
        PURPOSE: Determines if a given MIDI note belongs to the current active scale.
        ACTION: Returns a boolean indicating membership.
        MECHANISM: Checks if the note exists in the pre-calculated _scale_notes set (always True for Chromatic).
        """
        if self.scale_type == ScaleType.CHROMATIC:
            return True
        return note in self._scale_notes
    
    def find_nearest_in_scale(self, note: int) -> int:
        """
        PURPOSE: Identifies the musically closest valid note when an input falls outside the current scale.
        ACTION: Returns a corrected MIDI note number.
        MECHANISM: 
            1. Checks for exact matches first.
            2. For RANDOM mode, picks a random direction and searches linearly.
            3. For standard modes, searches outwards in both directions simultaneously, with a slight preference for lower notes to maintain gravity.
        """
        if note in self._scale_notes:
            return note
        
        if self.scale_type == ScaleType.CHROMATIC:
            return note
        
        # For RANDOM scale type, pick a random direction
        if self.scale_type == ScaleType.RANDOM:
            direction = random.choice([-1, 1])
            offset = 0
            while True:
                offset += 1
                if direction > 0:
                    candidate = note + offset
                else:
                    candidate = note - offset
                if candidate in self._scale_notes and 0 <= candidate <= 127:
                    return candidate
                if offset > 12:  # Failsafe
                    return note
        
        # Standard nearest-note algorithm
        # Search both directions simultaneously
        for offset in range(1, 13):
            # Prefer going down slightly (more common in music)
            if (note - offset) in self._scale_notes:
                return note - offset
            if (note + offset) in self._scale_notes:
                return note + offset
        
        # Failsafe: return original note
        return note
    
    def process_note(self, note: int, velocity: int = 100) -> Tuple[int, bool]:
        """
        PURPOSE: The core MIDI event transformer that enforces scale locking.
        ACTION: Processes an incoming note and returns a corrected version along with a status flag.
        MECHANISM: 
            1. Bypasses if disabled or scale is Chromatic.
            2. Validates against the current scale.
            3. If invalid, applies correction probability (strength) and finds the nearest valid note.
            4. Updates statistics and invokes visual feedback callbacks.
        """
        self.total_notes += 1
        
        # If disabled or chromatic, pass through
        if not self.enabled or self.scale_type == ScaleType.CHROMATIC:
            return note, False
        
        # Check if already in scale
        if self.is_in_scale(note):
            self._correct_streak += 1
            self._update_learning_progress()
            return note, False
        
        # Apply correction strength (probabilistic correction)
        if self.correction_strength < 1.0:
            if random.random() > self.correction_strength:
                return note, False
        
        # Find corrected note
        corrected = self.find_nearest_in_scale(note)
        was_corrected = corrected != note
        
        if was_corrected:
            self.corrected_notes += 1
            self._correct_streak = 0
            
            # Record correction
            import time
            event = CorrectionEvent(
                original_note=note,
                corrected_note=corrected,
                timestamp=time.time(),
                was_corrected=True
            )
            self.correction_history.append(event)
            
            # Keep only last 100 corrections
            if len(self.correction_history) > 100:
                self.correction_history = self.correction_history[-100:]
            
            # Trigger callback for visual feedback
            if self.on_correction:
                try:
                    self.on_correction(note, corrected)
                except Exception as e:
                    LOG.warning(f"Correction callback error: {e}")
            
            LOG.debug(
                f"Scale Lock: {NOTE_NAMES[note % 12]} -> "
                f"{NOTE_NAMES[corrected % 12]} "
                f"(streak: {self._correct_streak})"
            )
        
        return corrected, was_corrected
    
    def _update_learning_progress(self):
        """
        PURPOSE: Gradually reduces the AI "assistance" (correction strength) as the user plays more valid notes.
        ACTION: Increments learning progress and decrements correction strength.
        MECHANISM: Tracks 'correct streaks' and adjusts self.correction_strength every 10 notes, capping the reduction at 50% of original assistance.
        """
        if not self.learning_mode:
            return
        
        # Every 10 correct notes, reduce correction strength slightly
        if self._correct_streak > 0 and self._correct_streak % 10 == 0:
            self._learning_progress = min(1.0, self._learning_progress + 0.05)
            new_strength = max(0.0, 1.0 - self._learning_progress * 0.5)
            
            if new_strength != self.correction_strength:
                self.correction_strength = new_strength
                LOG.info(
                    f"Learning Mode: Correction strength reduced to "
                    f"{self.correction_strength:.1%}"
                )
    
    def get_scale_notes(self, octave: int = 4) -> List[int]:
        """
        PURPOSE: Provides a list of valid MIDI note numbers for a specific octave in the current scale.
        ACTION: Returns an integer list of notes.
        MECHANISM: Calculates the starting pitch for the octave and applies intervals from SCALE_INTERVALS.
        """
        intervals = SCALE_INTERVALS.get(self.scale_type, SCALE_INTERVALS[ScaleType.MAJOR])
        base_note = (octave * 12) + self.root_note
        return [base_note + i for i in intervals if 0 <= base_note + i <= 127]
    
    def get_statistics(self) -> dict:
        """
        PURPOSE: Summarizes the efficacy and activity of the Scale Lock system.
        ACTION: Returns a dictionary of formatted strings and raw counters.
        MECHANISM: Calculates correction rates and retrieves strength/progress metrics for display in the UI.
        """
        correction_rate = (
            self.corrected_notes / self.total_notes * 100
            if self.total_notes > 0 else 0
        )
        return {
            "total_notes": self.total_notes,
            "corrected_notes": self.corrected_notes,
            "correction_rate": f"{correction_rate:.1f}%",
            "current_streak": self._correct_streak,
            "learning_progress": f"{self._learning_progress:.1%}",
            "correction_strength": f"{self.correction_strength:.1%}",
        }
    
    def suggest_scale(self, played_notes: List[int]) -> List[Tuple[ScaleType, int, float]]:
        """
        PURPOSE: Analyzes performance history to recommend the most suitable musical scale.
        ACTION: Returns an ordered list of potential scales with match confidence scores.
        MECHANISM: 
            1. Converts input notes to pitch classes (0-11).
            2. Iterates through all known scales and root positions.
            3. Intersects played pitches with scale pitches to calculate a match percentage.
            4. Filters results above a 70% threshold and sorts by confidence.
        """
        if not played_notes:
            return []
        
        # Convert to pitch classes (0-11)
        pitch_classes = set(note % 12 for note in played_notes)
        
        suggestions = []
        
        for scale_type in ScaleType:
            if scale_type in (ScaleType.CHROMATIC, ScaleType.RANDOM):
                continue
            
            intervals = SCALE_INTERVALS[scale_type]
            
            # Try each possible root note
            for root in range(12):
                scale_pitches = set((root + i) % 12 for i in intervals)
                
                # Calculate match percentage
                matches = len(pitch_classes & scale_pitches)
                total = len(pitch_classes)
                match_pct = matches / total if total > 0 else 0
                
                if match_pct >= 0.7:  # At least 70% match
                    suggestions.append((scale_type, root, match_pct))
        
        # Sort by match percentage descending
        suggestions.sort(key=lambda x: x[2], reverse=True)
        return suggestions[:5]  # Top 5 suggestions


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

# Global scale lock instance for easy access
_scale_lock: Optional[ScaleLock] = None


def get_scale_lock() -> ScaleLock:
    """
    PURPOSE: Safe accessor for the global ScaleLock singleton.
    ACTION: Returns the active ScaleLock instance, creating it if it doesn't exist.
    MECHANISM: Uses a lazy-instantiation pattern inside the global scope.
    """
    global _scale_lock
    if _scale_lock is None:
        _scale_lock = ScaleLock()
    return _scale_lock


def set_scale_lock(scale_lock: ScaleLock):
    """
    PURPOSE: Allows manual override/injection of a specific ScaleLock instance.
    ACTION: Replaces the current global instance.
    MECHANISM: Assigns the provided object to the global _scale_lock variable.
    """
    global _scale_lock
    _scale_lock = scale_lock


def process_midi_note(note: int, velocity: int = 100) -> Tuple[int, bool]:
    """
    PURPOSE: One-line interface for scale correction from external modules.
    ACTION: Runs a MIDI note through the global processor.
    MECHANISM: Calls process_note() on the instance returned by get_scale_lock().
    """
    return get_scale_lock().process_note(note, velocity)


# ============================================================================
# QUICK SCALE PRESETS
# ============================================================================

SCALE_PRESETS = {
    "Easy Mode (C Pentatonic)": (0, ScaleType.PENTATONIC_MINOR),
    "Blues (A Blues)": (9, ScaleType.BLUES),
    "Pop (C Major)": (0, ScaleType.MAJOR),
    "Sad (A Minor)": (9, ScaleType.MINOR),
    "Jazz (G Mixolydian)": (7, ScaleType.MIXOLYDIAN),
    "Middle Eastern (D Arabic)": (2, ScaleType.ARABIC),
    "Asian (E Japanese)": (4, ScaleType.JAPANESE),
    "Experimental (Whole Tone)": (0, ScaleType.WHOLE_TONE),
    "No Rules (Chromatic)": (0, ScaleType.CHROMATIC),
}


def apply_preset(preset_name: str) -> bool:
    """
    PURPOSE: Quickly configures the DAW for a specific musical style.
    ACTION: Applications a root note and scale type based on a descriptive name string.
    MECHANISM: Looks up the name in SCALE_PRESETS and invokes set_scale() on the global instance if found.
    """
    if preset_name in SCALE_PRESETS:
        root, scale = SCALE_PRESETS[preset_name]
        get_scale_lock().set_scale(root, scale)
        return True
    return False
