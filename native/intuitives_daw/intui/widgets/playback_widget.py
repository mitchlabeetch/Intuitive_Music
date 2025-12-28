from intui import shared as glbl_shared
from intui.sgqt import *

class playback_widget:
    """
    PURPOSE: A local transport control interface.
    ACTION: Provides Play and Stop buttons that trigger the global sequencer state.
    MECHANISM: 
        1. Instantiates two QRadioButtons, leveraging their mutually exclusive nature for Play vs. Stop state.
        2. Hooks into glbl_shared.TRANSPORT to communicate with the central playback engine.
        3. Stylized via CSS selectors (#play_button, #stop_button) to appear as standard DAW icons.
    """
    def __init__(self):
        self.play_button = QRadioButton()
        self.play_button.setObjectName("play_button")
        self.play_button.clicked.connect(glbl_shared.TRANSPORT.on_play)
        self.stop_button = QRadioButton()
        self.stop_button.setChecked(True)
        self.stop_button.setObjectName("stop_button")
        self.stop_button.clicked.connect(glbl_shared.TRANSPORT.on_stop)

