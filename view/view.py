import logging
import os
import copy
from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtWidgets import QFileDialog, QMessageBox, QMainWindow, QApplication
from PySide6.QtWidgets import QWidget, QAbstractItemView, QHeaderView
from helpFunctions import string_to_qdate
from model.Base.Progress import ProgressSignal
from model.Enum.GTFSEnums import CreatePlanMode, DfRouteColumnEnum, DfAgencyColumnEnum
from view.Custom.ProgressListView import ProgressHistoryModel, ProgressBarDelegate
from view.Custom.round_progress_bar import RoundProgress
from view.Custom.select_table_view import TableModel
from view.Custom.sort_table_view import TableModelSort
from view.pyui.ui_main_window import Ui_MainWindow

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

# todo: add custom progressUpdated = pyqtSignal(int, str, ProgressBar)
# display it in a list to track all processes (also in parallel)

class View(QMainWindow):
    def __init__(self, viewModel):
        super().__init__()
        self.viewModel = viewModel

        self.progressRound = None
        self.spinner_label = None

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.messageBox_model = QMessageBox()

        self.createTableImport_btn = self.ui.pushButton_2
        self.createTableSelect_btn = self.ui.pushButton_3
        self.createTableCreate_btn = self.ui.pushButton_4
        self.generalNavPush_btn = self.ui.pushButton_5
        self.downloadGTFSNavPush_btn = self.ui.pushButton_6

        self.menu_btns_dict = {self.createTableImport_btn: self.ui.create_import_page,
                               self.createTableSelect_btn: self.ui.create_select_page,
                               self.createTableCreate_btn: self.ui.create_create_page,
                               self.generalNavPush_btn: self.ui.general_information_page,
                               self.downloadGTFSNavPush_btn: self.ui.download_page}

        self.initialize_window()
        self.initialize_modified_progress_bar()
        self.initialize_tabs()
        self.initialize_buttons_links()
        self.init_signals()
        self.ui.toolBox.setCurrentIndex(0)

        self.show_home_window()


    def initialize_buttons_links(self):

        self.ui.AgenciesTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.AgenciesTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.AgenciesTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.ui.progress_history_list_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.progress_history_list_view.setSelectionMode(QAbstractItemView.SingleSelection)

        self.ui.progress_history_list_view.setModel(ProgressHistoryModel())
        self.ui.progress_history_list_view.setItemDelegate(ProgressBarDelegate())

        self.ui.TripsTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.TripsTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.TripsTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.ui.listDatesWeekday.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.listDatesWeekday.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.listDatesWeekday.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.ui.pushButton_2.clicked.connect(self.show_Create_Import_Window)
        self.ui.pushButton_3.clicked.connect(self.show_Create_Select_Window)
        self.ui.pushButton_4.clicked.connect(self.show_Create_Create_Window)
        self.ui.pushButton_5.clicked.connect(self.show_home_window)
        self.ui.pushButton_6.clicked.connect(self.show_GTFSDownload_window)

        self.ui.btnImport.clicked.connect(self.viewModel.start_import_gtfs_data)

        self.viewModel.on_changed_individualsorting_table.connect(self.update_individualsorting_table)

        self.ui.btnRestart.clicked.connect(self.viewModel.restart)

        # view gets updated if view model changed model successfully
        self.ui.btnGetFile.clicked.connect(self.get_file_path)
        self.viewModel.input_file_path.connect(self.update_file_input_path)

        self.ui.btnGetPickleFile.clicked.connect(self.get_pickle_save_path)
        self.viewModel.pickle_file_path.connect(self.update_pickle_file_path)

        self.ui.btnGetOutputDir.clicked.connect(self.get_output_dir_path)
        self.viewModel.output_file_path.connect(self.update_output_file_path)

        self.ui.checkBox_savepickle.clicked.connect(self.viewModel.on_changed_pickle_export_checked)
        self.viewModel.update_pickle_export_checked.connect(self.update_pickle_export_checked)

        #self.ui.comboBox_display.activated[int].connect(self.viewModel.on_changed_time_format_mode)
        self.viewModel.export_plan_time_format.connect(self.update_time_format)

        self.viewModel.update_agency_list.connect(self.update_agency_list)
        self.viewModel.update_routes_list_signal.connect(self.update_routes_list)

        self.ui.AgenciesTableView.clicked.connect(self.get_selected_agency_table_record)
        self.ui.TripsTableView.clicked.connect(self.get_changed_selected_record_trip)
        self.viewModel.update_selected_agency.connect(self.update_selected_agency)

        self.viewModel.update_options_state_signal.connect(self.update_create_options_state)

        self.ui.btnStart.clicked.connect(self.viewModel.start_create_table)
        self.viewModel.create_table_finshed.connect(self.update_create_table)

        self.ui.btnContinueCreate.clicked.connect(self.viewModel.create_table_continue)

        self.ui.btnStop.clicked.connect(self.viewModel.create_table_stop)

        self.ui.UseIndividualSorting.clicked.connect(self.viewModel.on_changed_individualsorting)
        self.viewModel.update_individualsorting.connect(self.update_individualsorting)

        self.ui.listDatesWeekday.clicked.connect(self.get_changed_selected_weekday)

        self.ui.dateEdit.editingFinished.connect(self.handle_selected_date)
        self.viewModel.update_select_data.connect(self.update_select_data)

        self.ui.comboBox.activated[int].connect(self.viewModel.on_changed_create_plan_mode)
        self.viewModel.update_create_plan_mode.connect(self.update_create_plan_mode)

        self.ui.comboBox_direction.activated[int].connect(self.viewModel.on_changed_direction_mode)
        self.viewModel.update_direction_mode.connect(self.update_direction_mode)

        self.viewModel.set_up_create_tab_signal.connect(self.initialize_create_view_weekdaydate_option)

        self.viewModel.update_progress_value.connect(self.update_progress)
        self.viewModel.error_message.connect(self.send_message_box)

    def initialize_busy_inficator(self):
        NotImplemented()

    def update_selected_agency(self, row):
        self.ui.AgenciesTableView.selectRow(row)

    def update_individualsorting(self, checked):
        self.ui.UseIndividualSorting.setChecked(checked)

    def update_select_data(self, data):
        self.ui.dateEdit.setDate(string_to_qdate(data))

    def update_importing_start(self):
        self.ui.create_import_page.ui.btnImport.setEnabled(False)
        self.ui.create_import_page.ui.btnRestart.setEnabled(True)
        self.ui.create_import_page.ui.btnGetFile.setEnabled(False)
        self.ui.create_import_page.ui.btnGetPickleFile.setEnabled(False)
        self.ui.create_import_page.ui.btnGetOutputDir.setEnabled(False)
        self.ui.create_import_page.ui.checkBox_savepickle.setEnabled(False)

    def get_selected_agency_table_record(self):
        index = self.ui.AgenciesTableView.selectedIndexes()[0]
        logging.debug(f"index {index}")
        id_us = self.ui.AgenciesTableView.model().wholeData(index)
        logging.debug(f"index {id_us["agency_id"]}")
        self.viewModel.on_changed_selected_record_agency(id_us)

    def update_create_table(self):
        self.send_message_box(
            f"Success. Create table successfully. Saved here: {self.viewModel.model.planer.export_plan.full_output_path}")

    def update_file_input_path(self, input_path):
        self.ui.lineInputPath.setText(input_path)

    def update_pickle_file_path(self, pickle_path):
        self.ui.picklesavename.setText(pickle_path)

    def update_output_file_path(self, output_path):
        self.ui.lineOutputPath.setText(output_path)

    def update_pickle_export_checked(self, checked):
        self.ui.checkBox_savepickle.setChecked(checked)

    def update_time_format(self, time_format):
        self.ui.line_Selection_format.setText(time_format)

    def update_time_format_based_on_dto(self):
        self.ui.line_Selection_format.setText(
            f'time format {self.viewModel.model.planer.create_settings_for_table_dto.timeformat}')

    def update_direction_mode(self, mode):
        self.ui.comboBox_direction.setCurrentText(mode)

    def update_create_plan_mode(self, mode):
        #self.ui.comboBox.setCurrentText(mode)
        if mode == CreatePlanMode.date.value:
            self.ui.dateEdit.setDate(
                string_to_qdate(self.viewModel.model.planer.analyze_data.sample_date))
            self.ui.dateEdit.setEnabled(True)
            self.ui.listDatesWeekday.setEnabled(False)
        elif mode == CreatePlanMode.weekday.value:
            self.ui.dateEdit.setEnabled(False)
            self.ui.listDatesWeekday.setEnabled(True)
        elif mode == CreatePlanMode.umlauf_date.value:
            self.ui.dateEdit.setDate(
                string_to_qdate(self.viewModel.model.planer.analyze_data.sample_date))
            self.ui.dateEdit.setEnabled(True)
            self.ui.listDatesWeekday.setEnabled(False)
            self.ui.comboBox_direction.setEnabled(False)
        elif mode == CreatePlanMode.umlauf_weekday.value:
            self.ui.dateEdit.setEnabled(False)
            self.ui.listDatesWeekday.setEnabled(True)
            self.ui.comboBox_direction.setEnabled(False)

    def update_create_options_state(self):
        self.ui.line_Selection_agency.setText(
            f"selected agency: {self.viewModel.model.planer.create_settings_for_table_dto.agency[DfAgencyColumnEnum.agency_name.value].iloc[0]}")
        self.ui.line_Selection_trips.setText(
            f"selected Trip: {self.viewModel.model.planer.create_settings_for_table_dto.route[DfRouteColumnEnum.route_short_name.value].iloc[0]}")
        self.update_time_format_based_on_dto()

    def initialize_window(self):
        self.setFixedSize(1920, 1080)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.center()
        self.oldPos = self.pos()

    def init_signals(self):
        #self.ui.create_import_page.ui.comboBox_display.activated[int].connect(self.viewModel.export_plan_time_format.emit)
        self.ui.lineInputPath.textChanged.connect(self.viewModel.input_file_path.emit)
        self.ui.lineOutputPath.textChanged.connect(self.viewModel.output_file_path.emit)
        self.ui.picklesavename.textChanged.connect(self.viewModel.pickle_file_path.emit)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def center(self):
        qr = self.frameGeometry()
        screen = QApplication.primaryScreen()  # Get the primary screen
        screen_geometry = screen.availableGeometry()  # Retrieve available screen geometry
        cp = screen_geometry.center()  # Get the center point of the screen
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_progress(self, progress_data: ProgressSignal):
        self.update_progress_bar(progress_data.value)
        self.update_progress_list(progress_data)
        return True

    def update_progress_list(self, progress_data: ProgressSignal):
        self.ui.progress_history_list_view.updateProgress(progress_data)

    def update_progress_bar(self, value: int):
        self.ui.progressBar.set_value(value)
        return True

    def initialize_modified_progress_bar(self):
        # add the modified progress ui element
        self.ui.progressBar = RoundProgress()
        self.ui.progressBar.value = 0
        self.ui.progressBar.setMinimumSize(self.ui.progressBar.width, self.ui.progressBar.height)
        #self.ui.progress_widget.addWidget(self.ui.label_progress, 0, 1, 1, 1, Qt.AlignHCenter | Qt.AlignVCenter)
        self.ui.progress_widget.addWidget(self.ui.progressBar, 1, 1, 1, 1, Qt.AlignHCenter | Qt.AlignVCenter)


    def initialize_tabs(self):
        self.ui.main_view_stacked_widget.addWidget(self.ui.create_import_page)
        self.ui.main_view_stacked_widget.addWidget(self.ui.create_select_page)
        self.ui.main_view_stacked_widget.addWidget(self.ui.create_create_page)
        self.ui.main_view_stacked_widget.addWidget(self.ui.download_page)
        self.ui.main_view_stacked_widget.addWidget(self.ui.general_information_page)

    def show_GTFSDownload_window(self):
        self.set_btn_checked(self.downloadGTFSNavPush_btn)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.download_page)

    def show_home_window(self):
        self.set_btn_checked(self.generalNavPush_btn)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.general_information_page)


    def show_Create_Import_Window(self):
        self.set_btn_checked(self.createTableImport_btn)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.create_import_page)
        #self.ui.main_view_stacked_widget.resize(1100, 900)

    def show_Create_Select_Window(self):
        self.set_btn_checked(self.createTableSelect_btn)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.create_select_page)

    def show_Create_Create_Window(self):
        self.set_btn_checked(self.createTableCreate_btn)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.create_create_page)

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
        self.ui.comboBox.setEnabled(True)
        #self.ui.comboBox_display.setEnabled(True)
        self.ui.comboBox_direction.setEnabled(True)
        self.ui.btnStart.setEnabled(True)

    def handle_update_weekdate_option_list(self, event):
        self.initialize_create_base_option()
        self.update_weekday_option_table()

    def initialize_create_view_weekdaydate_option(self):
        self.initialize_create_base_option()
        self.ui.dateEdit.setDate(string_to_qdate(self.viewModel.model.planer.analyze_data.sample_date))
        self.ui.dateEdit.setEnabled(True)
        self.update_weekday_option_table()

    def handle_selected_date(self):
        date = self.ui.dateEdit.date()
        self.viewModel.on_changed_selected_dates(date)

    def reset_weekdayDate(self):
        self.ui.comboBox.setEnabled(False)
        #self.ui.comboBox_display.setEnabled(True)
        self.ui.comboBox_direction.setEnabled(False)
        self.ui.dateEdit.setEnabled(False)

    def update_weekday_option_table(self, ):
        self.ui.listDatesWeekday.setModel(TableModel(self.viewModel.model.planer.create_plan.weekdays_df))

    def update_routes_list(self):
        self.ui.TripsTableView.setModel(
            TableModel(self.viewModel.model.planer.select_data.df_selected_routes))

    def update_individualsorting_table(self):
        self.ui.tableView_sorting_stops.setModel(
            TableModelSort(self.viewModel.model.planer.create_plan.strategy.plans.create_dataframe.FilteredStopNamesDataframe))
        self.ui.btnContinueCreate.setEnabled(True)
        # self.CreateCreate_Tab.ui.tableView_sorting_stops.populate()

    def update_agency_list(self):
        self.ui.AgenciesTableView.setModel(
            TableModel(self.viewModel.model.planer.select_data.gtfs_data_frame_dto.Agencies))
        self.ui.line_Selection_date_range.setText(self.viewModel.model.planer.analyze_data.date_range)
        self.ui.dateEdit.setDate(string_to_qdate(self.viewModel.model.planer.analyze_data.sample_date))
        self.show_Create_Select_Window()
        # self.model.start_get_date_range()
        logging.debug("done with creating dfs")
        # self.model.gtfs.save_h5(h5_filename="C:/Tmp/test.h5", data=self.model.gtfs.dfTrips, labels="trips")

    def get_file_path(self):
        try:
            input_file_path = QFileDialog.getOpenFileName(parent=self,
                                                          caption='Select GTFS Zip File',
                                                          dir='C:/Tmp',
                                                          filter='Zip File (*.zip)',
                                                          selectedFilter='Zip File (*.zip)')

        except:
            input_file_path = QFileDialog.getOpenFileName(parent=self,
                                                          caption='Select GTFS Zip File',
                                                          dir=os.getcwd(),
                                                          filter='Zip File (*.zip)',
                                                          selectedFilter='Zip File (*.zip)')
        if input_file_path[0] > '':
            self.viewModel.on_change_input_file_path(input_file_path)

    def get_output_dir_path(self):
        output_file_path = QFileDialog.getExistingDirectory(self,
                                                            caption='Select GTFS Zip File',
                                                            dir='C:/Tmp')
        if output_file_path > '':
            self.viewModel.on_change_output_file_path(output_file_path)

    def get_pickle_save_path(self):
        try:
            pickle_file_path = QFileDialog.getSaveFileName(parent=self,
                                                           caption='Select GTFS Zip File',
                                                           dir='C:/Tmp',
                                                           filter='Zip File (*.zip)',
                                                           selectedFilter='Zip File (*.zip)')

        except:
            pickle_file_path = QFileDialog.getSaveFileName(parent=self,
                                                           caption='Select GTFS Zip File',
                                                           dir=os.getcwd(),
                                                           filter='Zip File (*.zip)',
                                                           selectedFilter='Zip File (*.zip)')
        if pickle_file_path[0] > '':
            self.viewModel.on_changed_pickle_path(pickle_file_path)

    def get_changed_selected_record_trip(self):
        index = self.ui.TripsTableView.selectedIndexes()[2]
        logging.debug(f"index {index}")
        id_us = self.ui.TripsTableView.model().wholeData(index)
        logging.debug(f"id {id_us["route_short_name"]}")
        self.viewModel.on_changed_selected_record_trip(id_us)

    def get_changed_selected_weekday(self):
        index = self.ui.listDatesWeekday.selectedIndexes()[0]
        logging.debug(f"index {index}")
        id_us = self.ui.listDatesWeekday.model().wholeData(index)
        logging.debug(f"id {id_us["day"]}")
        self.viewModel.on_changed_selected_weekday(id_us)

    def reset_view(self):
        self.ui.btnImport.setEnabled(True)
        self.ui.btnRestart.setEnabled(False)
        #self.ui.comboBox_display.setEnabled(True)

        self.ui.btnStart.setEnabled(False)
        self.ui.btnContinueCreate.setEnabled(False)
        self.ui.comboBox.setEnabled(False)
        self.ui.comboBox_direction.setEnabled(False)
        self.ui.UseIndividualSorting.setEnabled(False)

        self.ui.listDatesWeekday.clear()
        self.ui.tableView_sorting_stops.clear()
        self.viewModel.model.planer.initilize_scheduler()
