from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QAbstractItemView

from view.widgets.progress_list import ProgressBarDelegate, ProgressHistoryModel

class ViewSignalBinder(QObject):
    def __init__(self, view, view_model, parent=None):
        super().__init__(parent)
        self.view = view
        self.view_model = view_model

    def connect_signals(self):
        self.view.ui.AgenciesTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.ui.AgenciesTableView.setSelectionMode(QAbstractItemView.SingleSelection)

        self.view.ui.progress_history_list_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.ui.progress_history_list_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.ui.progress_history_list_view.setEnabled(True)
        self.view.ui.progress_history_list_view.setModel(ProgressHistoryModel())
        self.view.ui.progress_history_list_view.setItemDelegate(ProgressBarDelegate())

        self.view.ui.TripsTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.ui.TripsTableView.setSelectionMode(QAbstractItemView.SingleSelection)

        self.view.ui.listDatesWeekday.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.ui.listDatesWeekday.setSelectionMode(QAbstractItemView.SingleSelection)

        self.view.ui.pushButton_2.clicked.connect(self.view.show_import_page)
        self.view.ui.pushButton_3.clicked.connect(self.view.show_selection_page)
        self.view.ui.pushButton_4.clicked.connect(self.view.show_create_page)
        self.view.ui.pushButton_5.clicked.connect(self.view.show_home_window)
        self.view.ui.pushButton_6.clicked.connect(self.view.show_download_page)

        self.view.ui.btnImport.clicked.connect(self.view_model.import_view_model.start_import)

        self.view.ui.btnGetFile.clicked.connect(self.view.get_file_path)
        self.view_model.import_view_model.input_file_path.connect(self.view.update_file_input_path)

        self.view.ui.btnGetOutputDir.clicked.connect(self.view.get_output_dir_path)
        self.view_model.import_view_model.output_file_path.connect(self.view.update_output_file_path)

        self.view.ui.comboBox_time_format.activated[int].connect(self.view_model.import_view_model.set_time_format)
        self.view_model.import_view_model.export_plan_time_format.connect(self.view.update_time_format)

        self.view.ui.comboBox.activated[int].connect(self.view_model.create_view_model.set_plan_mode)
        self.view_model.create_view_model.update_create_plan_mode.connect(self.view.update_create_plan_mode)

        self.view.ui.comboBox_direction.activated[int].connect(self.view_model.create_view_model.set_direction)
        self.view_model.create_view_model.update_direction_mode.connect(self.view.update_direction_mode)

        self.view.ui.AgenciesTableView.clicked.connect(self.view.select_agency)
        self.view.ui.TripsTableView.clicked.connect(self.view.select_route)
        self.view.ui.listDatesWeekday.clicked.connect(self.view.select_weekday)

        self.view_model.import_view_model.update_warning_table_view.connect(self.view.update_warning_table_view)

        self.view_model.import_view_model.update_agency_list_signal.connect(
            self.view.update_agency_list,
            Qt.ConnectionType.UniqueConnection,
        )
        self.view_model.selection_view_model.update_routes_list_signal.connect(self.view.update_routes_list)
        self.view_model.create_view_model.update_options_state_signal.connect(self.view.update_create_options_state)
        self.view_model.create_view_model.update_select_data.connect(self.view.update_select_data)
        self.view_model.import_view_model.set_up_create_tab_signal.connect(self.view.initialize_planning_options)
        self.view_model.update_progress_value.connect(self.view.update_progress)
        self.view_model.error_message.connect(self.view.show_message)

        self.view.ui.btnStart.clicked.connect(self.view_model.create_view_model.start_table_creation)
        self.view_model.create_view_model.table_created.connect(self.view.update_create_table)

        self.view.ui.btnContinueCreate.clicked.connect(self.view_model.create_view_model.continue_table_creation)
        #self.view.ui.btnStop.clicked.connect(self.view_model.view_model_create_data.create_table_stop)

        self.view.ui.UseIndividualSorting.clicked.connect(self.view_model.create_view_model.set_individual_sorting)
        self.view_model.create_view_model.individual_sorting_changed.connect(
            self.view.update_individual_sorting
        )
        self.view_model.create_view_model.individual_sorting_requested.connect(self.view.update_individual_sorting_table)

        self.view.ui.dateEdit.editingFinished.connect(self.view.select_date)
