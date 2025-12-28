from intlib.lib.translate import _
from intui.sgqt import *


class preset_browser_widget:
    """
    PURPOSE: A modern, tag-based navigation system for plugin presets (Beta).
    ACTION: Provides a menu for administrative tasks (Reload) and a list of searchable tags to filter preset results.
    MECHANISM: 
        1. Encapsulates a QListWidget for tag display and a QPushButton with a QMenu for actions.
        2. Intended to interface with the reconfigure_callback to swap plugin states without global DAW reloads.
        3. Designed to eventually replace the file-based bank/program selector with a metadata-driven database view.
    """
    def __init__(
        self,
        a_plugin_name,
        a_configure_dict=None,
        a_reconfigure_callback=None,
    ):
        self.plugin_name = str(a_plugin_name)
        self.configure_dict = a_configure_dict
        self.reconfigure_callback = a_reconfigure_callback
        self.widget = QWidget()
        self.widget.setObjectName("plugin_groupbox")
        self.main_vlayout = QVBoxLayout(self.widget)
        self.hlayout1 = QHBoxLayout()
        self.menu_button = QPushButton(_("Menu"))
        self.hlayout1.addWidget(self.menu_button)
        self.menu = QMenu(self.menu_button)
        self.menu_button.setMenu(self.menu)
        self.reload_action = self.menu.addAction(_("Reload"))
        self.reload_action.triggered.connect(self.on_reload)
        self.main_vlayout.addLayout(self.hlayout1)
        self.hlayout2 = QHBoxLayout()
        self.main_vlayout.addLayout(self.hlayout2)
        self.tag_list = QListWidget()
        self.hlayout2.addWidget(self.tag_list)

    def on_reload(self):
        pass

