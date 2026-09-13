"""Qt progress adapter for the persistent GTFS import workflow."""
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QObject, QThread, Signal

from model.domain.import_settings import ImportSettings
from model.enums import ProcessKind
from model.planning.progress import ProgressUpdate
from model.services.cached_gtfs_data import CachedGtfsData
from model.services.gtfs_cache_service import GtfsCacheService


class GtfsDataLoader(QObject):
    progress_updated = Signal(ProgressUpdate)
    error_occurred = Signal(str)

    def __init__(self, app, cache_service: GtfsCacheService):
        super().__init__()
        self.app = app
        self.cache_service = cache_service
        self.reset_import = False
        self.progress = ProgressUpdate()
        self.missing_columns_in_gtfs_file = pd.DataFrame(columns=["table", "column"])

    @staticmethod
    def check_cancelled():
        if QThread.currentThread().isInterruptionRequested():
            raise InterruptedError("Operation cancelled.")

    def update_progress(self, value, message):
        self.progress_updated.emit(self.progress.set_progress(value, ProcessKind.IMPORT_DATA, message))

    def import_gtfs(self, settings: ImportSettings) -> CachedGtfsData:
        if not settings.input_path:
            raise ValueError("Select a GTFS ZIP file")
        result = self.cache_service.open_or_import_gtfs(
            Path(settings.input_path), self.check_cancelled, self.update_progress)
        return CachedGtfsData(result.feed, self.cache_service.repository)

    def open_feed(self, feed_id: str) -> CachedGtfsData:
        self.check_cancelled()
        feed = self.cache_service.open_feed(feed_id)
        self.update_progress(100, "Cached GTFS feed opened")
        return CachedGtfsData(feed, self.cache_service.repository)
