from dataclasses import dataclass
from datetime import date, datetime

CURRENT_GTFS_SCHEMA_VERSION = 1


def is_schema_compatible(version: int) -> bool:
    return version == CURRENT_GTFS_SCHEMA_VERSION


class IncompatibleFeedError(ValueError):
    pass


@dataclass(frozen=True)
class FileFingerprint:
    filename: str
    size: int
    modified: datetime
    modified_ns: int
    sha256: str


@dataclass(frozen=True)
class FeedMetadata:
    source_filename: str
    source_hash: str
    source_size: int
    source_modified: datetime
    imported_at: datetime
    feed_publisher_name: str | None = None
    feed_start_date: date | None = None
    feed_end_date: date | None = None
    agency_count: int = 0
    route_count: int = 0
    trip_count: int = 0
    stop_count: int = 0
    stop_time_count: int = 0
    import_schema_version: int = CURRENT_GTFS_SCHEMA_VERSION


@dataclass(frozen=True)
class GtfsFeed:
    feed_id: str
    metadata: FeedMetadata
