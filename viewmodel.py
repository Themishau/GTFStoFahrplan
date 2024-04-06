import datetime as dt
import logging
import os
from PyQt5.Qt import QMessageBox, QObject
from PyQt5.QtCore import pyqtSignal, QCoreApplication
from view.select_table_view import TableModel
from view.sort_table_view import TableModelSort
from model.Base.GTFSEnums import *

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
delimiter = " "
lineend = '\n'


class ViewModel(QObject):
    input_file_path = pyqtSignal(str)
    pickle_file_path = pyqtSignal(str)
    output_file_path = pyqtSignal(str)
    export_plan_time_format = pyqtSignal(str)
    reset_view = pyqtSignal()
    update_create_plan_mode = pyqtSignal(str)
    update_direction_mode = pyqtSignal(str)
    update_pickle_export_checked = pyqtSignal(bool)
    update_selected_agency = pyqtSignal()
    update_selected_trip = pyqtSignal(str)
    update_create_plan_continue = pyqtSignal()
    update_select_data = pyqtSignal(str)
    update_weekdate_option = pyqtSignal(str)
    update_individualsorting = pyqtSignal(bool)
    create_table_finshed = pyqtSignal()

    def __init__(self, app, model):
        super().__init__()
        self.app = app
        self.model = model
        self.initilize_schedule_planer()

    def on_changed_pickle_export_checked(self, checked):
        self.model.planer.import_Data.pickle_export_checked = checked
        self.update_pickle_export_checked.emit(checked)

    def on_changed_create_plan_mode(self, text):
        if text == 'date':
            # self.model.planer.select_data.date_range =
            self.model.planer.select_data.selected_weekday = None
        elif text == 'weekday':
            # self.model.planer.select_data.selected_weekday =
            self.model.planer.select_data.selected_dates = None
        # change property in view
        self.update_create_plan_mode.emit(text)

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
        logging.debug(text)
        if text == 'time format 1':
            self.model.planer.select_data.selected_timeformat = 1
        elif text == 'time format 2':
            self.model.planer.select_data.selected_timeformat = 2
        self.export_plan_time_format.emit(text)

    def on_changed_direction_mode(self, text):
        if text == 'direction 1':
            self.model.gtfs.selected_direction = 0
        elif text == 'direction 2':
            self.model.gtfs.selected_direction = 1

    def on_changed_selected_weekday(self, text):
        self.model.planer.select_data.selected_weekday = text

    def initilize_schedule_planer(self):
        # init model with publisher
        self.model.set_up_schedule_planer()

    def set_process(self, task):
        self.model.gtfs.gtfs_process = task

    def on_changed_individualsorting(self, value):
        self.model.gtfs.individualsorting = value
        self.update_individualsorting.emit(value)

    def restart(self):
        self.reset_view()
        self.model.reset_model()

    # based on linked event subscriber are going to be notified
    def notify_subscriber(self, event, message):
        logging.debug(f'notify_subscriber event: {event}, message {message}')
        notify_function, parameters = self.notify_functions.get(event, self.notify_not_function)
        if not parameters:
            notify_function()
        else:
            notify_function(message)

    def trigger_action(self, event, message):
        logging.debug(f'trigger_action event: {event}, message {message}')
        notify_function, parameters = self.notify_functions.get(event, self.notify_not_function)
        if not parameters:
            notify_function()
        else:
            notify_function(message)

    def update_gui(self, event, message):
        logging.debug(f'update_gui event: {event}, message {message}')
        notify_function, parameters = self.notify_functions.get(event, self.notify_not_function)
        if not parameters:
            notify_function()
        else:
            notify_function(message)

    def notify_not_function(self, event):
        logging.debug('event not found in class gui: {}'.format(event))

    def select_weekday_option(self, selected_weekday):
        if self.model.gtfs.week_day_options_list is None:
            return False
        self.model.gtfs.selected_weekday = selected_weekday


    def on_changed_selected_record_agency(self, index):
        self.model.gtfs.selectedAgency = index
        logging.debug(f"selectedAgency {self.model.gtfs.selectedAgency}")
        self.update_selected_agency.emit(index)


    def on_changed_selected_record_trip(self, id_us):
        self.model.gtfs.selectedRoute = id_us


    def on_changed_selected_dates(self, selected_dates):
        self.model.gtfs.selected_dates = selected_dates
        self.update_select_data.emit(selected_dates)

    def notify_StopNameTableView(self):
        logging.debug(f"click stop")


    def create_table_continue(self):
        self.model.start_function_async(ModelTriggerActionsEnum.planer_start_create_table_continue.value)

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
            logging.debug("started import test")
        else:
            event = ShowErrorMessageEvent("Error. Could not load data.")
            QCoreApplication.postEvent(self.app, event)
            return

    def start_create_table(self):
        self.model.start_function_async(ModelTriggerActionsEnum.planer_start_create_table.value)

    def notify_select_option_button_direction(self):
        return self.dispatch("select_option_button_direction",
                             "select_option_button_direction routine started! Notify subscriber!")




def get_current_time():
    """ Helper function to get the current time in seconds. """
    now = dt.datetime.now()
    total_time = (now.hour * 3600) + (now.minute * 60) + now.second
    return total_time


if __name__ == '__main__':
    logging.debug('no')
