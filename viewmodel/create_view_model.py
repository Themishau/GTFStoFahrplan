import pandas as pd
from PySide6.QtCore import QDate, QObject, Signal

from model.application_model import ApplicationModel
from model.enums import DirectionIndex, ModelAction, PlanMode
from view.view_helpers import qdate_to_string

WEEKDAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)
WEEKEND_DAYS = frozenset({"Saturday", "Sunday"})


class CreateViewModel(QObject):
    plan_mode_changed = Signal(int)
    selected_date_changed = Signal(str)
    individual_sorting_changed = Signal(bool)
    error_message = Signal(str)
    timetable_created = Signal()
    individual_sorting_requested = Signal()

    def __init__(
            self,
            model: ApplicationModel,
            parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.model = model

        options = [
            {"day": "All Days", "category": "All Days"},
            {"day": "Weekend", "category": "Weekend"},
            {"day": "Weekdays", "category": "Weekdays"},
            *({"day": day, "category": f"{day} only"} for day in WEEKDAYS),
        ]
        self.weekdays_df = pd.DataFrame(options)

        for day in WEEKDAYS:
            category = self.weekdays_df["category"]
            selected = (
                    (self.weekdays_df["day"] == day)
                    | ((category == "Weekend") & (day in WEEKEND_DAYS))
                    | ((category == "Weekdays") & (day not in WEEKEND_DAYS))
                    | (category == "All Days")
            )
            self.weekdays_df[day] = selected.map({True: day, False: "-"})

    def continue_timetable_creation(self) -> None:
        self.model.start_action(ModelAction.CONTINUE_TIMETABLE)

    def get_sample_date(self) -> str | None:
        return self.model.planner.planning_settings.sample_date

    def get_success_message(self) -> str:
        output_path = self.model.planner.planning_settings.full_output_path
        return f"Timetable created successfully and saved to: {output_path}"

    def get_sorting_df(self) -> pd.DataFrame:
        return self.model.planner.timetable_creator.timetable_plan.timetable_data.ordered_stops

    def start_timetable_creation(self) -> None:
        if self.model.thread is not None:
            return
        if self.model.planner.gtfs_data is None:
            self.send_error_message('Open a GTFS feed before creating a plan.')
            return
        self.model.planner.refresh_timetable_creator()
        self.model.start_action(ModelAction.CREATE_TIMETABLE)

    def handle_import_finished(self) -> None:
        self.model.planner.planning_settings.direction = 0

    def handle_planning_finished(self) -> None:
        self.timetable_created.emit()

    def handle_sorting_requested(self) -> None:
        self.individual_sorting_requested.emit()

    def set_individual_sorting(self, value: bool) -> None:
        self.model.planner.planning_settings.use_individual_sorting = value
        self.individual_sorting_changed.emit(value)

    def select_weekday(self, weekdays: pd.DataFrame) -> None:
        self.model.planner.planning_settings.weekday = weekdays

    def select_date(self, selected_dates: QDate) -> None:
        # gtfs format uses "YYYYMMDD" as date format
        self.model.planner.planning_settings.date = qdate_to_string(selected_dates)
        self.selected_date_changed.emit(self.model.planner.planning_settings.date)

    def set_direction(self, index: int) -> None:
        if index == DirectionIndex.FIRST.value:
            self.model.planner.planning_settings.direction = 0
        elif index == DirectionIndex.SECOND.value:
            self.model.planner.planning_settings.direction = 1

    def set_plan_mode(self, index: int) -> None:
        match index:
            case PlanMode.DATE.value:
                mode = PlanMode.DATE
                self.model.planner.planning_settings.weekday = None
            case PlanMode.WEEKDAY.value:
                mode = PlanMode.WEEKDAY
                self.model.planner.planning_settings.date = None
            case PlanMode.CIRCULATION_DATE.value:
                mode = PlanMode.CIRCULATION_DATE
                self.model.planner.planning_settings.weekday = None
            case PlanMode.CIRCULATION_WEEKDAY.value:
                mode = PlanMode.CIRCULATION_WEEKDAY
                self.model.planner.planning_settings.date = None
            case _:
                self.send_error_message("Invalid create plan mode selected. Please select a valid mode.")
                return

        self.model.planner.planning_settings.plan_mode = mode
        self.plan_mode_changed.emit(index)

    def send_error_message(self, message: str) -> None:
        self.error_message.emit(message)
