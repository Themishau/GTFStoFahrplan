from PySide6.QtCore import QObject


class ViewModelSignalBinder(QObject):
    def __init__(self, view_model, model, parent=None):
        super().__init__(parent)
        self.view_model = view_model
        self.model = model

    def connect_signals(self):
        self.model.import_finished.connect(self.view_model.import_view_model.handle_import_finished)
        self.model.import_finished.connect(self.view_model.create_view_model.handle_import_finished)
        self.model.progress_updated.connect(self.view_model.forward_progress)
        self.model.error_occurred.connect(self.view_model.send_error_message)
        self.model.sorting_requested.connect(
            self.view_model.create_view_model.handle_sorting_requested
        )
        self.model.planning_finished.connect(
            self.view_model.create_view_model.handle_planning_finished
        )

        for child in (
                self.view_model.import_view_model,
                self.view_model.create_view_model,
                self.view_model.selection_view_model,
        ):
            child.error_message.connect(self.view_model.send_error_message)
