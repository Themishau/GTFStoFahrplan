"""Progress data shared between background services and the UI."""

from dataclasses import dataclass
from time import time

from model.enums import ProcessKind


@dataclass(slots=True)
class ProgressUpdate:
    value: int = 0
    process_kind: ProcessKind | None = None
    message: str | None = None
    timestamp: float | None = None

    def set_progress(
            self,
            value: int,
        process_kind: ProcessKind | None = None,
            message: str | None = None,
    ) -> "ProgressUpdate":
        self.value = value
        self.process_kind = process_kind
        self.message = message
        self.timestamp = time()
        return self
