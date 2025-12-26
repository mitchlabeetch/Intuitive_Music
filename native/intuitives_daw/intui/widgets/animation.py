"""
INTUITIVES DAW - Animation Utilities

Smooth, modern animations for a premium DAW experience.
Performance-optimized with 60fps targets.
"""

from intui.sgqt import *
from intlib.log import LOG


class AnimatedValue:
    """
    Smooth value interpolation with easing.
    Used for animating UI properties like opacity, position, size.
    """
    
    # Easing functions
    EASE_LINEAR = 'linear'
    EASE_IN_OUT = 'ease_in_out'
    EASE_OUT = 'ease_out'
    EASE_OUT_BACK = 'ease_out_back'  # Slight overshoot
    EASE_SPRING = 'spring'
    
    def __init__(self, initial_value=0.0, speed=0.12, easing='ease_out'):
        self.current = initial_value
        self.target = initial_value
        self.speed = speed
        self.easing = easing
        self.velocity = 0.0  # For spring physics
        
    def set_target(self, value):
        """Set the target value to animate towards"""
        self.target = value
        
    def update(self) -> bool:
        """
        Update the current value towards target.
        Returns True if still animating, False if complete.
        """
        if abs(self.current - self.target) < 0.001:
            self.current = self.target
            self.velocity = 0.0
            return False
            
        if self.easing == self.EASE_LINEAR:
            delta = (self.target - self.current) * self.speed
            self.current += delta
            
        elif self.easing == self.EASE_IN_OUT:
            # Smoothstep-like easing
            t = abs(self.target - self.current) / max(abs(self.target - self.current), 0.01)
            t = t * t * (3 - 2 * t)
            self.current += (self.target - self.current) * self.speed * t
            
        elif self.easing == self.EASE_OUT:
            # Exponential ease out
            self.current += (self.target - self.current) * self.speed
            
        elif self.easing == self.EASE_OUT_BACK:
            # Overshoot then settle
            self.current += (self.target - self.current) * self.speed * 1.1
            
        elif self.easing == self.EASE_SPRING:
            # Spring physics simulation
            stiffness = 0.15
            damping = 0.75
            force = (self.target - self.current) * stiffness
            self.velocity = (self.velocity + force) * damping
            self.current += self.velocity
            
        return True
    
    @property
    def value(self):
        return self.current
        
    def snap(self, value):
        """Instantly set both current and target"""
        self.current = value
        self.target = value
        self.velocity = 0.0


class AnimatedWidget(QWidget):
    """
    Base class for widgets with built-in animation support.
    Provides fade, slide, and scale animations.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Animation values
        self._opacity = AnimatedValue(1.0)
        self._scale = AnimatedValue(1.0)
        self._slide_x = AnimatedValue(0.0)
        self._slide_y = AnimatedValue(0.0)
        
        # Animation timer (shared for performance)
        self._anim_timer = QtCore.QTimer(self)
        self._anim_timer.timeout.connect(self._on_animate)
        self._anim_active = False
        
        # Graphics effect for opacity
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        
    def _start_animation(self):
        """Start the animation timer if not already running"""
        if not self._anim_active:
            self._anim_active = True
            self._anim_timer.start(16)  # ~60fps
            
    def _on_animate(self):
        """Update all animation values"""
        still_animating = False
        
        if self._opacity.update():
            self._opacity_effect.setOpacity(self._opacity.value)
            still_animating = True
            
        # Add scale/slide updates as needed
        if self._slide_x.update() or self._slide_y.update():
            still_animating = True
            
        if self._scale.update():
            still_animating = True
            
        if not still_animating:
            self._anim_timer.stop()
            self._anim_active = False
            
        self.update()
        
    def fade_in(self, duration_hint=200):
        """Animate opacity from 0 to 1"""
        self._opacity.snap(0.0)
        self._opacity.set_target(1.0)
        self._opacity.speed = 16.0 / duration_hint
        self._start_animation()
        
    def fade_out(self, duration_hint=200):
        """Animate opacity from 1 to 0"""
        self._opacity.set_target(0.0)
        self._opacity.speed = 16.0 / duration_hint
        self._start_animation()
        
    def slide_in_from_bottom(self, offset=20):
        """Slide in from below"""
        self._slide_y.snap(offset)
        self._slide_y.set_target(0)
        self._start_animation()
        
    def pulse_glow(self):
        """Create a subtle attention pulse"""
        self._opacity.snap(0.7)
        self._opacity.set_target(1.0)
        self._opacity.easing = AnimatedValue.EASE_OUT_BACK
        self._start_animation()


class GlowButton(QPushButton):
    """
    Modern button with animated glow effect on hover/press.
    Used for primary actions.
    """
    
    def __init__(self, text="", parent=None, accent_color="#7c3aed"):
        super().__init__(text, parent)
        self.accent_color = accent_color
        self._glow_opacity = AnimatedValue(0.0, speed=0.15)
        self._press_scale = AnimatedValue(1.0, speed=0.2)
        
        self._anim_timer = QtCore.QTimer(self)
        self._anim_timer.timeout.connect(self._on_animate)
        
        self.setObjectName('glow_button')
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        
    def enterEvent(self, event):
        super().enterEvent(event)
        self._glow_opacity.set_target(0.6)
        self._start_animation()
        
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._glow_opacity.set_target(0.0)
        self._start_animation()
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self._press_scale.set_target(0.95)
        self._glow_opacity.set_target(0.9)
        self._start_animation()
        
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self._press_scale.set_target(1.0)
        self._glow_opacity.set_target(0.6 if self.underMouse() else 0.0)
        self._start_animation()
        
    def _start_animation(self):
        if not self._anim_timer.isActive():
            self._anim_timer.start(16)
            
    def _on_animate(self):
        animating = self._glow_opacity.update() or self._press_scale.update()
        self.update()
        if not animating:
            self._anim_timer.stop()
            
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Scale transform
        scale = self._press_scale.value
        if scale != 1.0:
            painter.translate(rect.center())
            painter.scale(scale, scale)
            painter.translate(-rect.center())
        
        # Outer glow
        if self._glow_opacity.value > 0.01:
            glow_color = QColor(self.accent_color)
            glow_color.setAlphaF(self._glow_opacity.value * 0.3)
            painter.setPen(QPen(QtCore.Qt.PenStyle.NoPen))
            painter.setBrush(QBrush(glow_color))
            painter.drawRoundedRect(
                rect.adjusted(-4, -4, 4, 4),
                12, 12
            )
        
        # Button background
        bg_color = QColor("#1a1a25")
        if self.isChecked():
            bg_color = QColor(self.accent_color)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(self.accent_color), 1.5))
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 8, 8)
        
        # Text
        painter.setPen(QColor("#f8fafc"))
        painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, self.text())


class HoverRevealWidget(QWidget):
    """
    Widget that reveals additional content/controls on hover.
    Used for non-essential UI that should be discoverable.
    """
    
    def __init__(self, main_content, hover_content, parent=None):
        super().__init__(parent)
        
        self._layout = QStackedLayout(self)
        self._layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        
        # Hover content on bottom
        self._hover_widget = hover_content
        self._hover_widget.setVisible(False)
        self._layout.addWidget(self._hover_widget)
        
        # Main content on top
        self._main_widget = main_content
        self._layout.addWidget(self._main_widget)
        
        self._opacity = AnimatedValue(0.0)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._animate)
        
    def enterEvent(self, event):
        super().enterEvent(event)
        self._hover_widget.setVisible(True)
        self._opacity.set_target(1.0)
        self._timer.start(16)
        
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._opacity.set_target(0.0)
        self._timer.start(16)
        
    def _animate(self):
        if not self._opacity.update():
            self._timer.stop()
            if self._opacity.value < 0.01:
                self._hover_widget.setVisible(False)


class PulseIndicator(QWidget):
    """
    Animated pulsing indicator for drawing attention.
    Used for new features, suggestions, and notifications.
    """
    
    def __init__(self, color="#7c3aed", size=12, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.setFixedSize(size + 8, size + 8)
        self.size = size
        
        self._pulse_phase = 0.0
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(33)  # ~30fps for pulse
        
    def _animate(self):
        import math
        self._pulse_phase += 0.1
        if self._pulse_phase > math.pi * 2:
            self._pulse_phase = 0
        self.update()
        
    def paintEvent(self, event):
        import math
        from PyQt5.QtGui import QPainter, QBrush, QPen
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = self.rect().center()
        
        # Outer pulse ring
        pulse = (math.sin(self._pulse_phase) + 1) / 2  # 0-1
        ring_color = QColor(self.color)
        ring_color.setAlphaF(0.3 * (1 - pulse))
        ring_size = self.size + int(pulse * 6)
        
        painter.setPen(QPen(QtCore.Qt.PenStyle.NoPen))
        painter.setBrush(QBrush(ring_color))
        painter.drawEllipse(
            center.x() - ring_size // 2,
            center.y() - ring_size // 2,
            ring_size,
            ring_size
        )
        
        # Inner solid dot
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(
            center.x() - self.size // 2,
            center.y() - self.size // 2,
            self.size,
            self.size
        )
        
    def stop(self):
        self._timer.stop()
        
    def start(self):
        self._timer.start(33)


class TypingLabel(QLabel):
    """
    Label that types out text character by character.
    Creates a dynamic, engaging feel for suggestions.
    """
    
    finished = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._full_text = ""
        self._current_index = 0
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._type_next)
        self._char_delay = 30  # ms per character
        
    def type_text(self, text, delay=30):
        """Start typing the given text"""
        self._full_text = text
        self._current_index = 0
        self._char_delay = delay
        self.setText("")
        self._timer.start(self._char_delay)
        
    def _type_next(self):
        if self._current_index < len(self._full_text):
            self._current_index += 1
            self.setText(self._full_text[:self._current_index] + "▌")
        else:
            self.setText(self._full_text)
            self._timer.stop()
            self.finished.emit()
            
    def skip(self):
        """Instantly show full text"""
        self._timer.stop()
        self.setText(self._full_text)
        self.finished.emit()


class SmoothScrollArea(QScrollArea):
    """
    Scroll area with momentum-based smooth scrolling.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._velocity = 0.0
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._apply_momentum)
        self.setWidgetResizable(True)
        
    def wheelEvent(self, event):
        # Add to velocity instead of instant scroll
        delta = event.angleDelta().y()
        self._velocity += delta * 0.5
        if not self._timer.isActive():
            self._timer.start(16)
        event.accept()
        
    def _apply_momentum(self):
        if abs(self._velocity) < 0.5:
            self._velocity = 0
            self._timer.stop()
            return
            
        # Apply velocity with friction
        scroll = self.verticalScrollBar()
        scroll.setValue(int(scroll.value() - self._velocity * 0.1))
        self._velocity *= 0.92  # Friction


LOG.info("Animation utilities loaded")
