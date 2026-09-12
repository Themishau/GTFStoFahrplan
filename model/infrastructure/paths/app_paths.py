from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QStandardPaths


@dataclass(frozen=True)
class AppPaths:
    root: Path

    @classmethod
    def for_user(cls) -> "AppPaths":
        location = QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)
        if not location:
            raise OSError("Qt could not determine the application data directory")
        paths = cls(Path(location))
        paths.ensure_directories()
        return paths

    @property
    def database(self) -> Path:
        return self.root / "data" / "gtfs.duckdb"

    @property
    def settings_file(self) -> Path:
        return self.root / "settings" / "settings.json"

    @property
    def logs(self) -> Path:
        return self.root / "logs"

    @property
    def temp(self) -> Path:
        return self.root / "temp"

    def ensure_directories(self) -> None:
        for directory in (self.database.parent, self.settings_file.parent, self.logs, self.temp):
            directory.mkdir(parents=True, exist_ok=True)
