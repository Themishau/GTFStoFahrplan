import hashlib
import logging
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

from model.domain.gtfs_feed import FileFingerprint

logger = logging.getLogger(__name__)


def _never_cancel() -> None:
    return None


class GtfsFingerprintService:
    CHUNK_SIZE: Final = 8 * 1024 * 1024

    @staticmethod
    def calculate(
        path: Path,
        check_cancelled: Callable[[], None] = _never_cancel,
    ) -> FileFingerprint:
        path = Path(path)
        before = path.stat()
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while True:
                check_cancelled()
                chunk = stream.read(GtfsFingerprintService.CHUNK_SIZE)
                if not chunk:
                    break
                digest.update(chunk)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise OSError("GTFS ZIP changed while calculating its fingerprint; please retry")
        fingerprint = FileFingerprint(path.name, before.st_size,
                                      datetime.fromtimestamp(before.st_mtime, timezone.utc),
                                      before.st_mtime_ns, digest.hexdigest())
        logger.info("GTFS fingerprint generated: %s (%s)", path.name, fingerprint.sha256)
        return fingerprint
