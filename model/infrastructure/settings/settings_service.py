import json
import logging
import os
import tempfile
from dataclasses import asdict, dataclass, fields
from pathlib import Path

logger = logging.getLogger(__name__)
CURRENT_SETTINGS_VERSION = 1


@dataclass(frozen=True)
class AppSettings:
    settings_version: int = CURRENT_SETTINGS_VERSION
    last_feed_id: str | None = None
    theme: str = "system"
    default_export_path: str = ""
    time_format: str = "HH:mm"


def migrate_settings(data: dict) -> dict:
    """Apply ordered migrations. Version 0 represents unversioned preferences."""
    data = dict(data)
    version = data.get("settings_version", 0)
    if type(version) is not int or not 0 <= version <= CURRENT_SETTINGS_VERSION:
        logger.warning("Unsupported settings version: %r; using defaults", version)
        return {}
    while version < CURRENT_SETTINGS_VERSION:
        if version == 0:
            # Version 1 introduced the version field; preference names are unchanged.
            version = 1
            data["settings_version"] = version
    return data


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
        values = {}
        for field in fields(defaults):
            value = data.get(field.name, getattr(defaults, field.name))
            if field.name == "last_feed_id":
                values[field.name] = value if isinstance(value, str) and value else None
            elif type(value) is type(getattr(defaults, field.name)):
                values[field.name] = value
        if values.get("theme") not in ("system", "light", "dark"):
            values.pop("theme", None)
        if values.get("time_format") not in ("HH:mm", "HH:mm:ss"):
            values.pop("time_format", None)
        return AppSettings(**values)

    def save(self, settings: AppSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                             prefix="settings-", suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(asdict(settings), stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
