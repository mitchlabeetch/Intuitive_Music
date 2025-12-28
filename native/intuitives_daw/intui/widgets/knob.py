from intui.sgqt import *
from intlib.models import theme

from intlib.log import LOG
from intlib.math import clip_value
from intui import shared as glbl_shared
from intlib.lib import util
from intlib.lib.translate import _
from intui.util import svg_to_pixmap
from enum import Enum
import os


DEFAULT_THEME_KNOB = None
DEFAULT_THEME_KNOB_BG = None
# This is for plugins to consume, it's not a default value anywhere
DEFAULT_KNOB_SIZE = 48
DEFAULT_LARGE_KNOB_SIZE = 64

class PixmapKnobCache:
    """
    PURPOSE: Optimizes performance by caching scaled pixmaps of knob assets.
    ACTION: Stores and retrieves QPixmap objects based on their file path and size.
    MECHANISM: Uses a dictionary (self.cache) where the key is a tuple of (path, size).
    """
    def __init__(self):
        """
        PURPOSE: Initializes the knob pixmap cache.
        ACTION: Creates an empty cache dictionary.
        MECHANISM: simple assignment.
        """
        self.cache = {}

    def get_scaled_pixmap_knob(self, path, size):
        """
        PURPOSE: Retrieves a scaled pixmap for a knob from the cache or disk.
        ACTION: Returns a QPixmap of the requested SVG at the specified size.
        MECHANISM: 
            1. Resolves 'default' placeholders to theme-defined paths.
            2. Checks the cache dictionary for a hit.
            3. On miss, calls svg_to_pixmap() to render the SVG and stores it in the cache.
        """
        if not path:
            return None
        if path == 'default':
            path = DEFAULT_THEME_KNOB
        if path == 'default_bg':
            path = DEFAULT_THEME_KNOB_BG
        path = util.pi_path(path)
        key = (path, size)
        if key in self.cache:
            return self.cache[key]
        else:
            pixmap = svg_to_pixmap(
                path,
                size,
                size,
            )
            self.cache[key] = pixmap
            return pixmap

def knob_setup():
    """
    PURPOSE: Global initialization of theme-dependent knob assets.
    ACTION: populates the default asset paths and instantiates the global pixmap cache.
    MECHANISM: 
        1. Joins theme.ASSETS_DIR with theme.SYSTEM_COLORS configuration.
        2. Assigns the results to DEFAULT_THEME_KNOB and DEFAULT_THEME_KNOB_BG.
    """
    global DEFAULT_THEME_KNOB, DEFAULT_THEME_KNOB_BG, KNOB_PIXMAP_CACHE
    DEFAULT_THEME_KNOB = os.path.join(
        theme.ASSETS_DIR,
        theme.SYSTEM_COLORS.widgets.knob_fg_image,
    )
    DEFAULT_THEME_KNOB_BG = os.path.join(
        theme.ASSETS_DIR,
        theme.SYSTEM_COLORS.widgets.knob_bg_image,
    )
    KNOB_PIXMAP_CACHE = PixmapKnobCache()

class ArcType(Enum):
    # Arc goes from minimal at -135 degrees to full at +135 degrees from top
    UP = 0
    # Arc is minimal at 0 degrees (top), half-full at -/+135 degrees from top
    BIDIRECTIONAL = 1

class PixmapKnob(QDial):
    """
    PURPOSE: A skinnable, high-performance rotary control (knob) using SVG assets.
    ACTION: Displays a foreground and optional background image with a custom indicator arc.
    MECHANISM: 
        1. Inherits from QDial for core range/value logic.
        2. Loads SVG assets as scaled pixmaps.
        3. Customizes paintEvent to handle rotation and arc drawing.
    """
    def __init__(
        self,
        a_size,
        a_min_val,
        a_max_val,
        fg_svg="default",
        bg_svg=None,
        arc_width_pct=12.0,  # 0.0 to disable
        arc_type=ArcType.UP,
        arc_brush=None,
        arc_bg_brush=None,
        arc_pen_kwargs: dict = {},
        draw_line: bool = False,
        arc_space: float = 0.0,
    ) -> None:
        """
        PURPOSE: Initializes the skinnable knob with graphical and range parameters.
        ACTION: Sets the knob's size, range, colors, and loads asset pixmaps.
        MECHANISM: 
            1. Configures internal brushes (arc_brush, etc.) based on the system theme.
            2. Calculates pixmap dimensions relative to the total size and arc width.
            3. Uses KNOB_PIXMAP_CACHE to get appropriately sized foreground/background images.
        """
        self.arc_brush = arc_brush if arc_brush else QColor(
            theme.SYSTEM_COLORS.widgets.knob_arc_pen,
        )
        self.arc_bg_brush = arc_bg_brush if arc_bg_brush else QColor(
            theme.SYSTEM_COLORS.widgets.knob_arc_background_pen,
        )
        self.arc_width_pct = arc_width_pct
        self.arc_type = arc_type
        self.arc_space = arc_space
        self.arc_pen_kwargs = arc_pen_kwargs
        QDial.__init__(self)
        self.bg_svg = bg_svg
        self.fg_svg = fg_svg
        self.draw_line = draw_line
        self._size = a_size
        self.setRange(int(a_min_val), int(a_max_val))
        self.val_step = float(a_max_val - a_min_val) * 0.005  # / 200.0
        self.val_step_small = self.val_step * 0.1
        self.setGeometry(0, 0, a_size, a_size)
        self.pixmap_size = (
            a_size - (arc_width_pct * a_size * 0.02) - (arc_space * 2)
        )
        self.pixmap_fg = KNOB_PIXMAP_CACHE.get_scaled_pixmap_knob(
            self.fg_svg,
            self.pixmap_size,
        )
        self.pixmap_bg = KNOB_PIXMAP_CACHE.get_scaled_pixmap_knob(
            self.bg_svg,
            self.pixmap_size,
        )
        self.setFixedSize(a_size, a_size)
        self._button = QtCore.Qt.MouseButton.NoButton

    def wheelEvent(self, event):
        """PURPOSE: Disables mouse wheel interaction for the knob to prevent accidental changes."""
        event.ignore()

    def keyPressEvent(self, a_event):
        """
        PURPOSE: Handles keyboard input, specifically allowing spacebar to control the transport.
        ACTION: Passes key events to parent or triggers transport toggle.
        MECHANISM: Calls QDial.keyPressEvent and emits spacebar signal to glbl_shared.TRANSPORT.
        """
        QDial.keyPressEvent(self, a_event)
        if a_event.key() == QtCore.Qt.Key.Key_Space:
            glbl_shared.TRANSPORT.on_spacebar()

    def paintEvent(self, a_event):
        """
        PURPOSE: Renders the custom graphical representation of the knob.
        ACTION: Draws background pixmap, indicators, foreground rotated pixmap, and arcs.
        MECHANISM: 
            1. Calculates fractional rotation (0-270 degrees).
            2. Draws the background arc (unfilled) and foreground arc (filled) using QPainter.drawArc.
            3. Translates and rotates the painter to draw the foreground pixmap in the center.
            4. Optionally draws a pointer line for high-precision visual feedback.
        """
        p = QPainter(self)
        p.setRenderHints(
            QPainter.RenderHint.Antialiasing
            |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        f_frac_val = (
            (float(self.value() - self.minimum()))
            /
            (float(self.maximum() - self.minimum()))
        )
        f_rotate_value = f_frac_val * 270.0
        f_rect = self.rect()
        arc_width = int(self.arc_width_pct * f_rect.width() * 0.01)
        f_rect.setWidth(int(f_rect.width() - arc_width))
        f_rect.setHeight(int(f_rect.height() - arc_width))
        f_rect.setX(int(f_rect.x() + arc_width))
        f_rect.setY(int(f_rect.y() + arc_width))

        if self.arc_width_pct:
            knob_arc_pen = QPen(
                self.arc_brush,
                arc_width,
                **self.arc_pen_kwargs
            )
            knob_arc_background_pen = QPen(
                self.arc_bg_brush,
                arc_width,
            )
            p.setPen(knob_arc_background_pen)
            p.drawArc(f_rect, -135 * 16, 135 * 2 * -16)
            p.setPen(knob_arc_pen)
            if self.arc_type == ArcType.UP:
                p.drawArc(
                    f_rect,
                    -135 * 16,
                    int((f_rotate_value + 1.0) * -16),
                )
            elif self.arc_type == ArcType.BIDIRECTIONAL:
                if f_rotate_value < 135.:
                    span_angle = (135. - f_rotate_value) * 16
                else:
                    span_angle = (f_rotate_value - 135.) * -16
                p.drawArc(
                    f_rect,
                    90 * 16,
                    int(span_angle),
                )
            else:
                raise ValueError(f"Invalid arc_type: {self.arc_type}")

        if self.draw_line:
            rectf_width = float(self._size - (arc_width * 2.))
            rectf = QtCore.QRectF(
                arc_width,
                arc_width,
                rectf_width,
                rectf_width,
            )
            ppath = QPainterPath()
            ppath.arcMoveTo(rectf, -float(f_rotate_value) - 135.)
            center = self._size * 0.5
            ppath.lineTo(center, center)
            cap_style = knob_arc_pen.capStyle()
            knob_arc_pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            p.setPen(knob_arc_pen)
            p.drawPath(ppath)
            knob_arc_pen.setCapStyle(cap_style)
            p.setPen(knob_arc_pen)

        if self.pixmap_bg:
            p.drawPixmap(
                int(arc_width + self.arc_space),
                int(arc_width + self.arc_space),
                self.pixmap_bg,
            )

        if self.pixmap_fg:
            # xc and yc are the center of the widget's rect.
            xc = self.width() * 0.5
            yc = self.height() * 0.5
            # translates the coordinate system by xc and yc
            p.translate(xc, yc)
            p.rotate(
                int(
                    round(f_rotate_value),
                ),
            )
            # we need to move the rectangle that we draw by
            # rx and ry so it's in the center.
            rx = -(self.pixmap_size * 0.5)
            ry = -(self.pixmap_size * 0.5)
            p.drawPixmap(int(rx), int(ry), self.pixmap_fg)

    def mousePressEvent(self, a_event):
        """
        PURPOSE: Initiates interactive value changes.
        ACTION: Stores original values and hides the cursor for "infinite" vertical drag logic.
        MECHANISM: Captures mouse position, original value, and modifiers (e.g., Ctrl for fine adjustment).
        """
        self._button = a_event.button()
        self.mouse_pos = QCursor.pos()
        if self._button == QtCore.Qt.MouseButton.RightButton:
            QDial.mousePressEvent(self, a_event)
            return
        f_pos = qt_event_pos(a_event)
        self.orig_x = f_pos.x()
        self.orig_y = f_pos.y()
        self.orig_value = self.value()
        self.fine_only = (
            a_event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier
        )
        QApplication.setOverrideCursor(QtCore.Qt.CursorShape.BlankCursor)

    def mouseMoveEvent(self, a_event):
        """
        PURPOSE: Handles value updates during drag operations.
        ACTION: Calculates a new value based on mouse displacement and updates the widget.
        MECHANISM: 
            1. Reads Y-axis movement for coarse/fine adjustment.
            2. If 'fine_only' is active, uses X-axis delta for ultra-high precision.
            3. Clamps and emits valueChanged signal.
        """
        if self._button != QtCore.Qt.MouseButton.LeftButton:
            QDial.mouseMoveEvent(self, a_event)
            return
        f_pos = qt_event_pos(a_event)
        f_x = f_pos.x()
        f_diff_x = f_x - self.orig_x
        if self.fine_only:
            f_val = (f_diff_x * self.val_step_small) + self.orig_value
        else:
            f_y = f_pos.y()
            f_diff_y = self.orig_y - f_y
            f_val = ((f_diff_y * self.val_step) +
                (f_diff_x * self.val_step_small)) + self.orig_value
        f_val = clip_value(
            f_val, self.minimum(), self.maximum())
        f_val = int(f_val)
        if f_val != self.value():
            self.setValue(f_val)
            self.valueChanged.emit(f_val)

    def mouseReleaseEvent(self, a_event):
        """
        PURPOSE: Completes a drag operation.
        ACTION: Restores the application cursor and resets interaction state.
        MECHANISM: Calls QApplication.restoreOverrideCursor() and emits sliderReleased.
        """
        # Does not work on Wayland
        #QCursor.setPos(self.mouse_pos)
        self._button = QtCore.Qt.MouseButton.NoButton
        QApplication.restoreOverrideCursor()
        self.sliderReleased.emit()


# ============================================================================
# NEOBRUTALIST KNOB (Intuitives Style)
# ============================================================================

class NeobrutalistKnob(QDial):
    """
    PURPOSE: A specialized rotary control following the Intuitives "Neobrutalist" aesthetic.
    ACTION: Displays a high-contrast, geometric knob with bold colors and hard shadows.
    MECHANISM: 
        1. Implements custom vector drawing (no SVG dependencies).
        2. Uses Chromasynesthesia-aware color mapping for parameter recognition.
        3. Features center-aligned value display and hover effects.
    """
    
    # Chromasynesthesia colors (for parameter-specific coloring)
    CHROMA_COLORS = [
        QColor("#FF3366"),  # C - Red
        QColor("#FF9933"),  # C# - Orange
        QColor("#FFEE33"),  # D - Yellow
        QColor("#33FF66"),  # E - Green
        QColor("#33EEFF"),  # F - Cyan
        QColor("#3366FF"),  # G - Blue
        QColor("#FF33EE"),  # A - Magenta
    ]
    
    # Default Intuitives purple
    DEFAULT_COLOR = QColor("#7c3aed")
    BACKGROUND_COLOR = QColor("#12121a")
    SHADOW_COLOR = QColor("#000000")
    TEXT_COLOR = QColor("#f8fafc")
    
    def __init__(
        self,
        a_size,
        a_min_val,
        a_max_val,
        color_index: int = -1,  # -1 = default purple, 0-6 = chroma colors
        show_value: bool = True,
        value_format: str = "{:.0f}",
        label: str = "",
        arc_width_pct: float = 15.0,
        shadow_offset: int = 3,
    ) -> None:
        """
        PURPOSE: Initializes the Neobrutalist knob with styling and range parameters.
        ACTION: Sets the color palette and physical dimensions.
        MECHANISM: Assigns internal state variables and maps color_index to CHROMA_COLORS.
        """
        super().__init__()
        
        self._size = a_size
        self.setRange(int(a_min_val), int(a_max_val))
        self.setGeometry(0, 0, a_size, a_size)
        self.setFixedSize(a_size, a_size)
        
        # Styling
        self.color_index = color_index
        self.show_value = show_value
        self.value_format = value_format
        self.label = label
        self.arc_width_pct = arc_width_pct
        self.shadow_offset = shadow_offset
        
        # Calculate colors
        if color_index >= 0 and color_index < len(self.CHROMA_COLORS):
            self.accent_color = self.CHROMA_COLORS[color_index]
        else:
            self.accent_color = self.DEFAULT_COLOR
        
        # Interaction state
        self.val_step = float(a_max_val - a_min_val) * 0.005
        self.val_step_small = self.val_step * 0.1
        self._button = QtCore.Qt.MouseButton.NoButton
        self._hover = False
        
        # Enable hover tracking
        self.setMouseTracking(True)
    
    def wheelEvent(self, event):
        event.ignore()
    
    def keyPressEvent(self, a_event):
        QDial.keyPressEvent(self, a_event)
        if a_event.key() == QtCore.Qt.Key.Key_Space:
            glbl_shared.TRANSPORT.on_spacebar()
    
    def enterEvent(self, event):
        """PURPOSE: Toggles hover state on mouse entry."""
        self._hover = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """PURPOSE: Toggles hover state on mouse leave."""
        self._hover = False
        self.update()
        super().leaveEvent(event)
    
    def paintEvent(self, a_event):
        """
        PURPOSE: Renders the Neobrutalist visual style.
        ACTION: Draws the hard shadow, background circle, progress arc, and indicator.
        MECHANISM: 
            1. Manual offset drawing for the "hard shadow" effect.
            2. QPainter.drawArc for the primary value indicator.
            3. Dynamic font scaling for the center value display.
            4. Coordinate transformation for drawing the rotated pointer line.
        """
        p = QPainter(self)
        p.setRenderHints(
            QPainter.RenderHint.Antialiasing
            |
            QPainter.RenderHint.TextAntialiasing
        )
        
        # Calculate dimensions
        size = self._size
        center = size // 2
        arc_width = int(self.arc_width_pct * size * 0.01)
        knob_radius = int((size - arc_width * 2 - self.shadow_offset * 2) // 2)
        
        # Calculate value fraction
        f_frac = (
            (float(self.value() - self.minimum()))
            /
            max(1, float(self.maximum() - self.minimum()))
        )
        f_rotate = f_frac * 270.0
        
        # ========================================
        # HARD SHADOW (Neobrutalist signature)
        # ========================================
        shadow_center_x = center + self.shadow_offset
        shadow_center_y = center + self.shadow_offset
        
        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.setBrush(self.SHADOW_COLOR)
        p.drawEllipse(
            shadow_center_x - knob_radius,
            shadow_center_y - knob_radius,
            knob_radius * 2,
            knob_radius * 2,
        )
        
        # ========================================
        # BACKGROUND CIRCLE
        # ========================================
        p.setBrush(self.BACKGROUND_COLOR)
        p.drawEllipse(
            center - knob_radius,
            center - knob_radius,
            knob_radius * 2,
            knob_radius * 2,
        )
        
        # ========================================
        # ARC BACKGROUND (unfilled portion)
        # ========================================
        arc_rect = QtCore.QRectF(
            arc_width // 2 + self.shadow_offset // 2,
            arc_width // 2 + self.shadow_offset // 2,
            size - arc_width - self.shadow_offset,
            size - arc_width - self.shadow_offset,
        )
        
        arc_bg_pen = QPen(QColor("#3a3a4a"), arc_width)
        arc_bg_pen.setCapStyle(QtCore.Qt.PenCapStyle.FlatCap)
        p.setPen(arc_bg_pen)
        p.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        p.drawArc(arc_rect, -135 * 16, -270 * 16)
        
        # ========================================
        # ARC FOREGROUND (filled portion)
        # ========================================
        # Hover effect: brighten color
        arc_color = self.accent_color
        if self._hover:
            arc_color = arc_color.lighter(120)
        
        arc_pen = QPen(arc_color, arc_width)
        arc_pen.setCapStyle(QtCore.Qt.PenCapStyle.FlatCap)
        p.setPen(arc_pen)
        p.drawArc(arc_rect, -135 * 16, int(-f_rotate * 16))
        
        # ========================================
        # KNOB BORDER
        # ========================================
        border_pen = QPen(self.accent_color, 2)
        p.setPen(border_pen)
        p.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        p.drawEllipse(
            center - knob_radius,
            center - knob_radius,
            knob_radius * 2,
            knob_radius * 2,
        )
        
        # ========================================
        # INDICATOR LINE
        # ========================================
        p.save()
        p.translate(center, center)
        p.rotate(f_rotate - 135)
        
        indicator_pen = QPen(self.accent_color, 3)
        indicator_pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        p.setPen(indicator_pen)
        p.drawLine(0, -knob_radius + 8, 0, -knob_radius + knob_radius // 2)
        
        p.restore()
        
        # ========================================
        # VALUE TEXT (center)
        # ========================================
        if self.show_value:
            value_text = self.value_format.format(self.value())
            
            font = p.font()
            font.setPixelSize(max(10, size // 5))
            font.setBold(True)
            p.setFont(font)
            
            p.setPen(self.TEXT_COLOR)
            text_rect = QtCore.QRect(0, 0, size, size)
            p.drawText(
                text_rect,
                QtCore.Qt.AlignmentFlag.AlignCenter,
                value_text,
            )
    
    def mousePressEvent(self, a_event):
        self._button = a_event.button()
        self.mouse_pos = QCursor.pos()
        if self._button == QtCore.Qt.MouseButton.RightButton:
            QDial.mousePressEvent(self, a_event)
            return
        f_pos = qt_event_pos(a_event)
        self.orig_x = f_pos.x()
        self.orig_y = f_pos.y()
        self.orig_value = self.value()
        self.fine_only = (
            a_event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier
        )
        QApplication.setOverrideCursor(QtCore.Qt.CursorShape.BlankCursor)
    
    def mouseMoveEvent(self, a_event):
        if self._button != QtCore.Qt.MouseButton.LeftButton:
            QDial.mouseMoveEvent(self, a_event)
            return
        f_pos = qt_event_pos(a_event)
        f_x = f_pos.x()
        f_diff_x = f_x - self.orig_x
        if self.fine_only:
            f_val = (f_diff_x * self.val_step_small) + self.orig_value
        else:
            f_y = f_pos.y()
            f_diff_y = self.orig_y - f_y
            f_val = ((f_diff_y * self.val_step) +
                (f_diff_x * self.val_step_small)) + self.orig_value
        f_val = clip_value(
            f_val, self.minimum(), self.maximum())
        f_val = int(f_val)
        if f_val != self.value():
            self.setValue(f_val)
            self.valueChanged.emit(f_val)
    
    def mouseReleaseEvent(self, a_event):
        self._button = QtCore.Qt.MouseButton.NoButton
        QApplication.restoreOverrideCursor()
        self.sliderReleased.emit()
