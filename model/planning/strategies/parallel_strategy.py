import copy
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtCore import QObject, Signal

from model.domain.gtfs_data_source import GtfsDataSource
from model.domain.planning_settings import PlanningSettings
from model.enums import PlanMode
from model.planning.progress import ProgressUpdate
from model.planning.strategies.metaclasses import QObjectABCMeta
from model.planning.strategies.date_strategy import DateTimetableStrategy
from model.planning.strategies.base import TimetableCreationStrategy
from model.planning.strategies.individual_date_strategy import IndividualDateTimetableStrategy
from model.planning.strategies.individual_weekday_strategy import IndividualWeekdayTimetableStrategy
from model.planning.strategies.weekday_strategy import WeekdayTimetableStrategy
from model.planning.timetable_planner import TimetablePlanner


class ParallelTimetableStrategy(QObject, TimetableCreationStrategy, metaclass=QObjectABCMeta):
    progress_updated = Signal(ProgressUpdate)

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

        # Configure plans
        self.plans[0].planning_settings = copy.deepcopy(self.planning_settings)
        self.plans[0].gtfs_data = self.gtfs_data
        self.plans[0].planning_settings.direction = 0

        self.plans[1].planning_settings = copy.deepcopy(self.planning_settings)
        self.plans[1].planning_settings.direction = 1
        self.plans[1].gtfs_data = self.gtfs_data

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
                    logging.exception('Direction planning failed')
                    raise

    def continue_timetable(self) -> None:
        self.plans[0].create_timetable_after_sorting()
        self.plans[1].create_timetable_after_sorting()
