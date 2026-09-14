import logging
import tempfile
import zipfile
from collections.abc import Callable, Iterator
from pathlib import Path, PurePosixPath

from model.domain.gtfs_feed import FileFingerprint, GtfsFeed
from .gtfs_repository import GtfsRepository
from .schema import REQUIRED_TABLES, TABLE_COLUMNS

logger = logging.getLogger(__name__)


def _never_cancel() -> None:
    return None


def _ignore_progress(_value: int, _message: str) -> None:
    return None


class GtfsImporter:
    def __init__(self, repository: GtfsRepository, temp_directory: Path):
        self.repository = repository
        self.temp_directory = Path(temp_directory)

    def import_feed(self, path: Path, fingerprint: FileFingerprint,
                    check_cancelled: Callable[[], None] = _never_cancel,
                    progress: Callable[[int, str], None] = _ignore_progress) -> GtfsFeed:
        path = Path(path)
        logger.info("GTFS import started: %s", fingerprint.filename)
        self.temp_directory.mkdir(parents=True, exist_ok=True)

        def check_source() -> None:
            check_cancelled()
            stat = path.stat()
            if (stat.st_size, stat.st_mtime_ns) != (fingerprint.size, fingerprint.modified_ns):
                raise OSError("GTFS ZIP changed after fingerprinting; please retry")

        try:
            check_source()
            with zipfile.ZipFile(path) as archive, tempfile.TemporaryDirectory(
                    prefix="import-", dir=self.temp_directory) as directory:
                members = {}
                for member in archive.infolist():
                    if member.is_dir():
                        continue
                    filename = PurePosixPath(member.filename).name
                    table = filename.removesuffix(".txt")
                    if filename != f"{table}.txt" or table not in TABLE_COLUMNS:
                        continue
                    if table in members:
                        raise ValueError(f"Duplicate GTFS member: {filename}")
                    members[table] = member
                if not REQUIRED_TABLES <= members.keys() or not {"calendar", "calendar_dates"} & members.keys():
                    raise ValueError("Select a GTFS CSV ZIP containing the required tables and a calendar. "
                                     "Legacy pickle archives are not supported.")

                def extracted_tables() -> Iterator[tuple[str, Path]]:
                    available_tables = [
                        table_name
                        for table_name in TABLE_COLUMNS
                        if table_name in members
                    ]
                    for index, table_name in enumerate(available_tables):
                        check_source()
                        progress(15 + index * 9, f"Reading {table_name}.txt")
                        # Fixed destination names, never ZIP paths or extractall().
                        target = Path(directory) / f"{table_name}.txt"
                        with archive.open(members[table_name]) as source, target.open("wb") as destination:
                            while True:
                                check_cancelled()
                                chunk = source.read(8 * 1024 * 1024)
                                if not chunk:
                                    break
                                destination.write(chunk)
                        yield table_name, target
                        target.unlink()
                    check_source()

                feed = self.repository.import_tables(fingerprint, extracted_tables(), check_source, progress)
            logger.info("GTFS feed import completed: %s", feed.feed_id)
            return feed
        except InterruptedError:
            logger.info("GTFS feed import cancelled: %s", fingerprint.filename)
            raise
        except Exception:
            logger.exception("GTFS feed import failed: %s", fingerprint.filename)
            raise
