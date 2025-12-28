from .multifx import MultiFXSingle
from intlib.models.multifx_settings import multifx_settings
from intlib.lib.translate import _
from intui.sgqt import *


class per_audio_item_fx_widget:
    """
    PURPOSE: A dedicated effect rack for per-clip (Audio Item) processing.
    ACTION: Displays a scrollable list of 8 MultiFXSingle slots that apply specifically to the selected audio item.
    MECHANISM: 
        1. Instantiates 8 MultiFXSingle instances, each mapped to a block of 4 ports.
        2. Encapsulates the rack in a QScrollArea to manage UI verticality.
        3. Provides set_from_list() and get_list() to synchronize UI state with the clip's underlying multifx_settings model.
        4. clear_effects(): Resets all slots to "Off" and knobs to default positions.
    """
    def __init__(
        self,
        a_rel_callback,
        a_val_callback,
    ):
        self.effects = []
        self.widget = QWidget()
        self.widget.setObjectName("plugin_ui")
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        f_port = 0
        for f_i in range(8):
            f_effect = MultiFXSingle(
                _("FX{}").format(f_i),
                f_port,
                a_rel_callback,
                a_val_callback,
                fixed_height=True,
                fixed_width=True,
                knob_kwargs={
                    'fg_svg': 'default',
                    'bg_svg': 'default_bg',
                },
            )
            f_effect.disable_mousewheel()
            self.effects.append(f_effect)
            self.layout.addWidget(f_effect.group_box)
            f_port += 4
        self.widget.setGeometry(0, 0, 348, 1100)  #ensure minimum size
        self.scroll_area = QScrollArea()
        self.scroll_area.setGeometry(0, 0, 360, 1120)
        self.scroll_area.setWidget(self.widget)

    def set_from_list(self, a_list):
        """ a_class is a multifx_settings instance """
        for f_i in range(len(a_list)):
            self.effects[f_i].set_from_class(a_list[f_i])

    def get_list(self):
        """ return a list of multifx_settings instances """
        f_result = []
        for f_effect in self.effects:
            f_result.append(f_effect.get_class())
        return f_result

    def clear_effects(self):
        for f_effect in self.effects:
            f_effect.combobox.set_value(0)
            for f_knob in f_effect.knobs:
                f_knob.set_value(64)

