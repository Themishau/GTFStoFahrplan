from model.planning.strategies.timetable_creation_strategy import TimetableCreationStrategy
from model.planning.timetable_planner import TimetablePlanner


class IndividualDateTimetableStrategy(TimetableCreationStrategy):
    def __init__(self, timetable_planner: TimetablePlanner) -> None:
        super().__init__()
        self.plan = timetable_planner

    def create_timetable(self) -> None:
        steps = [
            (self.plan.prepare_date_data, "Prepare date selection"),
            (self.plan.select_dates_for_range, "Select service dates"),
            (self.plan.apply_date_exceptions, "Apply calendar exceptions"),
            (self.plan.select_stops_for_trips, "Select trip stops"),
            (self.plan.build_daily_trip_stops, "Build daily trip stops"),
            (self.plan.prepare_stop_sorting, "Prepare stop order"),
        ]

        self._run_steps(steps)
