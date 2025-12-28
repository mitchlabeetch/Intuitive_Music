# -*- coding: utf-8 -*-
"""
This file is part of the Intuitives project, Copyright Intuitives Team

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

from intui.plugins import *
from intui.sgqt import *
from intui.widgets import *
from intlib.lib.util import *
from intlib.lib.normalize import normalize_in_place

from . import *
from .filedragdrop import FileDragDropper
from .hardware import HardwareWidget, MidiDevicesDialog
from .item_editor.audio import (
    AudioItemSeq,
    AudioItemSeqWidget,
)
from .item_editor.automation import (
    AutomationEditor,
    AutomationEditorWidget,
)
from .item_editor.editor import ItemEditorWidget
from .item_editor.notes import (
    PianoRollEditor,
    PianoRollEditorWidget,
)
from .sequencer import (
    ItemListWidget,
    ItemSequencer,
    PlaylistWidget,
    SequencerWidget,
    TrackPanel,
)
from .transport import (
    MREC_EVENTS,
    TransportWidget,
)
from intlib import constants
from intlib.api.daw import api_project_notes
from intui import plugins
from intui import shared as glbl_shared
from intui.daw import strings as daw_strings
from intui.daw.lib import undo as undo_lib
from intlib.lib import *
from intlib.lib import strings as sg_strings
from intlib.lib.translate import _
from intlib.log import LOG

import datetime
import math
import os
import random
import shutil
import subprocess
import traceback


CLOSE_ENGINE_ON_RENDER = True

class MainWindow(QTabWidget):
    """ The main window for DAW that contains all widgets
        except TransportWidget
    """
    def __init__(self):
        """
        PURPOSE: Initializes the primary DAW interface, including the sequencer, plugin rack, item editor, mixer, and hardware settings.
        ACTION: Sets up the main tabbed interface, registers global shortcuts, instantiates core sub-widgets, and clears painter path caches.
        MECHANISM: 
            1. Calls shared.setup() to initialize global state.
            2. Configures default directories and corner widgets (engine monitor).
            3. Registers QActions for global shortcuts (Play, Stop, Record, Tools).
            4. Populates the QTabWidget with specific module views (Sequencer, Mixer, etc.) using shared references.
            5. Connects tab change signals to synchronization logic.
        """
        super().__init__()
        shared.setup()
        self.first_offline_render = True
        self.last_offline_dir = HOME
        self.copy_to_clipboard_checked = False
        self.last_midi_dir = None
        shared.ROUTING_GRAPH_WIDGET.setToolTip(sg_strings.routing_graph)

        # Otherwise they are incorrect on project reload
        painter_path.clear_caches()

        self.engine_mon_label = QLabel()
        self.engine_mon_label.setFixedWidth(150)
        self.engine_mon_label.setToolTip(sg_strings.ENGINE_MON)
        self.setCornerWidget(self.engine_mon_label)

        self.setObjectName("plugin_ui")

        # Transport shortcuts (added here so they will work
        # when the transport is hidden)

        self.loop_mode_action = QAction(self)
        self.addAction(self.loop_mode_action)
        self.loop_mode_action.setShortcut(
            QKeySequence.fromString("CTRL+L")
        )
        self.loop_mode_action.triggered.connect(
            shared.TRANSPORT.loop_mode_checkbox.trigger
        )

        self.select_mode_action = QAction(self)
        self.addAction(self.select_mode_action)
        self.select_mode_action.setShortcut(QKeySequence.fromString("A"))
        self.select_mode_action.triggered.connect(
            shared.TRANSPORT.tool_select_clicked,
        )

        self.draw_mode_action = QAction(self)
        self.addAction(self.draw_mode_action)
        self.draw_mode_action.setShortcut(QKeySequence.fromString("S"))
        self.draw_mode_action.triggered.connect(
            shared.TRANSPORT.tool_draw_clicked)

        self.erase_mode_action = QAction(self)
        self.addAction(self.erase_mode_action)
        self.erase_mode_action.setShortcut(QKeySequence.fromString("D"))
        self.erase_mode_action.triggered.connect(
            shared.TRANSPORT.tool_erase_clicked)

        self.split_mode_action = QAction(self)
        self.addAction(self.split_mode_action)
        self.split_mode_action.setShortcut(QKeySequence.fromString("F"))
        self.split_mode_action.triggered.connect(
            shared.TRANSPORT.tool_split_clicked)

        # TODO: SG MISC: Move this to it's own class
        self.song_sequence_tab = QWidget()
        self.song_sequence_vlayout = QVBoxLayout()
        self.song_sequence_vlayout.setContentsMargins(1, 1, 1, 1)
        self.song_sequence_tab.setLayout(self.song_sequence_vlayout)
        self.sequencer_widget = QWidget()
        self.sequencer_vlayout = QVBoxLayout(self.sequencer_widget)
        self.sequencer_vlayout.setContentsMargins(0, 0, 0, 0)
        self.sequencer_vlayout.setSpacing(0)
        self.sequencer_vlayout.addWidget(self.song_sequence_tab)
        self.addTab(self.sequencer_widget, _("Sequencer"))

        self.song_sequence_vlayout.addWidget(shared.SEQ_WIDGET.widget)

        self.midi_scroll_area = QScrollArea()
        self.midi_scroll_area.setWidgetResizable(True)
        self.midi_scroll_widget = QWidget()
        self.midi_scroll_widget.setContentsMargins(0, 0, 0, 0)
        self.midi_hlayout = QHBoxLayout(self.midi_scroll_widget)
        self.midi_hlayout.setContentsMargins(0, 0, 0, 0)
        self.midi_scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn,
        )
        self.midi_scroll_area.setWidget(self.midi_scroll_widget)
        self.midi_hlayout.addWidget(shared.TRACK_PANEL.tracks_widget)
        self.midi_hlayout.addWidget(shared.SEQUENCER)

        self.file_browser = FileDragDropper(util.is_audio_midi_file)
        self.file_browser.list_file.setToolTip(
            'Files in the current directory.  Drag and drop audio or '
            'MIDI files into the sequencer to create a new item Multiple '
            'audio files can be dragged at once (one item or per track), '
            'only one MIDI file at a time'
        )

        shared.PLAYLIST_EDITOR = PlaylistWidget()
        self.file_browser.folders_tab_widget.insertTab(
            0,
            shared.PLAYLIST_EDITOR.parent,
            _("Songs"),
        )

        shared.ITEMLIST = ItemListWidget()
        self.file_browser.folders_tab_widget.insertTab(
            0,
            shared.ITEMLIST.parent,
            _("Items"),
        )

        self.file_browser.folders_tab_widget.setCurrentIndex(0)
        self.file_browser.set_multiselect(True)
        self.file_browser.hsplitter.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.sequencer_vlayout.addWidget(self.file_browser.hsplitter)
        self.file_browser.hsplitter.insertWidget(0, self.midi_scroll_area)
        self.file_browser.hsplitter.setSizes([9999, 200])

        self.midi_scroll_area.scrollContentsBy = self.midi_scrollContentsBy
        self.vscrollbar = self.midi_scroll_area.verticalScrollBar()
        self.vscrollbar.sliderReleased.connect(self.vscrollbar_released)
        self.vscrollbar.setSingleStep(shared.SEQUENCE_EDITOR_TRACK_HEIGHT)

        self.addTab(
            shared.PLUGIN_RACK.widget,
            _("Plugin Rack"),
        )
        self.addTab(
            shared.ITEM_EDITOR.widget,
            _("Item Editor"),
        )

        self.automation_tab = QWidget()
        self.automation_tab.setObjectName("plugin_ui")

        self.addTab(
            shared.ROUTING_GRAPH_WIDGET,
            _("Routing"),
        )
        self.addTab(
            shared.MIXER_WIDGET.widget,
            _("Mixer"),
        )
        self.addTab(
            shared.HARDWARE_WIDGET,
            _("Hardware"),
        )

        self.notes_tab = ProjectNotes(
            self,
            api_project_notes.load,
            api_project_notes.save,
        )
        self.addTab(
            self.notes_tab.widget,
            _("Notepad"),
        )

        self.currentChanged.connect(self.tab_changed)
        shared.DAW = self

    def open_project(self):
        """
        PURPOSE: Triggers the internal UI update sequence when an existing project is opened.
        ACTION: Refreshes the recent project directory, loads project notes, and updates playlist/item list views.
        MECHANISM: Updates self.last_offline_dir and calls .load() or .open() on the notes tab and shared list widgets.
        """
        # TODO: SG DEPRECATED: Use new files/folders
        MAIN_WINDOW.last_offline_dir = constants.PROJECT.user_folder
        MAIN_WINDOW.notes_tab.load()
        shared.PLAYLIST_EDITOR.open()
        shared.ITEMLIST.open()

    def new_project(self):
        """
        PURPOSE: Triggers the internal UI update sequence when a new project is created.
        ACTION: Resets the recent directory and clears/initializes project-specific widgets.
        MECHANISM: Resets last_offline_dir and invokes load/open sequences for notes and file browsing widgets.
        """
        # TODO: SG DEPRECATED: Use new files/folders
        self.last_offline_dir = constants.PROJECT.user_folder
        self.notes_tab.load()
        shared.PLAYLIST_EDITOR.open()
        shared.ITEMLIST.open()

    def vscrollbar_released(self, a_val=None):
        """
        PURPOSE: Snap the sequencer's vertical scrollbar to track height increments after user interaction.
        ACTION: Adjusts the scrollbar position to align perfectly with track boundaries.
        MECHANISM: Calculates the current value's proximity to multiples of shared.SEQUENCE_EDITOR_TRACK_HEIGHT and calls self.vscrollbar.setValue().
        """
        # Avoid a bug where the bottom track is truncated
        if self.vscrollbar.value() == self.vscrollbar.maximum():
            return
        f_val = round(
            self.vscrollbar.value() /
            shared.SEQUENCE_EDITOR_TRACK_HEIGHT
        ) * shared.SEQUENCE_EDITOR_TRACK_HEIGHT
        self.vscrollbar.setValue(int(f_val))

    def on_offline_render(self):
        """
        PURPOSE: Initiates the process of rendering the project (or a specific region) to an audio file.
        ACTION: Opens a render dialog, allows configuration (sample rate, stems, normalization), and triggers the background rendering command.
        MECHANISM: 
            1. Validates region marker positions.
            2. Saves current plugin state.
            3. Displays a QDialog for user input.
            4. Executes a shell command using the configured parameters.
        """
        def copy_cmd_args():
            """
            PURPOSE: Development utility to copy the raw render command line to the clipboard.
            ACTION: Formats render arguments into a string and sets the system clipboard text.
            MECHANISM: Joins a list of command arguments and calls QApplication.clipboard().setText().
            """
            f_run_cmd = [
                str(x) for x in (
                    "daw",
                    "'{}'".format(constants.DAW_PROJECT.project_folder),
                    "test.wav",
                    f_start_beat,
                    f_end_beat,
                    "44100",
                    512,
                    1,
                    0,
                    0,
                    constants.DAW_CURRENT_SEQUENCE_UID,
                )
            ]
            f_clipboard = QApplication.clipboard()
            f_clipboard.setText(" ".join(f_run_cmd))

        def ok_handler():
            """
            PURPOSE: Processes the render dialog confirmation and starts the export.
            ACTION: Collects settings (path, stems, sample rate), hide/shows UI elements, and invokes the rendering background task.
            MECHANISM: 
                1. Validates the output name.
                2. Gathers device settings (buffer size, threads).
                3. Constructs the command arguments (util.BIN_PATH, "daw", etc.).
                4. Triggers global_shared.MAIN_WINDOW.show_offline_rendering_wait_window_v2.
            """
            if str(f_name.text()) == "":
                QMessageBox.warning(
                    f_window,
                    _("Error"),
                    _("Name cannot be empty"),
                )
                return

            if f_copy_to_clipboard_checkbox.isChecked():
                self.copy_to_clipboard_checked = True
                f_clipboard = QApplication.clipboard()
                f_clipboard.setText(f_name.text())
            else:
                self.copy_to_clipboard_checked = False

            f_stem = 1 if f_stem_render_checkbox.isChecked() else 0
            f_out_file = f_name.text()
            f_fini = os.path.join(f_out_file, "finished") if f_stem else None
            f_samp_rate = f_sample_rate.currentText()
            f_buff_size = util.DEVICE_SETTINGS["bufferSize"]
            if int(util.DEVICE_SETTINGS["threads"]) > 0:
                f_thread_count = int(util.DEVICE_SETTINGS["threads"])
            else:
                f_thread_count = util.AUTO_CPU_COUNT

            self.last_offline_dir = os.path.dirname(str(f_name.text()))

            f_window.close()

            f_cmd = [
                str(x) for x in (
                    util.BIN_PATH,
                    "daw",
                    constants.DAW_PROJECT.project_folder,
                    f_out_file,
                    f_start_beat,
                    f_end_beat,
                    f_samp_rate,
                    f_buff_size,
                    f_thread_count,
                    util.USE_HUGEPAGES,
                    f_stem,
                    constants.DAW_CURRENT_SEQUENCE_UID,
                    '--no-print-progress',
                )
            ]
            LOG.info(f"Rendering {f_cmd} to '{f_out_file}'")
            def _post_func():
                """
                PURPOSE: Performs post-rendering normalization on the resulting file.
                ACTION: Executes the normalization algorithm on the rendered audio file.
                MECHANISM: Calls normalize_in_place() with the specified dB value.
                """
                LOG.info(f'Normalizing {f_out_file}')
                normalize_in_place(f_out_file, normalize_db.value())
                LOG.info(f'Finished normalizing {f_out_file}')

            if (
                not f_stem_render_checkbox.isChecked()
                and
                normalize_checkbox.isChecked()
            ):
                post_func = _post_func
            else:
                post_func = None

            glbl_shared.MAIN_WINDOW.show_offline_rendering_wait_window_v2(
                f_cmd,
                f_out_file,
                f_file_name=f_fini,
                post_func=post_func,
            )

            if f_stem:
                f_tracks = constants.DAW_PROJECT.get_tracks()
                for f_file in os.listdir(f_out_file):
                    f_track_num = f_file.split(".", 1)[0].zfill(3)
                    f_track_name = f_tracks.tracks[int(f_track_num)].name
                    f_new = "{}-{}.wav".format(f_track_num, f_track_name)
                    shutil.move(
                        os.path.join(f_out_file, f_file),
                        os.path.join(f_out_file, f_new),
                    )

        def cancel_handler():
            """Closes the render dialog without any action."""
            f_window.close()

        def stem_check_changed(a_val=None):
            """
            PURPOSE: Updates the UI state when the Stem Render option is toggled.
            ACTION: Toggles visibility of normalization controls and resets the output name field.
            MECHANISM: Uses .hide() and .show() methods on normalization widgets based on the boolean state.
            """
            f_name.setText("")
            if a_val:
                normalize_checkbox.hide()
                normalize_db.hide()
            else:
                normalize_checkbox.show()
                normalize_db.show()

        def file_name_select():
            """
            PURPOSE: Opens a file selection dialog for the render output.
            ACTION: Prompts the user to choose a directory (for stems) or a filename (for single render).
            MECHANISM: 
                1. Checks stem rendering state.
                2. Calls QFileDialog.getExistingDirectory or QFileDialog.getSaveFileName accordingly.
                3. Updates the f_name text field and persistence directory.
            """
            if not os.path.isdir(self.last_offline_dir):
                self.last_offline_dir = HOME
            if f_stem_render_checkbox.isChecked():
                f_file = QFileDialog.getExistingDirectory(
                    MAIN_WINDOW,
                    _('Select an empty directory to render stems to'),
                    self.last_offline_dir,
                    (
                        QFileDialog.Option.ShowDirsOnly
                        |
                        QFileDialog.Option.DontUseNativeDialog
                    ),
                )
                if f_file and str(f_file):
                    if os.listdir(f_file):
                        QMessageBox.warning(
                            self, _("Error"),
                            _("The directory is not empty"))
                    else:
                        f_name.setText(f_file)
                        self.last_offline_dir = f_file
            else:
                f_file_name, f_filter = QFileDialog.getSaveFileName(
                    shared.MAIN_WINDOW,
                    _("Select a file name to save to..."),
                    self.last_offline_dir,
                    options=QFileDialog.Option.DontUseNativeDialog,
                )
                f_file_name = str(f_file_name)
                if f_file_name and str(f_file_name):
                    if not f_file_name.endswith(".wav"):
                        f_file_name += ".wav"
                    if f_file_name and str(f_file_name):
                        f_name.setText(f_file_name)
                    self.last_offline_dir = os.path.dirname(f_file_name)

        f_marker_pos = shared.SEQUENCER.get_loop_pos(a_warn=False)

        if not f_marker_pos:
            QMessageBox.warning(
                MAIN_WINDOW,
                _("Error"),
                _(
                    "You must set the region markers first by "
                    "right-clicking on the sequencer timeline.  "
                    "Only the region will be exported."
                ),
            )
            return

        # Force the plugin state to be saved to disk first if it changed
        shared.PLUGIN_RACK.tab_selected(False)

        f_start_beat, f_end_beat = f_marker_pos

        f_window = QDialog(MAIN_WINDOW)
        f_window.setWindowTitle(_("Render"))
        vlayout = QVBoxLayout()
        f_layout = QGridLayout()
        vlayout.addLayout(f_layout)
        f_window.setLayout(vlayout)

        f_name = QLineEdit()
        f_name.setToolTip('The full path to the rendered file to be created')
        f_name.setReadOnly(True)
        f_name.setMinimumWidth(360)
        f_layout.addWidget(QLabel(_("File Name:")), 0, 0)
        f_layout.addWidget(f_name, 0, 1)
        f_select_file = QPushButton(_("Select"))
        f_select_file.pressed.connect(file_name_select)
        f_layout.addWidget(f_select_file, 0, 2)

        f_sample_rate_hlayout = QHBoxLayout()
        f_layout.addLayout(f_sample_rate_hlayout, 3, 1)
        f_sample_rate_hlayout.addWidget(QLabel(_("Sample Rate")))
        f_sample_rate = QComboBox()
        f_sample_rate.setToolTip(
            'The sample rate of the rendered file.  Note that setting to a '
            'different rate than what the project was produced at can change '
            'the sound and throw off the mix'
        )
        f_sample_rate.setMinimumWidth(105)
        f_sample_rate.addItems([
            "44100",
            "48000",
            "88200",
            "96000",
            "192000",
            "384000",
            "768000",
            "1536000",
        ])

        try:
            f_sr_index = f_sample_rate.findText(
                util.DEVICE_SETTINGS["sampleRate"])
            f_sample_rate.setCurrentIndex(f_sr_index)
        except:
            pass

        f_sample_rate_hlayout.addWidget(f_sample_rate)

        f_stem_render_checkbox = QCheckBox(_("Stem Render"))
        f_stem_render_checkbox.setToolTip(
            'Render each track as an individual audio file'
        )
        f_sample_rate_hlayout.addWidget(f_stem_render_checkbox)
        f_stem_render_checkbox.stateChanged.connect(stem_check_changed)

        f_sample_rate_hlayout.addItem(
            QSpacerItem(1, 1, QSizePolicy.Policy.Expanding),
        )

        f_layout.addWidget(QLabel(
            _("File is exported to 32 bit .wav at the selected sample rate. "
            "\nYou can convert the format using "
            "Menu->Tools->MP3/Ogg Converter")),
            6, 1)
        f_copy_to_clipboard_checkbox = QCheckBox(
            _("Copy export path to clipboard?"),
        )
        f_copy_to_clipboard_checkbox.setChecked(self.copy_to_clipboard_checked)
        f_layout.addWidget(f_copy_to_clipboard_checkbox, 7, 1)

        normalize_layout = QHBoxLayout()
        f_layout.addLayout(normalize_layout, 8, 1)
        normalize_checkbox = QCheckBox('Normalize')
        normalize_checkbox.setToolTip('Check to normalize the rendered file')
        normalize_layout.addWidget(normalize_checkbox)

        normalize_db = QDoubleSpinBox()
        normalize_db.setToolTip(
            'The volume level, in decibels, to normalize the rendered file to'
        )
        normalize_layout.addWidget(normalize_db)
        normalize_db.setRange(-12., 0.)
        normalize_db.setSingleStep(0.1)
        normalize_db.setValue(-0.1)

        normalize_layout.addItem(
            QSpacerItem(1, 1, QSizePolicy.Policy.Expanding),
        )

        f_layout.addItem(
            QSpacerItem(
                10,
                10,
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Expanding,
            ),
            100,
            1,
        )


        f_ok_layout = QHBoxLayout()

        if util.IS_LINUX:
            f_debug_button = QPushButton(_("Copy cmd args"))
            f_debug_button.setToolTip(
                "For developer use only, copy the render command to the "
                "system clipboard"
            )
            f_ok_layout.addWidget(f_debug_button)
            f_debug_button.pressed.connect(copy_cmd_args)

        f_ok_layout.addItem(
            QSpacerItem(
                10,
                10,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum,
            )
        )
        f_ok = QPushButton(_("OK"))
        f_ok.setMinimumWidth(75)
        f_ok.pressed.connect(ok_handler)
        f_ok_layout.addWidget(f_ok)
        vlayout.addLayout(f_ok_layout)
        f_cancel = QPushButton(_("Cancel"))
        f_cancel.setMinimumWidth(75)
        f_cancel.pressed.connect(cancel_handler)
        f_ok_layout.addWidget(f_cancel)
        f_window.exec()

    def on_undo(self):
        """
        PURPOSE: Reverts the last user action in the project.
        ACTION: Calls the undo library and refreshes the UI.
        MECHANISM: Invokes undo_lib.undo() and triggers global_ui_refresh_callback() if successful.
        """
        if glbl_shared.IS_PLAYING or not self.check_tab_for_undo():
            return
        glbl_shared.APP.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        if undo_lib.undo():
            global_ui_refresh_callback()
            glbl_shared.APP.restoreOverrideCursor()
        else:
            glbl_shared.APP.restoreOverrideCursor()
            QMessageBox.warning(
                MAIN_WINDOW,
                "Error",
                "No more undo history left",
            )

    def on_redo(self):
        """
        PURPOSE: Reapplies a previously undone action.
        ACTION: Calls the redo library and refreshes the UI.
        MECHANISM: Invokes undo_lib.redo() and triggers global_ui_refresh_callback() if successful.
        """
        if glbl_shared.IS_PLAYING or not self.check_tab_for_undo():
            return
        glbl_shared.APP.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        if undo_lib.redo():
            shared.global_ui_refresh_callback()
            glbl_shared.APP.restoreOverrideCursor()
        else:
            glbl_shared.APP.restoreOverrideCursor()
            QMessageBox.warning(
                shared.MAIN_WINDOW,
                "Error",
                "Already at the latest commit",
            )

    def check_tab_for_undo(self):
        """
        PURPOSE: Determines if the current active tab supports undo/redo operations.
        ACTION: Returns True if the current tab is the Item Editor, Routing, or Sequencer.
        MECHANISM: Checks self.currentIndex() against predefined tab constants.
        """
        index = self.currentIndex()
        if index in (
            shared.TAB_ITEM_EDITOR,
            shared.TAB_ROUTING,
            shared.TAB_SEQUENCER,
        ):
            return True
        else:
            QMessageBox.warning(
                shared.MAIN_WINDOW, "Error",
                "Undo/redo only supported for the sequencer, item editor "
                "and routing tab.  Individual plugins have undo for each "
                "control by right-clicking and selecting the undo menu")
            return False

    def tab_changed(self):
        """
        PURPOSE: Orchestrates UI synchronization when the user switches between different DAW views.
        ACTION: Updates global contexts, refreshes specific tab data, and manages solo loop state.
        MECHANISM: 
            1. Clears solo loops.
            2. Notifies the transport of the tab change.
            3. Updates undo context.
            4. Triggers tab-specific refresh logic (e.g., drawing the routing graph or opening the mixer).
        """
        try:
            f_index = self.currentIndex()

            shared.ITEM_EDITOR.clear_solo_loop()
            shared.TRANSPORT.tab_changed(f_index)

            constants.DAW_PROJECT.set_undo_context(f_index)
            if f_index == shared.TAB_SEQUENCER and not glbl_shared.IS_PLAYING:
                shared.SEQUENCER.open_sequence()
            elif f_index == shared.TAB_ITEM_EDITOR:
                shared.ITEM_EDITOR.tab_changed()
            elif f_index == shared.TAB_ROUTING:
                shared.ROUTING_GRAPH_WIDGET.draw_graph(
                    constants.DAW_PROJECT.get_routing_graph(),
                    shared.TRACK_NAMES,
                )
            elif f_index == shared.TAB_MIXER:
                global_open_mixer()

            shared.PLUGIN_RACK.tab_selected(f_index == shared.TAB_PLUGIN_RACK)
        except Exception as ex:
            LOG.error(f"Error changing tab to index {self.currentIndex()}")
            LOG.exception(ex)
            QMessageBox.warning(
                self,
                _("Error"),
                _("An error occurred while changing tabs. check the log for details."),
            )
        finally:
            QApplication.restoreOverrideCursor()


    def midi_scrollContentsBy(self, x, y):
        """
        PURPOSE: Synchronizes the vertical scroll position of the sequencer header with the track content.
        ACTION: Scrolls the main area and then updates the header's Y position.
        MECHANISM: Calls super().scrollContentsBy() and then shared.SEQUENCER.set_header_y_pos().
        """
        QScrollArea.scrollContentsBy(self.midi_scroll_area, x, y)
        f_y = self.midi_scroll_area.verticalScrollBar().value()
        shared.SEQUENCER.set_header_y_pos(f_y)

    def configure_callback(self, arr):
        """
        PURPOSE: Processes real-time status updates from the audio engine to update the GUI.
        ACTION: Synchronizes playback position, peak meters, and plugin parameter values.
        MECHANISM: 
            1. Parses the semicolon-delimited input string into commands (pc, cur, peak, cc, etc.).
            2. Distributes updates to relevant widgets (Mixer, Item Editor, Plugin Rack).
        """
        f_pc_dict = {}
        f_ui_dict = {}
        f_cc_dict = {}
        for f_line in arr.split("\n"):
            if f_line == "":
                break
            a_key, a_val = f_line.split("|", 1)
            if a_key == "pc":
                f_plugin_uid, f_port, f_val = a_val.split("|")
                f_pc_dict[(f_plugin_uid, f_port)] = f_val
            elif a_key == "cur":
                if glbl_shared.IS_PLAYING:
                    f_beat = float(a_val)
                    global_set_playback_pos(f_beat)
            elif a_key == "peak":
                global_update_peak_meters(a_val)
            elif a_key == "cc":
                f_track_num, f_cc, f_val, channel = (
                    int(x) for x in a_val.split("|")
                )
                f_cc_dict[(f_track_num, f_cc, channel)] = f_val
            elif a_key == "ui":
                f_plugin_uid, f_name, f_val = a_val.split("|", 2)
                f_ui_dict[(f_plugin_uid, f_name)] = f_val
            elif a_key == "mrec":
                MREC_EVENTS.append(a_val)
            elif a_key == "ne":
                f_state, f_note = a_val.split("|")
                shared.PIANO_ROLL_EDITOR.highlight_keys(f_state, f_note)
            elif a_key == "ml":
                glbl_shared.PLUGIN_UI_DICT.midi_learn_control[0].update_cc_map(
                    a_val,
                    glbl_shared.PLUGIN_UI_DICT.midi_learn_control[1],
                )
            elif a_key == "ready":
                glbl_shared.on_ready()
        #This prevents multiple events from moving the same control,
        #only the last goes through
        for k, f_val in f_ui_dict.items():
            f_plugin_uid, f_name = k
            if int(f_plugin_uid) in glbl_shared.PLUGIN_UI_DICT:
                glbl_shared.PLUGIN_UI_DICT[int(f_plugin_uid)].ui_message(
                    f_name, f_val)
        for k, f_val in f_pc_dict.items():
            f_plugin_uid, f_port = (int(x) for x in k)
            if f_plugin_uid in glbl_shared.PLUGIN_UI_DICT:
                glbl_shared.PLUGIN_UI_DICT[f_plugin_uid].set_control_val(
                    f_port,
                    float(f_val),
                )
        for k, f_val in f_cc_dict.items():
            f_track_num, f_cc, channel = (int(x) for x in k)
            uids = []
            if f_track_num in shared.PLUGIN_RACK.plugin_racks:
                rack = shared.PLUGIN_RACK.plugin_racks[f_track_num]
                uids.extend(rack.get_plugin_uids())
            if f_track_num in shared.MIXER_WIDGET.tracks:
                track = shared.MIXER_WIDGET.tracks[f_track_num]
                uids.extend(track.get_plugin_uids())
            for f_plugin_uid, plugin_channel in uids:
                if (
                    f_plugin_uid in glbl_shared.PLUGIN_UI_DICT
                    and
                    plugin_channel == channel
                ):
                    plugin =  glbl_shared.PLUGIN_UI_DICT[f_plugin_uid]
                    plugin.set_cc_val(f_cc, f_val)

    def prepare_to_quit(self):
        """
        PURPOSE: Cleans up widget states and saves necessary data before the application exits.
        ACTION: Calls prepare_to_quit() on all major sub-widgets.
        MECHANISM: Iterates through a tuple of widgets (AUDIO_SEQ, CC_EDITOR, etc.) and invokes their cleanup methods.
        """
        try:
            for f_widget in (
                shared.AUDIO_SEQ,
                shared.CC_EDITOR,
                shared.PB_EDITOR,
                shared.PIANO_ROLL_EDITOR,
                shared.ROUTING_GRAPH_WIDGET,
                shared.SEQUENCER,
            ):
                f_widget.prepare_to_quit()
        except Exception as ex:
            LOG.error("Exception raised while attempting to close DAW")
            LOG.exception(ex)

def init():
    """
    PURPOSE: Bootstraps the entire DAW GUI infrastructure.
    ACTION: Instantiates all core singleton widgets and establishes the main window.
    MECHANISM: 
        1. Initializes shared sequencer, editors, panels, and routing widgets.
        2. Configures default startup states (snap index, scroll positions).
        3. Creates the MainWindow instance which ties everything together.
    """
    global MAIN_WINDOW, TRANSPORT
    shared.ATM_SEQUENCE = DawAtmRegion()
    shared.SEQUENCER = ItemSequencer()
    shared.PB_EDITOR = AutomationEditor(a_is_cc=False)
    shared.CC_EDITOR = AutomationEditor()
    shared.CC_EDITOR_WIDGET = AutomationEditorWidget(shared.CC_EDITOR)

    shared.SEQ_WIDGET = SequencerWidget()
    shared.TRACK_PANEL = TrackPanel()

    shared.PIANO_ROLL_EDITOR = PianoRollEditor()
    shared.PIANO_ROLL_EDITOR_WIDGET = PianoRollEditorWidget()
    shared.AUDIO_SEQ = AudioItemSeq()
    shared.AUDIO_SEQ_WIDGET = AudioItemSeqWidget()
    shared.ITEM_EDITOR = ItemEditorWidget()
    shared.MIXER_WIDGET = plugins.MixerWidget(TRACK_COUNT_ALL)

    get_mixer_peak_meters()

    shared.MIDI_EDITORS = (
        shared.CC_EDITOR,
        shared.PB_EDITOR,
        shared.PIANO_ROLL_EDITOR,
    )

    shared.MIDI_DEVICES_DIALOG = MidiDevicesDialog()
    shared.HARDWARE_WIDGET = HardwareWidget()
    shared.TRANSPORT = TransportWidget()
    TRANSPORT = shared.TRANSPORT

    shared.ROUTING_GRAPH_WIDGET = widgets.RoutingGraphWidget(
        routing_graph_toggle_callback,
    )

    shared.PLUGIN_RACK = PluginRackTab()

    # Must call this after instantiating the other widgets,
    # as it relies on them existing
    shared.MAIN_WINDOW = MainWindow()
    MAIN_WINDOW = shared.MAIN_WINDOW

    shared.PIANO_ROLL_EDITOR.verticalScrollBar().setSliderPosition(
        int(shared.PIANO_ROLL_EDITOR.scene.height() * 0.4),
    )

    shared.ITEM_EDITOR.snap_combobox.setCurrentIndex(4)

