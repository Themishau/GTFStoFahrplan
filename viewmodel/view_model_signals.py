from PySide6.QtCore import QObject
from PySide6.QtWidgets import QAbstractItemView, QHeaderView
from view.Custom.ProgressListView import ProgressHistoryModel, ProgressBarDelegate
from PySide6.QtWidgets import QWidget, QAbstractItemView, QHeaderView
import logging

class ViewModelSignals(QObject):
    def __init__(self, viewModel, model):
        super().__init__()
        self.viewModel = viewModel
        self.model = model


    def connect_signals(self):
        self.model.planer.progress_Update.connect(self.viewModel.on_changed_progress_value)
        self.model.planer.select_data.select_agency_signal.connect(self.viewModel.on_loaded_agency_list)
        self.model.planer.error_occured.connect(self.viewModel.send_error_message)
        self.model.planer.update_routes_list_signal.connect(self.viewModel.on_loaded_trip_list)
        self.model.planer.update_options_state_signal.connect(self.viewModel.on_changed_options_state)
        self.model.planer.create_sorting_signal.connect(self.viewModel.on_create_sorting_signal)
        self.model.planer.create_finished.connect(self.viewModel.on_create_plan_finished)