import pandas as pd

from PySide6.QtCore import QObject, Signal

from model.enums import DirectionIndex, ModelAction, PlanMode
from view.view_helpers import qdate_to_string


class CreateViewModel(QObject):
    update_create_plan_mode = Signal(int)
    update_direction_mode = Signal(str)
    update_select_data = Signal(str)
    individual_sorting_changed = Signal(bool)
    update_options_state_signal = Signal(bool)
    error_message = Signal(str)
    table_created = Signal()
    individual_sorting_requested = Signal()

    def __init__(self, app, model, parent=None):
        super().__init__(parent)
        self.app = app
        self.model = model

        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Create DataFrames with category information
        self.df_all = pd.DataFrame(['All Days'], columns=['day']).assign(category='All Days')
        self.df_weekend = pd.DataFrame(['Weekend'], columns=['day']).assign(category='Weekend')
        self.df_weekdays = pd.DataFrame(['Weekdays'], columns=['day']).assign(category='Weekdays')
        self.df_days_only = pd.DataFrame({
            'day': self.days,
            'category': [f'{day} only' for day in self.days]
        })

        self.weekdays_df = pd.concat([
            self.df_all,
            self.df_weekend,
            self.df_weekdays,
            self.df_days_only
        ])

        for day in self.days:
            weekend_days = ['Saturday', 'Sunday']
            weekday_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

            self.weekdays_df[day] = (
                    (self.weekdays_df['day'] == day.capitalize()) |
                    ((self.weekdays_df['category'] == 'Weekend') &
                     (day.capitalize() in weekend_days)) |
                    ((self.weekdays_df['category'] == 'Weekdays') &
                     (day.capitalize() in weekday_days)) |
                    (self.weekdays_df['category'] == 'All Days')
            ).map({True: day.capitalize(), False: '-'})


    def continue_table_creation(self):
        self.model.start_function_async(ModelAction.CONTINUE_TIMETABLE.value)

    def get_sample_date(self):
        return self.model.planner.planning_settings.sample_date

    def get_success_message(self):
        output_path = self.model.planner.planning_settings.full_output_path
        return f"Success. Create table successfully. Saved here: {output_path}"

    def get_sorting_df(self):
        strategy = getattr(self.model.planner.plan_creator, "strategy", None)
        plans = getattr(strategy, "plans", None)
        timetable_data = getattr(plans, "timetable_data", None)
        return getattr(timetable_data, "filtered_stop_names", None)

    def stop_table_creation(self):
        self.model.cancel_async_operation()

    def start_table_creation(self):
        if self.model.thread is not None:
            return
        if self.model.planner.gtfs_data is None:
            self.send_error_message('Open a GTFS feed before creating a plan.')
            return
        self.model.planner.update_settings_for_create_table()
        self.model.start_function_async(ModelAction.CREATE_TIMETABLE.value)

    def handle_import_finished(self):
        self.model.planner.planning_settings.direction = 0

    def handle_plan_created(self):
        self.table_created.emit()

    def handle_sorting_requested(self):
        self.individual_sorting_requested.emit()

    def set_individual_sorting(self, value):
        self.model.planner.planning_settings.use_individual_sorting = value
        self.individual_sorting_changed.emit(value)

    def select_weekday(self, id_us):
        self.model.planner.planning_settings.weekday = id_us

    def select_date(self, selected_dates):
        # gtfs format uses "YYYYMMDD" as date format
        self.model.planner.planning_settings.date = qdate_to_string(selected_dates)
        self.update_select_data.emit(self.model.planner.planning_settings.date)

    def set_direction(self, text):
        if text == DirectionIndex.FIRST.value:
            self.model.planner.planning_settings.direction = 0
        elif text == DirectionIndex.SECOND.value:
            self.model.planner.planning_settings.direction = 1

    def set_plan_mode(self, index):
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

        self.model.planner.planning_settings.create_plan_mode = mode
        self.update_create_plan_mode.emit(index)

    def send_error_message(self, message):
        self.error_message.emit(message)



