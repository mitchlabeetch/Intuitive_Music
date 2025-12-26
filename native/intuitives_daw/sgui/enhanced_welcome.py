"""
INTUITIVES DAW - Enhanced Welcome Screen

A modern, animated welcome experience that sets the tone for
rule-free experimental music creation.
"""

from sgui.sgqt import *
from sgui.widgets.animation import (
    AnimatedValue,
    GlowButton,
    PulseIndicator,
    TypingLabel,
)
from sgui.widgets.happy_accidents import HappyAccidentWidget
from sglib.brand import (
    APP_NAME,
    APP_TAGLINE,
    VERSION_STRING,
    VERSION_NAME,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_TERTIARY,
    CHROMA_COLORS,
)
from sglib.log import LOG

import random
import time


class AnimatedBackground(QWidget):
    """
    Subtle animated background for the welcome screen.
    Creates a feeling of life and movement.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # Floating particles
        self.particles = []
        for _ in range(15):
            self.particles.append({
                'x': random.random(),
                'y': random.random(),
                'size': random.randint(4, 12),
                'speed': 0.0005 + random.random() * 0.001,
                'color': random.choice(list(CHROMA_COLORS.values())),
                'opacity': 0.2 + random.random() * 0.3,
            })
            
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(33)  # ~30fps
        
    def _animate(self):
        for p in self.particles:
            p['y'] -= p['speed']
            if p['y'] < -0.1:
                p['y'] = 1.1
                p['x'] = random.random()
        self.update()
        
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        
        for p in self.particles:
            color = QColor(p['color'])
            color.setAlphaF(p['opacity'])
            painter.setPen(QPen(QtCore.Qt.PenStyle.NoPen))
            painter.setBrush(QBrush(color))
            
            x = int(p['x'] * w)
            y = int(p['y'] * h)
            s = p['size']
            painter.drawEllipse(x - s//2, y - s//2, s, s)


class WelcomeHeader(QWidget):
    """
    Animated welcome header with logo and tagline.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(180)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        
        # Logo/Title
        title = QLabel(APP_NAME.upper())
        title.setObjectName('welcome_title')
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 48px;
                font-weight: 700;
                color: #f8fafc;
                letter-spacing: 8px;
            }}
        """)
        layout.addWidget(title)
        
        # Version badge
        version_layout = QHBoxLayout()
        version_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(version_layout)
        
        version = QLabel(f"v{VERSION_STRING} β")
        version.setStyleSheet(f"""
            QLabel {{
                background: rgba(124, 58, 237, 0.2);
                border: 1px solid rgba(124, 58, 237, 0.5);
                color: #c4b5fd;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        version_layout.addWidget(version)
        
        # Tagline with typing effect
        self.tagline = TypingLabel()
        self.tagline.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.tagline.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #94a3b8;
                font-style: italic;
            }
        """)
        layout.addWidget(self.tagline)
        
        # Animate tagline after a delay
        QtCore.QTimer.singleShot(500, self._start_tagline)
        
    def _start_tagline(self):
        self.tagline.type_text(f'"{APP_TAGLINE}"', delay=50)


class QuickActionCard(QWidget):
    """
    A card for a quick action (New, Open, etc.)
    """
    
    clicked = Signal()
    
    def __init__(self, icon, title, description, accent_color=COLOR_PRIMARY, parent=None):
        super().__init__(parent)
        self.accent_color = accent_color
        self._hovered = False
        self._hover_anim = AnimatedValue(0.0, speed=0.15)
        
        self.setFixedSize(200, 160)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 36px;")
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #f8fafc;
            }
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #94a3b8;
            }
        """)
        layout.addWidget(desc_label)
        
        # Animation timer
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._animate)
        
    def enterEvent(self, event):
        self._hovered = True
        self._hover_anim.set_target(1.0)
        self._timer.start(16)
        
    def leaveEvent(self, event):
        self._hovered = False
        self._hover_anim.set_target(0.0)
        self._timer.start(16)
        
    def mousePressEvent(self, event):
        self.clicked.emit()
        
    def _animate(self):
        if not self._hover_anim.update():
            self._timer.stop()
        self.update()
        
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(4, 4, -4, -4)
        
        # Glow on hover
        if self._hover_anim.value > 0.01:
            glow = QColor(self.accent_color)
            glow.setAlphaF(self._hover_anim.value * 0.3)
            painter.setPen(QPen(QtCore.Qt.PenStyle.NoPen))
            painter.setBrush(QBrush(glow))
            painter.drawRoundedRect(rect.adjusted(-4, -4, 4, 4), 20, 20)
        
        # Card background
        bg = QColor("#1a1a25")
        painter.setBrush(QBrush(bg))
        
        border = QColor("#2e2e3e")
        if self._hover_anim.value > 0.5:
            border = QColor(self.accent_color)
        painter.setPen(QPen(border, 1.5))
        painter.drawRoundedRect(rect, 16, 16)


class RecentProjectItem(QWidget):
    """
    A recent project item with hover animation.
    """
    
    clicked = Signal(str)
    
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self._hovered = False
        self._hover_anim = AnimatedValue(0.0, speed=0.2)
        
        self.setFixedHeight(48)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Folder icon
        icon = QLabel("📁")
        layout.addWidget(icon)
        
        # Project name
        import os
        name = os.path.basename(os.path.dirname(path))
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 500;
                color: #f8fafc;
            }
        """)
        layout.addWidget(self.name_label, 1)
        
        # Path hint
        dir_path = os.path.dirname(path)
        short_path = dir_path[-40:] if len(dir_path) > 40 else dir_path
        path_label = QLabel(short_path)
        path_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #64748b;
            }
        """)
        layout.addWidget(path_label)
        
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._animate)
        
    def enterEvent(self, event):
        self._hovered = True
        self._hover_anim.set_target(1.0)
        self._timer.start(16)
        
    def leaveEvent(self, event):
        self._hovered = False
        self._hover_anim.set_target(0.0)
        self._timer.start(16)
        
    def mousePressEvent(self, event):
        self.clicked.emit(self.path)
        
    def _animate(self):
        if not self._hover_anim.update():
            self._timer.stop()
        self.update()
        
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        # Background on hover
        if self._hover_anim.value > 0.01:
            bg = QColor("#2a2a45")
            bg.setAlphaF(self._hover_anim.value)
            painter.setPen(QPen(QtCore.Qt.PenStyle.NoPen))
            painter.setBrush(QBrush(bg))
            painter.drawRoundedRect(rect, 8, 8)
            
            # Left accent
            accent = QColor(COLOR_PRIMARY)
            accent.setAlphaF(self._hover_anim.value)
            painter.setBrush(QBrush(accent))
            painter.drawRoundedRect(0, 8, 3, self.height() - 16, 1, 1)


class EnhancedWelcome(QWidget):
    """
    The complete enhanced welcome screen.
    """
    
    # Signals
    new_project_requested = Signal()
    open_project_requested = Signal()
    clone_project_requested = Signal()
    recent_project_selected = Signal(str)
    hardware_settings_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('enhanced_welcome')
        
        # Animated background
        self.bg = AnimatedBackground(self)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(24)
        
        # Header
        self.header = WelcomeHeader()
        layout.addWidget(self.header)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(20)
        actions_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(actions_layout)
        
        new_card = QuickActionCard(
            "✨", "New Project",
            "Start fresh and experiment",
            COLOR_PRIMARY
        )
        new_card.clicked.connect(self.new_project_requested.emit)
        actions_layout.addWidget(new_card)
        
        open_card = QuickActionCard(
            "📂", "Open Project",
            "Continue where you left off",
            COLOR_SECONDARY
        )
        open_card.clicked.connect(self.open_project_requested.emit)
        actions_layout.addWidget(open_card)
        
        clone_card = QuickActionCard(
            "📋", "Clone Project",
            "Remix an existing project",
            COLOR_TERTIARY
        )
        clone_card.clicked.connect(self.clone_project_requested.emit)
        actions_layout.addWidget(clone_card)
        
        # Recent projects section
        recent_layout = QVBoxLayout()
        layout.addLayout(recent_layout, 1)
        
        recent_header = QHBoxLayout()
        recent_layout.addLayout(recent_header)
        
        recent_label = QLabel("Recent Projects")
        recent_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
        """)
        recent_header.addWidget(recent_label)
        recent_header.addStretch()
        
        # Recent projects list (will be populated externally)
        self.recent_scroll = QScrollArea()
        self.recent_scroll.setWidgetResizable(True)
        self.recent_scroll.setObjectName('recent_scroll')
        self.recent_scroll.setStyleSheet("""
            QScrollArea {
                background: rgba(18, 18, 26, 0.5);
                border: 1px solid #2e2e3e;
                border-radius: 12px;
            }
            QScrollArea > QWidget {
                background: transparent;
            }
        """)
        recent_layout.addWidget(self.recent_scroll)
        
        self.recent_container = QWidget()
        self.recent_list_layout = QVBoxLayout(self.recent_container)
        self.recent_list_layout.setSpacing(4)
        self.recent_list_layout.setContentsMargins(8, 8, 8, 8)
        self.recent_list_layout.addStretch()
        self.recent_scroll.setWidget(self.recent_container)
        
        # Bottom bar
        bottom_layout = QHBoxLayout()
        layout.addLayout(bottom_layout)
        
        # Settings button
        settings_btn = QPushButton("⚙️ Hardware Settings")
        settings_btn.setObjectName('subtle_button')
        settings_btn.clicked.connect(self.hardware_settings_requested.emit)
        bottom_layout.addWidget(settings_btn)
        
        bottom_layout.addStretch()
        
        # Happy Accident teaser
        teaser = QLabel("\"Does this sound cool?\" — The only rule.")
        teaser.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #64748b;
                font-style: italic;
            }
        """)
        bottom_layout.addWidget(teaser)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resize background to fill
        self.bg.resize(self.size())
        
    def add_recent_project(self, path):
        """Add a recent project to the list"""
        item = RecentProjectItem(path)
        item.clicked.connect(self.recent_project_selected.emit)
        # Insert before stretch
        self.recent_list_layout.insertWidget(
            self.recent_list_layout.count() - 1,
            item
        )
        
    def clear_recent_projects(self):
        """Clear the recent projects list"""
        while self.recent_list_layout.count() > 1:
            item = self.recent_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


LOG.info("Enhanced welcome screen loaded")
