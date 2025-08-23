from PySide6.QtCore import QObject

class ViewModelSignals(QObject):
    def __init__(self, viewModel, model):
        super().__init__()
        self.viewModel = viewModel
        self.model = model


    def connect_signals(self):

        self.model.planer.import_finished.connect(self.viewModel.view_model_import_data.on_import_gtfs_data_finished)

        self.viewModel.view_model_import_data.update_progress_value.connect(self.viewModel.on_changed_progress_value)
        self.model.planer.progress_Update.connect(self.viewModel.view_model_import_data.on_changed_progress_value)
        self.model.planer.error_occured.connect(self.viewModel.view_model_import_data.send_error_message)
        self.viewModel.view_model_import_data.error_message.connect(self.viewModel.send_error_message)

        self.viewModel.view_model_create_data.update_progress_value.connect(self.viewModel.on_changed_progress_value)
        self.model.planer.progress_Update.connect(self.viewModel.view_model_create_data.on_changed_progress_value)
        self.model.planer.error_occured.connect(self.viewModel.view_model_create_data.send_error_message)
        self.viewModel.view_model_create_data.error_message.connect(self.viewModel.send_error_message)
        self.model.planer.create_sorting_signal.connect(self.viewModel.view_model_create_data.on_create_sorting_signal)
        self.model.planer.create_finished.connect(self.viewModel.view_model_create_data.on_create_plan_finished)

        self.viewModel.view_model_download_data.update_progress_value.connect(self.viewModel.on_changed_progress_value)
        self.model.planer.progress_Update.connect(self.viewModel.view_model_download_data.on_changed_progress_value)
        self.model.planer.error_occured.connect(self.viewModel.view_model_download_data.send_error_message)
        self.viewModel.view_model_download_data.error_message.connect(self.viewModel.send_error_message)

        self.viewModel.view_model_select_data.update_progress_value.connect(self.viewModel.on_changed_progress_value)
        self.model.planer.progress_Update.connect(self.viewModel.view_model_select_data.on_changed_progress_value)
        self.model.planer.error_occured.connect(self.viewModel.view_model_select_data.send_error_message)
        self.viewModel.view_model_select_data.error_message.connect(self.viewModel.send_error_message)