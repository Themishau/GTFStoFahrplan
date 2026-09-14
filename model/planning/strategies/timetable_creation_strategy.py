import copy
from collections.abc import Callable, Sequence

from PySide6.QtCore import QObject, QThread, Signal

from model.enums import ProcessKind
from model.planning.progress_update import ProgressUpdate


class TimetableCreationStrategy(QObject):
    """Qt-aware base for timetable creation workflows."""

    progress_updated = Signal(ProgressUpdate)

    def __init__(self) -> None:
        super().__init__()
        self._progress = ProgressUpdate()
        self._progress_value = 10

    def create_timetable(self) -> None:
        """Build one or more timetables."""
        raise NotImplementedError

    def continue_timetable(self) -> None:
        """Finish a timetable after an optional manual ordering step."""
        raise RuntimeError("This timetable workflow cannot be continued")

    def update_progress(self, value: ProgressUpdate) -> None:
        self.progress_updated.emit(copy.deepcopy(value))

    def _run_steps(self, steps: Sequence[tuple[Callable[[], None], str]]) -> None:
        for step, description in steps:
            self._check_cancelled()
            self._progress_value += 10
            self.progress_updated.emit(
                self._progress.set_progress(
                    self._progress_value,
                    ProcessKind.CREATE_TIMETABLE,
                    description,
                )
            )
            step()

    @staticmethod
    def _check_cancelled() -> None:
        if QThread.currentThread().isInterruptionRequested():
            raise InterruptedError("Operation cancelled.")
