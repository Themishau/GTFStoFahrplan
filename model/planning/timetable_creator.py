"""Select and execute the appropriate timetable creation strategy."""

import copy

from PySide6.QtCore import QObject, Signal

from model.domain.gtfs_data_source import GtfsDataSource
from model.domain.planning_settings import PlanningSettings
from model.enums import PlanMode
from model.planning.progress import ProgressUpdate
from model.planning.strategies.parallel_strategy import ParallelTimetableStrategy
from model.planning.strategies.sequential_strategy import SequentialTimetableStrategy


class TimetableCreator(QObject):
    progress_updated = Signal(ProgressUpdate)

    def __init__(self):
        super().__init__()
        self.gtfs_data: GtfsDataSource | None = None
        self.planning_settings = PlanningSettings()
        self.strategy: ParallelTimetableStrategy | SequentialTimetableStrategy | None = None

    def update_progress(self, value: ProgressUpdate) -> None:
        self.progress_updated.emit(copy.deepcopy(value))

    def create_timetable(self) -> None:
        if self.gtfs_data is None:
            raise RuntimeError("Open a GTFS feed before creating a timetable")
        mode = self.planning_settings.plan_mode
        if mode in (PlanMode.CIRCULATION_DATE, PlanMode.CIRCULATION_WEEKDAY):
            self.strategy = ParallelTimetableStrategy(self.planning_settings,
                                                      self.gtfs_data,
                                                      )
        elif mode in (PlanMode.DATE, PlanMode.WEEKDAY):
            self.strategy = SequentialTimetableStrategy(self.planning_settings,
                                                        self.gtfs_data,
                                                        )
        else:
            raise ValueError(f"Unsupported planning mode: {mode!r}")

        self.strategy.progress_updated.connect(self.update_progress)
        self.strategy.create_timetable()

    def continue_timetable(self) -> None:
        if self.strategy is None:
            raise RuntimeError("Create a timetable before continuing it")
        self.strategy.continue_timetable()
