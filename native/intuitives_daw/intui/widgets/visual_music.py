"""
INTUITIVES DAW - Visual Music Widget

Chromasynesthesia-enabled visual representation of music.
See your music as colors, shapes, and movement.
"""

import math
import time
from collections import deque
from typing import List, Tuple, Optional

from intui.sgqt import *
from intlib.brand import CHROMA_COLORS, COLOR_PRIMARY
from intlib.log import LOG


class NoteParticle:
    """
    PURPOSE: A transient visual entity representing a MIDI note event.
    ACTION: Animates a glowing circle that drifts and fades over its lifetime.
    MECHANISM: 
        1. Stores position, velocity (mapped to size), and color.
        2. In update(), applies physics (velocity drift) and life decay.
        3. In draw(), renders a multi-layered circle with varying opacity for a glow effect.
    """
    def __init__(self, x, y, velocity, note, color):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.note = note
        self.color = QColor(color)
        self.life = 1.0  # 0-1, fades out
        self.size = 8 + (velocity / 127.0) * 12
        self.decay_rate = 0.015
        self.vx = 0  # Drift velocity
        self.vy = -0.5  # Slight upward drift
        
    def update(self):
        self.life -= self.decay_rate
        self.x += self.vx
        self.y += self.vy
        self.size *= 0.995  # Slight shrink
        return self.life > 0
        
    def draw(self, painter):
        if self.life <= 0:
            return
            
        color = QColor(self.color)
        color.setAlphaF(self.life * 0.8)
        
        # Outer glow
        glow = QColor(self.color)
        glow.setAlphaF(self.life * 0.3)
        painter.setPen(QPen(QtCore.Qt.PenStyle.NoPen))
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(
            int(self.x - self.size),
            int(self.y - self.size),
            int(self.size * 2),
            int(self.size * 2)
        )
        
        # Core
        painter.setBrush(QBrush(color))
        core_size = self.size * 0.6
        painter.drawEllipse(
            int(self.x - core_size / 2),
            int(self.y - core_size / 2),
            int(core_size),
            int(core_size)
        )


class WaveformRing:
    """
    PURPOSE: A reactive circular pulse synchronized with audio amplitude.
    ACTION: Expands and fades an outline ring in response to audio "triggers".
    MECHANISM: 
        1. Maintains current and target radii for smooth expansion.
        2. Uses exponential decay for opacity and target radius to create a "snappy" pulse feel.
        3. Renders a QPainter drawEllipse with no brush and a colored pen.
    """
    def __init__(self, cx, cy, max_radius=100):
        self.cx = cx
        self.cy = cy
        self.max_radius = max_radius
        self.current_radius = 0
        self.target_radius = 0
        self.color = QColor(COLOR_PRIMARY)
        self.opacity = 0.0
        
    def trigger(self, level: float, color: str = None):
        """Trigger a pulse with given audio level (0-1)"""
        self.target_radius = self.max_radius * level
        self.opacity = min(1.0, level + 0.3)
        if color:
            self.color = QColor(color)
            
    def update(self):
        # Smooth interpolation
        self.current_radius += (self.target_radius - self.current_radius) * 0.15
        self.opacity *= 0.96
        self.target_radius *= 0.95
        
    def draw(self, painter):
        if self.opacity < 0.02:
            return
            
        color = QColor(self.color)
        color.setAlphaF(self.opacity * 0.5)
        
        pen = QPen(color, 2)
        painter.setPen(pen)
        painter.setBrush(QBrush(QtCore.Qt.BrushStyle.NoBrush))
        painter.drawEllipse(
            int(self.cx - self.current_radius),
            int(self.cy - self.current_radius),
            int(self.current_radius * 2),
            int(self.current_radius * 2)
        )


class ChromasynesthesiaVisualizer(QWidget):
    """
    PURPOSE: A pitch-to-color mapping visualizer (Synesthesia engine).
    ACTION: Spawns particles and rings where the color depends on the MIDI note's pitch class.
    MECHANISM: 
        1. Bridges MIDI events (note_on/off) to particle system management.
        2. Maps Note % 12 to specific color palettes (CHROMA_COLORS).
        3. Uses a 60fps local QTimer to drive animation calculations and repaints.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('chroma_visualizer')
        self.setMinimumSize(200, 150)
        
        # Visual elements
        self.particles: List[NoteParticle] = []
        self.waveform_ring = None
        self.active_notes: dict = {}  # note -> particle
        
        # Audio level history for waveform
        self.level_history = deque(maxlen=100)
        
        # Animation
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(16)  # ~60fps
        
        # Background color animation
        self._bg_hue = 0.0
        self._bg_saturation = 0.1
        
    def note_on(self, note: int, velocity: int):
        """Called when a MIDI note starts"""
        note_in_octave = note % 12
        color = CHROMA_COLORS.get(note_in_octave, COLOR_PRIMARY)
        
        # Calculate position based on pitch
        x = (note / 127.0) * self.width()
        y = self.height() * 0.5  # Start in middle
        
        particle = NoteParticle(x, y, velocity, note, color)
        self.particles.append(particle)
        self.active_notes[note] = particle
        
        # Trigger waveform ring
        if self.waveform_ring:
            self.waveform_ring.trigger(velocity / 127.0, color)
            
    def note_off(self, note: int):
        """Called when a MIDI note ends"""
        if note in self.active_notes:
            # Speed up decay
            self.active_notes[note].decay_rate = 0.05
            del self.active_notes[note]
            
    def set_audio_level(self, level: float):
        """Update with current audio level (0-1)"""
        self.level_history.append(level)
        if self.waveform_ring:
            self.waveform_ring.trigger(level * 0.5)
            
    def _animate(self):
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Update waveform ring
        if self.waveform_ring:
            self.waveform_ring.update()
            
        # Subtle background hue shift
        self._bg_hue = (self._bg_hue + 0.1) % 360
        
        self.update()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Re-center waveform ring
        self.waveform_ring = WaveformRing(
            self.width() / 2,
            self.height() / 2,
            min(self.width(), self.height()) * 0.4
        )
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background with subtle gradient
        bg = QColor("#0a0a0f")
        painter.fillRect(self.rect(), bg)
        
        # Draw level meter as background glow
        if self.level_history:
            avg_level = sum(self.level_history) / len(self.level_history)
            if avg_level > 0.01:
                glow = QColor(COLOR_PRIMARY)
                glow.setAlphaF(avg_level * 0.2)
                painter.fillRect(self.rect(), glow)
        
        # Draw waveform ring
        if self.waveform_ring:
            self.waveform_ring.draw(painter)
            
        # Draw particles
        for particle in self.particles:
            particle.draw(painter)
            
        # Draw horizontal piano roll hint
        self._draw_keyboard_hint(painter)
        
    def _draw_keyboard_hint(self, painter):
        """Draw subtle keyboard reference at bottom"""
        h = 4
        y = self.height() - h
        
        for i in range(12):
            # Is black key?
            is_black = i in [1, 3, 6, 8, 10]
            
            x = int((i / 12.0) * self.width())
            w = int(self.width() / 12)
            
            color = QColor("#1a1a25") if not is_black else QColor("#0a0a0f")
            painter.fillRect(x, y, w - 1, h, color)


class OrbitalVisualizer(QWidget):
    """
    PURPOSE: A circular geometry visualizer for musical harmony.
    ACTION: Renders notes as orbiting orbs where radius relates to octave and angle relates to pitch class.
    MECHANISM: 
        1. Maintains a list of 'orbits' dictionaries containing physics state.
        2. Calculates cartesian coordinates from polar (r, theta) for rendering.
        3. Animates a central "pulsing" sun synchronized with note velocity.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        
        # Orbital state
        self.orbits: List[dict] = []
        self.center_pulse = 0.0
        self.rotation_offset = 0.0
        
        # Animation
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(16)
        
    def add_note(self, note: int, velocity: int, duration: float = 2.0):
        """Add a note as an orbiting element"""
        note_in_octave = note % 12
        color = CHROMA_COLORS.get(note_in_octave, COLOR_PRIMARY)
        
        # Orbit radius based on octave
        octave = note // 12
        radius_ratio = 0.2 + (octave / 10.0) * 0.6
        
        # Angular position based on note in octave
        angle = (note_in_octave / 12.0) * math.pi * 2
        
        self.orbits.append({
            'note': note,
            'angle': angle,
            'radius_ratio': radius_ratio,
            'color': QColor(color),
            'size': 5 + (velocity / 127.0) * 10,
            'life': 1.0,
            'decay': 1.0 / (duration * 60),  # 60fps
            'speed': 0.02 + (127 - note) / 127.0 * 0.03,  # Lower notes slower
        })
        
        self.center_pulse = min(1.0, self.center_pulse + 0.3)
        
    def _animate(self):
        # Update orbits
        new_orbits = []
        for orbit in self.orbits:
            orbit['angle'] += orbit['speed']
            orbit['life'] -= orbit['decay']
            if orbit['life'] > 0:
                new_orbits.append(orbit)
        self.orbits = new_orbits
        
        # Update center pulse
        self.center_pulse *= 0.95
        
        # Global rotation
        self.rotation_offset += 0.002
        
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor("#0a0a0f"))
        
        cx = self.width() / 2
        cy = self.height() / 2
        max_radius = min(cx, cy) * 0.85
        
        # Draw orbit circles (subtle)
        painter.setPen(QPen(QColor("#1a1a25"), 1))
        for i in range(5):
            r = max_radius * (0.2 + i * 0.2)
            painter.drawEllipse(
                int(cx - r), int(cy - r),
                int(r * 2), int(r * 2)
            )
            
        # Draw center with pulse
        center_size = 20 + self.center_pulse * 30
        center_color = QColor(COLOR_PRIMARY)
        center_color.setAlphaF(0.3 + self.center_pulse * 0.5)
        painter.setPen(QPen(QtCore.Qt.PenStyle.NoPen))
        painter.setBrush(QBrush(center_color))
        painter.drawEllipse(
            int(cx - center_size / 2),
            int(cy - center_size / 2),
            int(center_size),
            int(center_size)
        )
        
        # Draw orbiting notes
        for orbit in self.orbits:
            angle = orbit['angle'] + self.rotation_offset
            radius = max_radius * orbit['radius_ratio']
            
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            
            # Color with fade
            color = QColor(orbit['color'])
            color.setAlphaF(orbit['life'] * 0.8)
            
            # Glow
            glow = QColor(orbit['color'])
            glow.setAlphaF(orbit['life'] * 0.3)
            painter.setBrush(QBrush(glow))
            size = orbit['size'] * 1.5
            painter.drawEllipse(
                int(x - size), int(y - size),
                int(size * 2), int(size * 2)
            )
            
            # Core
            painter.setBrush(QBrush(color))
            size = orbit['size']
            painter.drawEllipse(
                int(x - size / 2), int(y - size / 2),
                int(size), int(size)
            )


class SpectrumBars(QWidget):
    """
    PURPOSE: A standard multi-band frequency analyzer with themed aesthetics.
    ACTION: Displays vertical bars that jump with frequency intensity and slowly decay with peak-hold physics.
    MECHANISM: 
        1. Interpolates bar heights toward target levels derived from FFT analysis.
        2. Uses QLinearGradients for each bar to match the Chromasynesthesia color scheme.
        3. Features "falling" peak indicators at the top of each bar.
    """
    def __init__(self, num_bars=12, parent=None):
        super().__init__(parent)
        self.num_bars = num_bars
        self.levels = [0.0] * num_bars
        self.targets = [0.0] * num_bars
        self.peaks = [0.0] * num_bars
        
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(16)
        
    def set_levels(self, levels: List[float]):
        """Set target levels for each bar (0-1)"""
        for i, level in enumerate(levels[:self.num_bars]):
            self.targets[i] = level
            if level > self.peaks[i]:
                self.peaks[i] = level
                
    def _animate(self):
        for i in range(self.num_bars):
            # Smooth interpolation
            self.levels[i] += (self.targets[i] - self.levels[i]) * 0.3
            # Peak decay
            self.peaks[i] *= 0.98
            # Target decay
            self.targets[i] *= 0.9
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor("#0a0a0f"))
        
        bar_width = self.width() / self.num_bars
        gap = 2
        
        for i in range(self.num_bars):
            # Get chromasynesthesia color for this bar
            color_hex = CHROMA_COLORS.get(i, COLOR_PRIMARY)
            color = QColor(color_hex)
            
            x = int(i * bar_width + gap)
            w = int(bar_width - gap * 2)
            
            # Bar height
            h = int(self.levels[i] * self.height() * 0.9)
            y = self.height() - h
            
            # Gradient fill
            gradient = QLinearGradient(x, self.height(), x, y)
            color_dark = QColor(color)
            color_dark.setAlphaF(0.4)
            gradient.setColorAt(0, color_dark)
            gradient.setColorAt(1, color)
            
            painter.setPen(QPen(QtCore.Qt.PenStyle.NoPen))
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(x, y, w, h, 2, 2)
            
            # Peak indicator
            peak_h = int(self.peaks[i] * self.height() * 0.9)
            peak_y = self.height() - peak_h
            if peak_h > h + 4:
                painter.fillRect(x, peak_y, w, 3, color)


class VisualizerSelector(QWidget):
    """
    PURPOSE: A container for switching between various visualization modes.
    ACTION: Provides a toggle interface to select between Particle, Orbital, and Spectrum views.
    MECHANISM: Uses a QStackedWidget indexed by a set of QPushButtons. Forwards incoming data to all sub-visualizers.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('visualizer_selector')
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Selector bar
        selector = QHBoxLayout()
        selector.setSpacing(4)
        layout.addLayout(selector)
        
        self.buttons = []
        visualizers = [
            ("🌈", "Particles", "Note particles with chromasynesthesia colors"),
            ("🔮", "Orbital", "Notes orbit around a central point"),
            ("📊", "Spectrum", "Frequency spectrum visualization"),
        ]
        
        for i, (icon, name, tooltip) in enumerate(visualizers):
            btn = QPushButton(f"{icon} {name}")
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda _, idx=i: self._select(idx))
            selector.addWidget(btn)
            self.buttons.append(btn)
            
        self.buttons[0].setChecked(True)
        
        # Stacked visualizers
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)
        
        self.chroma_viz = ChromasynesthesiaVisualizer()
        self.orbital_viz = OrbitalVisualizer()
        self.spectrum_viz = SpectrumBars()
        
        self.stack.addWidget(self.chroma_viz)
        self.stack.addWidget(self.orbital_viz)
        self.stack.addWidget(self.spectrum_viz)
        
    def _select(self, index):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        self.stack.setCurrentIndex(index)
        
    def note_on(self, note: int, velocity: int):
        """Forward note to active visualizer"""
        self.chroma_viz.note_on(note, velocity)
        self.orbital_viz.add_note(note, velocity)
        
    def note_off(self, note: int):
        """Forward note off to active visualizer"""
        self.chroma_viz.note_off(note)
        
    def set_audio_level(self, level: float):
        """Forward audio level"""
        self.chroma_viz.set_audio_level(level)
        
    def set_spectrum(self, levels: List[float]):
        """Set spectrum levels"""
        self.spectrum_viz.set_levels(levels)


LOG.info("Visual music widgets loaded")
