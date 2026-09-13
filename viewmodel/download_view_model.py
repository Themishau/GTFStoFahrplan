from PySide6.QtCore import QObject, Signal


class DownloadViewModel(QObject):
    error_message = Signal(str)

    def __init__(self, app, model, parent=None):
        super().__init__(parent)
        self.app = app
        self.model = model

    def send_error_message(self, message):
        self.error_message.emit(message)

