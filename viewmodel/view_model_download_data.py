import logging
from PySide6.QtCore import Signal, QObject
from model.Base.Progress import ProgressSignal

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
delimiter = " "
lineend = '\n'


class ViewModelDownloadedData(QObject):
    update_progress_value = Signal(ProgressSignal)
    error_message = Signal(str)

    def __init__(self, app, model):
        super().__init__()
        self.app = app
        self.model = model

    def send_error_message(self, message):
        self.error_message.emit(message)

    def on_changed_progress_value(self, progress_data: ProgressSignal):
        self.update_progress_value.emit(progress_data)