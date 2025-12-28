import os
import sys
import traceback
import time

from .preflight import preflight
from intlib.log import LOG
from intlib.lib.translate import _
from intlib.lib import util
from intui import (
    shared as glbl_shared,
    project as project_mod,
    widgets,
)
from intui.daw import shared as daw_shared
from intui.main import main as main_window_open
from intui import sgqt
from intui.sgqt import (
    create_hintbox,
    QApplication,
    QGuiApplication,
    QMessageBox,
    QStackedWidget,
    QtCore,
    Signal,
)
from intui.splash import SplashScreen
from intui.util import setup_theme, ui_scaler_factory
from intui.util import setup_theme, ui_scaler_factory
from intui.enhanced_welcome import EnhancedWelcome
from intui.project import (
    new_project,
    open_project,
    clone_project,
    check_project_version,
    set_project,
    get_history,
    IntuitivesProjectVersionError,
)


class MainStackedWidget(QStackedWidget):
    resized = Signal()

    def __init__(self, *args, **kwargs):
        """
        PURPOSE: Initializes the main container widget that manages switching between splash, welcome, and main DAW screens.
        ACTION: Sets the object name and initializes references for main_window, welcome_window, splash_screen, and hardware_dialog.
        MECHANISM: Calls the parent QStackedWidget constructor and sets internal state variables to None.
        """
        QStackedWidget.__init__(self, *args, **kwargs)
        self.setObjectName('main_window')
        self.main_window = None
        self.welcome_window = None
        self.splash_screen = None
        self.hardware_dialog = None
        self.next = None
        self.previous = None

    def toggle_full_screen(self):
        """
        PURPOSE: Switches the application window between full-screen mode and maximized window mode.
        ACTION: Checks the current screen state and toggles it.
        MECHANISM: Uses isFullScreen() to determine state, then calls showMaximized() or showFullScreen() accordingly.
        """
        fs = self.isFullScreen()
        if fs:
            self.showMaximized()
        else:
            self.showFullScreen()

    def show_main(self):
        """
        PURPOSE: Transitions the UI to the main DAW interface.
        ACTION: Displays the splash screen, initializes the main window with the current project, and adds it to the stack.
        MECHANISM: 
            1. Verifies splash screen availability via show_splash().
            2. Calls the main_window_open factory function.
            3. Registers the resulting widget in the QStackedWidget and sets it as current.
        """
        if not self.show_splash():
            return
        self.main_window = main_window_open(
            self.splash_screen,
            project_mod.PROJECT_DIR,
        )
        self.addWidget(self.main_window)
        self.setCurrentWidget(self.main_window)

    def show_welcome(self):
        """
        PURPOSE: Displays the initial "Welcome" screen where users can create or open projects.
        ACTION: Instantiates the EnhancedWelcome widget if needed, connects its signals to logic handlers, and refreshes the recent projects list.
        MECHANISM: Checks for welcome_window existence, connects Qt signals (new, open, clone, recent, hardware), and calls populate_welcome_recent().
        """
        if not self.welcome_window:
            self.welcome_window = EnhancedWelcome()
            self.addWidget(self.welcome_window)
            
            # Connect signals
            self.welcome_window.new_project_requested.connect(self.on_welcome_new)
            self.welcome_window.open_project_requested.connect(self.on_welcome_open)
            self.welcome_window.clone_project_requested.connect(self.on_welcome_clone)
            self.welcome_window.recent_project_selected.connect(self.on_welcome_recent)
            self.welcome_window.hardware_settings_requested.connect(self.on_welcome_hardware)
            
        self.setCurrentWidget(self.welcome_window)
        self.populate_welcome_recent()
        self.setWindowTitle('Intuitives DAW')

    def populate_welcome_recent(self):
        """
        PURPOSE: Updates the list of recently opened projects on the welcome screen.
        ACTION: Clears existing items and repopulates the list from the project history.
        MECHANISM: Retrieves path strings via get_history() and iterates through them to add items to the welcome_window.
        """
        self.welcome_window.clear_recent_projects()
        history = get_history()
        for path in history:
            self.welcome_window.add_recent_project(path)

    def on_welcome_new(self):
        """
        PURPOSE: Handles the "New Project" workflow from the welcome screen.
        ACTION: Checks hardware status, prompts for a new project file, and starts the DAW if successful.
        MECHANISM: 
            1. Calls check_hardware().
            2. Invokes new_project() from the project module.
            3. On success, calls self.start() to proceed.
        """
        try:
            if not self.check_hardware(self.on_welcome_new):
                return
            path = new_project(self.welcome_window)
            if path:
                self.start()
        except Exception as ex:
            LOG.exception(ex)
            QMessageBox.warning(None, "Error", f"An error occurred: {ex}")

    def on_welcome_open(self):
        """
        PURPOSE: Handles the "Open Project" workflow from the welcome screen.
        ACTION: Checks hardware status, opens an existing project file, and starts the DAW if successful.
        MECHANISM: 
            1. Calls check_hardware().
            2. Invokes open_project().
            3. On success, calls self.start().
        """
        try:
            if not self.check_hardware(self.on_welcome_open):
                return
            if open_project(self.welcome_window):
                self.start()
        except Exception as ex:
            LOG.exception(ex)
            QMessageBox.warning(None, "Error", f"An error occurred: {ex}")

    def on_welcome_clone(self):
        """
        PURPOSE: Handles the "Clone Project" workflow from the welcome screen.
        ACTION: Checks hardware status, clones an existing project, and starts the DAW.
        MECHANISM: 
            1. Calls check_hardware().
            2. Invokes clone_project().
            3. On success, calls self.start().
        """
        try:
            if not self.check_hardware(self.on_welcome_clone):
                return
            if clone_project(self.welcome_window):
                self.start()
        except Exception as ex:
            LOG.exception(ex)
            QMessageBox.warning(None, "Error", f"An error occurred: {ex}")

    def on_welcome_recent(self, path):
        """
        PURPOSE: Handles selecting a project from the "Recent" list.
        ACTION: Verifies hardware, file existence, and project version compatibility before setting it as the active project.
        MECHANISM: 
            1. Verifies hardware.
            2. Checks os.path.isfile().
            3. Validates version via check_project_version().
            4. Calls set_project(path) and self.start().
        """
        try:
            if not self.check_hardware():
               return
            if not os.path.isfile(path):
                QMessageBox.warning(
                    None,
                    "Error",
                    f"'{path}' was moved, deleted or the storage device is no longer readable"
                )
                self.populate_welcome_recent()
                return
                
            try:
                check_project_version(self.welcome_window, path)
            except IntuitivesProjectVersionError:
                return
                
            set_project(path)
            self.start()
        except Exception as ex:
           LOG.exception(ex)
           QMessageBox.warning(None, "Error", f"An error occurred: {ex}")

    def on_welcome_hardware(self):
        """
        PURPOSE: Opens the hardware settings dialog from the welcome screen.
        ACTION: Displays the hardware configuration UI.
        MECHANISM: Calls show_hardware_dialog() with the welcome screen as both next and previous target.
        """
        self.show_hardware_dialog(
            self.show_welcome,
            self.show_welcome
        )

    def start(self):
        """
        PURPOSE: Initiates the transition sequence from project selection to active DAW usage.
        ACTION: Shows the splash screen and then the main window.
        MECHANISM: Sequentially calls show_splash() and show_main().
        """
        if self.show_splash():
            self.show_main()

    def check_hardware(self, _next=None):
        """
        PURPOSE: Verifies that audio/MIDI hardware is correctly configured before starting engine-dependent tasks.
        ACTION: Performs a device check and opens the hardware dialog if interaction is required.
        MECHANISM: 
            1. Instantiates HardwareDialog and calls check_device().
            2. If an issue/message is returned, it calls show_hardware_dialog and returns False.
            3. Otherwise, returns True.
        """
        hardware_dialog = widgets.HardwareDialog()
        result = hardware_dialog.check_device()
        if result:
            self.show_hardware_dialog(
                _next if _next else self.show_welcome,
                self.show_welcome,
                result,
            )
            return False
        return True

    def show_splash(self):
        """
        PURPOSE: Displays the application splash screen during loading sequences.
        ACTION: Instantiates the SplashScreen if it doesn't exist and brings it to the front.
        MECHANISM: Uses lazy initialization for the SplashScreen widget and sets it as the current stacked widget.
        """
        if not self.splash_screen:
            self.splash_screen = SplashScreen(self)
            self.addWidget(self.splash_screen)
        self.setCurrentWidget(self.splash_screen)
        return True

    def show_hardware_dialog(
        self,
        _next,
        previous,
        msg=None,
    ):
        """
        PURPOSE: Displays the hardware configuration dialog to the user.
        ACTION: Replaces any existing hardware dialog with a new one and focuses it.
        MECHANISM: 
            1. Unregisters the old dialog instance.
            2. Calls the hardware_dialog_factory to create a new instance (potentially with a specific message).
            3. Adds it to the widget stack and makes it current.
        """
        self.next = _next
        self.previous = previous
        if self.hardware_dialog:
            self.removeWidget(self.hardware_dialog)
        hardware_dialog = widgets.HardwareDialog()
        self.hardware_dialog = hardware_dialog.hardware_dialog_factory(msg)
        self.addWidget(self.hardware_dialog)
        self.setCurrentWidget(self.hardware_dialog)

    def closeEvent(self, event):
        """
        PURPOSE: Intercepts the window close event to ensure data integrity and user confirmation.
        ACTION: Prevents closure if critical tasks (like project saving or playback) are occurring without consent.
        MECHANISM: 
            1. Checks IGNORE_CLOSE_EVENT and provides feedback if a dialog is open or audio is playing.
            2. Triggers a confirmation QMessageBox with 'Yes' and 'Cancel' options.
            3. If 'Yes', cleans up solo loops, prepares the window for quitting, and accepts the event.
        """
        self.raise_()
        if glbl_shared.IGNORE_CLOSE_EVENT:
            if sgqt.DIALOG_SHOWING:
                event.ignore()
                LOG.info(
                    "User tried to close the window while a dialog is open"
                )
                return
            event.ignore()
            if glbl_shared.IS_PLAYING:
                LOG.info("User tried to close the window during playback")
                return
            glbl_shared.MAIN_WINDOW.setEnabled(False)
            def _cancel():
                glbl_shared.MAIN_WINDOW.setEnabled(True)
            def _yes():
                daw_shared.ITEM_EDITOR.clear_solo_loop()
                glbl_shared.MAIN_WINDOW.prepare_to_quit()
                glbl_shared.IGNORE_CLOSE_EVENT = False
                self.close()
            f_reply = QMessageBox.question(
                self,
                _('Close'),
                _("Are you sure you want to close Intuitives DAW?"),
                (
                    QMessageBox.StandardButton.Yes
                    |
                    QMessageBox.StandardButton.Cancel
                ),
                QMessageBox.StandardButton.Cancel,
                callbacks={
                    QMessageBox.StandardButton.Yes: _yes,
                    QMessageBox.StandardButton.Cancel: _cancel,
                },
            )
        else:
            event.accept()

    def resizeEvent(self, event):
        """
        PURPOSE: Handles window resizing events for responsive layout adjustments.
        ACTION: Passes the event to the parent and emits a custom 'resized' signal.
        MECHANISM: Calls super().resizeEvent(event) and then self.resized.emit().
        """
        super().resizeEvent(event)
        self.resized.emit()

def qt_message_handler(mode, context, message):
    """
    PURPOSE: Captures and redirects low-level Qt framework messages to the application's logging system.
    ACTION: Formats Qt warnings, errors, and debug messages and writes them to the LOG.
    MECHANISM: Uses a conditional mapping of QtMsgType to LOG levels (warning, error, info).
    """
    line = (
        f'qt_message_handler: {mode} '
        f'{context.file}:{context.line}:{context.function}'
        f' "{message}"'
    )
    try:
        if mode == QtCore.QtMsgType.QtWarningMsg:
            LOG.warning(line)
        elif mode in (
            QtCore.QtMsgType.QtCriticalMsg,
            QtCore.QtMsgType.QtFatalMsg,
        ):
            LOG.error(line)
        else:
            LOG.info(line)
    except Exception as ex:
        LOG.warning(f'Could not log Qt message: {ex}')



def exception_hook(exctype, value, tb):
    """
    PURPOSE: Provides a global safety net to catch and log any unhandled Python exceptions.
    ACTION: Logs the exception traceback and displays a critical error message box to the user.
    MECHANISM: Uses the traceback module to format the error and attempts to show a QMessageBox.critical dialog.
    """
    LOG.error("Unhandled exception caught by global hook")
    LOG.error("".join(traceback.format_exception(exctype, value, tb)))
    
    # Try to show a message box if possible
    try:
        msg = f"An unexpected error occurred:\n\n{value}\n\nSee log for details."
        QMessageBox.critical(None, "Critical Error", msg)
    except:
        pass

def _setup():
    """
    PURPOSE: Performs pre-launch environment configuration and application-level setup.
    ACTION: Configures exception hooks, message handlers, DPI settings, and UI themes.
    MECHANISM: 
        1. Registers exception_hook and qt_message_handler.
        2. Sets HighDpiScaleFactorRoundingPolicy.
        3. Initializes the QApplication and applies the custom Intuitives theme.
    """
    LOG.info(f"sys.argv == {sys.argv}")
    sys.excepthook = exception_hook
    QtCore.qInstallMessageHandler(qt_message_handler)
    try:
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough,
        )
    except Exception as ex:
        LOG.warning(
            "Unable to set "
            "QGuiApplication.setHighDpiScaleFactorRoundingPolicy"
            f" {ex}"
        )
    app = QApplication(sys.argv)
    setup_theme(app)
    create_hintbox()
    return app

def main(args):
    """
    PURPOSE: Orchestrates the high-level startup sequence and manages the application lifecycle.
    ACTION: Initializes the app, checks for existing instances (PID check), sets up the main widget stack, and runs the main loop.
    MECHANISM: 
        1. Calls _setup() to get the QApp instance.
        2. Verifies uniqueness via check_pidfile.
        3. Configures global_shared.MAIN_STACKED_WIDGET.
        4. Runs preflight() checks.
        5. Switches to either the welcome screen or starts a specific project.
        6. Enters QAPP.exec() loop and performs final cleanup on exit.
    """
    if 'APPDIR' in os.environ:
        LD_LIBRARY_PATH = os.environ.get('LD_LIBRARY_PATH', None)
        LOG.info(f'LD_LIBRARY_PATH={LD_LIBRARY_PATH}')
    global QAPP
    QAPP = _setup()
    QAPP.restoreOverrideCursor()
    from intlib.constants import UI_PIDFILE
    from intlib.lib.pidfile import check_pidfile, create_pidfile
    pid = check_pidfile(UI_PIDFILE)
    if pid is not None:
        msg = (
            f"Detected Intuitives is already running with pid {pid}, "
            "please close the other instance first"
        )
        QMessageBox.warning(None, "Error", msg)
        LOG.error(msg)
        sys.exit(0)
    create_pidfile(UI_PIDFILE)
    glbl_shared.MAIN_STACKED_WIDGET = MainStackedWidget()
    glbl_shared.MAIN_STACKED_WIDGET.setMinimumSize(1280, 700)
    glbl_shared.MAIN_STACKED_WIDGET.showMaximized()
    preflight()
    if args.project_file:
        glbl_shared.MAIN_STACKED_WIDGET.start()
    else:
        glbl_shared.MAIN_STACKED_WIDGET.show_welcome()
    exit_code = QAPP.exec()
    #quit_timer = QtCore.QTimer(self)
    #quit_timer.setSingleShot(True)
    #quit_timer.timeout.connect(self.close)
    #quit_timer.start(1000)
    time.sleep(0.3)
    from intui import main
    main.flush_events()
    LOG.info("Calling os._exit()")
    os.remove(UI_PIDFILE)
    # Work around PyQt SEGFAULT-on-exit issues
    os._exit(exit_code)

