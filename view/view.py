import logging
import os
from PyQt5 import QtCore
from PyQt5.Qt import QPoint, QMessageBox, QDesktopWidget, QMainWindow
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QFileDialog

from helpFunctions import string_to_qdate
from .round_progress_bar import RoundProgress
from .pyui.main_window_ui import Ui_MainWindow
from .general_window_information import GeneralInformation
from .create_table_create import CreateTableCreate
from .create_table_import import CreateTableImport
from .create_table_select import CreateTableSelect
from .download_gtfs import DownloadGTFS
from .select_table_view import TableModel
from .sort_table_view import TableModelSort
from model.Base.GTFSEnums import *

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class View(QMainWindow):
    def __init__(self, viewModel):
        super().__init__()
        self.viewModel = viewModel

        self.progressRound = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.messageBox_model = QMessageBox()

        self.CreateMainTab = GeneralInformation()
        self.CreateImport_Tab = CreateTableImport()
        self.CreateSelect_Tab = CreateTableSelect()
        self.CreateCreate_Tab = CreateTableCreate()
        self.DownloadGTFS_Tab = DownloadGTFS()
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

        self.ui.pushButton_2.clicked.connect(self.show_Create_Import_Window)
        self.ui.pushButton_3.clicked.connect(self.show_Create_Select_Window)
        self.ui.pushButton_4.clicked.connect(self.show_Create_Create_Window)
        self.ui.pushButton_5.clicked.connect(self.show_home_window)
        self.ui.pushButton_6.clicked.connect(self.show_GTFSDownload_window)

        self.CreateImport_Tab.ui.btnImport.clicked.connect(self.viewModel.start_import_gtfs_data)

        self.viewModel.on_changed_individualsorting_table.connect(self.update_individualsorting_table)

        self.CreateImport_Tab.ui.btnRestart.clicked.connect(self.viewModel.restart)

        # view gets updated if view model changed model successfully
        self.CreateImport_Tab.ui.btnGetFile.clicked.connect(self.get_file_path)
        self.viewModel.input_file_path.connect(self.update_file_input_path)

        self.CreateImport_Tab.ui.btnGetPickleFile.clicked.connect(self.get_pickle_save_path)
        self.viewModel.pickle_file_path.connect(self.update_pickle_file_path)

        self.CreateImport_Tab.ui.btnGetOutputDir.clicked.connect(self.get_output_dir_path)
        self.viewModel.output_file_path.connect(self.update_output_file_path)

        self.CreateImport_Tab.ui.checkBox_savepickle.clicked.connect(self.viewModel.on_changed_pickle_export_checked)
        self.viewModel.update_pickle_export_checked.connect(self.update_pickle_export_checked)

        self.CreateImport_Tab.ui.comboBox_display.activated[str].connect(self.viewModel.on_changed_time_format_mode)
        self.viewModel.export_plan_time_format.connect(self.update_time_format)

        self.viewModel.update_agency_list.connect(self.update_agency_list)
        self.viewModel.update_routes_list_signal.connect(self.update_routes_list)

        self.CreateSelect_Tab.ui.AgenciesTableView.clicked.connect(self.get_selected_agency_table_record)
        self.viewModel.update_selected_agency.connect(self.update_selected_agency)

        self.CreateSelect_Tab.ui.TripsTableView.clicked.connect(self.get_changed_selected_record_trip)
        self.viewModel.update_options_state_signal.connect(self.update_create_options_state)

        self.CreateCreate_Tab.ui.btnStart.clicked.connect(self.viewModel.start_create_table)
        self.viewModel.create_table_finshed.connect(self.update_create_table)

        self.CreateCreate_Tab.ui.btnContinueCreate.clicked.connect(self.viewModel.create_table_continue)

        self.CreateCreate_Tab.ui.UseIndividualSorting.clicked.connect(self.viewModel.on_changed_individualsorting)
        self.viewModel.update_individualsorting.connect(self.update_individualsorting)

        self.CreateCreate_Tab.ui.listDatesWeekday.clicked.connect(self.get_selected_weekday)

        self.CreateCreate_Tab.ui.dateEdit.editingFinished.connect(self.handle_selected_date)
        self.viewModel.update_select_data.connect(self.update_select_data)

        self.CreateCreate_Tab.ui.comboBox.activated[str].connect(self.viewModel.on_changed_create_plan_mode)
        self.viewModel.update_create_plan_mode.connect(self.update_create_plan_mode)

        self.CreateCreate_Tab.ui.comboBox_direction.activated[str].connect(self.viewModel.on_changed_direction_mode)
        self.viewModel.update_direction_mode.connect(self.update_direction_mode)

        self.viewModel.set_up_create_tab_signal.connect(self.initialize_create_view_weekdaydate_option)

        self.viewModel.update_progress_value.connect(self.update_progress_bar)
        self.viewModel.error_message.connect(self.send_message_box)

    def update_selected_agency(self, row):
        self.CreateSelect_Tab.ui.AgenciesTableView.selectRow(row)

    def update_individualsorting(self, checked):
        self.CreateCreate_Tab.ui.UseIndividualSorting.setChecked(checked)

    def update_select_data(self, data):
        self.CreateCreate_Tab.ui.dateEdit.setDate(string_to_qdate(data))

    def update_importing_start(self):
        self.CreateImport_Tab.ui.btnImport.setEnabled(False)
        self.CreateImport_Tab.ui.btnRestart.setEnabled(True)
        self.CreateImport_Tab.ui.btnGetFile.setEnabled(False)
        self.CreateImport_Tab.ui.btnGetPickleFile.setEnabled(False)
        self.CreateImport_Tab.ui.btnGetOutputDir.setEnabled(False)
        self.CreateImport_Tab.ui.checkBox_savepickle.setEnabled(False)

    def get_selected_agency_table_record(self):
        index = self.CreateSelect_Tab.ui.AgenciesTableView.selectedIndexes()[0]
        logging.debug(f"index {index}")
        id_us = self.CreateSelect_Tab.ui.AgenciesTableView.model().data(index)
        logging.debug(f"index {id_us}")
        self.viewModel.on_changed_selected_record_agency(id_us)

    def update_create_table(self):
        self.send_message_box(f"Success. Create table successfully. Saved here: {self.viewModel.model.planer.export_plan.output_path}")

    def update_file_input_path(self, input_path):
        self.CreateImport_Tab.ui.lineInputPath.setText(input_path)

    def update_pickle_file_path(self, pickle_path):
        self.CreateImport_Tab.ui.picklesavename.setText(pickle_path)

    def update_output_file_path(self, output_path):
        self.CreateImport_Tab.ui.lineOutputPath.setText(output_path)

    def update_pickle_export_checked(self, checked):
        self.CreateImport_Tab.ui.checkBox_savepickle.setChecked(checked)

    def update_time_format(self, time_format):
        self.CreateCreate_Tab.ui.line_Selection_format.setText(time_format)
    def update_time_format_based_on_dto(self):
            self.CreateCreate_Tab.ui.line_Selection_format.setText(f'time format {self.viewModel.model.planer.create_settings_for_table_dto.timeformat}')

    def update_direction_mode(self, mode):
        self.CreateCreate_Tab.ui.comboBox_direction.setCurrentText(mode)

    def update_create_plan_mode(self, mode):
        self.CreateCreate_Tab.ui.comboBox.setCurrentText(mode)
        if mode == 'date':
            self.CreateCreate_Tab.ui.listDatesWeekday.clear()
            self.CreateCreate_Tab.ui.dateEdit.setDate(string_to_qdate(self.viewModel.model.planer.analyze_data.sample_date))
            self.CreateCreate_Tab.ui.dateEdit.setEnabled(True)
            self.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(False)
        elif mode == 'weekday':
            self.CreateCreate_Tab.ui.listDatesWeekday.addItems(
                self.viewModel.model.planer.select_data.week_day_options_list)
            self.CreateCreate_Tab.ui.dateEdit.setEnabled(False)
            self.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(True)

    def update_create_options_state(self):
        self.CreateCreate_Tab.ui.line_Selection_agency.setText(f"selected agency: {self.viewModel.model.planer.create_settings_for_table_dto.agency}")
        self.CreateCreate_Tab.ui.line_Selection_trips.setText(f"selected Trip: {self.viewModel.model.planer.create_settings_for_table_dto.route}")
        self.update_time_format_based_on_dto()



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

    def update_progress_bar(self, value):
        self.progressRound.set_value(value)
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
        self.ui.stackedWidget.resize(1100, 900)

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
    def send_message_box(self, text):
        self.messageBox_model.setStandardButtons(QMessageBox.Ok)
        self.messageBox_model.setText(text)
        self.messageBox_model.exec_()

    def initialize_create_base_option(self):
        self.CreateCreate_Tab.ui.comboBox.setEnabled(True)
        self.CreateImport_Tab.ui.comboBox_display.setEnabled(True)
        self.CreateCreate_Tab.ui.comboBox_direction.setEnabled(True)
        self.CreateCreate_Tab.ui.btnStart.setEnabled(True)

    def handle_update_weekdate_option_list(self, event):
        self.initialize_create_base_option()
        self.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(True)
        self.sub_update_weekday_list()

    def initialize_create_view_weekdaydate_option(self):
        self.initialize_create_base_option()
        self.CreateCreate_Tab.ui.listDatesWeekday.clear()
        self.CreateCreate_Tab.ui.dateEdit.setDate(string_to_qdate(self.viewModel.model.planer.analyze_data.sample_date))
        self.CreateCreate_Tab.ui.dateEdit.setEnabled(True)
        self.CreateCreate_Tab.ui.listDatesWeekday.setEnabled(False)
        self.CreateCreate_Tab.ui.listDatesWeekday.addItems(self.viewModel.model.planer.select_data.week_day_options_list)

    def get_selected_weekday(self):
        self.viewModel.select_weekday_option(self.CreateCreate_Tab.ui.listDatesWeekday.currentItem().text().split(',')[0])

    def handle_selected_date(self):
        date = self.CreateCreate_Tab.ui.dateEdit.date()
        self.viewModel.on_changed_selected_dates(date)

    def reset_weekdayDate(self):
        self.CreateCreate_Tab.ui.comboBox.setEnabled(False)
        self.CreateImport_Tab.ui.comboBox_display.setEnabled(True)
        self.CreateCreate_Tab.ui.comboBox_direction.setEnabled(False)
        self.CreateCreate_Tab.ui.dateEdit.setEnabled(False)
        self.CreateCreate_Tab.ui.listDatesWeekday.clear()

    def sub_update_weekday_list(self, ):
        self.CreateCreate_Tab.ui.listDatesWeekday.clear()
        self.CreateCreate_Tab.ui.listDatesWeekday.addItems(self.viewModel.model.planer.select_data.week_day_options_list)

    def update_routes_list(self):
        self.CreateSelect_Tab.ui.TripsTableView.setModel(TableModel(self.viewModel.model.planer.select_data.df_selected_routes))

    def update_individualsorting_table(self):
        self.CreateCreate_Tab.ui.tableView_sorting_stops.setModel(
            TableModelSort(self.viewModel.model.planer.create_plan.create_dataframe.FilteredStopNamesDataframe))
        self.CreateCreate_Tab.ui.btnContinueCreate.setEnabled(True)
        # self.CreateCreate_Tab.ui.tableView_sorting_stops.populate()

    def update_agency_list(self):
        self.CreateSelect_Tab.ui.AgenciesTableView.setModel(
            TableModel(self.viewModel.model.planer.select_data.gtfs_data_frame_dto.Agencies))
        self.CreateCreate_Tab.ui.line_Selection_date_range.setText(self.viewModel.model.planer.analyze_data.date_range)
        self.CreateCreate_Tab.ui.dateEdit.setDate(string_to_qdate(self.viewModel.model.planer.analyze_data.sample_date))
        self.show_Create_Select_Window()
        # self.model.start_get_date_range()
        logging.debug("done with creating dfs")
        # self.model.gtfs.save_h5(h5_filename="C:/Tmp/test.h5", data=self.model.gtfs.dfTrips, labels="trips")



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
            self.viewModel.on_change_input_file_path(input_file_path)

    def get_output_dir_path(self):
        output_file_path = QFileDialog.getExistingDirectory(self,
                                                            caption='Select GTFS Zip File',
                                                            directory='C:/Tmp')
        if output_file_path > '':
            self.viewModel.on_change_output_file_path(output_file_path)

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
            self.viewModel.on_changed_pickle_path(pickle_file_path)

    def get_changed_selected_record_trip(self):
        index = self.CreateSelect_Tab.ui.TripsTableView.selectedIndexes()[2]
        logging.debug(f"index {index}")
        id_us = self.CreateSelect_Tab.ui.TripsTableView.model().data(index)
        logging.debug(f"id {id_us}")
        self.viewModel.on_changed_selected_record_trip(id_us)

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

