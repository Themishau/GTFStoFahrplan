from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProgressSignal:
    """Custom signal type for progress updates"""
    value: int
    message: Optional[str] = None
    timestamp: Optional[float] = None

class ProgressClass(QObject):
    """Progress class using Qt signals"""

    progressChanged = Signal(ProgressSignal)

    def __init__(self):
        super().__init__()
        self._progress = 0

    def set_progress(self, value: int, message: Optional[str] = None):
        """Set progress and emit signal with custom type"""
        self._progress = value
        progress_data = ProgressSignal(
            value=value,
            message=message,
            timestamp=Optional[float](time.time()) if message else None
        )
        self.progressChanged.emit(progress_data)