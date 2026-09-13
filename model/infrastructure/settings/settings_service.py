import json
import logging
import os
import tempfile
from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Final

from model.enums import TimeFormat

logger = logging.getLogger(__name__)

CURRENT_SETTINGS_VERSION: Final = 1
VALID_THEMES: Final = frozenset({"system", "light", "dark"})
VALID_TIME_FORMATS: Final = frozenset(value.value for value in TimeFormat)


@dataclass(frozen=True, slots=True)
class AppSettings:
    settings_version: int = CURRENT_SETTINGS_VERSION
    last_feed_id: str | None = None
    theme: str = "system"
    default_export_path: str = ""
    time_format: str = TimeFormat.HOURS_MINUTES.value


def migrate_settings(data: Mapping[str, object]) -> dict[str, object]:
    """Apply ordered migrations. Version 0 represents unversioned preferences."""
    migrated = dict(data)
    version = migrated.get("settings_version", 0)
    if type(version) is not int or not 0 <= version <= CURRENT_SETTINGS_VERSION:
        logger.warning("Unsupported settings version: %r; using defaults", version)
        return {}

    while version < CURRENT_SETTINGS_VERSION:
        if version == 0:
            # Version 1 introduced the version field; preference names are unchanged.
            version = 1
            migrated["settings_version"] = version
    return migrated


class SettingsService:
    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self) -> AppSettings:
        try:
            with self.path.open(encoding="utf-8") as stream:
                data = json.load(stream)
            if not isinstance(data, dict):
                raise ValueError("Settings must be a JSON object")
            data = migrate_settings(data)
        except FileNotFoundError:
            return AppSettings()
        except (OSError, ValueError, UnicodeError):
            logger.warning("Could not read settings; using defaults", exc_info=True)
            return AppSettings()
        defaults = AppSettings()
        values: dict[str, object] = {}
        for setting_field in fields(defaults):
            default = getattr(defaults, setting_field.name)
            value = data.get(setting_field.name, default)
            if setting_field.name == "last_feed_id":
                values[setting_field.name] = value if isinstance(value, str) and value else None
            elif type(value) is type(default):
                values[setting_field.name] = value

        if values.get("theme") not in VALID_THEMES:
            values.pop("theme", None)
        if values.get("time_format") not in VALID_TIME_FORMATS:
            values.pop("time_format", None)
        return AppSettings(**values)

    def save(self, settings: AppSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=self.path.parent,
                    prefix="settings-",
                    suffix=".tmp",
                    delete=False,
            ) as stream:
                temporary_path = Path(stream.name)
                json.dump(asdict(settings), stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            if temporary_path is None:
                raise RuntimeError("Could not create a temporary settings file")
            os.replace(temporary_path, self.path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
