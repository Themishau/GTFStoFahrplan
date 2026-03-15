import logging
from PySide6.QtCore import Signal, QObject
from model.Base.Progress import ProgressSignal

class ViewModelSelectData(QObject):
    update_agency_list_signal = Signal()
    update_routes_list_signal = Signal()
    update_progress_value = Signal(ProgressSignal)
    error_message = Signal(str)

    def __init__(self, app, model, parent=None):
        super().__init__(parent)
        self.app = app
        self.model = model

    def on_changed_progress_value(self, progress_data: ProgressSignal):
        self.update_progress_value.emit(progress_data)

    def on_loaded_trip_list(self):
        self.update_routes_list_signal.emit()

    def get_selected_agency_text(self):
        return self.model.planer.create_settings_for_table_dto.selected_agency_text

    def get_selected_route_text(self):
        return self.model.planer.create_settings_for_table_dto.selected_route_text

    def get_routes_df(self):
        return self.model.planer.create_settings_for_table_dto.df_selected_routes

    def get_selected_route_date_range_text(self):
        date_range_df = self.model.planer.create_settings_for_table_dto.date_range_df_format
        if (date_range_df is None
                or date_range_df.get('start_date') is None
                or date_range_df.get('end_date') is None):
            return None

        start_date = date_range_df['start_date']
        end_date = date_range_df['end_date']
        return f"{start_date.iloc[0].strftime('%Y-%m-%d')} - {end_date.iloc[0].strftime('%Y-%m-%d')}"

    def get_selected_route_sample_date(self):
        date_range_df = self.model.planer.create_settings_for_table_dto.date_range_df_format
        if date_range_df is None or date_range_df.get('start_date') is None:
            return None
        return date_range_df['start_date'].iloc[0].strftime('%Y-%m-%d')

    def on_changed_selected_record_agency(self, index):
        self.model.planer.create_settings_for_table_dto.agency = index
        self.model.planer.create_settings_for_table_dto.df_selected_routes = self.model.planer.analyze_data.get_routes_of_agency(
            self.model.planer.gtfs_data_frame_dto,
            self.model.planer.create_settings_for_table_dto.agency,
        )
        self.on_loaded_trip_list()

    def on_changed_selected_record_trip(self, id_us):
        self.model.planer.create_settings_for_table_dto.route = id_us
        if self.model.planer.create_settings_for_table_dto.route is not None:
            self.model.planer.create_settings_for_table_dto.dates = self.model.planer.analyze_data.get_date_range(self.model.planer.gtfs_data_frame_dto)
            self.model.planer.analyze_data.get_date_range_based_on_selected_trip(self.model.planer.gtfs_data_frame_dto, self.model.planer.create_settings_for_table_dto)

    def send_error_message(self, message):
        self.error_message.emit(message)
