import logging
from PySide6.QtCore import Signal, QObject
from model.Base.Progress import ProgressSignal

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
delimiter = " "
lineend = '\n'


class ViewModelSelectData(QObject):
    update_agency_list_signal = Signal()
    update_routes_list_signal = Signal()
    update_progress_value = Signal(ProgressSignal)
    error_message = Signal(str)

    def __init__(self, app, model):
        super().__init__()
        self.app = app
        self.model = model

    def on_changed_progress_value(self, progress_data: ProgressSignal):
        self.update_progress_value.emit(progress_data)

    def on_loaded_trip_list(self):
        self.update_routes_list_signal.emit()

    def on_changed_selected_record_agency(self, index):
        self.model.planer.create_settings_for_table_dto.selected_agency = index
        self.model.planer.create_settings_for_table_dto.df_selected_routes =  self.model.planer.analyze_data.get_routes_of_agency(self.model.planer.gtfs_data_frame_dto, self.model.planer.create_settings_for_table_dto.selected_agency)
        self.on_loaded_trip_list()

    def on_changed_selected_record_trip(self, id_us):
        self.model.planer.create_settings_for_table_dto.selected_route = id_us
        if self.model.planer.create_settings_for_table_dto.selected_route is not None:
            self.model.planer.create_settings_for_table_dto.dates = self.model.planer.analyze_data.get_date_range(self.model.planer.gtfs_data_frame_dto)
            self.model.planer.create_settings_for_table_dto.sample_date = self.model.planer.analyze_data.get_date_range_based_on_selected_trip(self.model.planer.gtfs_data_frame_dto, self.model.planer.create_settings_for_table_dto)

    def send_error_message(self, message):
        self.error_message.emit(message)
