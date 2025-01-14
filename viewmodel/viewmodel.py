import datetime as dt
import logging
import os

from PySide6.QtCore import Signal, QObject

from helpFunctions import qdate_to_string
from model.Enum.GTFSEnums import *

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
delimiter = " "
lineend = '\n'


class ViewModel(QObject):
    input_file_path = Signal(str)
    pickle_file_path = Signal(str)
    output_file_path = Signal(str)
    export_plan_time_format = Signal(str)
    reset_view = Signal()
    update_create_plan_mode = Signal(str)
    update_direction_mode = Signal(str)
    update_pickle_export_checked = Signal(bool)
    update_agency_list = Signal()
    update_routes_list_signal = Signal()
    update_selected_agency = Signal(int)
    update_create_plan_continue = Signal()
    update_select_data = Signal(str)
    update_weekdate_option = Signal(str)
    update_individualsorting = Signal(bool)
    update_progress_value = Signal(int)
    update_options_state_signal = Signal(bool)
    error_message = Signal(str)
    create_table_finshed = Signal()
    on_changed_individualsorting_table = Signal()
    set_up_create_tab_signal = Signal()

    def __init__(self, app, model):
        super().__init__()
        self.app = app
        self.model = model
        self.initilize_schedule_planer()

    def on_changed_pickle_export_checked(self, checked):
        self.model.planer.import_Data.pickle_export_checked = checked
        self.update_pickle_export_checked.emit(checked)

    def on_changed_create_plan_mode(self, text):
        match text:
            case CreatePlanMode.date.value:
                mode = CreatePlanMode.date
                self.model.planer.select_data.selected_weekday = None
            case CreatePlanMode.weekday.value:
                mode = CreatePlanMode.weekday
                self.model.planer.select_data.selected_dates = None
            case CreatePlanMode.umlauf_date.value:
                mode = CreatePlanMode.umlauf_date
                self.model.planer.select_data.selected_weekday = None
            case CreatePlanMode.umlauf_weekday.value:
                mode = CreatePlanMode.umlauf_weekday
                self.model.planer.select_data.selected_dates = None
            case _:
                logging.error(f"Unexpected text value: {text}")
                mode = None
        if mode is not None:
            self.model.planer.select_data.create_settings_for_table_dto.create_plan_mode = mode
            self.update_create_plan_mode.emit(text)
        else:
            self.send_error_message("Invalid create plan mode selected. Please select a valid mode.")

    def on_change_input_file_path(self, path):
        self.model.planer.import_Data.input_path = path[0]
        self.input_file_path.emit(path[0])

    def on_changed_weekdate_option(self, text):
        self.model.planer.select_data.selected_weekday = text
        self.update_weekdate_option.emit(text)

    def on_changed_pickle_path(self, path):
        self.model.planer.import_Data.pickle_save_path_filename = path[0]
        self.pickle_file_path.emit(path[0])

    def on_change_output_file_path(self, path):
        self.model.planer.export_plan.output_path = path
        self.output_file_path.emit(path)

    def on_changed_time_format_mode(self, text):
        logging.debug(f'time format {text}')
        if text == 'time format 1':
            self.model.planer.select_data.selected_timeformat = 1
        elif text == 'time format 2':
            self.model.planer.select_data.selected_timeformat = 2
        self.export_plan_time_format.emit(text)

    def on_changed_direction_mode(self, text):
        if text == Direction.direction_1.value:
            self.model.planer.select_data.selected_direction = 0
        elif text == Direction.direction_2.value:
            self.model.planer.select_data.selected_direction = 1

    def on_changed_selected_weekday(self, text):
        self.model.planer.select_data.selected_weekday = text

    def on_changed_progress_value(self, value):
        self.update_progress_value.emit(value)

    def initilize_schedule_planer(self):
        # init model with publisher
        self.model.set_up_schedule_planer()
        self.set_up_signals()

    def set_up_signals(self):
        self.model.planer.progress_Update.connect(self.on_changed_progress_value)
        self.model.planer.select_data.select_agency_signal.connect(self.on_loaded_agency_list)
        self.model.planer.error_occured.connect(self.send_error_message)
        self.model.planer.update_routes_list_signal.connect(self.on_loaded_trip_list)
        self.model.planer.update_options_state_signal.connect(self.on_changed_options_state)
        self.model.planer.create_sorting_signal.connect(self.on_create_sorting_signal)
        self.model.planer.create_finished.connect(self.on_create_plan_finished)

    def on_changed_options_state(self, value):
        self.update_options_state_signal.emit(value)

    def on_changed_individualsorting(self, value):
        self.model.planer.select_data.use_individual_sorting = value
        self.update_individualsorting.emit(value)

    def restart(self):
        self.reset_view()
        self.model.reset_model()

    def select_weekday_option(self, selected_weekday):
        if self.model.planer.select_data.week_day_options_list is None:
            return False
        self.model.planer.select_data.selected_weekday = selected_weekday

    def on_loaded_agency_list(self):
        self.update_agency_list.emit()

    def on_loaded_trip_list(self):
        self.update_routes_list_signal.emit()

    def on_changed_selected_record_agency(self, index):
        self.model.planer.select_data.selected_agency = index
        #self.update_selected_agency.emit(index)

    def on_changed_selected_record_trip(self, id_us):
        self.model.planer.select_data.selected_route = id_us
        logging.debug(f"{id_us["route_short_name"]}")

    def on_changed_selected_dates(self, selected_dates):
        # gtfs format uses "YYYYMMDD" as date format
        self.model.planer.select_data.selected_dates = qdate_to_string(selected_dates)
        self.update_select_data.emit(self.model.planer.select_data.selected_dates)

    def create_table_continue(self):
        self.model.start_function_async(ModelTriggerActionsEnum.planer_start_create_table_continue.value)

    def create_table_stop(self):
        self.model.model_instance.cancel_async_operation()

    @staticmethod
    def find(name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return True

    def start_import_gtfs_data(self):
        if (self.find(self.model.planer.import_Data.input_path.split('/')[-1],
                      self.model.planer.import_Data.input_path.replace(
                          self.model.planer.import_Data.input_path.split('/')[-1], ''))
        ):
            self.model.start_function_async(ModelTriggerActionsEnum.planer_start_load_data.value)
            self.set_up_create_tab_signal.emit()
            logging.debug("started import test")
        else:
            self.send_error_message(ErrorMessageRessources.error_load_data)
            return

    def start_create_table(self):
        self.model.planer.update_settings_for_create_table()
        self.model.start_function_async(ModelTriggerActionsEnum.planer_start_create_table.value)

    def send_error_message(self, message):
        self.error_message.emit(message)

    def on_create_sorting_signal(self):
        self.on_changed_individualsorting_table.emit()

    def on_create_plan_finished(self):
        self.create_table_finshed.emit()


def get_current_time():
    """ Helper function to get the current time in seconds. """
    now = dt.datetime.now()
    total_time = (now.hour * 3600) + (now.minute * 60) + now.second
    return total_time


if __name__ == '__main__':
    logging.debug('no')
