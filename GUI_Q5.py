from gtfs import gtfs
from observer import Publisher, Subscriber
import datetime as dt
import time
import sys
import os
from datetime import datetime
from PyQt5 import uic
from PyQt5.Qt import QPoint, QMutex, QWidget, QMessageBox, QDesktopWidget, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog

delimiter = " "


# noinspection PyUnresolvedReferences
class ImportGTFSDataWorker(QThread):
    importedGTFS = pyqtSignal(int)

    def __init__(self, worker_gtfs):
        super().__init__()
        self.gtfs = worker_gtfs

    def run(self):
        self.gtfs.update_agency_list()
        self.importedGTFS.emit(20)
        self.finished.emit()


# noinspection PyUnresolvedReferences
class GTFSWorker(QThread, Publisher, Subscriber):
    importedGTFS = pyqtSignal(int)

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
            elif self.process == 'fill_dates_range':
                self.dispatch("sub_worker_get_date_range",
                              "sub_worker_get_date_range routine started! Notify subscriber!")
            elif self.process == 'create_table_date':
                self.importedGTFS.emit(5)
                self.dispatch("sub_worker_prepare_data_fahrplan",
                              "sub_worker_prepare_data_fahrplan routine started! Notify subscriber!")
                self.importedGTFS.emit(15)
                self.dispatch("sub_worker_select_dates_for_date_range",
                              "sub_worker_select_dates_for_date_range routine started! Notify subscriber!")
                self.importedGTFS.emit(20)
                self.dispatch("sub_worker_select_dates_delete_exception_2",
                              "sub_worker_select_dates_delete_exception_2 routine started! Notify subscriber!")
                self.importedGTFS.emit(30)
                self.dispatch("sub_worker_select_stops_for_trips",
                              "sub_worker_select_stops_for_trips routine started! Notify subscriber!")
                self.importedGTFS.emit(40)
                self.dispatch("sub_worker_select_for_every_date_trips_stops",
                              "sub_worker_select_for_every_date_trips_stops routine started! Notify subscriber!")
                self.importedGTFS.emit(50)
                self.dispatch("sub_worker_select_stop_sequence_stop_name_sorted",
                              "sub_worker_select_stop_sequence_stop_name_sorted routine started! Notify subscriber!")
                self.importedGTFS.emit(70)
                self.dispatch("sub_worker_create_fahrplan_dates",
                              "sub_worker_create_fahrplan_dates routine started! Notify subscriber!")
                self.importedGTFS.emit(90)
                self.dispatch("sub_worker_create_output_fahrplan",
                              "sub_worker_create_output_fahrplan routine started! Notify subscriber!")
                self.importedGTFS.emit(100)
            elif self.process == 'create_table_weekday':
                self.importedGTFS.emit(5)
                self.dispatch("sub_worker_weekday_prepare_data_fahrplan",
                              "sub_worker_weekday_prepare_data_fahrplan routine started! Notify subscriber!")
                self.importedGTFS.emit(15)
                self.dispatch("sub_worker_select_dates_for_date_range",
                              "sub_worker_select_dates_for_date_range routine started! Notify subscriber!")
                self.importedGTFS.emit(20)
                self.dispatch("sub_worker_weekday_select_weekday_exception_2",
                              "sub_worker_weekday_select_weekday_exception_2 routine started! Notify subscriber!")
                self.importedGTFS.emit(30)
                self.dispatch("sub_worker_select_stops_for_trips",
                              "sub_worker_select_stops_for_trips routine started! Notify subscriber!")
                self.importedGTFS.emit(40)
                self.dispatch("sub_worker_select_for_every_date_trips_stops",
                              "sub_worker_select_for_every_date_trips_stops routine started! Notify subscriber!")
                self.importedGTFS.emit(50)
                self.dispatch("sub_worker_select_stop_sequence_stop_name_sorted",
                              "sub_worker_select_stop_sequence_stop_name_sorted routine started! Notify subscriber!")
                self.importedGTFS.emit(70)
                self.dispatch("sub_worker_create_fahrplan_dates",
                              "sub_worker_create_fahrplan_dates routine started! Notify subscriber!")
                self.importedGTFS.emit(90)
                self.dispatch("sub_worker_create_output_fahrplan",
                              "sub_worker_create_output_fahrplan routine started! Notify subscriber!")
                self.importedGTFS.emit(100)
            self.finished.emit()
        # except:
        #     print('Error in creating table!')
        #     self.finished.emit()



# noinspection PyUnresolvedReferences
class Model(Publisher, Subscriber):
    def __init__(self, events, name):
        Publisher.__init__(self, events)
        Subscriber.__init__(self, name)
        self.gtfs = gtfs()
        self.mutex = QMutex()
        self.worker = None

    def sub_reset_gtfs(self):
        self.gtfs = gtfs()

    def find(self, name, path):

        for root, dirs, files in os.walk(path):
            print(files)
            if name in files:
                return True

    def set_paths(self, input_path, output_path) -> bool:
        print(input_path.replace(input_path.split('/')[-1], ''))
        print(input_path.split('/')[-1])
        try:
            self.gtfs.set_paths(input_path, output_path)
            return self.find(input_path.split('/')[-1], input_path.replace(input_path.split('/')[-1], ''))
        except FileNotFoundError:
            print('error setting paths')
            return False

    def sub_load_gtfsdata_event(self):
        self.gtfs.processing = "loading data"
        self.notify_set_process("loading GTFS data...")
        # worker = ImportGTFSDataWorker(self.worker_gtfs)

        self.worker = GTFSWorker(['sub_worker_load_gtfsdata'], 'Worker', 'ImportGTFS')
        self.worker.register('sub_worker_load_gtfsdata', self)

        self.worker.importedGTFS.connect(lambda: self.notify_set_process("GTFS still loading..."))
        self.worker.start()
        self.worker.finished.connect(self.update_agency_list)

        self.gtfs.processing = None

    def error_reset_model(self):
        self.dispatch("restart",
                      "restart routine started! Notify subscriber!")

    def sub_worker_load_gtfsdata(self):
        self.gtfs.async_task_load_GTFS_data()

    def sub_worker_update_routes_list(self):
        self.gtfs.get_routes_of_agency()

    def sub_worker_get_date_range(self):
        self.gtfs.getDateRange()

    # dates
    def sub_worker_prepare_data_fahrplan(self):
        self.gtfs.dates_prepare_data_fahrplan()

    def sub_worker_select_dates_for_date_range(self):
        self.gtfs.datesWeekday_select_dates_for_date_range()

    def sub_worker_select_dates_delete_exception_2(self):
        self.gtfs.dates_select_dates_delete_exception_2()

    def sub_worker_select_stops_for_trips(self):
        self.gtfs.datesWeekday_select_stops_for_trips()

    def sub_worker_select_for_every_date_trips_stops(self):
        self.gtfs.datesWeekday_select_for_every_date_trips_stops()

    def sub_worker_select_stop_sequence_stop_name_sorted(self):
        self.gtfs.datesWeekday_select_stop_sequence_stop_name_sorted()

    # weekday

    def sub_worker_weekday_prepare_data_fahrplan(self):
        self.gtfs.weekday_prepare_data_fahrplan()

    def sub_worker_weekday_select_weekday_exception_2(self):
        self.gtfs.weekday_select_weekday_exception_2()

    def sub_worker_create_fahrplan_dates(self):
        self.gtfs.datesWeekday_create_fahrplan()

    def sub_worker_create_output_fahrplan(self):
        self.gtfs.datesWeekday_create_output_fahrplan()

    def start_get_date_range(self):
        self.gtfs.processing = "load dates list"
        self.notify_set_process("loading load dates ...")
        # worker = ImportGTFSDataWorker(self.worker_gtfs)

        self.worker = GTFSWorker(['sub_worker_get_date_range'], 'Worker', 'fill_dates_range')
        self.worker.register('sub_worker_get_date_range', self)

        self.worker.importedGTFS.connect(lambda: self.notify_set_process("dates still loading..."))
        self.worker.start()

        self.worker.finished.connect(self.update_date_range)

    def sub_select_agency_event(self):
        self.gtfs.processing = "load routes list"
        self.notify_set_process("loading load routes list...")
        # worker = ImportGTFSDataWorker(self.worker_gtfs)

        self.worker = GTFSWorker(['sub_worker_update_routes_list'], 'Worker', 'fill_agency_list')
        self.worker.register('sub_worker_update_routes_list', self)

        self.worker.importedGTFS.connect(lambda: self.notify_set_process("routes still loading..."))
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
        # worker = ImportGTFSDataWorker(self.worker_gtfs)

        if self.gtfs.selected_weekday is None:
            self.worker = GTFSWorker(['sub_worker_prepare_data_fahrplan',
                                      'sub_worker_select_dates_for_date_range',
                                      'sub_worker_select_dates_delete_exception_2',
                                      'sub_worker_select_stops_for_trips',
                                      'sub_worker_select_for_every_date_trips_stops',
                                      'sub_worker_select_stop_sequence_stop_name_sorted',
                                      'sub_worker_create_fahrplan_dates',
                                      'sub_worker_create_output_fahrplan'], 'Worker', 'create_table_date')

            self.worker.register('sub_worker_prepare_data_fahrplan', self)
            self.worker.register('sub_worker_select_dates_for_date_range', self)
            self.worker.register('sub_worker_select_dates_delete_exception_2', self)
            self.worker.register('sub_worker_select_stops_for_trips', self)
            self.worker.register('sub_worker_select_for_every_date_trips_stops', self)
            self.worker.register('sub_worker_select_stop_sequence_stop_name_sorted', self)
            self.worker.register('sub_worker_create_fahrplan_dates', self)
            self.worker.register('sub_worker_create_output_fahrplan', self)

        else:
            self.worker = GTFSWorker(['sub_worker_weekday_prepare_data_fahrplan',
                                      'sub_worker_select_dates_for_date_range',
                                      'sub_worker_weekday_select_weekday_exception_2',
                                      'sub_worker_select_stops_for_trips',
                                      'sub_worker_select_for_every_date_trips_stops',
                                      'sub_worker_select_stop_sequence_stop_name_sorted',
                                      'sub_worker_create_fahrplan_dates',
                                      'sub_worker_create_output_fahrplan'], 'Worker', 'create_table_weekday')

            self.worker.register('sub_worker_weekday_prepare_data_fahrplan', self)
            self.worker.register('sub_worker_select_dates_for_date_range', self)
            self.worker.register('sub_worker_weekday_select_weekday_exception_2', self)
            self.worker.register('sub_worker_select_stops_for_trips', self)
            self.worker.register('sub_worker_select_for_every_date_trips_stops', self)
            self.worker.register('sub_worker_select_stop_sequence_stop_name_sorted', self)
            self.worker.register('sub_worker_create_fahrplan_dates', self)
            self.worker.register('sub_worker_create_output_fahrplan', self)

        self.worker.importedGTFS.connect(self.notify_set_progressbar)
        self.worker.start()

        self.worker.finished.connect(self.finished_create_table)
        self.gtfs.processing = None

    def notify_set_progressbar(self, val):
        self.gtfs.progress = val
        return self.dispatch("update_progress_bar",
                             "update_progress_bar routine started! Notify subscriber!")

    def finished_create_table(self):
        self.notify_finished()
        print('fertig')

    def update_agency_list(self):
        if self.gtfs.noError:
            self.gtfs.read_gtfs_agencies()

            self.start_get_date_range()
            self.notify_update_agency_List()
            self.worker = None


    def update_date_range(self):
        self.worker = None
        # self.update_weekdate_options()

    def update_routes_list(self):
        self.notify_update_routes_List()
        self.worker = None
        # self.update_weekdate_options()

    def update_weekdate_options(self):
        self.notify_update_weekdate_option()
        self.worker = None

    def notify_set_process(self, task):
        self.dispatch("data_changed", "{}".format(task))
        print('task: {}'.format(task))
        self.gtfs.processing = task

    def notify_delete_process(self):
        self.dispatch("data_changed", "{} finished".format(self.gtfs.processing))
        self.gtfs.processing = None

    def notify_update_agency_List(self):
        return self.dispatch("update_agency_list",
                             "update_agency_list routine started! Notify subscriber!")


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
        print('model: {}'.format(event))
        if event == 'load_gtfsdata_event':
            self.sub_load_gtfsdata_event()
        elif event == 'select_agency':
            self.sub_select_agency_event()
        elif event == 'select_route':
            self.sub_select_route_event()
        elif event == 'select_weekday':
            self.sub_select_weekday_event()
        elif event == 'reset_gtfs':
            self.sub_reset_gtfs()
        elif event == 'sub_worker_load_gtfsdata':
            self.sub_worker_load_gtfsdata()
        elif event == 'sub_worker_update_routes_list':
            self.sub_worker_update_routes_list()
        elif event == 'sub_worker_get_date_range':
            self.sub_worker_get_date_range()
        elif event == 'start_create_table':
            self.sub_start_create_table()
        elif event == 'sub_worker_weekday_prepare_data_fahrplan':
            self.sub_worker_weekday_prepare_data_fahrplan()
        elif event == 'sub_worker_weekday_select_weekday_exception_2':
            self.sub_worker_weekday_select_weekday_exception_2()
        elif event == 'sub_worker_prepare_data_fahrplan':
            self.sub_worker_prepare_data_fahrplan()
        elif event == 'sub_worker_select_dates_for_date_range':
            self.sub_worker_select_dates_for_date_range()
        elif event == 'sub_worker_select_dates_delete_exception_2':
            self.sub_worker_select_dates_delete_exception_2()
        elif event == 'sub_worker_select_stops_for_trips':
            self.sub_worker_select_stops_for_trips()
        elif event == 'sub_worker_select_for_every_date_trips_stops':
            self.sub_worker_select_for_every_date_trips_stops()
        elif event == 'sub_worker_select_stop_sequence_stop_name_sorted':
            self.sub_worker_select_stop_sequence_stop_name_sorted()
        elif event == 'sub_worker_create_fahrplan_dates':
            self.sub_worker_create_fahrplan_dates()
        elif event == 'sub_worker_create_output_fahrplan':
            self.sub_worker_create_output_fahrplan()
        else:
            print('event not found in class model: {}'.format(event))


class Gui(QWidget, Publisher, Subscriber):
    def __init__(self, events, name):
        super().__init__(events=events, name=name)
        # uic.loadUi(self.resource_path('add_files\\GTFSQT5Q.ui'), self)
        # pixmap = QPixmap(self.resource_path('add_files\\5282.jpg'))
        uic.loadUi('add_files\\GTFSQT5Q.ui', self)
        pixmap = QPixmap('add_files\\5282.jpg')
        self.setFixedSize(1244, 889)
        self.label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.center()
        self.oldPos = self.pos()
        self.messageBox_model = QMessageBox()

        # connect gui elements to methods
        self.btnImport.clicked.connect(self.notify_load_gtfsdata_event)
        self.btnRestart.clicked.connect(self.notify_restart)
        self.btnStart.clicked.connect(self.notify_create_table)
        self.btnGetFile.clicked.connect(self.getFilePath)
        self.btnGetDir.clicked.connect(self.getDirPath)
        self.btnGetOutputDir.clicked.connect(self.getOutputDirPath)
        self.listAgencies.clicked.connect(self.notify_select_agency)
        self.listRoutes.clicked.connect(self.notify_select_route)
        self.listDatesWeekday.clicked.connect(self.notify_select_weekday_option)

        self.comboBox.activated[str].connect(self.onChanged)
        self.comboBox_display.activated[str].connect(self.onChangedTimeFormatMode)
        self.comboBox_direction.activated[str].connect(self.onChangedDirectionMode)
        self.lineend = '\n'
        self.textBrowserText = ''
        self.notify_functions = {'update_routes_list': [self.sub_update_routes_list, False],
                                'update_weekday_list': [self.sub_update_weekdate_option, False],
                                'update_agency_list': [self.sub_update_agency_list, False],
                                'update_weekdate_option': [self.sub_update_weekdate_option, False],
                                'message': [self.sub_write_gui_log, True],
                                'error_message': [self.sub_write_gui_log, True],
                                'data_changed': [self.sub_write_gui_log, True],
                                'update_progress_bar': [self.sub_update_progress_bar, False],
                                'restart': [self.notify_restart, False]
                               }

        # init subs and publisher

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
                            'restart'], 'model')

        # init Observer model -> controller
        self.model.register('update_routes_list', self)  # Achtung, sich selbst angeben und nicht self.controller
        self.model.register('update_date_range', self)
        self.model.register('update_weekday_list', self)
        self.model.register('update_agency_list', self)
        self.model.register('update_weekdate_option', self)
        self.model.register('message', self)
        self.model.register('error_message', self)
        self.model.register('data_changed', self)
        self.model.register('update_progress_bar', self)
        self.model.register('restart', self)

        # init Observer controller -> model
        self.register('message_test', self.model)
        self.register('load_gtfsdata_event', self.model)
        self.register('select_agency', self.model)
        self.register('select_route', self.model)
        self.register('select_weekday', self.model)
        self.register('reset_gtfs', self.model)
        self.register('start_create_table', self.model)

        self.refresh_time = get_current_time()

        self.line_Selection_format.setText('time format 1')

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
            self.listDatesWeekday.clear()
            self.lineDateInput.setEnabled(True)
            self.listDatesWeekday.setEnabled(False)
            self.model.gtfs.selected_weekday = None
        elif text == 'weekday':
            self.listDatesWeekday.addItems(self.model.gtfs.weekDayOptionsList)
            self.lineDateInput.clear()
            self.lineDateInput.setEnabled(False)
            self.listDatesWeekday.setEnabled(True)
            self.model.gtfs.selected_dates = None

    def onChangedTimeFormatMode(self, text):
        if text == 'time format 1':
            self.model.gtfs.timeformat = 1
        elif text == 'time format 2':
            self.model.gtfs.timeformat = 2
        self.line_Selection_format.setText(text)

    def onChangedDirectionMode(self, text):
        if text == 'direction 1':
            self.model.gtfs.selected_direction = 0
        elif text == 'direction 2':
            self.model.gtfs.selected_direction = 1

    def send_message_box(self, text):
        self.messageBox_model.setStandardButtons(QMessageBox.Ok)
        self.messageBox_model.setText(text)
        self.messageBox_model.exec_()

    # based on linked event subscriber are going to be notified
    def notify_subscriber(self, event, message):
        notify_function, parameters = self.notify_functions.get(event, self.notify_not_function)
        if not parameters:
            notify_function()
        else:
            notify_function(message)


    def notify_not_function(self, event):
            print('event not found in class gui: {}'.format(event))

    # activity on gui will trigger notify events
    def notify_select_route(self):
        if self.model.gtfs.routesList is None:
            return False
        self.line_Selection_trips.setText(self.listRoutes.currentItem().text())
        self.model.gtfs.selectedRoute = self.listRoutes.currentItem().text().split(',')[1]
        self.dispatch("select_route", "select_route routine started! Notify subscriber!")
        self.sub_update_weekdate_option()

    # activity on gui will trigger notify events
    def notify_select_weekday_option(self):
        if self.model.gtfs.weekDayOptionsList is None:
            return False
        self.model.gtfs.selected_weekday = self.listDatesWeekday.currentItem().text().split(',')[0]
        self.dispatch("select_weekday", "select_weekday routine started! Notify subscriber!")

    def notify_select_agency(self):
        try:
            if self.model.gtfs.agenciesList is None:
                return False
            self.line_Selection_agency.setText(self.listAgencies.currentItem().text())
            self.model.gtfs.selectedAgency = self.listAgencies.currentItem().text().split(',')[0]
            self.reset_weekdayDate()
            self.dispatch("select_agency", "select_agency routine started! Notify subscriber!")

        except TypeError:
            print("TypeError in notify_select_agency")

    def notify_create_table(self):
        if self.model.gtfs.selected_weekday is None:
            self.model.gtfs.selected_dates = self.lineDateInput.text()
        self.dispatch("start_create_table", "start_create_table routine started! Notify subscriber!")

    def sub_update_weekdate_option(self):
        print('in sub_update_weekdate_option')
        self.comboBox.setEnabled(True)
        self.comboBox_display.setEnabled(True)
        self.comboBox_direction.setEnabled(True)
        self.listDatesWeekday.setEnabled(True)
        self.sub_update_weekday_list()
        self.btnStart.setEnabled(True)
        self.btnStop.setEnabled(True)

    def reset_weekdayDate(self):
        self.comboBox.setEnabled(False)
        self.comboBox_display.setEnabled(True)
        self.comboBox_direction.setEnabled(False)
        self.lineDateInput.setEnabled(False)
        self.listDatesWeekday.clear()

    def notify_restart(self):
        print('RESTART')
        self.btnImport.setEnabled(True)
        self.btnRestart.setEnabled(False)
        self.btnStart.setEnabled(False)
        self.btnStop.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.comboBox_display.setEnabled(True)
        self.comboBox_direction.setEnabled(False)
        self.listAgencies.clear()
        self.listRoutes.clear()
        self.listDatesWeekday.clear()

        return self.dispatch("reset_gtfs", "reset_gtfs started! Notify subscriber!")

    def notify_load_gtfsdata_event(self):
        self.btnImport.setEnabled(False)
        self.btnRestart.setEnabled(True)
        if self.model.set_paths(self.lineInputPath.text(), self.lineOutputPath.text()):
            return self.dispatch("load_gtfsdata_event", "load_gtfsdata_event routine started! Notify subscriber!")
        else:
            self.notify_restart()
            self.send_message_box('Error. Could not find GTFS Data.')

    def notify_select_option_button_direction(self):
        return self.dispatch("select_option_button_direction",
                             "select_option_button_direction routine started! Notify subscriber!")

    def notify_close_program(self):
        return self.dispatch("close_program", "close_program routine started! Notify subscriber!")

    def sub_update_weekday_list(self):
        self.listDatesWeekday.clear()
        self.listDatesWeekday.addItems(self.model.gtfs.weekDayOptionsList)

    def sub_update_routes_list(self):
        self.listRoutes.clear()
        self.listRoutes.addItems(self.model.gtfs.routesList)

    def sub_update_agency_list(self):
        self.listAgencies.clear()
        self.listAgencies.addItems(self.model.gtfs.agenciesList)
        self.line_Selection_date_range.setText(self.model.gtfs.date_range)

    def sub_update_progress_bar(self):
        self.progressBar.setValue(self.model.gtfs.progress)

    def sub_write_gui_log(self, text):
        time_now = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
        self.textBrowserText = self.textBrowserText + str(time_now) + ': ' + text + self.lineend
        self.textBrowser.setText(self.textBrowserText)

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
            self.lineInputPath.setText(file_path[0])

    def getDirPath(self):
        file_path = QFileDialog.getExistingDirectory(self,
                                                     caption='Select GTFS Zip File', )
        if file_path > '':
            self.GTFSInputPath.setText(file_path)

    def getOutputDirPath(self):
        file_path = QFileDialog.getExistingDirectory(self,
                                                     caption='Select GTFS Zip File',
                                                     directory='C:/Tmp')
        if file_path > '':
            self.lineOutputPath.setText(f'{file_path}/')

    def delete_process(self):
        self.sub_write_gui_log("{} finished".format(self.process))
        self.model.gtfs.gtfs_process = None

    def refresh_data(self):
        if (get_current_time() - self.refresh_time) > 10:
            time.sleep(1)
            self.refresh_time = get_current_time()
        self.update_log(("still processing. Please wait...", "{} finished".format(self.process)))


def get_current_time():
    """ Helper function to get the current time in seconds. """

    now = dt.datetime.now()
    total_time = (now.hour * 3600) + (now.minute * 60) + now.second
    return total_time


def main(events, name):
    gtfs_app = QApplication(sys.argv)
    application_window = Gui(events=events, name=name)
    application_window.show()
    gtfs_app.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Gui(events=['update_process', 'toggle_button_direction_event', 'toggle_button_date_week_event'],
                 name='controller')
    app.exec_()
