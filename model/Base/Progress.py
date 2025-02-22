from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass
from typing import Optional
import time as Time

@dataclass
class ProgressSignal:
    """Custom signal type for progress updates"""
    value: Optional[int] = 0
    message: Optional[str] = None
    timestamp: Optional[float] = None

    def set_progress(self, value: int, message: Optional[str] = None):
        """Set progress and emit signal with custom type"""
        self.value= value
        self.message= message
        self.timestamp= Time.time()
        return self

