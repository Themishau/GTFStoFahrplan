import copy
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from model.domain.gtfs_data_source import GtfsDataSource
from model.domain.planning_settings import PlanningSettings
from model.enums import PlanMode
from model.planning.strategies.date_strategy import DateTimetableStrategy
from model.planning.strategies.individual_date_strategy import IndividualDateTimetableStrategy
from model.planning.strategies.individual_weekday_strategy import IndividualWeekdayTimetableStrategy
from model.planning.strategies.timetable_creation_strategy import TimetableCreationStrategy
from model.planning.strategies.weekday_strategy import WeekdayTimetableStrategy
from model.planning.timetable_planner import TimetablePlanner

logger = logging.getLogger(__name__)


class ParallelTimetableStrategy(TimetableCreationStrategy):
    def __init__(
            self,
            planning_settings: PlanningSettings,
            gtfs_data: GtfsDataSource,
    ) -> None:
        super().__init__()
        self.planning_settings = planning_settings
        self.gtfs_data = gtfs_data
        self.plans: list[TimetablePlanner] = []

    def create_timetable(self) -> None:
        self.plans = [TimetablePlanner(), TimetablePlanner()]

        for direction, plan in enumerate(self.plans):
            plan.planning_settings = copy.deepcopy(self.planning_settings)
            plan.planning_settings.direction = direction
            plan.gtfs_data = self.gtfs_data

        mode = self.planning_settings.plan_mode
        if mode == PlanMode.CIRCULATION_DATE:
            strategy_type = (
                IndividualDateTimetableStrategy
                if self.planning_settings.use_individual_sorting
                else DateTimetableStrategy
            )
        elif mode == PlanMode.CIRCULATION_WEEKDAY:
            strategy_type = (
                IndividualWeekdayTimetableStrategy
                if self.planning_settings.use_individual_sorting
                else WeekdayTimetableStrategy
            )
        else:
            raise ValueError(f"Unsupported parallel planning mode: {mode!r}")

        strategies = [strategy_type(plan) for plan in self.plans]
        for strategy in strategies:
            strategy.progress_updated.connect(self.update_progress)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(strategy.create_timetable) for strategy in strategies]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    logger.exception("Direction planning failed")
                    raise

    def continue_timetable(self) -> None:
        if len(self.plans) != 2:
            raise RuntimeError("Create both direction timetables before continuing")
        for plan in self.plans:
            plan.create_timetable_after_sorting()
