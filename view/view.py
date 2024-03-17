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
from model.model import Model

# from model.Base.gtfs import gtfs
from model.SchedulePlaner.SchedulePlaner import SchedulePlaner
from model.observer import Publisher, Subscriber


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
        self.CreateImport_Tab.ui.btnRestart.clicked.connect(self.viewModel.restart)

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

        self.CreateCreate_Tab.ui.comboBox.activated[str].connect(self.viewModel.onChangedCreatePlanMode)
        self.viewModel.update_create_plan_mode.connect(self.update_create_plan_mode)

        self.CreateCreate_Tab.ui.comboBox_direction.activated[str].connect(self.viewModel.onChangedDirectionMode)
        self.viewModel.update_direction_mode.connect(self.update_direction_mode)

    def update_file_input_path(self, input_path):
        self.CreateImport_Tab.ui.lineInputPath.setText(input_path)

    def update_pickle_file_path(self, pickle_path):
        self.CreateImport_Tab.ui.picklesavename.setText(pickle_path)

    def update_output_file_path(self, output_path):
        self.CreateImport_Tab.ui.lineOutputPath.setText(output_path)

    def update_time_format(self, time_format):
        self.CreateCreate_Tab.ui.line_Selection_format.setText(time_format)

    def update_direction_mode(self, mode):
        self.CreateCreate_Tab.ui.comboBox_direction.setCurrentText(mode)

    def update_create_plan_mode(self, mode):
        self.CreateCreate_Tab.ui.comboBox_mode.setCurrentText(mode)
        if mode == 'date':
            self.CreateCreate_Tab.ui.listDatesWeekday.clear()
            self.CreateCreate_Tab.ui.lineDateInput.setText(self.viewModel.model.planer.select_data.date_range)
            self.CreateCreate_Tab.ui.lineDateInput.setEnabled(True)
            self.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(False)
        elif mode == 'weekday':
            self.CreateCreate_Tab.ui.listDatesWeekday.addItems(self.viewModel.model.planer.select_data.week_day_options_list)
            self.CreateCreate_Tab.ui.lineDateInput.clear()
            self.CreateCreate_Tab.ui.lineDateInput.setEnabled(False)
            self.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(True)

    def initialize_window(self):
        self.setFixedSize(1350, 900)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.center()
        self.oldPos = self.pos()

    def init_signals(self):
        self.CreateImport_Tab.ui.comboBox_display.activated[str].connect(self.viewModel.export_plan_time_format.emit)
        self.CreateImport_Tab.ui.lineInputPath.textChanged.connect(self.viewModel.input_file_path.emit)
        self.CreateImport_Tab.ui.lineOutputPath.textChanged.connect(self.viewModel.output_file_path.emit)
        self.CreateImport_Tab.ui.picklesavename.textChanged.connect(self.viewModel.pickle_file_path.emit)

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
            self.viewModel.onChangeInputFilePath(input_file_path)

    def get_output_dir_path(self):
        output_file_path = QFileDialog.getExistingDirectory(self,
                                                            caption='Select GTFS Zip File',
                                                            directory='C:/Tmp')
        if output_file_path > '':
            self.viewModel.onChangeOutputFilePath(output_file_path)

    def get_pickle_save_path(self):
        try:
            pickle_file_path = QFileDialog.getSaveFileName(parent=self,
                                                           caption='Select GTFS Zip File',
                                                           directory='C:/Tmp',
                                                           filter='Zip File (*.zip)',
                                                           initialFilter='Zip File (*.zip)')

        except:
            pickle_file_path = QFileDialog.getSaveFileName(parent=self,
                                                           caption='Select GTFS Zip File',
                                                           directory=os.getcwd(),
                                                           filter='Zip File (*.zip)',
                                                           initialFilter='Zip File (*.zip)')
        if pickle_file_path[0] > '':
            self.viewModel.onChangePickleFilePath(pickle_file_path)

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