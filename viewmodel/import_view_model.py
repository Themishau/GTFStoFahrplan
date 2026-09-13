import logging
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from model.domain.gtfs_feed import is_schema_compatible
from model.enums import ErrorMessages, ModelAction


class ImportViewModel(QObject):
    input_file_path = Signal(str)
    output_file_path = Signal(str)
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
        self.model.cache_cleared.connect(self._on_cache_cleared)

    @property
    def last_feed_id(self):
        return self.model.cache_service.settings.last_feed_id

    def can_open_feed(self, feed_id):
        return any(feed.feed_id == feed_id and is_schema_compatible(feed.metadata.import_schema_version)
                   for feed in self.recent_feeds)

    def open_feed(self, feed_id):
        if feed_id:
            return self.model.start_function_async(ModelAction.OPEN_CACHED_FEED, feed_id)
        return False

    def delete_feed(self, feed_id):
        if feed_id:
            return self.model.start_function_async(ModelAction.DELETE_CACHED_FEED, feed_id)
        return False

    def delete_all_feeds(self):
        if self.recent_feeds:
            return self.model.start_function_async(ModelAction.DELETE_ALL_CACHED_FEEDS)
        return False

    def get_database_size_text(self):
        size = self.model.cache_service.database_size_bytes()
        gibibyte = 1024 ** 3
        mebibyte = 1024 ** 2
        if size >= gibibyte:
            return f'{size / gibibyte:.2f} GB'
        return f'{size / mebibyte:.2f} MB'

    def _on_busy_changed(self, busy):
        if not busy:
            self.recent_feeds = self.model.cache_service.get_recent_feeds()
            self.recent_feeds_changed.emit()
        self.busy_changed.emit(busy)

    def _on_feed_deleted(self, _feed_id):
        if self.model.cache_service.active_feed is None:
            self.feed_cleared.emit()

    def _on_cache_cleared(self):
        self.feed_cleared.emit()

    def get_missing_columns_df(self):
        return self.model.planner.data_loader.missing_columns_in_gtfs_file

    def has_missing_columns(self):
        missing_columns_df = self.get_missing_columns_df()
        return missing_columns_df is not None and not missing_columns_df.empty

    def get_agencies_df(self):
        gtfs_data = self.model.planner.gtfs_data
        if gtfs_data is None:
            return None
        return gtfs_data.agencies

    def get_time_format(self):
        return self.model.planner.planning_settings.time_format

    def get_sample_date(self):
        return self.model.planner.planning_settings.sample_date

    def set_input_path(self, path):
        if not path or not path[0]:
            return
        self.model.planner.import_settings.input_path = path[0]
        self.input_file_path.emit(path[0])

    def handle_import_finished(self):
        self.recent_feeds = self.model.cache_service.get_recent_feeds()
        self.recent_feeds_changed.emit()
        self.update_warning_table_view.emit()
        self.update_agency_list_signal.emit()
        self.set_up_create_tab_signal.emit()


    def start_import(self):
        path = self.model.planner.import_settings.input_path
        if path and Path(path).is_file():
            self.model.start_function_async(ModelAction.IMPORT_GTFS.value)
        else:
            self.send_error_message(ErrorMessages.INVALID_PATH.value)


    def set_output_path(self, path):
        if not path:
            return
        try:
            self.model.cache_service.update_settings(default_export_path=path)
        except OSError as error:
            self.send_error_message(str(error))
            return
        self.model.planner.planning_settings.output_path = path
        self.output_file_path.emit(path)

    def set_time_format(self, text):
        logging.debug(f'time format {text}')
        if text == 0:
            self.model.planner.planning_settings.time_format = 1
        elif text == 1:
            self.model.planner.planning_settings.time_format = 2
        try:
            self.model.cache_service.update_settings(time_format='HH:mm' if text == 0 else 'HH:mm:ss')
        except OSError as error:
            self.send_error_message(str(error))
        self.export_plan_time_format.emit(str(text))

    def send_error_message(self, message):
        self.error_message.emit(message)
