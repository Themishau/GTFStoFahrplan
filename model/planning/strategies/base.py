import copy
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence

from PySide6.QtCore import QThread

from model.enums import ProcessKind


class TimetableCreationStrategy(ABC):
    @abstractmethod
    def create_timetable(self) -> None:
        """Build one or more timetables."""

    def update_progress(self, value) -> None:
        self.progress_updated.emit(copy.deepcopy(value))

    def _run_steps(self, steps: Sequence[tuple[Callable[[], None], str]]) -> None:
        for step, description in steps:
            self._check_cancelled()
            self.process += 10
            self.progress_updated.emit(
                self.progress.set_progress(
                    self.process,
                    ProcessKind.CREATE_TIMETABLE,
                    description,
                )
            )
            step()

    @staticmethod
    def _check_cancelled() -> None:
        if QThread.currentThread().isInterruptionRequested():
            raise InterruptedError("Operation cancelled.")
