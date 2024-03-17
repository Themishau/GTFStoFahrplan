import datetime as dt
import logging
import os
from PyQt5.Qt import QMessageBox, QObject
from PyQt5.QtCore import pyqtSignal
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

    def __init__(self, app, model):
        super().__init__()
        self.app = app
        self.model = model
        self.notify_functions = {UpdateGuiEnum.update_routes_list: [self.sub_update_routes_list, False],
                                 UpdateGuiEnum.update_weekday_list: [self.sub_update_weekdate_option, False],
                                 UpdateGuiEnum.update_agency_list: [self.sub_update_agency_list, False],
                                 UpdateGuiEnum.update_weekdate_option: [self.sub_update_weekdate_option, False],
                                 UpdateGuiEnum.update_stopname_create_list: [self.sub_update_stopname_create_list,
                                                                             False],
                                 UpdateGuiEnum.message: [self.send_message_box, True],
                                 UpdateGuiEnum.update_progress_bar: [self.sub_update_progress_bar, False],
                                 UpdateGuiEnum.show_error: [self.send_message_box, True],
                                 ControllerTriggerActionsEnum.restart: [self.notify_restart, False]
                                 }
        self.initilize_schedule_planer()

    def onChangedCreatePlanMode(self, text):
        # change property in
        self.update_create_plan_mode.emit(text)
        if text == 'date':
            self.model.planer.select_data.date_range =
            self.model.planer.select_data.selected_weekday = None
        elif text == 'weekday':
            self.model.planer.select_data.
            self.model.planer.select_data.selected_dates = None


    def onChangeInputFilePath(self, path):
        self.model.planer.import_Data.input_path = path
        self.input_file_path.emit(path)

    def onChangedPicklePath(self, path):
        self.model.planer.import_Data.pickle_save_path_filename = path
        self.pickle_file_path.emit(path)

    def onChangeOutputFilePath(self, path):
        self.model.planer.export_plan.output_path = path
        self.output_file_path.emit(path)

    def onChangedTimeFormatMode(self, text):
        logging.debug(text)
        if text == 'time format 1':
            self.model.planer.select_data.selected_timeformat = 1
        elif text == 'time format 2':
            self.model.planer.select_data.selected_timeformat = 2
        self.export_plan_time_format.emit(text)

    def onChangedDirectionMode(self, text):
        if text == 'direction 1':
            self.model.gtfs.selected_direction = 0
        elif text == 'direction 2':
            self.model.gtfs.selected_direction = 1

    def send_message_box(self, text):
        self.view.messageBox_model.setStandardButtons(QMessageBox.Ok)
        self.view.messageBox_model.setText(text)
        self.view.messageBox_model.exec_()

    def initialize_create_base_option(self):
        self.CreateCreate_Tab.ui.comboBox.setEnabled(True)
        self.CreateImport_Tab.ui.comboBox_display.setEnabled(True)
        self.CreateCreate_Tab.ui.comboBox_direction.setEnabled(True)
        self.CreateCreate_Tab.ui.btnStart.setEnabled(True)

    def sub_update_weekdate_option(self):
        self.initialize_create_base_option()
        self.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(True)
        self.sub_update_weekday_list()

    def sub_initialize_create_view_weekdaydate_option(self):
        self.initialize_create_base_option()
        self.CreateCreate_Tab.ui.listDatesWeekday.clear()
        self.CreateCreate_Tab.ui.lineDateInput.setText(self.model.gtfs.date_range)
        self.CreateCreate_Tab.ui.lineDateInput.setEnabled(True)
        self.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(False)
        self.model.gtfs.selected_weekday = None

    def reset_weekdayDate(self):
        self.CreateCreate_Tab.ui.comboBox.setEnabled(False)
        self.CreateImport_Tab.ui.comboBox_display.setEnabled(True)
        self.CreateCreate_Tab.ui.comboBox_direction.setEnabled(False)
        self.CreateCreate_Tab.ui.lineDateInput.setEnabled(False)
        self.CreateCreate_Tab.ui.listDatesWeekday.clear()

    def sub_update_weekday_list(self):
        self.CreateCreate_Tab.ui.listDatesWeekday.clear()
        self.CreateCreate_Tab.ui.listDatesWeekday.addItems(self.model.gtfs.week_day_options_list)

    def sub_update_routes_list(self):
        self.CreateSelect_Tab.ui.TripsTableView.setModel(TableModel(self.model.planer.select_data.df_selected_routes))

    def sub_update_stopname_create_list(self):
        self.CreateCreate_Tab.ui.tableView_sorting_stops.setModel(
            TableModelSort(self.model.gtfs.df_filtered_stop_names))
        self.CreateCreate_Tab.ui.btnContinueCreate.setEnabled(True)
        # self.CreateCreate_Tab.ui.tableView_sorting_stops.populate()

    def sub_update_agency_list(self):
        self.CreateSelect_Tab.ui.AgenciesTableView.setModel(
            TableModel(self.model.planer.select_data.imported_data["Agencies"]))
        self.CreateCreate_Tab.ui.line_Selection_date_range.setText(self.model.gtfs.date_range)
        self.CreateCreate_Tab.ui.lineDateInput.setText(self.model.gtfs.date_range)
        self.show_Create_Select_Window()
        # self.model.start_get_date_range()
        logging.debug("done with creating dfs")
        # self.model.gtfs.save_h5(h5_filename="C:/Tmp/test.h5", data=self.model.gtfs.dfTrips, labels="trips")

    def initilize_schedule_planer(self):
        # init model with publisher
        self.model.set_up_schedule_planer()

    def set_process(self, task):
        self.model.gtfs.gtfs_process = task

    def set_individualsorting(self):
        self.model.gtfs.individualsorting = not self.model.gtfs.individualsorting
        logging.debug(f"individualsorting: {self.model.gtfs.individualsorting}")

    def set_pickleExport_checked(self):
        self.model.planer.pickle_export_checked = self.view.CreateImport_Tab.ui.checkBox_savepickle.isChecked()

    def restart(self):
        self.view.reset_view()
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

    def notify_select_weekday_option(self):
        if self.model.gtfs.week_day_options_list is None:
            return False
        self.model.gtfs.selected_weekday = self.CreateCreate_Tab.ui.listDatesWeekday.currentItem().text().split(',')[0]
        self.dispatch("select_weekday", "select_weekday routine started! Notify subscriber!")

    def notify_AgenciesTableView_agency(self):
        index = self.CreateSelect_Tab.ui.AgenciesTableView.selectedIndexes()[0]
        logging.debug(f"index {index}")
        id_us = self.CreateSelect_Tab.ui.AgenciesTableView.model().data(index)
        logging.debug(f"index {id_us}")
        self.model.gtfs.selectedAgency = id_us
        logging.debug(f"selectedAgency {self.model.gtfs.selectedAgency}")
        self.reset_weekdayDate()
        self.dispatch("select_agency", "select_agency routine started! Notify subscriber!")

    def notify_TripsTableView(self):
        index = self.CreateSelect_Tab.ui.TripsTableView.selectedIndexes()[2]
        logging.debug(f"index {index}")
        id_us = self.CreateSelect_Tab.ui.TripsTableView.model().data(index)
        logging.debug(f"index {id_us}")
        self.model.gtfs.selectedRoute = id_us
        logging.debug(f"selectedRoute {self.model.gtfs.selectedRoute}")
        """ change initial selection (weekday mode or date mode) """
        self.sub_initialize_create_view_weekdaydate_option()
        # self.sub_update_weekdate_option()
        self.CreateCreate_Tab.ui.line_Selection_agency.setText(f"selected agency: {self.model.gtfs.selectedAgency}")
        self.CreateCreate_Tab.ui.line_Selection_trips.setText(f"selected Trip: {self.model.gtfs.selectedRoute}")

    def notify_StopNameTableView(self):
        logging.debug(f"click stop")

    def notify_create_table(self):
        if self.model.gtfs.selected_weekday is None:
            self.model.gtfs.selected_dates = self.CreateCreate_Tab.ui.lineDateInput.text()
            self.model.gtfs.selected_weekday = None
        else:
            self.model.gtfs.selected_dates = None

        self.dispatch("start_create_table", "start_create_table routine started! Notify subscriber!")

    def notify_create_table_continue(self):
        # self.model.gtfs.df_filtered_stop_names = self.CreateCreate_Tab.ui.tableView_sorting_stops.model.getData()
        self.dispatch("start_create_table_continue", "start_create_table_continue routine started! Notify subscriber!")

    """ Todo change to: start button is disabled till all checks are clear And add text, so user understands what is missing"""

    @staticmethod
    def find(name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return True

    def start_import_gtfs_data(self):
        self.view.CreateImport_Tab.ui.btnImport.setEnabled(False)
        self.view.CreateImport_Tab.ui.btnRestart.setEnabled(True)
        if (self.find(self.model.planer.import_Data.input_path.split('/')[-1],
                      self.model.planer.import_Data.input_path.replace(
                          self.model.planer.import_Data.input_path.split('/')[-1], ''))
        ):
            self.model.start_function_async("model_import_gtfs_data")
            logging.debug("started import test")
        else:
            self.send_message_box('Error. Could not load data.')
            self.notify_restart()
            return

    def notify_select_option_button_direction(self):
        return self.dispatch("select_option_button_direction",
                             "select_option_button_direction routine started! Notify subscriber!")

    def notify_close_program(self):
        return self.dispatch("close_program", "close_program routine started! Notify subscriber!")


def get_current_time():
    """ Helper function to get the current time in seconds. """
    now = dt.datetime.now()
    total_time = (now.hour * 3600) + (now.minute * 60) + now.second
    return total_time


if __name__ == '__main__':
    logging.debug('no')
