import copy

from PySide6.QtCore import QObject, QThread, Signal

from model.planning.progress import ProgressUpdate
from model.enums import ProcessKind
from model.planning.strategies.metaclasses import QObjectABCMeta
from model.planning.strategies.base import TableCreationStrategy
from model.planning.timetable_planner import TimetablePlanner

class IndividualDateTableCreationStrategy(QObject, TableCreationStrategy, metaclass=QObjectABCMeta):
    progress_updated = Signal(ProgressUpdate)
    create_sorting = Signal()
    error_occurred = Signal(str)
    def __init__(self, app, timetable_planner: TimetablePlanner):
        super().__init__()
        self.app = app
        self.progress = ProgressUpdate()
        self.process = 10
        self.plan = timetable_planner


    def create_table(self) -> None:
        steps = [
            (self.plan.prepare_date_data, "prepare_date_data"),
            (self.plan.select_dates_for_range, "select_dates_for_range"),
            (self.plan.apply_date_exceptions, "apply_date_exceptions"),
            (self.plan.select_stops_for_trips, "select_stops_for_trips"),
            (self.plan.build_daily_trip_stops, "build_daily_trip_stops"),
            (self.plan.prepare_stop_sorting, "prepare_stop_sorting"),
        ]

        for step, description in steps:
            if QThread.currentThread().isInterruptionRequested():
                raise InterruptedError("Operation cancelled.")
            self.process = self.process + 10
            self.progress_updated.emit(self.progress.set_progress(self.process, ProcessKind.CREATE_PLAN, description))
            step()

        if QThread.currentThread().isInterruptionRequested():
            raise InterruptedError("Operation cancelled.")
        self.create_sorting.emit()


    def update_progress(self, value):
        self.progress_updated.emit(copy.deepcopy(value))
