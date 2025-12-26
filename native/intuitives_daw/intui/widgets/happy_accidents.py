"""
INTUITIVES DAW - Happy Accidents System

"Does this sound cool?" - The only rule.

This module provides dynamic, AI-inspired suggestions that encourage
experimentation and help users discover unexpected creative possibilities.
The system learns from user actions and suggests "happy accidents" that
might lead to interesting results.
"""

import random
import time
from typing import List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from intui.sgqt import *
from intui.widgets.animation import (
    AnimatedValue,
    GlowButton,
    PulseIndicator,
    TypingLabel,
)
from intlib.brand import (
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_TERTIARY,
    CHROMA_COLORS,
)
from intlib.log import LOG


class SuggestionCategory(Enum):
    """Categories of creative suggestions"""
    MELODY = "melody"
    RHYTHM = "rhythm"
    HARMONY = "harmony"
    TEXTURE = "texture"
    EFFECT = "effect"
    STRUCTURE = "structure"
    EXPERIMENT = "experiment"


@dataclass
class Suggestion:
    """A creative suggestion for the user"""
    title: str
    description: str
    category: SuggestionCategory
    action: Optional[Callable] = None
    icon: str = "💡"
    probability_boost: float = 1.0  # Higher = more likely to be shown


# Pre-defined suggestion templates
SUGGESTION_POOL = [
    # Melody suggestions
    Suggestion("Flip It", "Invert the melody - make high notes low and low notes high",
               SuggestionCategory.MELODY, icon="🔄"),
    Suggestion("Mirror Time", "Reverse the melody playback order",
               SuggestionCategory.MELODY, icon="⏪"),
    Suggestion("Drunk Walk", "Add random microtonal variations to each note",
               SuggestionCategory.MELODY, icon="🍺"),
    Suggestion("Octave Jump", "Randomly shift some notes by octaves",
               SuggestionCategory.MELODY, icon="📈"),
    Suggestion("Ghost Notes", "Add subtle velocity variations for human feel",
               SuggestionCategory.MELODY, icon="👻"),
    
    # Rhythm suggestions
    Suggestion("Shuffle It", "Apply swing/shuffle to straight rhythms",
               SuggestionCategory.RHYTHM, icon="🔀"),
    Suggestion("Euclidean", "Try a Euclidean rhythm pattern",
               SuggestionCategory.RHYTHM, icon="⭕"),
    Suggestion("Half Speed", "Double the note lengths for a slower feel",
               SuggestionCategory.RHYTHM, icon="🐢"),
    Suggestion("Stutter", "Add repeating notes for a glitch effect",
               SuggestionCategory.RHYTHM, icon="💥"),
    Suggestion("Polyrhythm", "Layer a 3-beat pattern over 4-beat",
               SuggestionCategory.RHYTHM, icon="🌀"),
    
    # Harmony suggestions
    Suggestion("Modal Shift", "Try the same melody in a different mode",
               SuggestionCategory.HARMONY, icon="🎹"),
    Suggestion("Add 7ths", "Extend all chords to 7ths for richness",
               SuggestionCategory.HARMONY, icon="7️⃣"),
    Suggestion("Parallel", "Move the harmony in parallel motion",
               SuggestionCategory.HARMONY, icon="➡️"),
    Suggestion("Chromatic", "Add chromatic passing tones",
               SuggestionCategory.HARMONY, icon="🎨"),
    Suggestion("Tritone Sub", "Try tritone substitutions on dominants",
               SuggestionCategory.HARMONY, icon="↔️"),
    
    # Texture suggestions
    Suggestion("Layer It", "Duplicate the sound an octave higher/lower",
               SuggestionCategory.TEXTURE, icon="📚"),
    Suggestion("Thin It", "Remove some notes to create space",
               SuggestionCategory.TEXTURE, icon="✂️"),
    Suggestion("Stereo Split", "Pan different notes left and right",
               SuggestionCategory.TEXTURE, icon="↔️"),
    Suggestion("Velocity Fade", "Gradually change velocity over time",
               SuggestionCategory.TEXTURE, icon="📉"),
    
    # Effect suggestions
    Suggestion("Reverse Verb", "Apply reverb to reversed audio",
               SuggestionCategory.EFFECT, icon="🌊"),
    Suggestion("Extreme EQ", "Try cutting everything below 1kHz",
               SuggestionCategory.EFFECT, icon="📻"),
    Suggestion("Bit Crush", "Add lo-fi crunch with bit reduction",
               SuggestionCategory.EFFECT, icon="💾"),
    Suggestion("Tape Stop", "Add a tape stop effect at transitions",
               SuggestionCategory.EFFECT, icon="⏹️"),
    Suggestion("Wah Auto", "Apply auto-wah synchronized to tempo",
               SuggestionCategory.EFFECT, icon="🎸"),
    
    # Structure suggestions
    Suggestion("Drop Section", "Try removing a section entirely",
               SuggestionCategory.STRUCTURE, icon="🕳️"),
    Suggestion("Double Length", "Extend the loop for more development",
               SuggestionCategory.STRUCTURE, icon="📏"),
    Suggestion("Start Late", "Begin the phrase after the downbeat",
               SuggestionCategory.STRUCTURE, icon="⏭️"),
    Suggestion("Call Response", "Split into question and answer phrases",
               SuggestionCategory.STRUCTURE, icon="🗣️"),
    
    # Experimental suggestions
    Suggestion("Random Pitch", "Replace one random note with a surprise",
               SuggestionCategory.EXPERIMENT, icon="🎲"),
    Suggestion("Wrong Key", "Intentionally play in a 'wrong' key",
               SuggestionCategory.EXPERIMENT, icon="❌"),
    Suggestion("Speed Ramp", "Gradually speed up then slow down",
               SuggestionCategory.EXPERIMENT, icon="🎢"),
    Suggestion("Negative Space", "Make silence the feature",
               SuggestionCategory.EXPERIMENT, icon="⬛"),
    Suggestion("Combine", "Merge two completely different ideas",
               SuggestionCategory.EXPERIMENT, icon="🔗"),
]


class HappyAccidentWidget(QWidget):
    """
    The main "Happy Accident" suggestion widget.
    Shows dynamic, contextual suggestions to inspire experimentation.
    """
    
    suggestion_accepted = Signal(Suggestion)
    suggestion_dismissed = Signal(Suggestion)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('happy_accident_widget')
        self.current_suggestion: Optional[Suggestion] = None
        self._suggestion_history: List[Suggestion] = []
        self._last_interaction = time.time()
        
        self._setup_ui()
        self._setup_auto_refresh()
        
    def _setup_ui(self):
        self.setMinimumHeight(80)
        self.setMaximumHeight(120)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # Pulse indicator
        self.pulse = PulseIndicator(COLOR_PRIMARY, size=10)
        layout.addWidget(self.pulse)
        
        # Content area
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        layout.addLayout(content_layout, 1)
        
        # Title with typing effect
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        content_layout.addLayout(header_layout)
        
        self.icon_label = QLabel("💡")
        self.icon_label.setObjectName('suggestion_icon')
        header_layout.addWidget(self.icon_label)
        
        self.title_label = TypingLabel()
        self.title_label.setObjectName('suggestion_title')
        header_layout.addWidget(self.title_label, 1)
        
        # Category badge
        self.category_badge = QLabel("")
        self.category_badge.setObjectName('category_badge')
        header_layout.addWidget(self.category_badge)
        
        # Description
        self.desc_label = QLabel("")
        self.desc_label.setObjectName('suggestion_desc')
        self.desc_label.setWordWrap(True)
        content_layout.addWidget(self.desc_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        layout.addLayout(btn_layout)
        
        self.try_btn = GlowButton("Try It", accent_color=COLOR_PRIMARY)
        self.try_btn.setFixedWidth(80)
        self.try_btn.clicked.connect(self._on_try)
        btn_layout.addWidget(self.try_btn)
        
        self.skip_btn = QPushButton("Skip")
        self.skip_btn.setObjectName('subtle_button')
        self.skip_btn.setFixedWidth(60)
        self.skip_btn.clicked.connect(self._on_skip)
        btn_layout.addWidget(self.skip_btn)
        
        self.new_btn = QPushButton("🎲")
        self.new_btn.setObjectName('icon_button')
        self.new_btn.setFixedSize(32, 32)
        self.new_btn.setToolTip("Get a new random suggestion")
        self.new_btn.clicked.connect(self.show_random_suggestion)
        btn_layout.addWidget(self.new_btn)
        
        # Initial suggestion
        self.show_random_suggestion()
        
    def _setup_auto_refresh(self):
        """Auto-refresh suggestions periodically when idle"""
        self._refresh_timer = QtCore.QTimer(self)
        self._refresh_timer.timeout.connect(self._check_auto_refresh)
        self._refresh_timer.start(30000)  # Check every 30 seconds
        
    def _check_auto_refresh(self):
        """Refresh suggestion if user has been idle"""
        idle_time = time.time() - self._last_interaction
        if idle_time > 60:  # 1 minute idle
            self.show_random_suggestion()
            
    def show_suggestion(self, suggestion: Suggestion):
        """Display a specific suggestion"""
        self.current_suggestion = suggestion
        self._last_interaction = time.time()
        
        # Update UI with animation
        self.icon_label.setText(suggestion.icon)
        self.title_label.type_text(suggestion.title, delay=40)
        self.desc_label.setText(suggestion.description)
        
        # Category badge styling
        category_colors = {
            SuggestionCategory.MELODY: ("#ff5c5c", "MELODY"),
            SuggestionCategory.RHYTHM: ("#ffb84c", "RHYTHM"),
            SuggestionCategory.HARMONY: ("#4cffff", "HARMONY"),
            SuggestionCategory.TEXTURE: ("#8cff4c", "TEXTURE"),
            SuggestionCategory.EFFECT: ("#8c4cff", "EFFECT"),
            SuggestionCategory.STRUCTURE: ("#4c8cff", "STRUCTURE"),
            SuggestionCategory.EXPERIMENT: ("#ff4cff", "EXPERIMENT"),
        }
        color, name = category_colors.get(
            suggestion.category, 
            ("#7c3aed", "IDEA")
        )
        self.category_badge.setText(name)
        self.category_badge.setStyleSheet(f"""
            QLabel {{
                background: {color};
                color: #0a0a0f;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            }}
        """)
        
        # Pulse animation
        self.pulse.start()
        
    def show_random_suggestion(self):
        """Show a random suggestion from the pool"""
        # Avoid repeating recent suggestions
        available = [s for s in SUGGESTION_POOL if s not in self._suggestion_history[-5:]]
        if not available:
            available = SUGGESTION_POOL.copy()
            
        # Weight by probability boost
        weights = [s.probability_boost for s in available]
        suggestion = random.choices(available, weights=weights, k=1)[0]
        
        self._suggestion_history.append(suggestion)
        self.show_suggestion(suggestion)
        
    def show_contextual_suggestion(self, category: SuggestionCategory):
        """Show a suggestion from a specific category"""
        available = [s for s in SUGGESTION_POOL if s.category == category]
        if available:
            suggestion = random.choice(available)
            self._suggestion_history.append(suggestion)
            self.show_suggestion(suggestion)
        else:
            self.show_random_suggestion()
            
    def _on_try(self):
        """User wants to try the suggestion"""
        if self.current_suggestion:
            LOG.info(f"User accepted suggestion: {self.current_suggestion.title}")
            self.suggestion_accepted.emit(self.current_suggestion)
            if self.current_suggestion.action:
                try:
                    self.current_suggestion.action()
                except Exception as e:
                    LOG.error(f"Suggestion action failed: {e}")
        self.show_random_suggestion()
        
    def _on_skip(self):
        """User skipped the suggestion"""
        if self.current_suggestion:
            LOG.info(f"User skipped suggestion: {self.current_suggestion.title}")
            self.suggestion_dismissed.emit(self.current_suggestion)
        self.show_random_suggestion()
        
    def paintEvent(self, event):
        """Custom paint for glassmorphism effect"""
        from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Glassmorphism background
        bg = QColor("#1a1a25")
        bg.setAlpha(230)
        painter.setBrush(QBrush(bg))
        painter.setPen(QPen(QColor("#2e2e3e"), 1))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        
        # Accent line on left
        accent = QColor(COLOR_PRIMARY)
        painter.setPen(QPen(QtCore.Qt.PenStyle.NoPen))
        painter.setBrush(QBrush(accent))
        painter.drawRoundedRect(0, 8, 4, self.height() - 16, 2, 2)


class SuggestionToast(QWidget):
    """
    Floating toast notification for quick suggestions.
    Appears briefly and auto-dismisses.
    """
    
    def __init__(self, suggestion: Suggestion, parent=None):
        super().__init__(parent)
        self.suggestion = suggestion
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.Tool |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(300, 60)
        
        self._opacity = AnimatedValue(0.0)
        self._y_offset = AnimatedValue(20.0)
        
        self._setup_ui()
        self._animate_in()
        
        # Auto-dismiss after 5 seconds
        QtCore.QTimer.singleShot(5000, self._animate_out)
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        icon = QLabel(self.suggestion.icon)
        icon.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon)
        
        text_layout = QVBoxLayout()
        layout.addLayout(text_layout, 1)
        
        title = QLabel(self.suggestion.title)
        title.setStyleSheet("color: #f8fafc; font-weight: bold;")
        text_layout.addWidget(title)
        
        desc = QLabel(self.suggestion.description)
        desc.setStyleSheet("color: #94a3b8; font-size: 11px;")
        desc.setWordWrap(True)
        text_layout.addWidget(desc)
        
    def _animate_in(self):
        self._opacity.set_target(1.0)
        self._y_offset.set_target(0.0)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._update_animation)
        self._timer.start(16)
        self.show()
        
    def _animate_out(self):
        self._opacity.set_target(0.0)
        self._y_offset.set_target(-20.0)
        self._timer.timeout.disconnect()
        self._timer.timeout.connect(self._update_animation_out)
        
    def _update_animation(self):
        if not self._opacity.update() and not self._y_offset.update():
            self._timer.stop()
        self.setWindowOpacity(self._opacity.value)
        # Move Y position would need different approach
        self.update()
        
    def _update_animation_out(self):
        self._opacity.update()
        self._y_offset.update()
        self.setWindowOpacity(self._opacity.value)
        if self._opacity.value < 0.01:
            self._timer.stop()
            self.close()
            self.deleteLater()
            
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        bg = QColor("#1a1a25")
        bg.setAlpha(240)
        painter.setBrush(QBrush(bg))
        painter.setPen(QPen(QColor(COLOR_PRIMARY), 1.5))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)


class QuickExperimentBar(QWidget):
    """
    Horizontal bar with one-click experiment buttons.
    Encourages rapid experimentation without deep menu diving.
    """
    
    experiment_triggered = Signal(str)  # Emits action name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('quick_experiment_bar')
        self.setFixedHeight(48)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Label
        label = QLabel("Quick:")
        label.setStyleSheet("color: #64748b; font-weight: 600;")
        layout.addWidget(label)
        
        # Quick action buttons
        experiments = [
            ("🎲", "random", "Randomize something"),
            ("🔄", "reverse", "Reverse selection"),
            ("📈", "octave_up", "Octave up"),
            ("📉", "octave_down", "Octave down"),
            ("✂️", "split", "Split notes"),
            ("🔗", "merge", "Merge notes"),
            ("🎯", "quantize", "Quantize to grid"),
            ("🌀", "shuffle", "Apply shuffle"),
        ]
        
        for icon, action, tooltip in experiments:
            btn = QPushButton(icon)
            btn.setObjectName('experiment_btn')
            btn.setFixedSize(36, 36)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda _, a=action: self._on_experiment(a))
            layout.addWidget(btn)
            
        layout.addStretch()
        
        # "Surprise Me" button
        surprise_btn = GlowButton("✨ Surprise Me", accent_color=COLOR_TERTIARY)
        surprise_btn.setToolTip("Apply a random happy accident")
        surprise_btn.clicked.connect(self._on_surprise)
        layout.addWidget(surprise_btn)
        
    def _on_experiment(self, action: str):
        LOG.info(f"Quick experiment: {action}")
        self.experiment_triggered.emit(action)
        
    def _on_surprise(self):
        # Pick a random action
        actions = ["random", "reverse", "octave_up", "octave_down", 
                   "split", "merge", "quantize", "shuffle"]
        action = random.choice(actions)
        LOG.info(f"Surprise experiment: {action}")
        self.experiment_triggered.emit(action)


LOG.info("Happy Accidents system loaded")
