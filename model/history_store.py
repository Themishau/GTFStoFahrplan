from __future__ import annotations

import json
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


@dataclass
class ImportHistoryEntry:
    imported_at: str
    file_name: str
    input_path: str
    file_size_mb: float
    output_path: str
    pickle_export_checked: bool
    pickle_file_path: str
    agencies: int
    routes: int
    trips: int
    feed_start_date: str
    feed_end_date: str
    archived_copy_path: str = ""


class ImportHistoryStore:
    def __init__(self, app_name: str = "GTFSFahrplan"):
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            local_app_data = str(Path.home() / "AppData" / "Local")

        self.base_dir = Path(local_app_data) / app_name / "gtfs_data"
        self.archive_dir = self.base_dir / "archive"
        self.history_file = self.base_dir / "import_history.json"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def load_entries(self) -> list[ImportHistoryEntry]:
        if not self.history_file.exists():
            return []

        try:
            raw_entries = json.loads(self.history_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

        entries = []
        for entry in raw_entries:
            entry_data = dict(entry)
            entry_data.setdefault("archived_copy_path", "")
            entries.append(ImportHistoryEntry(**entry_data))
        return entries

    def append_entry(self, entry: ImportHistoryEntry, limit: int = 200):
        entries = self.load_entries()
        entries.append(entry)
        entries = entries[-limit:]

        serialized = [asdict(item) for item in entries]
        temp_file = self.history_file.with_suffix(".tmp")
        temp_file.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
        temp_file.replace(self.history_file)

    def archive_import_file(self, source_path: str, imported_at: str) -> str:
        if not source_path:
            return ""

        source = Path(source_path)
        if not source.exists():
            return ""

        safe_timestamp = imported_at.replace(":", "-").replace(" ", "_")
        destination = self.archive_dir / f"{safe_timestamp}_{source.name}"
        shutil.copy2(source, destination)
        return str(destination)

    def to_dataframe(self) -> pd.DataFrame:
        entries = self.load_entries()
        if not entries:
            return pd.DataFrame(
                columns=[
                    "imported_at",
                    "file_name",
                    "file_size_mb",
                    "agencies",
                    "routes",
                    "trips",
                    "feed_start_date",
                    "feed_end_date",
                    "input_path",
                    "archived_copy_path",
                    "output_path",
                    "pickle_export_checked",
                    "pickle_file_path",
                ]
            )

        return pd.DataFrame([asdict(entry) for entry in entries])
