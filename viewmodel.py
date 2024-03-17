import datetime as dt
import logging
import os
import sys
from datetime import datetime

from threading import Thread
from PyQt5 import QtCore
from PyQt5.Qt import QPoint, QThread, QMessageBox, QDesktopWidget, QMainWindow, QObject
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFileDialog

from view.round_progress_bar import RoundProgress
from view.select_table_view import TableModel
from view.sort_table_view import TableModelSort
from view.pyui.main_window_ui import Ui_MainWindow
from view.general_window_information import GeneralInformation
from view.create_table_create import CreateTableCreate
from view.create_table_import import CreateTableImport
from view.create_table_select import CreateTableSelect
from view.download_gtfs import DownloadGTFS

from model.Base.GTFSEnums import *

# from model.Base.gtfs import gtfs
from model.SchedulePlaner.SchedulePlaner import SchedulePlaner
from model.observer import Publisher, Subscriber

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
delimiter = " "
lineend = '\n'


# noinspection PyUnresolvedReferences
class GTFSWorker(QThread, Publisher, Subscriber):

    def __init__(self, events, name, process):
        super().__init__(events=events, name=name)
        self.process = process

    def run(self):
        # try:
        if self.process == 'ImportGTFS':
            self.dispatch("sub_worker_load_gtfsdata",
                          "sub_worker_load_gtfsdata routine started! Notify subscriber!")
        elif self.process == 'fill_agency_list':
            self.dispatch("sub_worker_update_routes_list",
                          "sub_worker_update_routes_list routine started! Notify subscriber!")
        elif self.process == 'create_table_date':
            self.dispatch("sub_worker_create_output_fahrplan_date",
                          "sub_worker_create_output_fahrplan_date routine started! Notify subscriber!")
        elif self.process == 'create_table_date_individual':
            self.dispatch("sub_worker_create_output_fahrplan_date_indi",
                          "sub_worker_create_output_fahrplan_date_indi routine started! Notify subscriber!")
        elif self.process == 'create_table_date_individual_continue':
            self.dispatch("sub_worker_create_output_fahrplan_date_indi_continue",
                          "sub_worker_create_output_fahrplan_date_indi_continue routine started! Notify subscriber!")
        elif self.process == 'create_table_weekday':
            self.dispatch("sub_worker_create_output_fahrplan_weekday",
                          "sub_worker_create_output_fahrplan_weekday routine started! Notify subscriber!")


class Worker(QObject):
    def __init__(self, param):
        super().__init__()
        self.param = param

    def run(self):
        # Use self.param in your long-running task
        print("Running task with parameter:", self.param)


# noinspection PyUnresolvedReferences
class Model(QObject):
    def __init__(self, event_loop):
        super().__init__()
        self.event_loop = event_loop

        self.planer = None

        # we use this thread, to start processes not in the main gui thread
        self.thread = None
        self.notify_functions = {
            SchedulePlanerTriggerActionsEnum.schedule_planer_reset_schedule_planer: [
                self.trigger_action_reset_schedule_planer, False],
            SchedulePlanerTriggerActionsEnum.schedule_planer_start_create_table: [
                self.schedule_planer_trigger_action_start_create_table, False],
            SchedulePlanerTriggerActionsEnum.schedule_planer_start_create_table_continue: [
                self.schedule_planer_trigger_action_start_create_table_continue, False],
            SchedulePlanerTriggerActionsEnum.schedule_planer_update_routes_list: [
                self.schedule_planer_trigger_action_update_routes_gui_selection, False],
            SchedulePlanerTriggerActionsEnum.schedule_planer_create_output_fahrplan_date: [
                self.schedule_planer_trigger_action_create_output_schedule_plan_for_date, False],
            SchedulePlanerTriggerActionsEnum.schedule_planer_create_output_fahrplan_date_indi: [
                self.schedule_planer_trigger_action_create_output_fahrplan_date_indi, False],
            SchedulePlanerTriggerActionsEnum.schedule_planer_create_output_fahrplan_date_indi_continue: [
                self.schedule_planer_trigger_action_create_output_fahrplan_date_indi_continue, False],
            SchedulePlanerTriggerActionsEnum.schedule_planer_create_output_fahrplan_weekday: [
                self.schedule_planer_trigger_action_create_output_fahrplan_weekday, False]
        }

    def set_up_schedule_planer(self):
        self.planer = SchedulePlaner(self.event_loop)
        self.planer.initilize_scheduler()

    def set_up_umlauf_planer(self):
        NotImplemented

    def start_function_async(self, function_name):
        """
        pass argument via getattr (object_name: self.model, function_name: foo)
        :param function_name: getattr (object_name: self.model, function_name: foo)
        :return:
        """
        self.thread = QThread()
        self.model.moveToThread(self.thread)
        self.thread.started.connect(getattr(self, function_name))
        self.thread.start()

    def model_import_gtfs_data(self):
        self.planer.import_gtfs_data()

    def trigger_action_reset_schedule_planer(self):
        self.planer = None
        self.set_up_schedule_planer()

    def error_reset_model(self):
        self.dispatch("restart",
                      "restart routine started! Notify subscriber!")

    def sub_worker_load_gtfsdata(self):
        self.planer.import_gtfs_data()

    def sub_worker_update_routes_list(self):
        self.gtfs.get_routes_of_agency()

    def sub_worker_load_gtfsdata_indi(self):
        print('sub_worker_load_gtfsdata_indi')

    def sub_worker_create_output_fahrplan_weekday(self):
        self.gtfs.sub_worker_create_output_fahrplan_weekday()

    def sub_worker_create_output_fahrplan_date(self):
        self.gtfs.sub_worker_create_output_fahrplan_date()

    def sub_worker_create_output_fahrplan_date_indi(self):
        self.gtfs.sub_worker_create_output_fahrplan_date_indi()

    def sub_worker_create_output_fahrplan_date_indi_continue(self):
        self.gtfs.sub_worker_create_output_fahrplan_date_indi_continue()

    def sub_select_date_event(self):
        self.gtfs.selected_weekday = None

    def sub_start_create_table_continue(self):
        self.gtfs.processing = "continue..."
        logging.debug(f'continue...: {self.gtfs.selected_dates}')
        self.worker = GTFSWorker(['sub_worker_create_output_fahrplan_date_indi_continue'], 'Worker',
                                 'create_table_date_individual_continue')
        self.worker.register('sub_worker_create_output_fahrplan_date_indi_continue', self)
        self.worker.start()
        self.worker.finished.connect(self.finished_create_table)

    def schedule_planer_trigger_action_start_create_table(self):
        NotImplemented()

    def schedule_planer_trigger_action_start_create_table_continue(self):
        NotImplemented()

    def schedule_planer_trigger_action_update_routes_gui_selection(self):
        NotImplemented()

    def schedule_planer_trigger_action_create_output_schedule_plan_for_date(self):
        NotImplemented()

    def schedule_planer_trigger_action_create_output_fahrplan_date_indi(self):
        NotImplemented

    def schedule_planer_trigger_action_create_output_fahrplan_date_indi_continue(self):
        NotImplemented

    def schedule_planer_trigger_action_create_output_fahrplan_weekday(self):
        NotImplemented

    def sub_start_create_table(self):
        self.gtfs.processing = "create table"
        logging.debug(f'create table date: {self.gtfs.selected_dates}')
        logging.debug(f'create table weekday: {self.gtfs.selected_weekday}')
        logging.debug(f'create table individualsorting: {self.gtfs.individualsorting}')
        if self.gtfs.selected_weekday is None and self.gtfs.individualsorting is True:
            self.worker = GTFSWorker(['sub_worker_create_output_fahrplan_date_indi'], 'Worker',
                                     'create_table_date_individual')
            self.worker.register('sub_worker_create_output_fahrplan_date_indi', self)

        elif self.gtfs.selected_weekday is None:
            self.worker = GTFSWorker(['sub_worker_create_output_fahrplan_date'], 'Worker', 'create_table_date')
            self.worker.register('sub_worker_create_output_fahrplan_date', self)

        else:
            self.worker = GTFSWorker(['sub_worker_create_output_fahrplan_weekday'], 'Worker', 'create_table_weekday')
            self.worker.register('sub_worker_create_output_fahrplan_weekday', self)

        self.worker.start()
        if self.gtfs.selected_weekday is None and self.gtfs.individualsorting is True:
            self.worker.finished.connect(self.update_sorting_table)
        else:
            self.worker.finished.connect(self.finished_create_table)

    def finished_create_table(self):
        self.notify_finished()

    def update_sorting_table(self):
        self.worker = None

    def update_agency_list(self):
        if self.gtfs.pickleExport_checked is True:
            logging.debug("save not imolemented yet")
        self.model.planer.read_gtfs_agencies()

    def update_date_range(self):
        self.worker = None
        # self.update_weekdate_options()

    def update_routes_list(self):
        self.worker = None

    def update_weekdate_options(self):
        self.notify_update_weekdate_option()
        self.worker = None

    def notify_set_process(self, task):
        self.gtfs.processing = task

    def notify_delete_process(self):
        self.gtfs.processing = None

    def notify_update_stopname_create_list(self):
        return self.dispatch("update_stopname_create_list",
                             "update_stopname_create_list routine started! Notify subscriber!")

    def notify_update_routes_List(self):
        return self.dispatch("update_routes_list",
                             "update_routes_list routine started! Notify subscriber!")

    def notify_update_weekdate_option(self):
        return self.dispatch("update_weekdate_option",
                             "update_weekdate_option routine started! Notify subscriber!")

    def notify_finished(self):
        return self.dispatch("message",
                             "Table created!")


class ViewModel(QObject):
    input_file_path = pyqtSignal(str)
    pickle_file_path = pyqtSignal(str)
    output_file_path = pyqtSignal(str)
    export_plan_time_format = pyqtSignal(str)

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

    def onChanged(self, text):
        if text == 'date':
            self.view.CreateCreate_Tab.ui.listDatesWeekday.clear()
            self.view.CreateCreate_Tab.ui.lineDateInput.setText(self.model.planer.select_data.date_range)
            self.view.CreateCreate_Tab.ui.lineDateInput.setEnabled(True)
            self.view.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(False)
            self.model.gtfs.selected_weekday = None
        elif text == 'weekday':
            self.view.CreateCreate_Tab.ui.listDatesWeekday.addItems(self.model.planer.select_data.weekDayOptionsList)
            self.view.CreateCreate_Tab.ui.lineDateInput.clear()
            self.view.CreateCreate_Tab.ui.lineDateInput.setEnabled(False)
            self.view.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(True)
            self.model.gtfs.selected_dates = None

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
        self.CreateCreate_Tab.ui.listDatesWeekday.addItems(self.model.gtfs.weekDayOptionsList)

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

    def notify_restart(self):
        self.view.reset_view()
        return self.dispatch("reset_gtfs", "reset_gtfs started! Notify subscriber!")

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
        if self.model.gtfs.weekDayOptionsList is None:
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


class View(QMainWindow):
    def __init__(self, viewModel):
        super().__init__()
        self.viewModel = viewModel
        self.event_handlers = {UpdateGuiEnum.update_progress_bar: self.handle_progress_update,
                               UpdateGuiEnum.update_weekday_list: self.handle,
                               }

        self.progressRound = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.messageBox_model = QMessageBox()

        self.CreateMainTab = GeneralInformation()
        self.CreateImport_Tab = CreateTableImport()
        self.CreateSelect_Tab = CreateTableSelect()
        self.CreateCreate_Tab = CreateTableCreate()
        self.DownloadGTFS_Tab = DownloadGTFS()

        # Connect UI elements to controller methods
        self.createTableImport_btn = self.ui.pushButton_2
        self.createTableSelect_btn = self.ui.pushButton_3
        self.createTableCreate_btn = self.ui.pushButton_4
        self.generalNavPush_btn = self.ui.pushButton_5
        self.downloadGTFSNavPush_btn = self.ui.pushButton_6

        self.menu_btns_dict = {self.createTableImport_btn: CreateTableImport,
                               self.createTableSelect_btn: CreateTableSelect,
                               self.createTableCreate_btn: CreateTableCreate,
                               self.generalNavPush_btn: GeneralInformation,
                               self.downloadGTFSNavPush_btn: DownloadGTFS}

        self.initialize_window()
        self.initialize_modified_progress_bar()
        self.initialize_tabs()
        self.initialize_buttons_links()
        self.init_signals()
        self.ui.toolBox.setCurrentIndex(0)

        self.show_home_window()

    def initialize_buttons_links(self):
        # connect gui elements to methods in the controller
        self.CreateImport_Tab.ui.btnImport.clicked.connect(self.viewModel.start_import_gtfs_data)
        self.CreateImport_Tab.ui.btnRestart.clicked.connect(self.restart)

        self.CreateImport_Tab.ui.btnGetFile.clicked.connect(self.get_file_path)
        self.viewModel.input_file_path.connect(self.update_file_input_path)

        self.CreateImport_Tab.ui.btnGetPickleFile.clicked.connect(self.get_pickle_save_path)
        self.viewModel.pickle_file_path.connect(self.update_pickle_file_path)

        self.CreateImport_Tab.ui.btnGetOutputDir.clicked.connect(self.get_output_dir_path)
        self.viewModel.output_file_path.connect(self.update_output_file_path)

        self.CreateImport_Tab.ui.checkBox_savepickle.stateChanged.connect(self.viewModel.set_pickleExport_checked)
        self.viewModel.export_pickle_checked.connect(self.update_pickle_export_checked)

        self.CreateImport_Tab.ui.comboBox_display.activated[str].connect(self.viewModel.onChangedTimeFormatMode)
        self.viewModel.export_plan_time_format.connect(self.update_time_format)

        self.ui.pushButton_2.clicked.connect(self.show_Create_Import_Window)
        self.ui.pushButton_3.clicked.connect(self.show_Create_Select_Window)
        self.ui.pushButton_4.clicked.connect(self.show_Create_Create_Window)
        self.ui.pushButton_5.clicked.connect(self.show_home_window)
        self.ui.pushButton_6.clicked.connect(self.show_GTFSDownload_window)

        self.CreateSelect_Tab.ui.AgenciesTableView.clicked.connect(self.viewModel.notify_AgenciesTableView_agency)
        self.CreateSelect_Tab.ui.TripsTableView.clicked.connect(self.notify_TripsTableView)

        self.CreateCreate_Tab.ui.btnStart.clicked.connect(self.notify_create_table)
        self.CreateCreate_Tab.ui.btnContinueCreate.clicked.connect(self.notify_create_table_continue)
        self.CreateCreate_Tab.ui.UseIndividualSorting.clicked.connect(self.set_individualsorting)
        self.CreateCreate_Tab.ui.listDatesWeekday.clicked.connect(self.notify_select_weekday_option)
        self.CreateCreate_Tab.ui.comboBox.activated[str].connect(self.onChanged)
        self.CreateCreate_Tab.ui.comboBox_direction.activated[str].connect(self.onChangedDirectionMode)

    def update_file_input_path(self, input_path):
        self.CreateImport_Tab.ui.lineInputPath.setText(input_path)

    def update_pickle_file_path(self, pickle_path):
        self.CreateImport_Tab.ui.picklesavename.setText(pickle_path)

    def update_output_file_path(self, output_path):
        self.CreateImport_Tab.ui.lineOutputPath.setText(output_path)

    def update_time_format(self, time_format):
        self.CreateCreate_Tab.ui.line_Selection_format.setText(time_format)

    def initialize_window(self):
        self.setFixedSize(1350, 900)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.center()
        self.oldPos = self.pos()

    def init_signals(self):
        self.CreateImport_Tab.ui.comboBox_display.activated[str].connect(self.export_plan_time_format.emit)
        self.CreateImport_Tab.ui.lineInputPath.textChanged.connect(self.input_file_path.emit)
        self.CreateImport_Tab.ui.lineOutputPath.textChanged.connect(self.output_file_path.emit)
        self.CreateImport_Tab.ui.picklesavename.textChanged.connect(self.pickle_file_path.emit)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def event(self, event):
        # Use the event type to look up the handler function in the dictionary
        handler = self.event_handlers.get(event.event_type)
        if handler:
            return handler(event)
        return super().event(event)

    def handle_progress_update(self, event):
        self.progressRound.set_value(event.progress)
        return True

    def initialize_modified_progress_bar(self):
        # add the modified progress ui element
        self.progressRound = RoundProgress()
        self.progressRound.value = 0
        self.progressRound.setMinimumSize(self.progressRound.width, self.progressRound.height)
        self.ui.gridLayout_7.addWidget(self.progressRound, 4, 0, 1, 1, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

    def initialize_tabs(self):
        self.ui.stackedWidget.addWidget(self.CreateImport_Tab)
        self.ui.stackedWidget.addWidget(self.CreateSelect_Tab)
        self.ui.stackedWidget.addWidget(self.CreateCreate_Tab)
        self.ui.stackedWidget.addWidget(self.DownloadGTFS_Tab)
        self.ui.stackedWidget.addWidget(self.CreateMainTab)

    def show_GTFSDownload_window(self):
        self.set_btn_checked(self.downloadGTFSNavPush_btn)
        self.ui.stackedWidget.setCurrentWidget(self.DownloadGTFS_Tab)

    def show_home_window(self):
        self.set_btn_checked(self.generalNavPush_btn)
        self.ui.stackedWidget.setCurrentWidget(self.CreateMainTab)

    def show_Create_Import_Window(self):
        self.set_btn_checked(self.createTableImport_btn)
        self.ui.stackedWidget.setCurrentWidget(self.CreateImport_Tab)

    """
    TODO: is this bugged? 
    """

    def show_Create_Select_Window(self):
        self.set_btn_checked(self.createTableSelect_btn)
        self.ui.stackedWidget.setCurrentWidget(self.CreateSelect_Tab)

    def show_Create_Create_Window(self):
        self.set_btn_checked(self.createTableCreate_btn)
        self.ui.stackedWidget.setCurrentWidget(self.CreateCreate_Tab)
        self.ui.stackedWidget.resize(500, 500)

    def set_btn_checked(self, btn):
        for button in self.menu_btns_dict.keys():
            if button != btn:
                button.setChecked(False)
            else:
                button.setChecked(True)

    def get_file_path(self):
        try:
            input_file_path = QFileDialog.getOpenFileName(parent=self,
                                                          caption='Select GTFS Zip File',
                                                          directory='C:/Tmp',
                                                          filter='Zip File (*.zip)',
                                                          initialFilter='Zip File (*.zip)')

        except:
            input_file_path = QFileDialog.getOpenFileName(parent=self,
                                                          caption='Select GTFS Zip File',
                                                          directory=os.getcwd(),
                                                          filter='Zip File (*.zip)',
                                                          initialFilter='Zip File (*.zip)')
        if input_file_path[0] > '':
            self.viewModel.

    def get_output_dir_path(self):
        self.output_file_path = QFileDialog.getExistingDirectory(self,
                                                                 caption='Select GTFS Zip File',
                                                                 directory='C:/Tmp')
        if self.output_file_path > '':
            self.CreateImport_Tab.ui.lineOutputPath.setText(f'{self.output_file_path}/')

    def get_pickle_save_path(self):
        try:
            self.pickle_file_path = QFileDialog.getSaveFileName(parent=self,
                                                                caption='Select GTFS Zip File',
                                                                directory='C:/Tmp',
                                                                filter='Zip File (*.zip)',
                                                                initialFilter='Zip File (*.zip)')

        except:
            self.pickle_file_path = QFileDialog.getSaveFileName(parent=self,
                                                                caption='Select GTFS Zip File',
                                                                directory=os.getcwd(),
                                                                filter='Zip File (*.zip)',
                                                                initialFilter='Zip File (*.zip)')
        if self.pickle_file_path[0] > '':
            self.CreateImport_Tab.ui.picklesavename.setText(self.pickle_file_path[0])

    def reset_view(self):
        self.CreateImport_Tab.ui.btnImport.setEnabled(True)
        self.CreateImport_Tab.ui.btnRestart.setEnabled(False)
        self.CreateImport_Tab.ui.comboBox_display.setEnabled(True)

        self.CreateSelect_Tab.ui.AgenciesTableView.clear()
        self.CreateSelect_Tab.ui.TripsTableView.clear()

        self.CreateCreate_Tab.ui.btnStart.setEnabled(False)
        self.CreateCreate_Tab.ui.btnContinueCreate.setEnabled(False)
        self.CreateCreate_Tab.ui.comboBox.setEnabled(False)
        self.CreateCreate_Tab.ui.comboBox_direction.setEnabled(False)
        self.CreateCreate_Tab.ui.UseIndividualSorting.setEnabled(False)

        self.CreateCreate_Tab.ui.listDatesWeekday.clear()
        self.CreateCreate_Tab.ui.tableView_sorting_stops.clear()


def get_current_time():
    """ Helper function to get the current time in seconds. """
    now = dt.datetime.now()
    total_time = (now.hour * 3600) + (now.minute * 60) + now.second
    return total_time


if __name__ == '__main__':
    logging.debug('no')
