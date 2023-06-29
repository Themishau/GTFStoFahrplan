from gtfs import gtfs
from observer import Publisher, Subscriber
import datetime as dt
import time
import sys
import os
from datetime import datetime
from PyQt5.Qt import QPoint, QMutex, QWidget, QMessageBox, QDesktopWidget, QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QColor, QPalette
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread, pyqtSignal, QAbstractTableModel
from PyQt5.QtWidgets import QFileDialog, QApplication, QTableView

from add_files.main_window_ui import Ui_MainWindow
from general_window_information import GeneralInformation
from create_table_create import CreateTableCreate
from create_table_import import CreateTableImport
from create_table_select import CreateTableSelect
from download_gtfs import DownloadGTFS
from SelectTableView import TableModel
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

delimiter = " "


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
        elif self.process == 'create_table_weekday':
            self.dispatch("sub_worker_create_output_fahrplan_weekday",
                          "sub_worker_create_output_fahrplan_weekday routine started! Notify subscriber!")

# noinspection PyUnresolvedReferences
class Model(Publisher, Subscriber):
    def __init__(self, events, name):
        Publisher.__init__(self, events)
        Subscriber.__init__(self, name)
        self.gtfs = gtfs(['ImportGTFS',
                          'fill_agency_list',
                          'create_table_date',
                          'create_table_weekday',
                          'update_weekday_list',
                          'update_routes_list',
                          'update_date_range',
                          'update_agency_list',
                          'active_weekdate_options',
                          'update_weekdate_option',
                          'update_progress_bar',
                          'message',
                          'update_import_progress_bar'], 'data')
        self.mutex = QMutex()
        self.worker = None
        self.notify_functions = {
                                 'load_gtfsdata_event': [self.sub_load_gtfsdata_event, False],
                                 'select_agency': [self.sub_select_agency_event, False],
                                 'select_route': [self.sub_select_route_event, False],
                                 'select_weekday': [self.sub_select_weekday_event, False],
                                 'reset_gtfs': [self.sub_reset_gtfs, False],
                                 'start_create_table': [self.sub_start_create_table, False],
                                 'sub_worker_load_gtfsdata': [self.sub_worker_load_gtfsdata, False],
                                 'sub_worker_update_routes_list': [self.sub_worker_update_routes_list, False]
                                 }

    def sub_reset_gtfs(self):
        self.gtfs = gtfs(['ImportGTFS',
                          'create_table_date',
                          'create_table_weekday'], 'data')

    def find(self, name, path):

        for root, dirs, files in os.walk(path):
            if name in files:
                return True

    def set_paths(self, input_path, output_path) -> bool:
        try:
            self.gtfs.set_paths(input_path, output_path)
            return self.find(input_path.split('/')[-1], input_path.replace(input_path.split('/')[-1], ''))
        except FileNotFoundError:
            logging.debug('error setting paths')
            return False

    def sub_load_gtfsdata_event(self):
        self.gtfs.processing = "loading data"
        self.notify_set_process("loading GTFS data...")

        self.worker = GTFSWorker(['sub_worker_load_gtfsdata'], 'Worker', 'ImportGTFS')
        self.worker.register('sub_worker_load_gtfsdata', self)

        self.worker.start()
        self.worker.finished.connect(self.update_agency_list)
        self.worker.exit()


    def error_reset_model(self):
            self.dispatch("restart",
                          "restart routine started! Notify subscriber!")

    def sub_worker_load_gtfsdata(self):
        self.gtfs.async_task_load_GTFS_data()


    def sub_worker_update_routes_list(self):
        self.gtfs.get_routes_of_agency()

    def sub_worker_create_output_fahrplan_weekday(self):
        self.gtfs.sub_worker_create_output_fahrplan_weekday()

    def sub_worker_create_output_fahrplan_date(self):
        self.gtfs.sub_worker_create_output_fahrplan_date()

    def sub_select_agency_event(self):
        self.gtfs.processing = "load routes list"
        self.notify_set_process("loading load routes list...")
        self.worker = GTFSWorker(['sub_worker_update_routes_list'], 'Worker', 'fill_agency_list')
        self.worker.register('sub_worker_update_routes_list', self)
        self.worker.start()
        self.worker.finished.connect(self.update_routes_list)

    def sub_select_route_event(self):
        self.dispatch("data_changed", "{} selected".format(self.gtfs.selectedRoute))

    def sub_select_weekday_event(self):
        self.gtfs.selected_dates = None
        self.dispatch("data_changed", "{} selected".format(self.gtfs.selected_weekday))

    def sub_select_date_event(self):
        self.gtfs.selected_weekday = None
        self.dispatch("data_changed", "{} selected".format(self.gtfs.selected_dates))

    def sub_start_create_table(self):
        self.gtfs.processing = "create table"
        self.notify_set_process("create table data...")

        if self.gtfs.selected_weekday is None:
            self.worker = GTFSWorker(['sub_worker_create_output_fahrplan'], 'Worker', 'create_table_date')
        else:
            self.worker = GTFSWorker(['sub_worker_create_output_fahrplan'], 'Worker', 'create_table_weekday')
        self.worker.register('sub_worker_create_output_fahrplan', self)

        self.worker.start()
        self.worker.finished.connect(self.finished_create_table)

    def finished_create_table(self):
        self.notify_finished()

    def update_agency_list(self):
        self.gtfs.read_gtfs_agencies()
        self.worker = None

    def update_date_range(self):
        self.worker = None
        # self.update_weekdate_options()

    def update_routes_list(self):
        self.worker = None
        # self.update_weekdate_options()

    def update_weekdate_options(self):
        self.notify_update_weekdate_option()
        self.worker = None

    def notify_set_process(self, task):
        self.dispatch("data_changed", "{}".format(task))
        self.gtfs.processing = task

    def notify_delete_process(self):
        self.dispatch("data_changed", "{} finished".format(self.gtfs.processing))
        self.gtfs.processing = None

    def notify_update_routes_List(self):
        return self.dispatch("update_routes_list",
                             "update_routes_list routine started! Notify subscriber!")

    def notify_update_weekdate_option(self):
        return self.dispatch("update_weekdate_option",
                             "update_weekdate_option routine started! Notify subscriber!")

    def notify_finished(self):
        return self.dispatch("message",
                             "Table created!")

    def notify_subscriber(self, event, message):
        logging.debug(f'event: {event}, message {message}')
        notify_function, parameters = self.notify_functions.get(event, self.notify_not_function)
        if not parameters:
            notify_function()
        else:
            notify_function(message)

    def notify_not_function(self, event):
        logging.debug('event not found in class gui: {}'.format(event))

class Gui(QMainWindow, Publisher, Subscriber):
    def __init__(self, events, name):
        super().__init__(events=events, name=name)
        # uic.loadUi(self.resource_path('add_files\\GTFSQT5Q.ui'), self)
        # pixmap = QPixmap(self.resource_path('add_files\\5282.jpg'))
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setFixedSize(1350, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.center()
        self.oldPos = self.pos()
        self.messageBox_model = QMessageBox()

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

        self.CreateMainTab = GeneralInformation()
        self.CreateImport_Tab = CreateTableImport()
        self.CreateSelect_Tab = CreateTableSelect()
        self.CreateCreate_Tab = CreateTableCreate()
        self.DownloadGTFS_Tab = DownloadGTFS()

        self.ui.stackedWidget.addWidget(self.CreateImport_Tab)
        self.ui.stackedWidget.addWidget(self.CreateSelect_Tab)
        self.ui.stackedWidget.addWidget(self.CreateCreate_Tab)
        self.ui.stackedWidget.addWidget(self.DownloadGTFS_Tab)
        self.ui.stackedWidget.addWidget(self.CreateImport_Tab)
        self.ui.stackedWidget.addWidget(self.CreateMainTab)

        # connect gui elements to methods

        self.CreateImport_Tab.ui.btnImport.clicked.connect(self.notify_load_gtfsdata_event)
        self.CreateImport_Tab.ui.btnRestart.clicked.connect(self.notify_restart)
        self.CreateCreate_Tab.ui.btnStart.clicked.connect(self.notify_create_table)
        self.CreateImport_Tab.ui.btnGetFile.clicked.connect(self.getFilePath)
        # self.DownloadGTFS_Tab.ui.btnGetDir.clicked.connect(self.getDirPath)
        self.CreateImport_Tab.ui.btnGetOutputDir.clicked.connect(self.getOutputDirPath)
        self.ui.pushButton_2.clicked.connect(self.show_Create_Import_Window)
        self.ui.pushButton_3.clicked.connect(self.show_Create_Select_Window)
        self.ui.pushButton_4.clicked.connect(self.show_Create_Create_Window)

        self.ui.pushButton_5.clicked.connect(self.show_home_window)
        self.ui.pushButton_6.clicked.connect(self.show_GTFSDownload_window)
        self.CreateSelect_Tab.ui.listAgencies.clicked.connect(self.notify_select_agency)
        """
         TODO: 
        """

        # self.listRoutes.clicked.connect(self.notify_select_route)
        # self.listDatesWeekday.clicked.connect(self.notify_select_weekday_option)
        # self.comboBox.activated[str].connect(self.onChanged)
        # self.comboBox_display.activated[str].connect(self.onChangedTimeFormatMode)
        # self.comboBox_direction.activated[str].connect(self.onChangedDirectionMode)
        # self.line_Selection_format.setText('time format 1')

        self.lineend = '\n'
        self.textBrowserText = ''
        self.notify_functions = {'update_routes_list': [self.sub_update_routes_list, False],
                                 'update_weekday_list': [self.sub_update_weekdate_option, False],
                                 'update_agency_list': [self.sub_update_agency_list, False],
                                 'update_weekdate_option': [self.sub_update_weekdate_option, False],
                                 'message': [self.send_message_box, True],
                                 'error_message': [self.sub_write_gui_log, True],
                                 'data_changed': [self.sub_write_gui_log, True],
                                 'update_progress_bar': [self.sub_update_progress_bar, False],
                                 'update_import_progress_bar': [self.sub_update_import_progress_bar, False],
                                 'restart': [self.notify_restart, False]
                                 }

        # init model with publisher
        self.model = Model(['update_weekday_list',
                            'update_routes_list',
                            'update_date_range',
                            'update_agency_list',
                            'active_weekdate_options',
                            'update_weekdate_option',
                            'error_message',
                            'message',
                            'data_changed',
                            'update_progress_bar',
                            'update_import_progress_bar',
                            'restart'], 'model')

        # init Observer model -> controller
        self.model.register('restart', self)
        self.model.register('message', self)
        self.model.register('error_message', self)

        self.model.gtfs.register('update_routes_list', self)  # Achtung, sich selbst angeben und nicht self.controller
        self.model.gtfs.register('update_date_range', self)
        self.model.gtfs.register('update_weekday_list', self)
        self.model.gtfs.register('update_agency_list', self)
        self.model.gtfs.register('update_weekdate_option', self)
        self.model.register('data_changed', self)
        self.model.gtfs.register('message', self)
        self.model.gtfs.register('update_progress_bar', self)
        self.model.gtfs.register('update_import_progress_bar', self)

        # init Observer controller -> model
        self.register('load_gtfsdata_event', self.model)
        self.register('select_agency', self.model)
        self.register('select_route', self.model)
        self.register('select_weekday', self.model)
        self.register('reset_gtfs', self.model)
        self.register('start_create_table', self.model)

        self.refresh_time = get_current_time()
        self.show_home_window()

    def show_GTFSDownload_window(self):
        self.set_btn_checked(self.downloadGTFSNavPush_btn)
        self.ui.stackedWidget.setCurrentWidget(self.DownloadGTFS_Tab)

    def show_home_window(self):
        self.set_btn_checked(self.generalNavPush_btn)
        self.ui.stackedWidget.setCurrentWidget(self.CreateMainTab)

    def show_Create_Import_Window(self):
        self.set_btn_checked(self.createTableImport_btn)
        self.ui.stackedWidget.setCurrentWidget(self.CreateImport_Tab)

    def show_Create_Select_Window(self):
        self.set_btn_checked(self.createTableSelect_btn)
        self.ui.stackedWidget.setCurrentWidget(self.CreateSelect_Tab)

    def show_Create_Create_Window(self):
        self.set_btn_checked(self.createTableCreate_btn)
        self.ui.stackedWidget.setCurrentWidget(self.CreateCreate_Tab)

    def set_btn_checked(self, btn):
        for button in self.menu_btns_dict.keys():
            logging.debug(f'set_btn_checked ?: {btn.objectName()}')
            if button != btn:
                button.setChecked(False)
            else:
                button.setChecked(True)

    # noinspection PyUnresolvedReferences
    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def onChanged(self, text):
        if text == 'date':
            self.CreateCreate_Tab.ui.listDatesWeekday.clear()
            self.CreateCreate_Tab.ui.lineDateInput.setEnabled(True)
            self.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(False)
            self.model.gtfs.selected_weekday = None
        elif text == 'weekday':
            self.CreateCreate_Tab.ui.listDatesWeekday.addItems(self.model.gtfs.weekDayOptionsList)
            self.CreateCreate_Tab.ui.lineDateInput.clear()
            self.CreateCreate_Tab.ui.lineDateInput.setEnabled(False)
            self.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(True)
            self.model.gtfs.selected_dates = None

    def onChangedTimeFormatMode(self, text):
        if text == 'time format 1':
            self.model.gtfs.timeformat = 1
        elif text == 'time format 2':
            self.model.gtfs.timeformat = 2
        self.CreateImport_Tab.ui.line_Selection_format.setText(text)

    def onChangedDirectionMode(self, text):
        if text == 'direction 1':
            self.model.gtfs.selected_direction = 0
        elif text == 'direction 2':
            self.model.gtfs.selected_direction = 1

    def send_message_box(self, text):
        self.messageBox_model.setStandardButtons(QMessageBox.Ok)
        self.messageBox_model.setText(text)
        self.messageBox_model.exec_()

    def sub_update_weekdate_option(self):
        self.CreateCreate_Tab.ui.comboBox.setEnabled(True)
        self.CreateImport_Tab.ui.comboBox_display.setEnabled(True)
        self.CreateCreate_Tab.ui.comboBox_direction.setEnabled(True)
        self.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(True)
        self.sub_update_weekday_list()
        self.CreateCreate_Tab.ui.btnStart.setEnabled(True)
        self.CreateCreate_Tab.ui.btnStop.setEnabled(True)

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
        self.CreateSelect_Tab.ui.listRoutes.clear()
        self.CreateSelect_Tab.ui.listRoutes.addItems(self.model.gtfs.routesList)

    def sub_update_agency_list(self):
        self.CreateSelect_Tab.ui.listAgencies.clear()
        self.CreateSelect_Tab.ui.listAgencies.addItems(self.model.gtfs.agenciesList)
        self.CreateSelect_Tab.ui.tableView.setModel(TableModel(self.model.gtfs.dfagency))
        self.CreateCreate_Tab.ui.line_Selection_date_range.setText(self.model.gtfs.date_range)
        self.show_Create_Select_Window()
        # self.model.start_get_date_range()
        logging.debug("done with creating dfs")
        # self.model.gtfs.save_h5(h5_filename="C:/Tmp/test.h5", data=self.model.gtfs.dfTrips, labels="trips")
    def sub_update_progress_bar(self):
        self.CreateCreate_Tab.ui.progressBar.setValue(self.model.gtfs.progress)

    def sub_update_import_progress_bar(self):
        self.CreateImport_Tab.ui.progressBar.setValue(self.model.gtfs.import_progress)

    def sub_write_gui_log(self, text):
        time_now = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
        self.textBrowserText = self.textBrowserText + str(time_now) + ': ' + text + self.lineend
        self.CreateCreate_Tab.ui.textBrowser.setText(self.textBrowserText)

    def set_process(self, task):
        self.sub_write_gui_log("{} started".format(task))
        self.model.gtfs.gtfs_process = task

    def getFilePath(self):
        try:
            file_path = QFileDialog.getOpenFileName(parent=self,
                                                    caption='Select GTFS Zip File',
                                                    directory='C:/Tmp',
                                                    filter='Zip File (*.zip)',
                                                    initialFilter='Zip File (*.zip)')

        except:
            file_path = QFileDialog.getOpenFileName(parent=self,
                                                    caption='Select GTFS Zip File',
                                                    directory=os.getcwd(),
                                                    filter='Zip File (*.zip)',
                                                    initialFilter='Zip File (*.zip)')
        if file_path[0] > '':
            self.CreateImport_Tab.ui.lineInputPath.setText(file_path[0])

    def getDirPath(self):
        file_path = QFileDialog.getExistingDirectory(self,
                                                     caption='Select GTFS Zip File', )
        if file_path > '':
            self.CreateImport_Tab.ui.GTFSInputPath.setText(file_path)

    def getOutputDirPath(self):
        file_path = QFileDialog.getExistingDirectory(self,
                                                     caption='Select GTFS Zip File',
                                                     directory='C:/Tmp')
        if file_path > '':
            self.CreateImport_Tab.ui.lineOutputPath.setText(f'{file_path}/')

    def notify_restart(self):
        self.CreateImport_Tab.ui.btnImport.setEnabled(True)
        self.CreateImport_Tab.ui.btnRestart.setEnabled(False)
        self.CreateCreate_Tab.ui.btnStart.setEnabled(False)
        self.CreateCreate_Tab.ui.btnStop.setEnabled(False)
        self.CreateCreate_Tab.ui.comboBox.setEnabled(False)
        self.CreateImport_Tab.ui.comboBox_display.setEnabled(True)
        self.CreateCreate_Tab.ui.comboBox_direction.setEnabled(False)
        self.CreateSelect_Tab.ui.listAgencies.clear()
        self.CreateSelect_Tab.ui.listRoutes.clear()
        self.CreateCreate_Tab.ui.listDatesWeekday.clear()

        return self.dispatch("reset_gtfs", "reset_gtfs started! Notify subscriber!")

    # based on linked event subscriber are going to be notified
    def notify_subscriber(self, event, message):
        logging.debug(f'CONTROLLER event: {event}, message {message}')
        notify_function, parameters = self.notify_functions.get(event, self.notify_not_function)
        if not parameters:
            notify_function()
        else:
            notify_function(message)

    def notify_not_function(self, event):
        logging.debug('event not found in class gui: {}'.format(event))

    # activity on gui will trigger notify events
    def notify_select_route(self):
        if self.model.gtfs.routesList is None:
            return False
        self.CreateSelect_Tab.ui.line_Selection_trips.setText(self.CreateSelect_Tab.ui.listRoutes.currentItem().text())
        self.model.gtfs.selectedRoute = self.CreateSelect_Tab.ui.listRoutes.currentItem().text().split(',')[1]
        self.dispatch("select_route", "select_route routine started! Notify subscriber!")
        self.sub_update_weekdate_option()

    # activity on gui will trigger notify events
    def notify_select_weekday_option(self):
        if self.model.gtfs.weekDayOptionsList is None:
            return False
        self.model.gtfs.selected_weekday = self.CreateSelect_Tab.ui.listDatesWeekday.currentItem().text().split(',')[0]
        self.dispatch("select_weekday", "select_weekday routine started! Notify subscriber!")

    def notify_select_agency(self):
        try:
            if self.model.gtfs.agenciesList is None:
                return False
            self.CreateCreate_Tab.ui.line_Selection_agency.setText(
                self.CreateSelect_Tab.ui.listAgencies.currentItem().text())
            self.model.gtfs.selectedAgency = self.CreateSelect_Tab.ui.listAgencies.currentItem().text().split(',')[0]
            self.reset_weekdayDate()
            self.dispatch("select_agency", "select_agency routine started! Notify subscriber!")
        except TypeError:
            logging.debug("TypeError in notify_select_agency")


    def notify_create_table(self):
        if self.model.gtfs.selected_weekday is None:
            self.model.gtfs.selected_dates = self.CreateSelect_Tab.ui.lineDateInput.text()
        self.dispatch("start_create_table", "start_create_table routine started! Notify subscriber!")

    def notify_load_gtfsdata_event(self):
        self.CreateImport_Tab.ui.btnImport.setEnabled(False)
        self.CreateImport_Tab.ui.btnRestart.setEnabled(True)
        if self.model.set_paths(self.CreateImport_Tab.ui.lineInputPath.text(),
                                self.CreateImport_Tab.ui.lineOutputPath.text()):
            return self.dispatch("load_gtfsdata_event", "load_gtfsdata_event routine started! Notify subscriber!")
        else:
            self.notify_restart()
            self.send_message_box('Error. Could not find GTFS Data.')

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


# SPLASH SCREEN


if __name__ == '__main__':
    logging.debug('no')
