import copy
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtCore import QObject, Signal

from model.enums import PlanMode
from model.planning.progress import ProgressUpdate
from model.planning.strategies.metaclasses import QObjectABCMeta
from model.planning.strategies.date_strategy import DateTableCreationStrategy
from model.planning.strategies.base import TableCreationStrategy
from model.planning.strategies.individual_date_strategy import IndividualDateTableCreationStrategy
from model.planning.strategies.individual_weekday_strategy import IndividualWeekdayTableCreationStrategy
from model.planning.strategies.weekday_strategy import WeekdayTableCreationStrategy
from model.planning.timetable_planner import TimetablePlanner


class ParallelTableCreationStrategy(QObject, TableCreationStrategy, metaclass=QObjectABCMeta):
    progress_updated = Signal(ProgressUpdate)
    error_occurred = Signal(str)

    def __init__(self, app, planning_settings, gtfs_data):
        super().__init__()
        self.app = app
        self.planning_settings = planning_settings
        self.gtfs_data = gtfs_data
        self.plans: list[TimetablePlanner] = []
        self.progress = ProgressUpdate()


    def create_table(self) -> None:
        self.plans = [TimetablePlanner(), TimetablePlanner()]

        # Configure plans
        self.plans[0].planning_settings = copy.deepcopy(self.planning_settings)
        self.plans[0].gtfs_data = self.gtfs_data
        self.plans[0].planning_settings.direction = 0

        self.plans[1].planning_settings = copy.deepcopy(self.planning_settings)
        self.plans[1].planning_settings.direction = 1
        self.plans[1].gtfs_data = self.gtfs_data

        mode = self.planning_settings.create_plan_mode
        if mode == PlanMode.CIRCULATION_DATE:
            strategy_type = (
                IndividualDateTableCreationStrategy
                if self.planning_settings.use_individual_sorting
                else DateTableCreationStrategy
            )
        elif mode == PlanMode.CIRCULATION_WEEKDAY:
            strategy_type = (
                IndividualWeekdayTableCreationStrategy
                if self.planning_settings.use_individual_sorting
                else WeekdayTableCreationStrategy
            )
        else:
            raise ValueError(f"Unsupported parallel planning mode: {mode!r}")

        strategies = [strategy_type(self.app, plan) for plan in self.plans]
        for strategy in strategies:
            strategy.progress_updated.connect(self.update_progress)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(strategy.create_table) for strategy in strategies]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    logging.exception('Direction planning failed')
                    raise

    def create_table_continue(self):
        self.plans[0].create_timetable_after_sorting()
        self.plans[1].create_timetable_after_sorting()

    def update_progress(self, value):
        self.progress_updated.emit(copy.deepcopy(value))
