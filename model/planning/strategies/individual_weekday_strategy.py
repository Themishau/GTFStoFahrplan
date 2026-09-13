from PySide6.QtCore import QObject, Signal

from model.planning.strategies.base import TimetableCreationStrategy
from model.planning.progress import ProgressUpdate
from model.planning.strategies.metaclasses import QObjectABCMeta
from model.planning.timetable_planner import TimetablePlanner


class IndividualWeekdayTimetableStrategy(
    QObject,
    TimetableCreationStrategy,
    metaclass=QObjectABCMeta,
):
    progress_updated = Signal(ProgressUpdate)

    def __init__(self, timetable_planner: TimetablePlanner):
        super().__init__()
        self.progress = ProgressUpdate()
        self.process = 10
        self.plan = timetable_planner

    def create_timetable(self) -> None:
        steps = [
            (self.plan.prepare_weekday_data, "prepare_weekday_data"),
            (self.plan.select_dates_for_range, "select_dates_for_range"),
            (self.plan.apply_weekday_exceptions, "apply_weekday_exceptions"),
            (self.plan.select_stops_for_trips, "select_stops_for_trips"),
            (self.plan.build_daily_trip_stops, "build_daily_trip_stops"),
            (self.plan.prepare_stop_sorting, "prepare_stop_sorting"),
        ]

        self._run_steps(steps)
