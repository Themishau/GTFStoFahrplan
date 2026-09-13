import copy

from PySide6.QtCore import QObject, Signal

from model.domain.gtfs_data_source import GtfsDataSource
from model.domain.planning_settings import PlanningSettings
from model.enums import PlanMode
from model.planning.progress import ProgressUpdate
from model.planning.strategies.metaclasses import QObjectABCMeta
from model.planning.strategies.date_strategy import DateTimetableStrategy
from model.planning.strategies.individual_date_strategy import IndividualDateTimetableStrategy
from model.planning.strategies.individual_weekday_strategy import IndividualWeekdayTimetableStrategy
from model.planning.strategies.base import TimetableCreationStrategy
from model.planning.strategies.weekday_strategy import WeekdayTimetableStrategy
from model.planning.timetable_planner import TimetablePlanner


class SequentialTimetableStrategy(QObject, TimetableCreationStrategy, metaclass=QObjectABCMeta):
    progress_updated = Signal(ProgressUpdate)

    def __init__(
        self,
        planning_settings: PlanningSettings,
        gtfs_data: GtfsDataSource,
    ) -> None:
        super().__init__()
        self.planning_settings = planning_settings
        self.gtfs_data = gtfs_data
        self.plans = TimetablePlanner()
        self._created = False

    def create_timetable(self) -> None:
        self.plans = TimetablePlanner()
        self.plans.planning_settings = copy.deepcopy(self.planning_settings)
        self.plans.gtfs_data = self.gtfs_data
        mode = self.planning_settings.plan_mode
        if mode == PlanMode.DATE:
            strategy_type = (
                IndividualDateTimetableStrategy
                if self.planning_settings.use_individual_sorting
                else DateTimetableStrategy
            )
        elif mode == PlanMode.WEEKDAY:
            strategy_type = (
                IndividualWeekdayTimetableStrategy
                if self.planning_settings.use_individual_sorting
                else WeekdayTimetableStrategy
            )
        else:
            raise ValueError(f"Unsupported sequential planning mode: {mode!r}")

        strategy = strategy_type(self.plans)
        strategy.progress_updated.connect(self.update_progress)
        strategy.create_timetable()
        self._created = True

    def continue_timetable(self) -> None:
        if not self._created:
            raise RuntimeError("Create a timetable before continuing it")
        self.plans.create_timetable_after_sorting()
