"""Progress data shared between background services and the UI."""

from dataclasses import dataclass
from time import time

from model.enums import ProcessKind


@dataclass(slots=True)
class ProgressUpdate:
    value: int = 0
    process_name: str | None = None
    message: str | None = None
    timestamp: float | None = None

    def set_progress(
        self,
        value: int,
        process_name: ProcessKind | None = None,
        message: str | None = None,
    ) -> "ProgressUpdate":
        self.value = value
        self.process_name = process_name.value if process_name is not None else None
        self.message = message
        self.timestamp = time()
        return self

