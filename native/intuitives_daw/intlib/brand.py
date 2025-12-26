"""
INTUITIVES DAW - Brand Constants

"Does this sound cool?" - The only rule.

Branding, versioning, and identity constants for Intuitives DAW.
"""

# ============================================================================
# BRAND IDENTITY
# ============================================================================

APP_NAME = "Intuitives"
APP_TAGLINE = "Rule-free Experimental DAW"
APP_DESCRIPTION = """
A digital audio workstation that prioritizes intuition, randomness, 
and AI-assisted discovery over traditional music theory constraints.
"""

APP_PHILOSOPHY = """
Does this sound cool? That's the only question that matters.
No piano roll constraints. No scale enforcement. No rules.
"""

# Version (SemVer)
VERSION_MAJOR = 0
VERSION_MINOR = 6
VERSION_PATCH = 0
VERSION_STRING = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}-beta"
VERSION_NAME = "Genesis"  # Version codename

# Copyright
COPYRIGHT_YEAR = "2024"
COPYRIGHT_HOLDER = "Intuitives Team"
LICENSE = "GPLv3 + MIT"

# URLs
URL_HOMEPAGE = "https://intuitives.dev"
URL_DOCS = "https://docs.intuitives.dev"
URL_GITHUB = "https://github.com/intuitives/daw"
URL_DISCORD = "https://discord.gg/intuitives"

# ============================================================================
# COLOR PALETTE - CHROMASYNESTHESIA
# ============================================================================

# Primary colors
COLOR_PRIMARY = "#7c3aed"       # Purple - creativity
COLOR_SECONDARY = "#06b6d4"     # Cyan - clarity
COLOR_TERTIARY = "#f97316"      # Orange - energy

# Semantic colors
COLOR_SUCCESS = "#10b981"
COLOR_WARNING = "#f59e0b"
COLOR_ERROR = "#ef4444"

# Background colors
COLOR_BG_DARK = "#0a0a0f"
COLOR_BG_PANEL = "#12121a"
COLOR_BG_ELEVATED = "#1a1a25"
COLOR_BG_SURFACE = "#22223a"

# Text colors
COLOR_TEXT_PRIMARY = "#f8fafc"
COLOR_TEXT_SECONDARY = "#94a3b8"
COLOR_TEXT_MUTED = "#64748b"

# Chromasynesthesia - Note to Color mapping (Scriabin-inspired)
CHROMA_COLORS = {
    0:  "#ff5c5c",  # C - Red
    1:  "#ff8c4c",  # C# - Orange-Red
    2:  "#ffb84c",  # D - Orange
    3:  "#ffe04c",  # D# - Yellow-Orange
    4:  "#e8ff4c",  # E - Yellow
    5:  "#8cff4c",  # F - Yellow-Green
    6:  "#4cff8c",  # F# - Green
    7:  "#4cffff",  # G - Cyan
    8:  "#4c8cff",  # G# - Blue
    9:  "#4c4cff",  # A - Indigo
    10: "#8c4cff",  # A# - Purple
    11: "#ff4cff",  # B - Magenta
}

# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURES = {
    # Core DAW
    "transport": True,
    "tracks": True,
    "patterns": True,
    "mixer": True,
    "plugins": True,
    
    # Intuitives Unique
    "generative_markov": True,
    "generative_genetic": True,
    "generative_cellular": True,
    "generative_lsystem": True,
    
    # Multimedia Input
    "input_image": True,
    "input_text": True,
    "input_color": True,
    "input_webcam": False,  # Planned
    "input_gesture": False,  # Planned
    
    # Visualization
    "visual_spectrum": True,
    "visual_waveform": True,
    "visual_chromasynesthesia": True,
    "visual_3d_mixer": False,  # Planned
    
    # AI Features
    "ai_accompaniment": False,  # Planned
    "ai_mastering": False,  # Planned
}

# ============================================================================
# KEYBOARD SHORTCUTS - DEFAULT
# ============================================================================

SHORTCUTS = {
    # Transport
    "play_pause": "Space",
    "stop": "0",
    "record": "R",
    "loop": "L",
    
    # Navigation
    "zoom_in": "Ctrl+=",
    "zoom_out": "Ctrl+-",
    "zoom_fit": "Ctrl+0",
    "scroll_left": "Left",
    "scroll_right": "Right",
    
    # Editing
    "undo": "Ctrl+Z",
    "redo": "Ctrl+Shift+Z",
    "cut": "Ctrl+X",
    "copy": "Ctrl+C",
    "paste": "Ctrl+V",
    "delete": "Delete",
    "select_all": "Ctrl+A",
    
    # Generators
    "gen_markov": "Ctrl+G",
    "gen_genetic": "Ctrl+Shift+G",
    "gen_cellular": "Ctrl+Alt+G",
    
    # Views
    "view_sequencer": "F1",
    "view_pattern": "F2",
    "view_mixer": "F3",
    "view_plugins": "F4",
    "view_generators": "F5",
    "view_visualizer": "F6",
}

# ============================================================================
# UI SIZING
# ============================================================================

UI_SCALE_MIN = 0.75
UI_SCALE_MAX = 2.0
UI_SCALE_DEFAULT = 1.0

FONT_SIZE_SMALL = 11
FONT_SIZE_NORMAL = 13
FONT_SIZE_LARGE = 16
FONT_SIZE_TITLE = 20
FONT_SIZE_HEADING = 24

BORDER_RADIUS_SMALL = 4
BORDER_RADIUS_MEDIUM = 8
BORDER_RADIUS_LARGE = 12
BORDER_RADIUS_XLARGE = 16

# ============================================================================
# ENGINE DEFAULTS
# ============================================================================

SAMPLE_RATE_DEFAULT = 48000
BUFFER_SIZE_DEFAULT = 256
CHANNELS_DEFAULT = 2

MAX_TRACKS = 64
MAX_PATTERNS = 256
MAX_PLUGINS_PER_TRACK = 8

# ============================================================================
# FILE EXTENSIONS
# ============================================================================

PROJECT_EXTENSION = ".intv"
PRESET_EXTENSION = ".intp"
THEME_EXTENSION = ".inttheme"

AUDIO_EXTENSIONS = [".wav", ".flac", ".aiff", ".mp3", ".ogg"]
MIDI_EXTENSIONS = [".mid", ".midi"]

# ============================================================================
# SPLASH MESSAGES
# ============================================================================

SPLASH_MESSAGES = [
    "Loading oscillators...",
    "Initializing chaos engine...",
    "Connecting neural pathways...",
    "Generating chromasynesthesia...",
    "Tuning the quantum strings...",
    "Evolving melodies...",
    "Preparing canvas for sound...",
    "Ready to break rules...",
]

WELCOME_MESSAGE = """
Welcome to Intuitives!

🎹 Press any key to play
🎲 Use 'G' for generative tools
🎨 Import an image to create music
📝 Type text to compose melodies

Remember: "Does this sound cool?" is the only rule.
"""

# ============================================================================
# ASCII ART LOGO
# ============================================================================

LOGO_ASCII = """
╔══════════════════════════════════════════════════════════════╗
║    ██╗███╗   ██╗████████╗██╗   ██╗██╗████████╗██╗██╗   ██╗███████╗  ║
║    ██║████╗  ██║╚══██╔══╝██║   ██║██║╚══██╔══╝██║██║   ██║██╔════╝  ║
║    ██║██╔██╗ ██║   ██║   ██║   ██║██║   ██║   ██║██║   ██║█████╗    ║
║    ██║██║╚██╗██║   ██║   ██║   ██║██║   ██║   ██║╚██╗ ██╔╝██╔══╝    ║
║    ██║██║ ╚████║   ██║   ╚██████╔╝██║   ██║   ██║ ╚████╔╝ ███████╗  ║
║    ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═══╝  ╚══════╝  ║
╠══════════════════════════════════════════════════════════════╣
║              Rule-free Experimental DAW                       ║
╚══════════════════════════════════════════════════════════════╝
"""

# Export version info function
def get_version_info():
    return {
        "name": APP_NAME,
        "version": VERSION_STRING,
        "codename": VERSION_NAME,
        "tagline": APP_TAGLINE,
    }
