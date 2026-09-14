"""Qt progress adapter for the persistent GTFS import workflow."""

import pandas as pd
from PySide6.QtCore import QObject, QThread, Signal

from model.domain.import_settings import ImportSettings
from model.enums import ProcessKind
from model.planning.progress_update import ProgressUpdate
from model.services.cached_gtfs_data import CachedGtfsData
from model.services.gtfs_cache_service import GtfsCacheService


class GtfsDataLoader(QObject):
    progress_updated = Signal(ProgressUpdate)

    def __init__(self, cache_service: GtfsCacheService):
        super().__init__()
        self.cache_service = cache_service
        self._progress = ProgressUpdate()
        self.missing_columns_in_gtfs_file = pd.DataFrame(
            {
                "table": pd.Series(dtype="string"),
                "column": pd.Series(dtype="string"),
            }
        )

    @staticmethod
    def _check_cancelled() -> None:
        if QThread.currentThread().isInterruptionRequested():
            raise InterruptedError("Operation cancelled.")

    def _emit_progress(self, value: int, message: str) -> None:
        self.progress_updated.emit(
            self._progress.set_progress(value, ProcessKind.IMPORT_DATA, message)
        )

    def import_gtfs(self, settings: ImportSettings) -> CachedGtfsData:
        if not settings.input_path:
            raise ValueError("Select a GTFS ZIP file")
        result = self.cache_service.open_or_import_gtfs(
            settings.input_path,
            self._check_cancelled,
            self._emit_progress,
        )
        return CachedGtfsData(result.feed, self.cache_service.repository)

    def open_feed(self, feed_id: str) -> CachedGtfsData:
        self._check_cancelled()
        feed = self.cache_service.open_feed(feed_id)
        self._emit_progress(100, "Cached GTFS feed opened")
        return CachedGtfsData(feed, self.cache_service.repository)
