import csv
import logging
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock, RLock
from typing import Callable, Iterable, Iterator
from uuid import uuid4

import duckdb
import pandas as pd

from model.domain.gtfs_feed import (
    CURRENT_GTFS_SCHEMA_VERSION, FeedMetadata, FileFingerprint, GtfsFeed,
)
from model.services.gtfs_time import GTFS_TIME_PATTERN
from .schema import DATABASE_LAYOUT_VERSION, REQUIRED_COLUMNS, REQUIRED_TABLES, TABLE_COLUMNS

logger = logging.getLogger(__name__)


class GtfsRepository:
    """Serialized access with a separate DuckDB cursor per operation/thread.

    Query results belong to the caller. No DataFrames are retained here. The
    connection must be closed only after the application's worker has finished.
    """

    def __init__(self, database: Path, temp_directory: Path, memory_limit: str = "512MB"):
        database, temp_directory = Path(database), Path(temp_directory)
        database.parent.mkdir(parents=True, exist_ok=True)
        temp_directory.mkdir(parents=True, exist_ok=True)
        self.database_path = database
        self.temp_directory = temp_directory
        self.memory_limit = memory_limit
        self._lock = RLock()
        self._interrupt_lock = Lock()
        self._active_cursor = None
        self._connection = None
        try:
            self._connection = duckdb.connect(str(database), config={
                "memory_limit": memory_limit, "threads": 2,
                "temp_directory": str(temp_directory), "preserve_insertion_order": False,
            })
            self._initialize()
        except Exception:
            logger.exception("GTFS database migration/version problem")
            self.close()
            raise

    @contextmanager
    def _session(self):
        with self._lock:
            if self._connection is None:
                raise RuntimeError("GTFS repository is closed")
            cursor = self._connection.cursor()
            with self._interrupt_lock:
                self._active_cursor = cursor
            try:
                yield cursor
            finally:
                with self._interrupt_lock:
                    self._active_cursor = None
                cursor.close()

    def interrupt(self) -> None:
        """Can be called by the GUI while a worker is inside DuckDB."""
        with self._interrupt_lock:
            if self._active_cursor is not None:
                self._active_cursor.interrupt()

    def close(self) -> None:
        with self._lock:
            if self._connection is not None:
                self._connection.close()
                self._connection = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _initialize(self) -> None:
        with self._session() as db:
            db.execute("BEGIN TRANSACTION")
            try:
                db.execute("CREATE TABLE IF NOT EXISTS cache_schema (version INTEGER NOT NULL)")
                versions = db.execute("SELECT version FROM cache_schema").fetchall()
                if versions and versions != [(DATABASE_LAYOUT_VERSION,)]:
                    raise ValueError("Unsupported GTFS database layout; a database migration is required")
                if not versions:
                    db.execute("INSERT INTO cache_schema VALUES (?)", [DATABASE_LAYOUT_VERSION])
                db.execute("""
                           CREATE TABLE IF NOT EXISTS feeds
                           (
                               feed_id
                               VARCHAR
                               PRIMARY
                               KEY,
                               source_filename
                               VARCHAR
                               NOT
                               NULL,
                               source_hash
                               VARCHAR
                               NOT
                               NULL,
                               source_size
                               BIGINT
                               NOT
                               NULL,
                               source_modified
                               TIMESTAMPTZ
                               NOT
                               NULL,
                               imported_at
                               TIMESTAMPTZ
                               NOT
                               NULL,
                               feed_publisher_name
                               VARCHAR,
                               feed_start_date
                               DATE,
                               feed_end_date
                               DATE,
                               agency_count
                               BIGINT,
                               route_count
                               BIGINT,
                               trip_count
                               BIGINT,
                               stop_count
                               BIGINT,
                               stop_time_count
                               BIGINT,
                               import_schema_version
                               INTEGER
                               NOT
                               NULL,
                               UNIQUE
                           (
                               source_hash,
                               import_schema_version
                           )
                               )
                           """)
                for table, columns in TABLE_COLUMNS.items():
                    definitions = ", ".join(
                        f'"{name}" {dtype}' + (" NOT NULL" if name in REQUIRED_COLUMNS[table] else "")
                        for name, dtype in columns.items())
                    db.execute(f'CREATE TABLE IF NOT EXISTS "{table}" (feed_id VARCHAR NOT NULL, {definitions})')
                # Vectorized equivalent of gtfs_time_to_seconds; no Python call per CSV row.
                db.execute(f"""
                    CREATE OR REPLACE MACRO gtfs_time_to_seconds(value) AS
                    CASE WHEN value IS NULL OR value = '' THEN NULL
                         WHEN regexp_full_match(value, '{GTFS_TIME_PATTERN}') THEN
                             cast(split_part(value, ':', 1) AS BIGINT) * 3600 +
                             cast(split_part(value, ':', 2) AS BIGINT) * 60 +
                             cast(split_part(value, ':', 3) AS BIGINT)
                         ELSE error('Invalid GTFS time') END
                """)
                db.execute("COMMIT")
            except BaseException:
                db.execute("ROLLBACK")
                raise

    @staticmethod
    def _feed(row) -> GtfsFeed | None:
        if row is None:
            return None
        return GtfsFeed(row[0], FeedMetadata(*row[1:]))

    def get_feed(self, feed_id: str) -> GtfsFeed | None:
        with self._session() as db:
            return self._feed(db.execute("SELECT * FROM feeds WHERE feed_id = ?", [feed_id]).fetchone())

    def feed_exists(self, feed_id: str) -> bool:
        return self.get_feed(feed_id) is not None

    def find_feed_by_hash(self, source_hash: str,
                          schema_version: int = CURRENT_GTFS_SCHEMA_VERSION) -> GtfsFeed | None:
        with self._session() as db:
            row = db.execute("SELECT * FROM feeds WHERE source_hash = ? AND import_schema_version = ?",
                             [source_hash, schema_version]).fetchone()
            if row is None and db.execute("SELECT 1 FROM feeds WHERE source_hash = ? LIMIT 1",
                                          [source_hash]).fetchone():
                logger.warning("GTFS import schema version mismatch; re-import required")
            return self._feed(row)

    def get_recent_feeds(self, limit: int = 100) -> list[GtfsFeed]:
        with self._session() as db:
            rows = db.execute("SELECT * FROM feeds ORDER BY imported_at DESC LIMIT ?", [limit]).fetchall()
            return [self._feed(row) for row in rows]

    def delete_feed(self, feed_id: str) -> None:
        with self._session() as db:
            db.execute("BEGIN TRANSACTION")
            try:
                for table in (*TABLE_COLUMNS, "feeds"):
                    db.execute(f'DELETE FROM "{table}" WHERE feed_id = ?', [feed_id])
                db.execute("COMMIT")
            except BaseException:
                db.execute("ROLLBACK")
                raise
        logger.info("GTFS feed deleted: %s", feed_id)

    def import_tables(self, fingerprint: FileFingerprint, tables: Iterator[tuple[str, Path]],
                      check_cancelled: Callable[[], None] = lambda: None,
                      progress: Callable[[int, str], None] = lambda *_: None) -> GtfsFeed:
        """Consume one extracted member at a time; publish metadata only at commit."""
        feed_id = uuid4().hex
        with self._session() as db:
            db.execute("BEGIN TRANSACTION")
            try:
                counts = dict.fromkeys(TABLE_COLUMNS, 0)
                imported = set()
                for table, path in tables:
                    check_cancelled()
                    self._import_csv(db, table, path, feed_id)
                    imported.add(table)
                    counts[table] = db.execute(f'SELECT count(*) FROM "{table}" WHERE feed_id = ?',
                                               [feed_id]).fetchone()[0]
                    progress(15 + len(imported) * 9, f"Imported {table}")
                if not REQUIRED_TABLES <= imported or not {"calendar", "calendar_dates"} & imported:
                    raise ValueError("GTFS requires agency, routes, trips, stops, stop_times and a calendar")
                self._normalize_single_agency(db, feed_id)
                info = db.execute("""SELECT min(feed_publisher_name), min(feed_start_date), max(feed_end_date)
                                     FROM feed_info
                                     WHERE feed_id = ?""", [feed_id]).fetchone()
                dates = db.execute("""
                                   SELECT min(start_date), max(end_date)
                                   FROM (SELECT start_date, end_date
                                         FROM calendar
                                         WHERE feed_id = ?
                                         UNION ALL
                                         SELECT date, date
                                         FROM calendar_dates
                                         WHERE feed_id = ?)
                                   """, [feed_id, feed_id]).fetchone()
                metadata = FeedMetadata(
                    fingerprint.filename, fingerprint.sha256, fingerprint.size, fingerprint.modified,
                    datetime.now(timezone.utc), info[0], info[1] or dates[0], info[2] or dates[1],
                    counts["agency"], counts["routes"], counts["trips"], counts["stops"], counts["stop_times"])
                values = [feed_id, *asdict(metadata).values()]
                db.execute(f"INSERT INTO feeds VALUES ({', '.join('?' for _ in values)})", values)
                check_cancelled()
                db.execute("COMMIT")
                return GtfsFeed(feed_id, metadata)
            except BaseException:
                db.execute("ROLLBACK")
                raise

    @staticmethod
    def _normalize_single_agency(db, feed_id):
        agencies = db.execute("SELECT agency_id FROM agency WHERE feed_id = ?", [feed_id]).fetchall()
        if len(agencies) == 1:
            agency_id = agencies[0][0] or "__single_agency__"
            db.execute("UPDATE agency SET agency_id = ? WHERE feed_id = ? AND agency_id IS NULL",
                       [agency_id, feed_id])
            db.execute("UPDATE routes SET agency_id = ? WHERE feed_id = ? AND agency_id IS NULL",
                       [agency_id, feed_id])
        elif any(row[0] is None for row in agencies):
            raise ValueError("agency_id is required for feeds with multiple agencies")

    @staticmethod
    def _import_csv(db, table: str, path: Path, feed_id: str):
        if table not in TABLE_COLUMNS:
            raise ValueError(f"Unsupported GTFS table: {table}")
        # Read only the CSV header in Python. DuckDB reads and converts all rows.
        with path.open(encoding="utf-8-sig", newline="") as stream:
            header = next(csv.reader(stream), [])
        if not header or len(set(header)) != len(header) or any(not name for name in header):
            raise ValueError(f"Invalid or duplicate CSV headers in {table}.txt")
        missing = REQUIRED_COLUMNS[table] - set(header)
        if missing:
            raise ValueError(f"Missing required columns in {table}.txt: {', '.join(sorted(missing))}")
        db.read_csv(str(path), header=True, auto_detect=False, sep=",", quotechar='"', escapechar='"',
                    columns={name: "VARCHAR" for name in header}, parallel=False).create_view("gtfs_csv", replace=True)
        expressions = []
        for name, dtype in TABLE_COLUMNS[table].items():
            if name in ("arrival_seconds", "departure_seconds"):
                source = name.replace("_seconds", "_time")
                expression = f'gtfs_time_to_seconds("{source}")' if source in header else "NULL"
            elif name not in header:
                expression = "0" if name == "direction_id" else "NULL"
            elif dtype == "DATE":
                expression = f"cast(strptime(\"{name}\", '%Y%m%d') AS DATE)"
            elif name == "direction_id":
                expression = 'coalesce(cast("direction_id" AS INTEGER), 0)'
            else:
                expression = f'cast("{name}" AS {dtype})'
            expressions.append(expression)
        db.execute(f'INSERT INTO "{table}" SELECT ?, {", ".join(expressions)} FROM gtfs_csv', [feed_id])
        db.execute("DROP VIEW gtfs_csv")

    def _query(self, table: str, feed_id: str, filters=()) -> pd.DataFrame:
        columns = ", ".join(f'"{column}"' for column in TABLE_COLUMNS[table])
        conditions, parameters = ["feed_id = ?"], [feed_id]
        for column, values in filters:
            if values is not None:
                conditions.append(f'"{column}" IN (SELECT unnest(?))')
                parameters.append(list(values))
        with self._session() as db:
            return db.execute(f'SELECT {columns} FROM "{table}" WHERE {" AND ".join(conditions)}',
                              parameters).fetchdf()

    def get_agencies(self, feed_id: str) -> pd.DataFrame:
        return self._query("agency", feed_id).sort_values("agency_name").reset_index(drop=True)

    def get_routes(self, feed_id: str, agency_id: str | None = None) -> pd.DataFrame:
        return self._query("routes", feed_id, [("agency_id", None if agency_id is None else [agency_id])])

    def get_trips(self, feed_id: str, route_id: str | None = None, direction_id: int | None = None,
                  service_ids: Iterable[str] | None = None) -> pd.DataFrame:
        return self._query("trips", feed_id, [("route_id", None if route_id is None else [route_id]),
                                              ("direction_id", None if direction_id is None else [direction_id]),
                                              ("service_id", service_ids)])

    def get_stop_times_for_trips(self, feed_id: str, trip_ids: Iterable[str]) -> pd.DataFrame:
        if trip_ids is None:
            raise ValueError("Explicit trip IDs are required to query stop times")
        return self._query("stop_times", feed_id, [("trip_id", trip_ids)])

    def get_stops(self, feed_id: str, stop_ids: Iterable[str] | None = None) -> pd.DataFrame:
        return self._query("stops", feed_id, [("stop_id", stop_ids)])

    def get_calendar(self, feed_id: str) -> pd.DataFrame:
        return self._query("calendar", feed_id)

    def get_calendar_dates(self, feed_id: str) -> pd.DataFrame:
        return self._query("calendar_dates", feed_id)

    def get_feed_info(self, feed_id: str) -> pd.DataFrame:
        return self._query("feed_info", feed_id)
