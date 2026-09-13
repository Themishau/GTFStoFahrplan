import logging

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox

from model.enums import PlanMode
from model.planning.progress import ProgressUpdate
from view.pyui.ui_main_window import Ui_MainWindow
from view.signal_binder import ViewSignalBinder
from view.widgets.data_frame_table_model import DataFrameTableModel
from view.widgets.sortable_data_frame_table_model import SortableDataFrameTableModel
from view.view_helpers import (
    select_gtfs_zip,
    select_output_directory,
    string_to_qdate,
    update_table_sizes,
)

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, view_model):
        super().__init__()
        self.drag_position = None
        self.view_model = view_model

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.message_box = QMessageBox(self)

        self.import_nav_button = self.ui.pushButton_2
        self.selection_nav_button = self.ui.pushButton_3
        self.create_nav_button = self.ui.pushButton_4
        self.general_nav_button = self.ui.pushButton_5
        self.download_nav_button = self.ui.pushButton_6

        self.navigation_pages = {self.import_nav_button: self.ui.create_import_page,
                                 self.selection_nav_button: self.ui.create_select_page,
                                 self.create_nav_button: self.ui.create_create_page,
                                 self.general_nav_button: self.ui.general_information_page,
                                 self.download_nav_button: self.ui.download_page}

        self.signal_binder = ViewSignalBinder(self, self.view_model, parent=self)
        self.signal_binder.connect_signals()

        self._initialize_window()
        self._initialize_tabs()
        self.initialize_recent_feeds()
        self.show_home_window()

    def initialize_recent_feeds(self):
        vm = self.view_model.import_view_model
        self._cache_busy = False
        self._closing_after_worker = False
        self.recent_feeds_combo = self.ui.recent_feeds_combo
        self.recent_feed_details = self.ui.recent_feed_details
        self.open_feed_button = self.ui.open_feed_button
        self.delete_feed_button = self.ui.delete_feed_button
        self.delete_all_feeds_button = self.ui.delete_all_feeds_button
        self.cache_size_label = self.ui.cache_size_label
        self.open_feed_button.clicked.connect(lambda: vm.open_feed(self.recent_feeds_combo.currentData()))
        self.delete_feed_button.clicked.connect(lambda: vm.delete_feed(self.recent_feeds_combo.currentData()))
        self.delete_all_feeds_button.clicked.connect(self.confirm_delete_all_feeds)
        self.recent_feeds_combo.currentIndexChanged.connect(self.update_recent_feed_details)
        vm.recent_feeds_changed.connect(self.refresh_recent_feeds)
        vm.busy_changed.connect(self.set_worker_busy)
        vm.feed_cleared.connect(self.clear_active_feed)
        self.ui.btnRestart.clicked.connect(self.view_model.model.cancel_current_action)
        settings = self.view_model.model.cache_service.settings
        self.show_output_path(settings.default_export_path)
        self.ui.comboBox_time_format.setCurrentIndex(0 if settings.time_format == 'HH:mm' else 1)
        self.refresh_recent_feeds()
        self.ui.btnStart.setEnabled(False)

    def refresh_recent_feeds(self):
        vm = self.view_model.import_view_model
        selected = vm.last_feed_id or self.recent_feeds_combo.currentData()
        self.recent_feeds_combo.blockSignals(True)
        self.recent_feeds_combo.clear()
        for feed in vm.recent_feeds:
            metadata = feed.metadata
            self.recent_feeds_combo.addItem(metadata.feed_publisher_name or metadata.source_filename, feed.feed_id)
        index = self.recent_feeds_combo.findData(selected)
        if index >= 0:
            self.recent_feeds_combo.setCurrentIndex(index)
        self.recent_feeds_combo.blockSignals(False)
        self.update_recent_feed_details()

    def update_recent_feed_details(self):
        vm = self.view_model.import_view_model
        feed_id = self.recent_feeds_combo.currentData()
        feed = next((item for item in vm.recent_feeds if item.feed_id == feed_id), None)
        text = 'No cached feeds yet.'
        if feed:
            metadata = feed.metadata
            text = (f'{metadata.source_filename}\n'
                    f'{metadata.feed_start_date or "?"} – {metadata.feed_end_date or "?"}\n'
                    f'Imported: {metadata.imported_at.astimezone():%d.%m.%Y %H:%M}')
            if not vm.can_open_feed(feed_id):
                text += '\nRe-import the ZIP to update this cached feed.'
        self.recent_feed_details.setText(text)
        self.open_feed_button.setEnabled(not self._cache_busy and vm.can_open_feed(feed_id))
        self.delete_feed_button.setEnabled(not self._cache_busy and feed is not None)
        self.delete_all_feeds_button.setEnabled(not self._cache_busy and bool(vm.recent_feeds))
        self.cache_size_label.setText(f'DuckDB storage: {vm.get_database_size_text()}')

    def confirm_delete_all_feeds(self):
        answer = QMessageBox.question(
            self,
            'Delete all cached GTFS data?',
            'Delete every cached GTFS feed from DuckDB? This cannot be undone.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.view_model.import_view_model.delete_all_feeds()

    def set_worker_busy(self, busy):
        self._cache_busy = busy
        for widget in (self.ui.btnImport, self.ui.btnGetFile, self.ui.btnGetOutputDir,
                       self.recent_feeds_combo, self.ui.create_select_page, self.ui.create_create_page):
            widget.setEnabled(not busy)
        self.ui.btnRestart.setEnabled(busy)
        self.update_recent_feed_details()

    def clear_active_feed(self):
        self.ui.AgenciesTableView.setModel(None)
        self.ui.TripsTableView.setModel(None)
        self.ui.tableView_sorting_stops.setModel(None)
        self.ui.btnStart.setEnabled(False)
        self.ui.btnContinueCreate.setEnabled(False)
        self.ui.line_Selection_agency.clear()
        self.ui.line_Selection_trips.clear()
        self.ui.line_Selection_date_range.clear()

    def closeEvent(self, event):
        model = self.view_model.model
        if model.thread is not None:
            event.ignore()
            if not self._closing_after_worker:
                self._closing_after_worker = True
                model.thread.finished.connect(self.close)
                model.cancel_current_action()
            return
        super().closeEvent(event)

    def update_individual_sorting(self, checked):
        self.ui.UseIndividualSorting.setChecked(checked)

    def update_selected_date(self, data):
        self.ui.dateEdit.setDate(string_to_qdate(data))

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

    def select_agency(self, index: QModelIndex):
        index = self._get_selected_row_index(self.ui.AgenciesTableView, index)
        if index is None:
            return
        agency = self.ui.AgenciesTableView.model().row_data(index)
        logger.debug("Selected agency: %s", agency["agency_id"].iloc[0])
        self.view_model.selection_view_model.select_agency(agency)
        self.ui.line_Selection_agency.setText(
            f"selected trips: {self.view_model.selection_view_model.get_selected_agency_text()}"
        )
        self.update_time_format(self.view_model.import_view_model.get_time_format())

    def show_timetable_created(self):
        self.show_message(self.view_model.create_view_model.get_success_message())

    def show_input_path(self, input_path):
        self.ui.lineInputPath.setText(input_path)

    def show_output_path(self, output_path):
        self.ui.lineOutputPath.setText(output_path)

    def update_missing_columns(self):
        missing_columns_df = self.view_model.import_view_model.get_missing_columns_df()
        self.ui.import_missing_view.setModel(SortableDataFrameTableModel(missing_columns_df))

        if not self.view_model.import_view_model.has_missing_columns():
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

    def update_planning_mode(self, mode):
        self.update_planning_mode_controls(mode)

    def update_planning_mode_controls(self, mode):
        self.ui.comboBox.setEnabled(True)
        match mode:
            case PlanMode.CIRCULATION_DATE.value:
                self.update_to_circulation_date_mode()
            case PlanMode.CIRCULATION_WEEKDAY.value:
                self.update_to_circulation_weekday_mode()
            case PlanMode.DATE.value:
                self.update_to_date_mode()
            case PlanMode.WEEKDAY.value:
                self.update_to_weekday_mode()

    def update_to_date_mode(self):
        self.show_selected_route_sample_date(
            self.view_model.create_view_model.get_sample_date())
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

    def update_to_circulation_date_mode(self):
        self.show_selected_route_sample_date(
            self.view_model.create_view_model.get_sample_date())
        self.ui.comboBox_direction.setEnabled(False)
        self.ui.comboBox_direction.setVisible(False)
        self.ui.dateEdit.setEnabled(True)
        self.ui.dateEdit.setVisible(True)

    def update_to_circulation_weekday_mode(self):
        self.ui.comboBox_direction.setEnabled(False)
        self.ui.comboBox_direction.setVisible(False)
        self.ui.listDatesWeekday.setEnabled(True)
        self.ui.listDatesWeekday.setVisible(True)
        self.ui.dateEdit.setEnabled(False)
        self.ui.dateEdit.setVisible(False)

    def _initialize_window(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.drag_position = self.pos()
        self._initialize_widgets()

    def _initialize_widgets(self):
        self.ui.import_missing_view.setVisible(False)
        self.ui.information_label_label.setVisible(False)
        self.ui.information_missingtext_label.setVisible(False)

    def mousePressEvent(self, event):
        self.drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        current_position = event.globalPosition().toPoint()
        delta = current_position - self.drag_position
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.drag_position = current_position

    def update_progress(self, progress_data: ProgressUpdate) -> None:
        self.ui.progress_history_list_view.update_progress(progress_data)

    def _initialize_tabs(self):
        self.ui.main_view_stacked_widget.addWidget(self.ui.create_import_page)
        self.ui.main_view_stacked_widget.addWidget(self.ui.create_select_page)
        self.ui.main_view_stacked_widget.addWidget(self.ui.create_create_page)
        self.ui.main_view_stacked_widget.addWidget(self.ui.download_page)
        self.ui.main_view_stacked_widget.addWidget(self.ui.general_information_page)

    def show_download_page(self):
        self.select_navigation_button(self.download_nav_button)
        self.ui.toolBox.setCurrentWidget(self.ui.page_3)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.download_page)

    def show_home_page(self):
        self.select_navigation_button(self.general_nav_button)
        self.ui.toolBox.setCurrentWidget(self.ui.page)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.general_information_page)

    def show_import_page(self):
        self.select_navigation_button(self.import_nav_button)
        self.ui.toolBox.setCurrentWidget(self.ui.page_2)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.create_import_page)

    def show_selection_page(self):
        self.select_navigation_button(self.selection_nav_button)
        self.ui.toolBox.setCurrentWidget(self.ui.page_2)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.create_select_page)

    def show_create_page(self):
        self.select_navigation_button(self.create_nav_button)
        self.ui.toolBox.setCurrentWidget(self.ui.page_2)
        self.ui.main_view_stacked_widget.setCurrentWidget(self.ui.create_create_page)

    def select_navigation_button(self, selected_button):
        for button in self.navigation_pages.keys():
            if button != selected_button:
                button.setChecked(False)
            else:
                button.setChecked(True)

    def show_message(self, text):
        self.message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.message_box.setText(text)
        self.message_box.exec()

    def enable_planning_controls(self):
        self.ui.comboBox.setEnabled(True)
        self.ui.comboBox_time_format.setEnabled(True)
        self.ui.comboBox_direction.setEnabled(True)
        self.ui.btnStart.setEnabled(True)

    def initialize_planning_options(self):
        self.enable_planning_controls()
        self.ui.dateEdit.setDate(string_to_qdate(self.view_model.import_view_model.get_sample_date()))
        self.ui.dateEdit.setEnabled(True)
        self.update_weekday_option_table()

    def select_date(self):
        date = self.ui.dateEdit.date()
        self.view_model.create_view_model.select_date(date)

    def update_weekday_option_table(self):
        self.ui.listDatesWeekday.setModel(DataFrameTableModel(self.view_model.create_view_model.weekdays_df))
        update_table_sizes(self.ui.listDatesWeekday)

    def update_routes_list(self):
        self.ui.TripsTableView.setModel(DataFrameTableModel(self.view_model.selection_view_model.get_routes_df()))
        update_table_sizes(self.ui.TripsTableView)

    def update_individual_sorting_table(self):
        self.ui.tableView_sorting_stops.setModel(
            SortableDataFrameTableModel(self.view_model.create_view_model.get_sorting_df()))
        update_table_sizes(self.ui.tableView_sorting_stops)
        self.ui.btnContinueCreate.setEnabled(True)

    def update_agency_list(self):
        self.ui.AgenciesTableView.setModel(DataFrameTableModel(self.view_model.import_view_model.get_agencies_df()))
        update_table_sizes(self.ui.AgenciesTableView)
        if not self.view_model.import_view_model.has_missing_columns():
            self.show_selection_page()

        self.update_to_date_mode()

    def show_selected_route_date_range(self, date_range):
        self.ui.line_Selection_date_range.setText(date_range)

    def show_selected_route_sample_date(self, sample_date):
        self.ui.dateEdit.setDate(string_to_qdate(sample_date))

    def choose_input_file(self):
        self.view_model.import_view_model.set_input_path(select_gtfs_zip(self))

    def choose_output_directory(self):
        self.view_model.import_view_model.set_output_path(select_output_directory(self))

    def select_route(self, index: QModelIndex):
        index = self._get_selected_row_index(self.ui.TripsTableView, index)
        if index is None:
            return
        route = self.ui.TripsTableView.model().row_data(index)
        logger.debug("Selected route: %s", route["route_short_name"].iloc[0])
        self.view_model.selection_view_model.select_route(route)
        self.ui.line_Selection_trips.setText(
            f"selected trips: {self.view_model.selection_view_model.get_selected_route_text()}"
        )
        date_range_text = self.view_model.selection_view_model.get_selected_route_date_range_text()
        if date_range_text is not None:
            self.show_selected_route_date_range(date_range_text)
        sample_date = self.view_model.selection_view_model.get_selected_route_sample_date()
        if sample_date is not None:
            self.show_selected_route_sample_date(sample_date)

    def select_weekday(self, index: QModelIndex):
        index = self._get_selected_row_index(self.ui.listDatesWeekday, index)
        if index is None:
            return
        weekday = self.ui.listDatesWeekday.model().row_data(index)
        logger.debug("Selected weekday option: %s", weekday["day"].iloc[0])
        self.view_model.create_view_model.select_weekday(weekday)

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
        self.view_model.reset_schedule_planner()
