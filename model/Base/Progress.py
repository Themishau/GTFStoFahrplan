from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass
from typing import Optional
import time as Time

from model.Enum.GTFSEnums import ProcessType


@dataclass
class ProgressSignal:
    value: Optional[int] = 0
    process_name: Optional[str] = None
    message: Optional[str] = None
    timestamp: Optional[float] = None

    def set_progress(self, value: int, process_name: Optional[ProcessType] = None, message: Optional[str] = None):
        self.value= value
        self.process_name = process_name.value
        self.message= message
        self.timestamp= Time.time()
        return self

