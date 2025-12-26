"""
INTUITIVES DAW - Keyboard Shortcuts Handler

"Does this sound cool?" - The only rule.

This module provides centralized keyboard shortcut handling for
the Intuitives-specific features like Scale Lock and Happy Accidents.
"""

from typing import Callable, Dict, Optional, Set
from intlib.log import LOG
from intlib.scale_lock import get_scale_lock, ScaleType, NOTE_NAMES
from intlib.mutation import get_mutation_engine, MUTATION_PRESETS


# ============================================================================
# SHORTCUT DEFINITIONS
# ============================================================================

class IntuitivesShortcuts:
    """
    Keyboard shortcuts for Intuitives-specific features.
    
    These are designed for quick access during creative flow.
    """
    
    # Mutation / Happy Accidents
    KEY_MUTATE = 'm'           # Gentle mutation
    KEY_MUTATE_WILD = 'M'      # Wild mutation (Shift+M)  
    KEY_HAPPY_ACCIDENT = 'h'   # Happy accident
    KEY_UNDO_MUTATION = 'z'    # Undo last mutation (when not Ctrl)
    
    # Scale Lock
    KEY_SCALE_TOGGLE = 's'     # Toggle scale lock
    KEY_SCALE_NEXT = '.'       # Next scale type
    KEY_SCALE_PREV = ','       # Previous scale type
    KEY_ROOT_UP = ']'          # Move root up a semitone
    KEY_ROOT_DOWN = '['        # Move root down a semitone
    
    # Quick Scale Presets (Number keys with Alt)
    SCALE_PRESET_KEYS = {
        '1': (0, ScaleType.PENTATONIC_MINOR),   # C Pentatonic Minor (Easy)
        '2': (9, ScaleType.BLUES),              # A Blues
        '3': (0, ScaleType.MAJOR),              # C Major
        '4': (9, ScaleType.MINOR),              # A Minor
        '5': (0, ScaleType.DORIAN),             # C Dorian
        '6': (7, ScaleType.MIXOLYDIAN),         # G Mixolydian
        '7': (0, ScaleType.CHROMATIC),          # No scale lock
    }
    
    def __init__(
        self,
        on_visual_feedback: Optional[Callable[[str, str], None]] = None,
        get_current_parameters: Optional[Callable[[], Dict[str, float]]] = None,
        set_parameters: Optional[Callable[[Dict[str, float]], None]] = None,
    ):
        """
        Initialize shortcuts handler.
        
        Args:
            on_visual_feedback: Callback(action, message) for UI feedback
            get_current_parameters: Function to get current track parameters
            set_parameters: Function to apply mutated parameters
        """
        self.on_visual_feedback = on_visual_feedback
        self.get_current_parameters = get_current_parameters
        self.set_parameters = set_parameters
        
        # Track scale types for cycling
        self._scale_types = list(ScaleType)
        self._current_scale_index = 0
        
        # Parameter snapshot before mutation
        self._last_params: Optional[Dict[str, float]] = None
        
        LOG.info("IntuitivesShortcuts initialized")
    
    def _feedback(self, action: str, message: str):
        """Send visual feedback."""
        if self.on_visual_feedback:
            try:
                self.on_visual_feedback(action, message)
            except Exception as e:
                LOG.warning(f"Feedback callback error: {e}")
        LOG.info(f"[{action}] {message}")
    
    def handle_key(
        self,
        key: str,
        modifiers: Set[str] = None,
    ) -> bool:
        """
        Handle a key press for Intuitives features.
        
        Args:
            key: The pressed key character
            modifiers: Set of active modifiers ('ctrl', 'alt', 'shift')
            
        Returns:
            True if the key was handled, False otherwise
        """
        modifiers = modifiers or set()
        
        # Don't intercept Ctrl+key combos (standard shortcuts)
        if 'ctrl' in modifiers:
            return False
        
        # Scale preset keys (Alt+number)
        if 'alt' in modifiers and key in self.SCALE_PRESET_KEYS:
            root, scale = self.SCALE_PRESET_KEYS[key]
            get_scale_lock().set_scale(root, scale)
            self._feedback(
                "scale",
                f"Scale: {NOTE_NAMES[root]} {scale.value}"
            )
            return True
        
        # Mutation keys
        if key == self.KEY_MUTATE:
            return self._handle_mutate(wild=False)
        
        if key == self.KEY_MUTATE_WILD:
            return self._handle_mutate(wild=True)
        
        if key == self.KEY_HAPPY_ACCIDENT:
            return self._handle_happy_accident()
        
        if key == self.KEY_UNDO_MUTATION:
            return self._handle_undo_mutation()
        
        # Scale lock keys
        if key == self.KEY_SCALE_TOGGLE:
            return self._handle_scale_toggle()
        
        if key == self.KEY_SCALE_NEXT:
            return self._handle_scale_cycle(1)
        
        if key == self.KEY_SCALE_PREV:
            return self._handle_scale_cycle(-1)
        
        if key == self.KEY_ROOT_UP:
            return self._handle_root_change(1)
        
        if key == self.KEY_ROOT_DOWN:
            return self._handle_root_change(-1)
        
        return False
    
    def _handle_mutate(self, wild: bool = False) -> bool:
        """Handle mutation key press."""
        if not self.get_current_parameters or not self.set_parameters:
            self._feedback("error", "Mutation not available (no parameter access)")
            return True
        
        try:
            # Get current parameters
            params = self.get_current_parameters()
            if not params:
                self._feedback("error", "No parameters to mutate")
                return True
            
            # Save for undo
            self._last_params = params.copy()
            engine = get_mutation_engine()
            engine.save_snapshot(params, "Before mutation")
            
            # Apply mutation
            if wild:
                mutated = engine.mutate_parameters(params, amount=0.25)
                self._feedback("mutation", "🎲 WILD MUTATION applied!")
            else:
                mutated = engine.mutate_parameters(params, amount=0.05)
                self._feedback("mutation", "🎲 Gentle mutation applied")
            
            # Apply mutated parameters
            self.set_parameters(mutated)
            return True
            
        except Exception as e:
            LOG.exception(e)
            self._feedback("error", f"Mutation error: {e}")
            return True
    
    def _handle_happy_accident(self) -> bool:
        """Handle happy accident key press."""
        if not self.get_current_parameters or not self.set_parameters:
            self._feedback("error", "Happy Accident not available")
            return True
        
        try:
            params = self.get_current_parameters()
            if not params:
                return True
            
            # Save for undo
            self._last_params = params.copy()
            engine = get_mutation_engine()
            engine.save_snapshot(params, "Before happy accident")
            
            # Apply happy accident
            mutated = engine.happy_accident(params, intensity=0.7)
            self.set_parameters(mutated)
            
            self._feedback("accident", "💥 HAPPY ACCIDENT! 🎉")
            return True
            
        except Exception as e:
            LOG.exception(e)
            return True
    
    def _handle_undo_mutation(self) -> bool:
        """Handle undo mutation key press."""
        if not self.set_parameters:
            return False
        
        # Try to restore from mutation engine
        engine = get_mutation_engine()
        restored = engine.restore_snapshot(-1)
        
        if restored:
            self.set_parameters(restored)
            self._feedback("undo", "↩ Mutation undone")
            return True
        
        # Fall back to last params
        if self._last_params:
            self.set_parameters(self._last_params)
            self._feedback("undo", "↩ Parameters restored")
            return True
        
        self._feedback("undo", "Nothing to undo")
        return True
    
    def _handle_scale_toggle(self) -> bool:
        """Toggle scale lock on/off."""
        sl = get_scale_lock()
        sl.enabled = not sl.enabled
        
        if sl.enabled:
            self._feedback(
                "scale",
                f"🎹 Scale Lock ON: {NOTE_NAMES[sl.root_note]} {sl.scale_type.value}"
            )
        else:
            self._feedback("scale", "🎹 Scale Lock OFF (Free play)")
        
        return True
    
    def _handle_scale_cycle(self, direction: int) -> bool:
        """Cycle through scale types."""
        sl = get_scale_lock()
        
        current_idx = self._scale_types.index(sl.scale_type)
        new_idx = (current_idx + direction) % len(self._scale_types)
        new_scale = self._scale_types[new_idx]
        
        sl.set_scale(sl.root_note, new_scale)
        self._feedback(
            "scale",
            f"Scale: {NOTE_NAMES[sl.root_note]} {new_scale.value}"
        )
        return True
    
    def _handle_root_change(self, semitones: int) -> bool:
        """Change the scale root note."""
        sl = get_scale_lock()
        new_root = (sl.root_note + semitones) % 12
        sl.set_scale(new_root, sl.scale_type)
        
        self._feedback(
            "scale",
            f"Root: {NOTE_NAMES[new_root]} {sl.scale_type.value}"
        )
        return True
    
    def get_help_text(self) -> str:
        """Get help text for available shortcuts."""
        return """
╔══════════════════════════════════════════════════════════════╗
║                 INTUITIVES SHORTCUTS                         ║
╠══════════════════════════════════════════════════════════════╣
║  MUTATION / HAPPY ACCIDENTS                                  ║
║  ─────────────────────────────────────────────────────────   ║
║  M        Gentle mutation (±5%)                              ║
║  Shift+M  Wild mutation (±25%)                               ║
║  H        Happy Accident (extreme randomization)             ║
║  Z        Undo last mutation                                 ║
║                                                              ║
║  SCALE LOCK (No-Theory Mode)                                 ║
║  ─────────────────────────────────────────────────────────   ║
║  S        Toggle scale lock on/off                           ║
║  . / ,    Cycle through scale types                          ║
║  ] / [    Change root note up/down                           ║
║                                                              ║
║  SCALE PRESETS (Alt + Number)                                ║
║  ─────────────────────────────────────────────────────────   ║
║  Alt+1    C Pentatonic Minor (Easy Mode)                     ║
║  Alt+2    A Blues                                            ║
║  Alt+3    C Major (Pop)                                      ║
║  Alt+4    A Minor (Sad)                                      ║
║  Alt+5    C Dorian (Jazz)                                    ║
║  Alt+6    G Mixolydian                                       ║
║  Alt+7    Chromatic (No correction)                          ║
╚══════════════════════════════════════════════════════════════╝
"""


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_shortcuts: Optional[IntuitivesShortcuts] = None


def get_shortcuts() -> IntuitivesShortcuts:
    """Get the global shortcuts instance."""
    global _shortcuts
    if _shortcuts is None:
        _shortcuts = IntuitivesShortcuts()
    return _shortcuts


def init_shortcuts(
    on_visual_feedback: Optional[Callable[[str, str], None]] = None,
    get_current_parameters: Optional[Callable[[], Dict[str, float]]] = None,
    set_parameters: Optional[Callable[[Dict[str, float]], None]] = None,
) -> IntuitivesShortcuts:
    """Initialize the global shortcuts with callbacks."""
    global _shortcuts
    _shortcuts = IntuitivesShortcuts(
        on_visual_feedback=on_visual_feedback,
        get_current_parameters=get_current_parameters,
        set_parameters=set_parameters,
    )
    return _shortcuts
