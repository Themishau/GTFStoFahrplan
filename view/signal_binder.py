from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QAbstractItemView


class ViewSignalBinder(QObject):
    def __init__(self, view, view_model, parent=None):
        super().__init__(parent)
        self.view = view
        self.view_model = view_model

    def connect_signals(self):
        self.view.ui.AgenciesTableView.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.view.ui.AgenciesTableView.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.view.ui.progress_history_list_view.setEnabled(True)

        self.view.ui.TripsTableView.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.view.ui.TripsTableView.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.view.ui.listDatesWeekday.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.view.ui.listDatesWeekday.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.view.ui.pushButton_2.clicked.connect(self.view.show_import_page)
        self.view.ui.pushButton_3.clicked.connect(self.view.show_selection_page)
        self.view.ui.pushButton_4.clicked.connect(self.view.show_create_page)
        self.view.ui.pushButton_5.clicked.connect(self.view.show_home_page)
        self.view.ui.pushButton_6.clicked.connect(self.view.show_download_page)

        self.view.ui.btnImport.clicked.connect(self.view_model.import_view_model.start_import)

        self.view.ui.btnGetFile.clicked.connect(self.view.choose_input_file)
        self.view_model.import_view_model.input_path_changed.connect(self.view.show_input_path)

        self.view.ui.btnGetOutputDir.clicked.connect(self.view.choose_output_directory)
        self.view_model.import_view_model.output_path_changed.connect(self.view.show_output_path)

        self.view.ui.comboBox_time_format.activated[int].connect(self.view_model.import_view_model.set_time_format)
        self.view_model.import_view_model.time_format_changed.connect(self.view.update_time_format)

        self.view.ui.comboBox.activated[int].connect(self.view_model.create_view_model.set_plan_mode)
        self.view_model.create_view_model.plan_mode_changed.connect(self.view.update_planning_mode)

        self.view.ui.comboBox_direction.activated[int].connect(self.view_model.create_view_model.set_direction)

        self.view.ui.AgenciesTableView.clicked.connect(self.view.select_agency)
        self.view.ui.TripsTableView.clicked.connect(self.view.select_route)
        self.view.ui.listDatesWeekday.clicked.connect(self.view.select_weekday)

        self.view_model.import_view_model.missing_columns_changed.connect(self.view.update_missing_columns)

        self.view_model.import_view_model.agencies_changed.connect(
            self.view.update_agency_list,
            Qt.ConnectionType.UniqueConnection,
        )
        self.view_model.selection_view_model.routes_changed.connect(self.view.update_routes_list)
        self.view_model.create_view_model.selected_date_changed.connect(self.view.update_selected_date)
        self.view_model.import_view_model.feed_activated.connect(self.view.initialize_planning_options)
        self.view_model.update_progress_value.connect(self.view.update_progress)
        self.view_model.error_message.connect(self.view.show_message)

        self.view.ui.btnStart.clicked.connect(self.view_model.create_view_model.start_timetable_creation)
        self.view_model.create_view_model.timetable_created.connect(self.view.show_timetable_created)

        self.view.ui.btnContinueCreate.clicked.connect(
            self.view_model.create_view_model.continue_timetable_creation
        )
        self.view.ui.UseIndividualSorting.clicked.connect(self.view_model.create_view_model.set_individual_sorting)
        self.view_model.create_view_model.individual_sorting_changed.connect(
            self.view.update_individual_sorting
        )
        self.view_model.create_view_model.individual_sorting_requested.connect(
            self.view.update_individual_sorting_table)

        self.view.ui.dateEdit.editingFinished.connect(self.view.select_date)
