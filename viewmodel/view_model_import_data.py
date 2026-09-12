import logging
from pathlib import Path
from model.Dto.gtfs_feed import is_schema_compatible
from PySide6.QtCore import Signal, QObject
from model.Base.Progress import ProgressSignal
from model.Enum.GTFSEnums import *
delimiter = " "
lineend = '\n'


class ViewModelImportData(QObject):
    input_file_path = Signal(str)
    output_file_path = Signal(str)
    update_progress_value = Signal(ProgressSignal)
    update_warning_table_view = Signal()
    export_plan_time_format = Signal(str)
    error_message = Signal(str)
    update_agency_list_signal = Signal()
    set_up_create_tab_signal = Signal()
    recent_feeds_changed = Signal()
    busy_changed = Signal(bool)
    feed_cleared = Signal()

    def __init__(self, app, model, parent=None):
        super().__init__(parent)
        self.app = app
        self.model = model
        self.recent_feeds = self.model.cache_service.get_recent_feeds()
        self.model.busy_changed.connect(self._on_busy_changed)
        self.model.feed_deleted.connect(self._on_feed_deleted)

    @property
    def last_feed_id(self):
        return self.model.cache_service.settings.last_feed_id

    def can_open_feed(self, feed_id):
        return any(feed.feed_id == feed_id and is_schema_compatible(feed.metadata.import_schema_version)
                   for feed in self.recent_feeds)

    def open_feed(self, feed_id):
        if feed_id:
            return self.model.start_function_async('open_cached_feed', feed_id)
        return False

    def delete_feed(self, feed_id):
        if feed_id:
            return self.model.start_function_async('delete_cached_feed', feed_id)
        return False

    def _on_busy_changed(self, busy):
        if not busy:
            self.recent_feeds = self.model.cache_service.get_recent_feeds()
            self.recent_feeds_changed.emit()
        self.busy_changed.emit(busy)

    def _on_feed_deleted(self, feed_id):
        if self.model.cache_service.active_feed is None:
            self.feed_cleared.emit()

    def on_changed_progress_value(self, progress_data: ProgressSignal):
        self.update_progress_value.emit(progress_data)

    def get_missing_columns_df(self):
        return self.model.planer.import_Data.missing_columns_in_gtfs_file

    def has_missing_columns(self):
        missing_columns_df = self.get_missing_columns_df()
        return missing_columns_df is not None and not missing_columns_df.empty

    def get_agencies_df(self):
        gtfs_data = self.model.planer.gtfs_data_frame_dto
        if gtfs_data is None:
            return None
        return gtfs_data.Agencies

    def get_time_format(self):
        return self.model.planer.create_settings_for_table_dto.timeformat

    def get_sample_date(self):
        return self.model.planer.create_settings_for_table_dto.sample_date

    def on_change_input_file_path(self, path):
        if not path or not path[0]:
            return
        self.model.planer.import_settings_dto.input_path = path[0]
        self.input_file_path.emit(path[0])

    def on_import_gtfs_data_finished(self):
        self.recent_feeds = self.model.cache_service.get_recent_feeds()
        self.recent_feeds_changed.emit()
        self.update_warning_table_view.emit()
        self.update_agency_list_signal.emit()
        self.set_up_create_tab_signal.emit()


    def start_import_gtfs_data(self):
        path = self.model.planer.import_settings_dto.input_path
        if path and Path(path).is_file():
            self.model.start_function_async(ModelTriggerActionsEnum.planer_start_load_data.value)
        else:
            self.send_error_message(ErrorMessageRessources.error_path_not_valid.value)


    def on_change_output_file_path(self, path):
        if not path:
            return
        try:
            self.model.cache_service.update_settings(default_export_path=path)
        except OSError as error:
            self.send_error_message(str(error))
            return
        self.model.planer.create_settings_for_table_dto.output_path = path
        self.output_file_path.emit(path)

    def on_changed_time_format_mode(self, text):
        logging.debug(f'time format {text}')
        if text == 0:
            self.model.planer.create_settings_for_table_dto.timeformat = 1
        elif text == 1:
            self.model.planer.create_settings_for_table_dto.timeformat = 2
        try:
            self.model.cache_service.update_settings(time_format='HH:mm' if text == 0 else 'HH:mm:ss')
        except OSError as error:
            self.send_error_message(str(error))
        self.export_plan_time_format.emit(str(text))

    def send_error_message(self, message):
        self.error_message.emit(message)
