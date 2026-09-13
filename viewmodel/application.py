"""Top-level view model that coordinates feature-specific view models."""

from PySide6.QtCore import QObject, Signal

from model.planning.progress import ProgressUpdate
from viewmodel.create_view_model import CreateViewModel
from viewmodel.import_view_model import ImportViewModel
from viewmodel.selection_view_model import SelectionViewModel
from viewmodel.signal_binder import ViewModelSignalBinder


class ApplicationViewModel(QObject):
    update_progress_value = Signal(ProgressUpdate)
    error_message = Signal(str)

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.signal_binder = ViewModelSignalBinder(self, self.model, parent=self)
        self.model.initialize_schedule_planner()
        self.import_view_model = ImportViewModel(self.model, parent=self)
        self.create_view_model = CreateViewModel(self.model, parent=self)
        self.selection_view_model = SelectionViewModel(self.model, parent=self)
        self.signal_binder.connect_signals()

    def forward_progress(self, progress_data: ProgressUpdate):
        self.update_progress_value.emit(progress_data)

    def send_error_message(self, message):
        self.error_message.emit(message)

    def reset_schedule_planner(self):
        self.model.reset_schedule_planner()
