import copy

from model.domain.gtfs_data_source import GtfsDataSource
from model.domain.planning_settings import PlanningSettings
from model.enums import PlanMode
from model.planning.strategies.date_strategy import DateTimetableStrategy
from model.planning.strategies.individual_date_strategy import IndividualDateTimetableStrategy
from model.planning.strategies.individual_weekday_strategy import IndividualWeekdayTimetableStrategy
from model.planning.strategies.timetable_creation_strategy import TimetableCreationStrategy
from model.planning.strategies.weekday_strategy import WeekdayTimetableStrategy
from model.planning.timetable_planner import TimetablePlanner


class SequentialTimetableStrategy(TimetableCreationStrategy):
    def __init__(
            self,
            planning_settings: PlanningSettings,
            gtfs_data: GtfsDataSource,
    ) -> None:
        super().__init__()
        self.planning_settings = planning_settings
        self.gtfs_data = gtfs_data
        self.plan = TimetablePlanner()
        self._created = False

    def create_timetable(self) -> None:
        self.plan = TimetablePlanner()
        self.plan.planning_settings = copy.deepcopy(self.planning_settings)
        self.plan.gtfs_data = self.gtfs_data
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

        strategy = strategy_type(self.plan)
        strategy.progress_updated.connect(self.update_progress)
        strategy.create_timetable()
        self._created = True

    def continue_timetable(self) -> None:
        if not self._created:
            raise RuntimeError("Create a timetable before continuing it")
        self.plan.create_timetable_after_sorting()
