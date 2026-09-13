import copy

from PySide6.QtCore import QObject, Signal
from model.planning.progress import ProgressUpdate
from model.enums import PlanMode
from model.planning.strategies.metaclasses import QObjectABCMeta
from model.planning.strategies.date_strategy import DateTableCreationStrategy
from model.planning.strategies.individual_date_strategy import IndividualDateTableCreationStrategy
from model.planning.strategies.individual_weekday_strategy import IndividualWeekdayTableCreationStrategy
from model.planning.strategies.base import TableCreationStrategy
from model.planning.strategies.weekday_strategy import WeekdayTableCreationStrategy
from model.planning.timetable_planner import TimetablePlanner

class SequentialTableCreationStrategy(QObject, TableCreationStrategy, metaclass=QObjectABCMeta):
    progress_updated = Signal(ProgressUpdate)
    create_sorting = Signal()
    error_occurred = Signal(str)
    def __init__(self, app, planning_settings, gtfs_data):
        super().__init__()
        self.app = app
        self.planning_settings = planning_settings
        self.gtfs_data = gtfs_data
        self.plans: TimetablePlanner | None = None
        self.progress = ProgressUpdate()

    def create_table(self) -> None:
        self.plans = TimetablePlanner()
        self.plans.planning_settings = copy.deepcopy(self.planning_settings)
        self.plans.gtfs_data = self.gtfs_data
        mode = self.planning_settings.create_plan_mode
        if mode == PlanMode.DATE:
            strategy_type = (
                IndividualDateTableCreationStrategy
                if self.planning_settings.use_individual_sorting
                else DateTableCreationStrategy
            )
        elif mode == PlanMode.WEEKDAY:
            strategy_type = (
                IndividualWeekdayTableCreationStrategy
                if self.planning_settings.use_individual_sorting
                else WeekdayTableCreationStrategy
            )
        else:
            raise ValueError(f"Unsupported sequential planning mode: {mode!r}")

        strategy = strategy_type(self.app, self.plans)
        strategy.progress_updated.connect(self.update_progress)
        strategy.create_table()

    def create_table_continue(self):
        self.plans.create_timetable_after_sorting()

    def update_progress(self, value):
        self.progress_updated.emit(copy.deepcopy(value))
