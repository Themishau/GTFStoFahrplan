from PySide6.QtCore import QObject

class ViewModelSignals(QObject):
    def __init__(self, viewModel, model):
        super().__init__()
        self.viewModel = viewModel
        self.model = model


    def connect_signals(self):
        self.model.planer.progress_Update.connect(self.viewModel.on_changed_progress_value)
        self.model.planer.error_occured.connect(self.viewModel.send_error_message)
        self.model.planer.update_options_state_signal.connect(self.viewModel.on_changed_options_state)
        self.model.planer.create_sorting_signal.connect(self.viewModel.on_create_sorting_signal)
        self.model.planer.create_finished.connect(self.viewModel.on_create_plan_finished)
        self.model.planer.import_finished.connect(self.viewModel.on_import_gtfs_data_finished)