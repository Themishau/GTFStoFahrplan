import logging
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QObject, Signal

from model.application_model import ApplicationModel
from model.domain.gtfs_feed import is_schema_compatible
from model.enums import ErrorMessage, ModelAction, TimeFormat

logger = logging.getLogger(__name__)


class ImportViewModel(QObject):
    input_path_changed = Signal(str)
    output_path_changed = Signal(str)
    missing_columns_changed = Signal()
    time_format_changed = Signal(str)
    error_message = Signal(str)
    agencies_changed = Signal()
    feed_activated = Signal()
    recent_feeds_changed = Signal()
    busy_changed = Signal(bool)
    feed_cleared = Signal()

    def __init__(
            self,
            model: ApplicationModel,
            parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.model = model
        self.recent_feeds = self.model.cache_service.get_recent_feeds()
        self.model.busy_changed.connect(self._on_busy_changed)
        self.model.feed_deleted.connect(self._on_feed_deleted)
        self.model.cache_cleared.connect(self._on_cache_cleared)

    @property
    def last_feed_id(self) -> str | None:
        return self.model.cache_service.settings.last_feed_id

    def can_open_feed(self, feed_id: str | None) -> bool:
        return any(feed.feed_id == feed_id and is_schema_compatible(feed.metadata.import_schema_version)
                   for feed in self.recent_feeds)

    def open_feed(self, feed_id: str | None) -> bool:
        if feed_id:
            return self.model.start_action(ModelAction.OPEN_CACHED_FEED, feed_id)
        return False

    def delete_feed(self, feed_id: str | None) -> bool:
        if feed_id:
            return self.model.start_action(ModelAction.DELETE_CACHED_FEED, feed_id)
        return False

    def delete_all_feeds(self) -> bool:
        if self.recent_feeds:
            return self.model.start_action(ModelAction.DELETE_ALL_CACHED_FEEDS)
        return False

    def get_database_size_text(self) -> str:
        size = int(self.model.cache_service.database_size_bytes())
        gibibyte = 1024 ** 3
        mebibyte = 1024 ** 2
        if size >= gibibyte:
            return f"{size / gibibyte:.2f} GB"
        return f"{size / mebibyte:.2f} MB"

    def _on_busy_changed(self, busy: bool) -> None:
        if not busy:
            self.recent_feeds = self.model.cache_service.get_recent_feeds()
            self.recent_feeds_changed.emit()
        self.busy_changed.emit(busy)

    def _on_feed_deleted(self, _feed_id: str) -> None:
        if self.model.cache_service.active_feed is None:
            self.feed_cleared.emit()

    def _on_cache_cleared(self) -> None:
        self.feed_cleared.emit()

    def get_missing_columns_df(self) -> pd.DataFrame:
        return self.model.planner.data_loader.missing_columns_in_gtfs_file

    def has_missing_columns(self) -> bool:
        missing_columns_df = self.get_missing_columns_df()
        return missing_columns_df is not None and not missing_columns_df.empty

    def get_agencies_df(self) -> pd.DataFrame | None:
        gtfs_data = self.model.planner.gtfs_data
        if gtfs_data is None:
            return None
        return gtfs_data.agencies

    def get_time_format(self) -> TimeFormat:
        return self.model.planner.planning_settings.time_format

    def get_sample_date(self) -> str | None:
        return self.model.planner.planning_settings.sample_date

    def set_input_path(self, input_path: Path | None) -> None:
        if input_path is None:
            return
        self.model.planner.import_settings.input_path = input_path
        self.input_path_changed.emit(str(input_path))

    def handle_import_finished(self) -> None:
        self.recent_feeds = self.model.cache_service.get_recent_feeds()
        self.recent_feeds_changed.emit()
        self.missing_columns_changed.emit()
        self.agencies_changed.emit()
        self.feed_activated.emit()

    def start_import(self) -> None:
        path = self.model.planner.import_settings.input_path
        if path is not None and path.is_file():
            self.model.start_action(ModelAction.IMPORT_GTFS)
        else:
            self.send_error_message(ErrorMessage.INVALID_PATH)

    def set_output_path(self, path: Path | None) -> None:
        if path is None:
            return
        path_text = str(path)
        try:
            self.model.cache_service.update_settings(default_export_path=path_text)
        except OSError as error:
            self.send_error_message(str(error))
            return
        self.model.planner.planning_settings.output_path = path_text
        self.output_path_changed.emit(path_text)

    def set_time_format(self, index: int) -> None:
        try:
            selected_format = tuple(TimeFormat)[index]
        except IndexError:
            self.send_error_message("Invalid time format selected.")
            return

        logger.debug("Time format: %s", selected_format)
        self.model.planner.planning_settings.time_format = selected_format
        try:
            self.model.cache_service.update_settings(time_format=selected_format.value)
        except OSError as error:
            self.send_error_message(str(error))
            return
        self.time_format_changed.emit(selected_format.value)

    def send_error_message(self, message: str) -> None:
        self.error_message.emit(message)
