import logging
from PySide6.QtCore import Signal, QObject
from view.view_helpers import qdate_to_string
from model.Base.Progress import ProgressSignal
from model.Enum.GTFSEnums import *

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
delimiter = " "
lineend = '\n'


class ViewModelCreateData(QObject):
    update_progress_value = Signal(ProgressSignal)
    update_create_plan_mode = Signal(int)
    update_direction_mode = Signal(str)
    update_select_data = Signal(str)
    update_create_plan_continue = Signal()
    update_weekdate_option = Signal(str)
    update_individualsorting = Signal(bool)
    update_options_state_signal = Signal(bool)
    error_message = Signal(str)
    create_table_finshed = Signal()
    on_changed_individualsorting_table = Signal()

    def __init__(self, app, model):
        super().__init__()
        self.app = app
        self.model = model

    def create_table_continue(self):
        self.model.start_function_async(ModelTriggerActionsEnum.planer_start_create_table_continue.value)

    def create_table_stop(self):
        self.model.model_instance.cancel_async_operation()

    def start_create_table(self):
        self.model.planer.update_settings_for_create_table()
        self.model.start_function_async(ModelTriggerActionsEnum.planer_start_create_table.value)

    def select_weekday_option(self, selected_weekday):
        if self.model.planer.create_settings_for_table_dto.week_day_options_list is None:
            return False
        self.model.planer.create_settings_for_table_dto.weekday = selected_weekday
        return None

    def on_create_plan_finished(self):
        self.create_table_finshed.emit()

    def on_create_sorting_signal(self):
        self.on_changed_individualsorting_table.emit()

    def on_changed_options_state(self, value):
        self.update_options_state_signal.emit(value)

    def on_changed_individualsorting(self, value):
        self.model.planer.create_settings_for_table_dto.use_individual_sorting = value
        self.update_individualsorting.emit(value)

    def on_changed_selected_weekday(self, id_us):
        self.model.planer.create_settings_for_table_dto.weekday = id_us

    def on_changed_selected_dates(self, selected_dates):
        # gtfs format uses "YYYYMMDD" as date format
        self.model.planer.create_settings_for_table_dto.dates = qdate_to_string(selected_dates)
        self.update_select_data.emit(self.model.planer.create_settings_for_table_dto.dates)

    def on_changed_direction_mode(self, text):
        if text == Direction.direction_1.value:
            self.model.planer.create_settings_for_table_dto.direction = 0
        elif text == Direction.direction_2.value:
            self.model.planer.create_settings_for_table_dto.direction = 1

    def on_changed_selected_weekday_text_based(self, text):
        self.model.planer.create_settings_for_table_dto.weekday = text

    def on_changed_create_plan_mode(self, text):
        match text:
            case CreatePlanMode.date.value:
                mode = CreatePlanMode.date
                self.model.planer.create_settings_for_table_dto.weekday = None
            case CreatePlanMode.weekday.value:
                mode = CreatePlanMode.weekday
                self.model.planer.create_settings_for_table_dto.dates = None
            case CreatePlanMode.umlauf_date.value:
                mode = CreatePlanMode.umlauf_date
                self.model.planer.create_settings_for_table_dto.weekday = None
            case CreatePlanMode.umlauf_weekday.value:
                mode = CreatePlanMode.umlauf_weekday
                self.model.planer.create_settings_for_table_dto.dates = None
            case _:
                logging.error(f"Unexpected text value: {text}")
                mode = None

        if mode is not None:
            self.model.planer.create_settings_for_table_dto.create_plan_mode = mode
            self.update_create_plan_mode.emit(text)
        else:
            self.send_error_message("Invalid create plan mode selected. Please select a valid mode.")

    def on_changed_weekdate_option(self, text):
        self.model.planer.create_settings_for_table_dto.weekday = text
        self.update_weekdate_option.emit(text)

    def on_changed_progress_value(self, progress_data: ProgressSignal):
        self.update_progress_value.emit(progress_data)

    def send_error_message(self, message):
        self.error_message.emit(message)



