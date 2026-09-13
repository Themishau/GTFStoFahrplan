"""Select and execute the appropriate timetable creation strategy."""

import copy
import re

from PySide6.QtCore import QObject, Signal

from model.domain.gtfs_data_source import GtfsDataSource
from model.domain.planning_settings import PlanningSettings
from model.enums import PlanMode
from model.planning.progress import ProgressUpdate
from model.planning.strategies.parallel_strategy import ParallelTableCreationStrategy
from model.planning.strategies.sequential_strategy import SequentialTableCreationStrategy


class PlanCreator(QObject):
    progress_updated = Signal(ProgressUpdate)
    error_occurred = Signal(str)
    data_selected = Signal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.gtfs_data = None
        self.planning_settings = PlanningSettings()
        self.strategy = None
        self.progress = ProgressUpdate()

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.progress_updated.emit(self._progress)

    def check_settings(self) -> bool:
        return self.is_valid_date_input(self.planning_settings.date)

    def update_progress(self, value):
        self.progress_updated.emit(copy.deepcopy(value))

    def create_timetable(self):
        mode = self.planning_settings.create_plan_mode
        if mode in (PlanMode.CIRCULATION_DATE, PlanMode.CIRCULATION_WEEKDAY):
            self.strategy = ParallelTableCreationStrategy(self.app,
                self.planning_settings,
                self.gtfs_data,
            )
        elif mode in (PlanMode.DATE, PlanMode.WEEKDAY):
            self.strategy = SequentialTableCreationStrategy(self.app,
                self.planning_settings,
                self.gtfs_data,
            )
        else:
            raise ValueError(f"Unsupported planning mode: {mode!r}")

        if self.planning_settings.use_individual_sorting:
            self.data_selected.emit()

        self.strategy.progress_updated.connect(self.update_progress)
        self.strategy.create_table()

    def continue_timetable(self):
        if self.strategy is None:
            raise RuntimeError("Create a timetable before continuing it")
        self.strategy.create_table_continue()

    @staticmethod
    def is_valid_date_input(dates) -> bool:
        return isinstance(dates, str) and re.fullmatch(r"\d{8}(?:,\d{8})*", dates) is not None
