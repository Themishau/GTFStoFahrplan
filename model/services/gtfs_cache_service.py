import logging
from dataclasses import dataclass, replace
from pathlib import Path
from threading import RLock
from typing import Callable

from model.Dto.gtfs_feed import GtfsFeed, IncompatibleFeedError, is_schema_compatible
from model.infrastructure.database.gtfs_importer import GtfsImporter
from model.infrastructure.database.gtfs_repository import GtfsRepository
from model.infrastructure.paths.app_paths import AppPaths
from model.infrastructure.settings.settings_service import SettingsService
from .gtfs_fingerprint import GtfsFingerprintService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OpenFeedResult:
    feed: GtfsFeed
    cache_hit: bool


class GtfsCacheService:
    def __init__(self, repository: GtfsRepository, importer: GtfsImporter,
                 settings_service: SettingsService, fingerprint_service=None):
        self.repository = repository
        self.importer = importer
        self.settings_service = settings_service
        self.fingerprint_service = fingerprint_service or GtfsFingerprintService()
        self._settings_lock = RLock()
        self.settings = settings_service.load()
        self.active_feed: GtfsFeed | None = None
        self.last_feed = None
        if self.settings.last_feed_id:
            self.last_feed = repository.get_feed(self.settings.last_feed_id)
            if self.last_feed is None or not is_schema_compatible(self.last_feed.metadata.import_schema_version):
                self.last_feed = None
                self.update_settings(last_feed_id=None)

    @classmethod
    def for_paths(cls, paths: AppPaths) -> "GtfsCacheService":
        paths.ensure_directories()
        repository = GtfsRepository(paths.database, paths.temp)
        try:
            return cls(repository, GtfsImporter(repository, paths.temp), SettingsService(paths.settings_file))
        except Exception:
            repository.close()
            raise

    def update_settings(self, **changes) -> None:
        with self._settings_lock:
            settings = replace(self.settings, **changes)
            self.settings_service.save(settings)
            self.settings = settings

    def open_or_import_gtfs(self, zip_path: Path,
                            check_cancelled: Callable[[], None] = lambda: None,
                            progress: Callable[[int, str], None] = lambda *_: None) -> OpenFeedResult:
        progress(1, "Calculating GTFS fingerprint")
        fingerprint = self.fingerprint_service.calculate(Path(zip_path), check_cancelled)
        check_cancelled()
        feed = self.repository.find_feed_by_hash(fingerprint.sha256)
        cache_hit = feed is not None
        if cache_hit:
            logger.info("GTFS cache hit: %s", feed.feed_id)
        else:
            logger.info("GTFS cache miss: %s", fingerprint.filename)
            feed = self.importer.import_feed(Path(zip_path), fingerprint, check_cancelled, progress)
        check_cancelled()
        self.open_feed(feed.feed_id)
        progress(100, "Cached GTFS feed opened" if cache_hit else "GTFS import completed")
        return OpenFeedResult(feed, cache_hit)

    def open_feed(self, feed_id: str) -> GtfsFeed:
        feed = self.repository.get_feed(feed_id)
        if feed is None:
            raise ValueError("This cached GTFS feed no longer exists")
        if not is_schema_compatible(feed.metadata.import_schema_version):
            logger.warning("GTFS import schema version mismatch: %s", feed_id)
            raise IncompatibleFeedError("This feed uses an older import schema. Please re-import the GTFS ZIP.")
        self.update_settings(last_feed_id=feed_id)
        self.active_feed = self.last_feed = feed
        return feed

    def get_recent_feeds(self) -> list[GtfsFeed]:
        return self.repository.get_recent_feeds()

    def delete_feed(self, feed_id: str) -> None:
        self.repository.delete_feed(feed_id)
        if self.active_feed and self.active_feed.feed_id == feed_id:
            self.active_feed = None
        if self.last_feed and self.last_feed.feed_id == feed_id:
            self.last_feed = None
        if self.settings.last_feed_id == feed_id:
            self.update_settings(last_feed_id=None)

    def close(self) -> None:
        self.repository.close()
