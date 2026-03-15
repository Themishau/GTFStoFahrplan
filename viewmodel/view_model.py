import logging
from PySide6.QtCore import Signal, QObject
from model.Base.Progress import ProgressSignal
from viewmodel.view_model_create_data import ViewModelCreateData
from viewmodel.view_model_download_data import ViewModelDownloadedData
from viewmodel.view_model_import_data import ViewModelImportData
from viewmodel.view_model_select_data import ViewModelSelectData
from viewmodel.view_model_signals import ViewModelSignals

delimiter = " "
lineend = '\n'

logger = logging.getLogger(__name__)

class ViewModel(QObject):
    update_progress_value = Signal(ProgressSignal)
    error_message = Signal(str)

    def __init__(self, app, model):
        super().__init__(app)
        self.app = app
        self.model = model
        self.signals = ViewModelSignals(self, self.model, parent=self)
        self.view_model_import_data = None
        self.view_model_download_data = None
        self.view_model_create_data = None
        self.view_model_select_data = None

        self.initilize_schedule_planer()
        self.initialize_view_models()
        self.signals.connect_signals()

    def initialize_view_models(self):
        self.view_model_import_data = ViewModelImportData(self, self.model, parent=self)
        self.view_model_download_data = ViewModelDownloadedData(self, self.model, parent=self)
        self.view_model_create_data = ViewModelCreateData(self, self.model, parent=self)
        self.view_model_select_data = ViewModelSelectData(self, self.model, parent=self)

    def initilize_schedule_planer(self):
        self.model.set_up_schedule_planer()

    def on_changed_progress_value(self, progress_data: ProgressSignal):
        self.update_progress_value.emit(progress_data)

    def send_error_message(self, message):
        self.error_message.emit(message)

    def reset_schedule_planer(self):
        self.model.planer.initilize_scheduler()


if __name__ == '__main__':
    logger.debug('no')
