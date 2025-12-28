"""
PURPOSE: The primary package entry point for the Intuitives Component Library.
ACTION: Aggregates and exports all specialized UI widgets, from low-level controls (Knobs, Buttons) to high-level DSP modules (ADSR, EQ, Generators).
MECHANISM: 
    1. Performs star-imports and explicit imports of all submodules to expose a flat API under intui.widgets.
    2. Categorizes exports into standard DAW widgets and 'Signature' components (Animations, Generative tools, Happy Accidents).
    3. Serves as the central registry for the DAW's polymorphic UI framework.
"""
from . import _shared
from ._shared import *
from .abstract_plugin_ui import AbstractPluginUI
from .add_mul_dialog import add_mul_dialog
from .additive_osc import *
from .adsr import adsr_widget
from .adsr_main import ADSRMainWidget
from .audio_item_viewer import *
from .control import *
from .hardware_dialog import HardwareDialog
from .distortion import MultiDistWidget
from .eq import *
from .file_browser import (
    AbstractFileBrowserWidget,
    FileBrowserWidget,
    FileDragDropListWidget,
)
from .file_select import file_select_widget
from .filter import filter_widget
from .freq_splitter import FreqSplitter
from .knob import *
from .lfo import lfo_widget
from .lfo_dialog import lfo_dialog
from .main import main_widget
from .multifx import MultiFXSingle, MULTIFX_ITEMS_SYNTH, MULTIFX_ITEMS_EFFECT
from .multifx10 import MultiFX10
from .note_selector import NoteSelectorWidget
from .ordered_table import ordered_table_dialog
from .paif import per_audio_item_fx_widget
from .peak_meter import peak_meter
from .perc_env import perc_env_widget
from .preset_browser import preset_browser_widget
from .preset_manager import preset_manager_widget
from .project_notes import ProjectNotes
from .pysound import *
from .ramp_env import ramp_env_widget
from .routing_matrix import *
from .sample_viewer import *
from .spectrum import spectrum
from .time_pitch_dialog import TimePitchDialogWidget
from .va_osc import osc_widget
from intlib.lib import util
from intlib.lib.translate import _
from intui.sgqt import *

# Intuitives Signature UI Widgets
from .animation import (
    AnimatedValue,
    AnimatedWidget,
    GlowButton,
    HoverRevealWidget,
    PulseIndicator,
    TypingLabel,
    SmoothScrollArea,
)
from .generators import (
    GeneratorPanel,
    ChromasynesthesiaWidget,
)
from .happy_accidents import (
    HappyAccidentWidget,
    SuggestionToast,
    QuickExperimentBar,
    Suggestion,
    SuggestionCategory,
)
from .visual_music import (
    ChromasynesthesiaVisualizer,
    OrbitalVisualizer,
    SpectrumBars,
    VisualizerSelector,
)
