from intui.sgqt import QTextEdit


class ProjectNotes:
    """
    PURPOSE: A simple, persistent text editor for project-specific metadata.
    ACTION: Allows the user to store lyrics, scales, or production ideas directly within the project.
    MECHANISM: 
        1. Encapsulates a QTextEdit widget restricted to plain text.
        2. Implements auto-save behavior by hooking into the leaveEvent (saving when the widget loses focus).
        3. Uses dependency injection for _load and _save functions, decoupling the UI from specific file systems or models.
    """
    def __init__(
        self._save = _save
        self._load = _load
        self.widget = QTextEdit(parent)
        self.widget.setToolTip(
            'Project notes.  Keep notes about your project here, anything '
            'that is useful, for example: lyrics, scales, ideas'
        )
        self.widget.setAcceptRichText(False)
        self.widget.leaveEvent = self.on_edit_notes

    def load(self):
        self.widget.setText(
            self._load(),
        )

    def on_edit_notes(self, a_event=None):
        QTextEdit.leaveEvent(self.widget, a_event)
        self._save(
            self.widget.toPlainText(),
        )

