import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import duckdb
import pandas as pd

from model.domain.gtfs_feed import CURRENT_GTFS_SCHEMA_VERSION, IncompatibleFeedError
from model.infrastructure.database.gtfs_repository import GtfsRepository
from model.infrastructure.database.schema import TABLE_COLUMNS
from model.infrastructure.paths.app_paths import AppPaths
from model.infrastructure.settings.settings_service import (
    AppSettings, CURRENT_SETTINGS_VERSION, SettingsService, migrate_settings,
)
from model.services.cached_gtfs_data import CachedGtfsData
from model.services.gtfs_cache_service import GtfsCacheService
from model.services.gtfs_fingerprint import GtfsFingerprintService
from model.services.gtfs_time import gtfs_time_to_seconds
from tests.gtfs_fixtures import make_feed


class FingerprintTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "feed.zip"
        self.path.write_bytes(b"same content")

    def test_same_file_same_hash(self):
        one = GtfsFingerprintService.calculate(self.path)
        two = GtfsFingerprintService.calculate(self.path)
        self.assertEqual(one, two)
        self.assertEqual(one.filename, "feed.zip")
        self.assertEqual(one.size, len(b"same content"))

    def test_changed_content_with_same_name_size_and_mtime(self):
        first = GtfsFingerprintService.calculate(self.path)
        self.path.write_bytes(b"new! content")
        os.utime(self.path, ns=(first.modified_ns, first.modified_ns))
        second = GtfsFingerprintService.calculate(self.path)
        self.assertEqual(first.size, second.size)
        self.assertEqual(first.modified, second.modified)
        self.assertNotEqual(first.sha256, second.sha256)

    def test_chunked_hashing(self):
        with patch.object(GtfsFingerprintService, "CHUNK_SIZE", 2):
            self.assertEqual(GtfsFingerprintService.calculate(self.path).sha256,
                             __import__("hashlib").sha256(self.path.read_bytes()).hexdigest())

    def test_cancel_hash(self):
        def cancel():
            raise InterruptedError()

        with self.assertRaises(InterruptedError):
            GtfsFingerprintService.calculate(self.path, cancel)


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "settings" / "settings.json"
        self.service = SettingsService(self.path)

    def write_json(self, data):
        self.path.parent.mkdir(exist_ok=True)
        self.path.write_text(json.dumps(data), encoding="utf-8")

    def test_missing_file_and_defaults(self):
        self.assertEqual(self.service.load(), AppSettings())
        self.assertEqual(AppSettings().settings_version, CURRENT_SETTINGS_VERSION)
        self.assertIsNone(AppSettings().last_feed_id)
        self.assertEqual(AppSettings().theme, "system")
        self.assertEqual(AppSettings().time_format, "HH:mm")

    def test_valid_settings_roundtrip(self):
        settings = AppSettings(last_feed_id="abc", theme="dark", default_export_path="exports", time_format="HH:mm:ss")
        self.service.save(settings)
        self.assertEqual(self.service.load(), settings)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_malformed_json(self):
        self.path.parent.mkdir()
        self.path.write_text("{", encoding="utf-8")
        self.assertEqual(self.service.load(), AppSettings())

    def test_unknown_fields(self):
        self.write_json({"settings_version": 1, "theme": "light", "future_option": [1, 2]})
        self.assertEqual(self.service.load().theme, "light")

    def test_invalid_types(self):
        for data in ([], {"last_feed_id": 123, "time_format": [], "theme": "invalid"},
                     {"settings_version": "1"}):
            with self.subTest(data=data):
                self.write_json(data)
                self.assertEqual(self.service.load(), AppSettings())

    def test_migration_entry_point(self):
        original = {"theme": "dark"}
        self.assertEqual(migrate_settings(original), {"theme": "dark", "settings_version": 1})
        self.assertNotIn("settings_version", original)
        self.assertEqual(migrate_settings({"settings_version": 1}), {"settings_version": 1})
        self.write_json({"settings_version": 0, "theme": "dark"})
        self.assertEqual(self.service.load().theme, "dark")

    def test_future_version_uses_defaults(self):
        self.write_json({"settings_version": 999, "last_feed_id": "unknown"})
        self.assertEqual(self.service.load(), AppSettings())

    def test_failed_atomic_save_preserves_old_settings(self):
        self.service.save(AppSettings(theme="dark"))
        with patch("model.infrastructure.settings.settings_service.os.replace", side_effect=OSError("disk error")):
            with self.assertRaises(OSError):
                self.service.save(AppSettings(theme="light"))
        self.assertEqual(self.service.load().theme, "dark")
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])


class TimeTests(unittest.TestCase):
    def test_service_day_times(self):
        for value, expected in [("06:30:00", 23400), ("23:59:59", 86399),
                                ("24:15:00", 87300), ("25:30:00", 91800)]:
            with self.subTest(value=value):
                self.assertEqual(gtfs_time_to_seconds(value), expected)

    def test_missing_and_invalid_times(self):
        self.assertIsNone(gtfs_time_to_seconds(None))
        self.assertIsNone(gtfs_time_to_seconds(""))
        for value in ("-1:00:00", "24:60:00", "25:30", "06:30:60"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                gtfs_time_to_seconds(value)


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.paths = AppPaths(self.root / "app")
        self.cache = GtfsCacheService.for_paths(self.paths)
        self.addCleanup(lambda: self.cache.close())
        self.zip_path = make_feed(self.root / "feed.zip")

    def test_import_metadata_hash_and_projection(self):
        result = self.cache.open_or_import_gtfs(self.zip_path)
        self.assertFalse(result.cache_hit)
        feed = result.feed
        metadata = feed.metadata
        self.assertEqual(metadata.feed_publisher_name, 'Transit, "City"')
        self.assertEqual((metadata.agency_count, metadata.route_count, metadata.trip_count,
                          metadata.stop_count, metadata.stop_time_count), (1, 2, 3, 2, 5))
        self.assertEqual(str(metadata.feed_start_date), "2026-09-12")
        self.assertEqual(self.cache.repository.find_feed_by_hash(metadata.source_hash), feed)
        self.assertEqual(self.cache.settings.last_feed_id, feed.feed_id)
        self.assertEqual(SettingsService(self.paths.settings_file).load().last_feed_id, feed.feed_id)
        trips = self.cache.repository.get_trips(feed.feed_id, route_id="r1", direction_id=0)
        self.assertEqual(trips.trip_id.tolist(), ["t1"])
        self.assertEqual(trips.block_id.tolist(), ["vehicle-01"])
        stops = self.cache.repository.get_stops(feed.feed_id)
        self.assertIn('Central, "A"', stops.stop_name.tolist())
        self.assertIn("01", stops.stop_id.tolist())
        times = self.cache.repository.get_stop_times_for_trips(feed.feed_id, ["t3"])
        self.assertEqual(times.arrival_seconds.iloc[0], gtfs_time_to_seconds("24:15:00"))
        self.assertEqual(times.departure_seconds.iloc[0], gtfs_time_to_seconds("25:30:00"))
        self.assertEqual(times.arrival_time.iloc[0], "24:15:00")
        self.assertNotIn("unused", times.columns)
        self.assertFalse(list(self.paths.temp.glob("import-*")))

    def test_sql_time_conversion_matches_reusable_function(self):
        with self.cache.repository._session() as db:
            for value in ("06:30:00", "23:59:59", "24:15:00", "25:30:00", "", None):
                self.assertEqual(db.execute("SELECT gtfs_time_to_seconds(?)", [value]).fetchone()[0],
                                 gtfs_time_to_seconds(value))
            with self.assertRaises(duckdb.Error):
                db.execute("SELECT gtfs_time_to_seconds('24:60:00')")

    def test_import_never_materializes_pandas_tables(self):
        with patch("pandas.read_csv", side_effect=AssertionError("no Pandas CSV import")), \
                patch.object(self.cache.repository, "_query", side_effect=AssertionError("no DataFrame queries")):
            self.cache.open_or_import_gtfs(self.zip_path)

    def test_qt_application_paths(self):
        with patch("model.infrastructure.paths.app_paths.QStandardPaths.writableLocation",
                   return_value=str(self.root / "qt-local-data")):
            paths = AppPaths.for_user()
        self.assertEqual(paths.root, self.root / "qt-local-data")
        self.assertTrue(paths.database.parent.is_dir())
        self.assertTrue(paths.settings_file.parent.is_dir())
        self.assertTrue(paths.logs.is_dir())
        self.assertTrue(paths.temp.is_dir())

    def test_reselecting_zip_skips_import(self):
        first = self.cache.open_or_import_gtfs(self.zip_path)
        with patch.object(self.cache.importer, "import_feed", side_effect=AssertionError("should reuse")):
            second = self.cache.open_or_import_gtfs(self.zip_path)
        self.assertTrue(second.cache_hit)
        self.assertEqual(first.feed.feed_id, second.feed.feed_id)
        self.assertEqual(len(self.cache.get_recent_feeds()), 1)

    def test_renamed_zip_reuses_hash(self):
        first = self.cache.open_or_import_gtfs(self.zip_path)
        renamed = self.root / "renamed.zip"
        self.zip_path.rename(renamed)
        self.assertEqual(self.cache.open_or_import_gtfs(renamed).feed, first.feed)

    def test_multiple_feeds_and_delete_isolation(self):
        first = self.cache.open_or_import_gtfs(self.zip_path).feed
        make_feed(self.zip_path, publisher='Updated feed')
        second = self.cache.open_or_import_gtfs(self.zip_path).feed
        self.assertNotEqual(first.feed_id, second.feed_id)
        self.assertEqual(len(self.cache.get_recent_feeds()), 2)
        self.cache.delete_feed(first.feed_id)
        self.assertFalse(self.cache.repository.feed_exists(first.feed_id))
        self.assertTrue(self.cache.repository.feed_exists(second.feed_id))
        with self.cache.repository._session() as db:
            for table in TABLE_COLUMNS:
                self.assertEqual(db.execute(f'SELECT count(*) FROM "{table}" WHERE feed_id=?',
                                            [first.feed_id]).fetchone()[0], 0)
        self.assertEqual(len(self.cache.repository.get_stop_times_for_trips(second.feed_id, ["t1"])), 2)

    def test_delete_active_feed_clears_last_setting(self):
        feed = self.cache.open_or_import_gtfs(self.zip_path).feed
        self.cache.delete_feed(feed.feed_id)
        self.assertIsNone(self.cache.settings.last_feed_id)
        self.assertIsNone(self.cache.active_feed)
        self.assertIsNone(self.cache.last_feed)

    def test_delete_all_feeds_recreates_database_and_reclaims_storage(self):
        self.cache.open_or_import_gtfs(self.zip_path)
        make_feed(self.zip_path, publisher='Second cached feed')
        self.cache.open_or_import_gtfs(self.zip_path)
        self.assertEqual(len(self.cache.get_recent_feeds()), 2)
        size_before = self.cache.database_size_bytes()
        self.assertGreater(size_before, 0)

        self.cache.delete_all_feeds()

        self.assertEqual(self.cache.get_recent_feeds(), [])
        self.assertIsNone(self.cache.settings.last_feed_id)
        self.assertIsNone(self.cache.active_feed)
        self.assertIsNone(self.cache.last_feed)
        self.assertTrue(self.paths.database.is_file())
        files_size = self.paths.database.stat().st_size
        wal = Path(f'{self.paths.database}.wal')
        if wal.exists():
            files_size += wal.stat().st_size
        self.assertEqual(self.cache.database_size_bytes(), files_size)
        self.assertLess(self.cache.database_size_bytes(), size_before)

        result = self.cache.open_or_import_gtfs(self.zip_path)
        self.assertFalse(result.cache_hit)
        self.assertEqual(len(self.cache.get_recent_feeds()), 1)

    def test_failed_deletion_rolls_back(self):
        feed = self.cache.open_or_import_gtfs(self.zip_path).feed
        # Simulate a failure after deletions from the valid GTFS tables.
        with patch.dict(TABLE_COLUMNS, {"missing_table": {}}):
            with self.assertRaises(duckdb.Error):
                self.cache.delete_feed(feed.feed_id)
        self.assertTrue(self.cache.repository.feed_exists(feed.feed_id))
        self.assertEqual(len(self.cache.repository.get_stop_times_for_trips(feed.feed_id, ["t1"])), 2)

    def test_restart_without_zip_and_no_table_loading_to_activate(self):
        feed = self.cache.open_or_import_gtfs(self.zip_path).feed
        self.cache.close()
        self.zip_path.unlink()
        self.cache = GtfsCacheService.for_paths(self.paths)
        self.assertEqual(self.cache.last_feed, feed)
        self.assertIsNone(self.cache.active_feed)
        with patch.object(self.cache.repository, "_query", side_effect=AssertionError("no table load on open")):
            self.assertEqual(self.cache.open_feed(feed.feed_id), feed)
        self.assertEqual(self.cache.repository.get_trips(feed.feed_id).shape[0], 3)

    def test_persistence_in_new_process(self):
        feed = self.cache.open_or_import_gtfs(self.zip_path).feed
        self.cache.close()
        self.zip_path.unlink()
        code = ("from pathlib import Path; from model.infrastructure.database.gtfs_repository import GtfsRepository; "
                "import sys; r=GtfsRepository(Path(sys.argv[1]), Path(sys.argv[2])); "
                "f=r.get_feed(sys.argv[3]); assert f and f.metadata.stop_time_count == 5; r.close()")
        result = subprocess.run([sys.executable, "-c", code, str(self.paths.database),
                                 str(self.paths.temp), feed.feed_id], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_dangling_last_feed_setting(self):
        self.cache.update_settings(last_feed_id="does-not-exist")
        self.cache.close()
        self.cache = GtfsCacheService.for_paths(self.paths)
        self.assertIsNone(self.cache.settings.last_feed_id)
        self.assertIsNone(SettingsService(self.paths.settings_file).load().last_feed_id)

    def test_incompatible_feed_cannot_reuse_or_open(self):
        feed = self.cache.open_or_import_gtfs(self.zip_path).feed
        with self.cache.repository._session() as db:
            db.execute("UPDATE feeds SET import_schema_version = 0 WHERE feed_id = ?", [feed.feed_id])
        self.assertIsNone(self.cache.repository.find_feed_by_hash(feed.metadata.source_hash))
        with self.assertRaises(IncompatibleFeedError):
            self.cache.open_feed(feed.feed_id)
        new_feed = self.cache.open_or_import_gtfs(self.zip_path).feed
        self.assertNotEqual(feed.feed_id, new_feed.feed_id)
        self.assertEqual(new_feed.metadata.import_schema_version, CURRENT_GTFS_SCHEMA_VERSION)
        self.assertEqual(len(self.cache.get_recent_feeds()), 2)

    def test_layout_version_is_checked(self):
        self.cache.close()
        with duckdb.connect(str(self.paths.database)) as db:
            db.execute("UPDATE cache_schema SET version = 999")
        with self.assertRaisesRegex(ValueError, "migration"):
            GtfsRepository(self.paths.database, self.paths.temp)

    def test_optional_columns_and_calendar_only(self):
        make_feed(self.zip_path, optional=False)
        feed = self.cache.open_or_import_gtfs(self.zip_path).feed
        trips = self.cache.repository.get_trips(feed.feed_id)
        self.assertTrue(trips.block_id.isna().all())
        self.assertTrue((trips.direction_id == 0).all())
        self.assertEqual(self.cache.repository.get_agencies(feed.feed_id).agency_id.iloc[0],
                         self.cache.repository.get_routes(feed.feed_id).agency_id.iloc[0])
        self.assertIsNone(CachedGtfsData(feed, self.cache.repository).feed_info)
        self.assertEqual(str(feed.metadata.feed_start_date), "2026-09-12")

    def test_calendar_without_exception_file(self):
        replacement = self.root / "calendar-only.zip"
        with zipfile.ZipFile(self.zip_path) as source, zipfile.ZipFile(replacement, "w") as target:
            for name in source.namelist():
                if name != "calendar_dates.txt":
                    target.writestr(name, source.read(name))
        feed = self.cache.open_or_import_gtfs(replacement).feed
        self.assertTrue(self.cache.repository.get_calendar_dates(feed.feed_id).empty)
        self.assertFalse(CachedGtfsData(feed, self.cache.repository).calendar.empty)

    def test_calendar_dates_only_feed(self):
        make_feed(self.zip_path, calendar=False)
        feed = self.cache.open_or_import_gtfs(self.zip_path).feed
        self.assertTrue(self.cache.repository.get_calendar(feed.feed_id).empty)
        legacy = CachedGtfsData(feed, self.cache.repository)
        self.assertEqual(legacy.calendar.service_id.tolist(), ["s1"])
        self.assertEqual(legacy.calendar.saturday.tolist(), ["0"])

    def test_filters_empty_ids_and_feed_isolation(self):
        feed = self.cache.open_or_import_gtfs(self.zip_path).feed
        repo = self.cache.repository
        self.assertTrue(repo.get_trips(feed.feed_id, service_ids=[]).empty)
        self.assertTrue(repo.get_stop_times_for_trips(feed.feed_id, []).empty)
        self.assertTrue(repo.get_stop_times_for_trips(feed.feed_id, ["x' OR 1=1 --"]).empty)
        self.assertTrue(repo.get_stop_times_for_trips("other-feed", ["t1"]).empty)
        with self.assertRaises(ValueError):
            repo.get_stop_times_for_trips(feed.feed_id, None)

    def test_failed_import_rolls_back_all_tables(self):
        make_feed(self.zip_path, invalid_stop_sequence=True)
        with self.assertRaises(duckdb.Error):
            self.cache.open_or_import_gtfs(self.zip_path)
        self.assertEqual(self.cache.get_recent_feeds(), [])
        self.assertIsNone(self.cache.settings.last_feed_id)
        with self.cache.repository._session() as db:
            for table in TABLE_COLUMNS:
                self.assertEqual(db.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0], 0)
        self.assertFalse(list(self.paths.temp.glob("import-*")))

    def test_cancel_import_rolls_back_and_cleans_temp(self):
        cancelled = False

        def progress(value, message):
            nonlocal cancelled
            if message == "Imported trips":
                cancelled = True

        def check():
            if cancelled:
                raise InterruptedError()

        with self.assertRaises(InterruptedError):
            self.cache.open_or_import_gtfs(self.zip_path, check, progress)
        self.assertEqual(self.cache.get_recent_feeds(), [])
        self.assertFalse(list(self.paths.temp.glob("import-*")))

    def test_pickle_zip_is_never_deserialized(self):
        with zipfile.ZipFile(self.zip_path, "w") as archive:
            archive.writestr("Tmp/dfTrips.pkl", b"not trusted")
        with patch("pandas.read_pickle", side_effect=AssertionError("unsafe")), self.assertRaises(ValueError):
            self.cache.open_or_import_gtfs(self.zip_path)
        self.assertEqual(self.cache.get_recent_feeds(), [])


if __name__ == "__main__":
    unittest.main()
