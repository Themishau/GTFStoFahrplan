import logging
from PySide6.QtCore import Qt, QPoint, QModelIndex
from PySide6.QtWidgets import QMessageBox, QMainWindow, QApplication
from model.Base.Progress import ProgressSignal
from model.Enum.GTFSEnums import CreatePlanMode
from view.Custom.select_table_view import TableModel
from view.Custom.sort_table_view import TableModelSort
from view.pyui.ui_main_window import Ui_MainWindow
from view.view_helpers import get_file_path, get_output_dir_path, get_pickle_save_path, string_to_qdate, update_table_sizes
from view.view_signals import ViewSignals

logger = logging.getLogger(__name__)


class View(QMainWindow):
    def __init__(self, viewModel):
        super().__init__()
        self.oldPos = None
        self.viewModel = viewModel

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.messageBox_model = QMessageBox(self)

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

        self.signals = ViewSignals(self, self.viewModel, parent=self)
        self.signals.connect_signals()
        self.signals.init_signals()

        self.initialize_window()
        self.initialize_tabs()
        self.show_home_window()

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

    def _get_selected_row_index(self, table_view, clicked_index: QModelIndex | None = None):
        if clicked_index is not None and clicked_index.isValid():
            return clicked_index

        selection_model = table_view.selectionModel()
        if selection_model is None:
            return None

        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return None
        return selected_rows[0]

    def get_selected_agency_table_record(self, index: QModelIndex):
        index = self._get_selected_row_index(self.ui.AgenciesTableView, index)
        if index is None:
            return
        logger.debug(f"index {index}")
        id_us = self.ui.AgenciesTableView.model().wholeData(index)
        logger.debug(f"index {id_us["agency_id"]}")
        self.viewModel.view_model_select_data.on_changed_selected_record_agency(id_us)
        self.ui.line_Selection_agency.setText(
            f"selected trips: {self.viewModel.view_model_select_data.get_selected_agency_text()}"
        )
        self.update_time_format(self.viewModel.view_model_import_data.get_time_format())

    def update_create_table(self):
        self.send_message_box(self.viewModel.view_model_create_data.get_success_message())

    def update_file_input_path(self, input_path):
        self.ui.lineInputPath.setText(input_path)

    def update_pickle_file_path(self, pickle_path):
        self.ui.picklesavename.setText(pickle_path)

    def update_output_file_path(self, output_path):
        self.ui.lineOutputPath.setText(output_path)

    def update_pickle_export_checked(self, checked):
        self.ui.checkBox_savepickle.setChecked(checked)

    def update_warning_table_view(self):
        missing_columns_df = self.viewModel.view_model_import_data.get_missing_columns_df()
        self.ui.import_missing_view.setModel(TableModelSort(missing_columns_df))

        if not self.viewModel.view_model_import_data.has_missing_columns():
            self.ui.import_missing_view.setVisible(False)
            self.ui.information_label_label.setVisible(False)
            self.ui.information_missingtext_label.setVisible(False)
            return

        self.ui.import_missing_view.setVisible(True)
        self.ui.information_label_label.setVisible(True)
        self.ui.information_missingtext_label.setVisible(True)
        update_table_sizes(self.ui.import_missing_view)

    def update_time_format(self, time_format):
        self.ui.line_Selection_format.setText(f'time format {time_format}')

    def update_direction_mode(self, mode):
        self.ui.comboBox_direction.setCurrentText(mode)

    def update_create_plan_mode(self, mode):
        self.update_ccreate_table_settings_ui(mode)

    def update_ccreate_table_settings_ui(self, mode):
        self.ui.comboBox.setEnabled(True)
        match mode:
            case CreatePlanMode.umlauf_date.value:
                self.update_to_umlauf_date_mode()
            case CreatePlanMode.umlauf_weekday.value:
                self.update_to_umlauf_weekday_mode()
            case CreatePlanMode.date.value:
                self.update_to_date_mode()
            case CreatePlanMode.weekday.value:
                self.update_to_weekday_mode()

    def update_to_date_mode(self):
        self.update_date_field_to_first_date_of_selected_route(
        self.viewModel.view_model_create_data.get_sample_date())
        self.ui.comboBox_direction.setEnabled(True)
        self.ui.comboBox_direction.setVisible(True)
        self.ui.listDatesWeekday.setEnabled(False)
        self.ui.listDatesWeekday.setVisible(False)
        self.ui.dateEdit.setEnabled(True)
        self.ui.dateEdit.setVisible(True)

    def update_to_weekday_mode(self):
        self.ui.comboBox_direction.setEnabled(True)
        self.ui.comboBox_direction.setVisible(True)
        self.ui.listDatesWeekday.setEnabled(True)
        self.ui.listDatesWeekday.setVisible(True)
        self.ui.dateEdit.setEnabled(False)
        self.ui.dateEdit.setVisible(False)

    def update_to_umlauf_date_mode(self):
        self.update_date_field_to_first_date_of_selected_route(
        self.viewModel.view_model_create_data.get_sample_date())
        self.ui.comboBox_direction.setEnabled(False)
        self.ui.comboBox_direction.setVisible(False)
        self.ui.dateEdit.setEnabled(True)
        self.ui.dateEdit.setVisible(True)

    def update_to_umlauf_weekday_mode(self):
        self.ui.comboBox_direction.setEnabled(False)
        self.ui.comboBox_direction.setVisible(False)
        self.ui.listDatesWeekday.setEnabled(True)
        self.ui.listDatesWeekday.setVisible(True)
        self.ui.dateEdit.setEnabled(False)
        self.ui.dateEdit.setVisible(False)

    def update_create_options_state(self):
        selected_agency_text = self.viewModel.view_model_select_data.get_selected_agency_text()
        if selected_agency_text:
            self.ui.line_Selection_agency.setText(f"selected agency: {selected_agency_text}")
        selected_route_text = self.viewModel.view_model_select_data.get_selected_route_text()
        if selected_route_text:
            self.ui.line_Selection_trips.setText(f"selected Trip: {selected_route_text}")
        return

    def initialize_window(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.oldPos = self.pos()
        self.initialize_objects()

    def initialize_objects(self):
        self.ui.import_missing_view.setVisible(False)
        self.ui.information_label_label.setVisible(False)
        self.ui.information_missingtext_label.setVisible(False)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def center(self):
        qr = self.frameGeometry()
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        cp = screen_geometry.center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_progress(self, progress_data: ProgressSignal):
        self.update_progress_list(progress_data)
        return True

    def update_progress_list(self, progress_data: ProgressSignal):
        self.ui.progress_history_list_view.updateProgress(progress_data)

    def initialize_tabs(self):
        self.ui.main_view_stacked_widget.addWidget(self.ui.create_import_page)
        self.ui.main_view_stacked_widget.addWidget(self.ui.create_select_page)
        self.ui.main_view_stacked_widget.addWidget(self.ui.create_create_page)
        self.ui.main_view_stacked_widget.addWidget(self.ui.download_page)
        self.ui.main_view_stacked_widget.addWidget(self.ui.general_information_page)

    def show_GTFSDownload_window(self):
        self.set_btn_checked(self.downloadGTFSNavPush_btn)
        self.ui.toolBox.setCurrentWidget(self.ui.page_3)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.download_page)

    def show_home_window(self):
        self.set_btn_checked(self.generalNavPush_btn)
        self.ui.toolBox.setCurrentWidget(self.ui.page)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.general_information_page)

    def show_Create_Import_Window(self):
        self.set_btn_checked(self.createTableImport_btn)
        self.ui.toolBox.setCurrentWidget(self.ui.page_2)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.create_import_page)

    def show_Create_Select_Window(self):
        self.set_btn_checked(self.createTableSelect_btn)
        self.ui.toolBox.setCurrentWidget(self.ui.page_2)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.create_select_page)

    def show_Create_Create_Window(self):
        self.set_btn_checked(self.createTableCreate_btn)
        self.ui.toolBox.setCurrentWidget(self.ui.page_2)
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
        self.ui.comboBox_time_format.setEnabled(True)
        self.ui.comboBox_direction.setEnabled(True)
        self.ui.btnStart.setEnabled(True)

    def handle_update_weekdate_option_list(self, event):
        self.initialize_create_base_option()
        self.update_weekday_option_table()

    def initialize_create_view_weekdaydate_option(self):
        self.initialize_create_base_option()
        self.ui.dateEdit.setDate(string_to_qdate(self.viewModel.view_model_import_data.get_sample_date()))
        self.ui.dateEdit.setEnabled(True)
        self.update_weekday_option_table()

    def handle_selected_date(self):
        date = self.ui.dateEdit.date()
        self.viewModel.view_model_create_data.on_changed_selected_dates(date)

    def update_weekday_option_table(self):
        self.ui.listDatesWeekday.setModel(TableModel(self.viewModel.view_model_create_data.weekdays_df))
        update_table_sizes(self.ui.listDatesWeekday)

    def update_routes_list(self):
        self.ui.TripsTableView.setModel(TableModel(self.viewModel.view_model_select_data.get_routes_df()))
        update_table_sizes(self.ui.TripsTableView)


    def update_individualsorting_table(self):
        self.ui.tableView_sorting_stops.setModel(TableModelSort(self.viewModel.view_model_create_data.get_sorting_df()))
        update_table_sizes(self.ui.tableView_sorting_stops)
        self.ui.btnContinueCreate.setEnabled(True)

    def update_agency_list(self):
        self.ui.AgenciesTableView.setModel(TableModel(self.viewModel.view_model_import_data.get_agencies_df()))
        update_table_sizes(self.ui.AgenciesTableView)
        if not self.viewModel.view_model_import_data.has_missing_columns():
            self.show_Create_Select_Window()

        self.update_to_date_mode()

    def update_date_range_based_on_selected_route(self, date_range):
        self.ui.line_Selection_date_range.setText(date_range)

    def update_date_field_to_first_date_of_selected_route(self, sample_date):
        self.ui.dateEdit.setDate(string_to_qdate(sample_date))

    def get_file_path(self):
        self.viewModel.view_model_import_data.on_change_input_file_path(get_file_path(self))

    def get_output_dir_path(self):
        self.viewModel.view_model_import_data.on_change_output_file_path(get_output_dir_path(self))

    def get_pickle_save_path(self):
        self.viewModel.view_model_import_data.on_changed_pickle_path(get_pickle_save_path(self))

    def get_changed_selected_record_trip(self, index: QModelIndex):
        index = self._get_selected_row_index(self.ui.TripsTableView, index)
        if index is None:
            return
        logger.debug(f"index {index}")
        id_us = self.ui.TripsTableView.model().wholeData(index)
        logger.debug(f"id {id_us["route_short_name"]}")
        self.viewModel.view_model_select_data.on_changed_selected_record_trip(id_us)
        self.ui.line_Selection_trips.setText(
            f"selected trips: {self.viewModel.view_model_select_data.get_selected_route_text()}"
        )
        date_range_text = self.viewModel.view_model_select_data.get_selected_route_date_range_text()
        if date_range_text is not None:
            self.update_date_range_based_on_selected_route(date_range_text)
        sample_date = self.viewModel.view_model_select_data.get_selected_route_sample_date()
        if sample_date is not None:
            self.update_date_field_to_first_date_of_selected_route(sample_date)

    def get_changed_selected_weekday(self, index: QModelIndex):
        index = self._get_selected_row_index(self.ui.listDatesWeekday, index)
        if index is None:
            return
        logger.debug(f"index {index}")
        id_us = self.ui.listDatesWeekday.model().wholeData(index)
        logger.debug(f"id {id_us["day"]}")
        self.viewModel.view_model_create_data.on_changed_selected_weekday(id_us)

    def reset_view(self):
        self.ui.btnImport.setEnabled(True)
        self.ui.btnRestart.setEnabled(False)

        self.ui.btnStart.setEnabled(False)
        self.ui.btnContinueCreate.setEnabled(False)
        self.ui.comboBox.setEnabled(False)
        self.ui.comboBox_direction.setEnabled(False)
        self.ui.UseIndividualSorting.setEnabled(False)

        self.ui.listDatesWeekday.clear()
        self.ui.tableView_sorting_stops.clear()
        self.viewModel.reset_schedule_planer()
