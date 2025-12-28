"""
Intuitives DAW - Neobrutalist Icon Utilities
Creates QIcons with full state support (normal, hover, pressed, disabled)
"""
from intui.sgqt import QIcon, QPixmap
from intlib.models.theme import get_asset_path
import os
from typing import Dict, Optional


ICON_CACHE: Dict[str, QIcon] = {}

def create_neobrutalist_icon(
    base_name: str,
    has_hover: bool = True,
    has_pressed: bool = True,
) -> QIcon:
    """
    PURPOSE: Creates or retrieves a QIcon with full Neobrutalist state support.
    ACTION: Returns a QIcon configured for Normal (On/Off), Active (Hover), selected (Pressed), and Disabled states.
    MECHANISM: 
        1. Checks a global ICON_CACHE to avoid redundant filesystem hits and resource allocation.
        2. Resolves SVG asset paths using get_asset_path.
        3. Configures specific QIcon.Mode and QIcon.State combinations to match the DAW's interaction design.
    """
    global ICON_CACHE
    if base_name in ICON_CACHE:
        return ICON_CACHE[base_name]

    icon = QIcon()
    
    # Normal state - On (colorful)
    on_path = get_asset_path(f'{base_name}-on.svg')
    if os.path.exists(on_path):
        icon.addPixmap(
            QPixmap(on_path),
            QIcon.Mode.Normal,
            QIcon.State.On,
        )
    
    # Normal state - Off (muted gray)
    off_path = get_asset_path(f'{base_name}-off.svg')
    if os.path.exists(off_path):
        icon.addPixmap(
            QPixmap(off_path),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
    
    # Active/Hover state (extended shadow, lighter color)
    if has_hover:
        hover_path = get_asset_path(f'hover/{base_name}-hover.svg')
        if os.path.exists(hover_path):
            # Active mode is used for hover in Qt
            icon.addPixmap(
                QPixmap(hover_path),
                QIcon.Mode.Active,
                QIcon.State.On,
            )
            icon.addPixmap(
                QPixmap(hover_path),
                QIcon.Mode.Active,
                QIcon.State.Off,
            )
    
    # Selected/Pressed state (no shadow, translated)
    if has_pressed:
        pressed_path = get_asset_path(f'pressed/{base_name}-pressed.svg')
        if os.path.exists(pressed_path):
            icon.addPixmap(
                QPixmap(pressed_path),
                QIcon.Mode.Selected,
                QIcon.State.On,
            )
            icon.addPixmap(
                QPixmap(pressed_path),
                QIcon.Mode.Selected,
                QIcon.State.Off,
            )
    
    # Disabled state - use off state with reduced opacity (Qt handles this)
    if os.path.exists(off_path):
        icon.addPixmap(
            QPixmap(off_path),
            QIcon.Mode.Disabled,
            QIcon.State.On,
        )
        icon.addPixmap(
            QPixmap(off_path),
            QIcon.Mode.Disabled,
            QIcon.State.Off,
        )
    
    ICON_CACHE[base_name] = icon
    return icon


def create_simple_icon(svg_name: str) -> QIcon:
    """
    Create a simple QIcon from an SVG file.
    
    Args:
        svg_name: The SVG filename (e.g., 'menu.svg', 'panic.svg')
    
    Returns:
        QIcon for the asset
    """
    return QIcon(get_asset_path(svg_name))


# Pre-defined icons for common transport controls
def get_play_icon() -> QIcon:
    return create_neobrutalist_icon('play')


def get_stop_icon() -> QIcon:
    return create_neobrutalist_icon('stop')


def get_rec_icon() -> QIcon:
    return create_neobrutalist_icon('rec')


def get_loop_icon() -> QIcon:
    return create_neobrutalist_icon('loop')


def get_mute_icon() -> QIcon:
    return create_neobrutalist_icon('mute')


def get_solo_icon() -> QIcon:
    return create_neobrutalist_icon('solo')


def get_fx_icon() -> QIcon:
    return create_neobrutalist_icon('fx')


def get_draw_icon() -> QIcon:
    return create_neobrutalist_icon('draw')


def get_select_icon() -> QIcon:
    return create_neobrutalist_icon('select')


def get_erase_icon() -> QIcon:
    return create_neobrutalist_icon('erase')


def get_split_icon() -> QIcon:
    return create_neobrutalist_icon('split')


def get_metronome_icon() -> QIcon:
    return create_neobrutalist_icon('metronome')


def get_follow_icon() -> QIcon:
    return create_neobrutalist_icon('follow')


def get_power_icon() -> QIcon:
    return create_neobrutalist_icon('power')


def get_hide_icon() -> QIcon:
    return create_neobrutalist_icon('hide')


def get_speaker_icon() -> QIcon:
    return create_neobrutalist_icon('speaker')


def get_dc_icon() -> QIcon:
    return create_neobrutalist_icon('dc')


def get_host_icon() -> QIcon:
    """
    Create the host toggle icon (DAW on / Wave Editor off).
    This icon needs special handling since it uses different assets for on/off.
    """
    icon = QIcon()
    
    # On state: DAW mode
    daw_path = get_asset_path('daw.svg')
    if os.path.exists(daw_path):
        icon.addPixmap(
            QPixmap(daw_path),
            QIcon.Mode.Normal,
            QIcon.State.On,
        )
    
    # Off state: Wave Editor mode
    wave_path = get_asset_path('wave-editor.svg')
    if os.path.exists(wave_path):
        icon.addPixmap(
            QPixmap(wave_path),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
    
    return icon
