from PySide6.QtCore import QObject
from view.Custom.ProgressListView import ProgressHistoryModel, ProgressBarDelegate
from PySide6.QtWidgets import QWidget, QAbstractItemView, QHeaderView
import logging

class ViewSignals(QObject):
    def __init__(self, view, viewModel):
        super().__init__()
        self.view = view
        self.viewModel = viewModel

    def connect_signals(self):
        self.view.ui.AgenciesTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.ui.AgenciesTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.ui.AgenciesTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.view.ui.progress_history_list_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.ui.progress_history_list_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.ui.progress_history_list_view.setModel(ProgressHistoryModel())
        self.view.ui.progress_history_list_view.setItemDelegate(ProgressBarDelegate())

        self.view.ui.TripsTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.ui.TripsTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.ui.TripsTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.view.ui.listDatesWeekday.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.ui.listDatesWeekday.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.ui.listDatesWeekday.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.view.ui.pushButton_2.clicked.connect(self.view.show_Create_Import_Window)
        self.view.ui.pushButton_3.clicked.connect(self.view.show_Create_Select_Window)
        self.view.ui.pushButton_4.clicked.connect(self.view.show_Create_Create_Window)
        self.view.ui.pushButton_5.clicked.connect(self.view.show_home_window)
        self.view.ui.pushButton_6.clicked.connect(self.view.show_GTFSDownload_window)

        self.view.ui.btnImport.clicked.connect(self.viewModel.start_import_gtfs_data)
        self.view.ui.btnRestart.clicked.connect(self.viewModel.restart)

        self.view.ui.btnGetFile.clicked.connect(self.view.get_file_path)
        self.viewModel.input_file_path.connect(self.view.update_file_input_path)

        self.view.ui.btnGetPickleFile.clicked.connect(self.view.get_pickle_save_path)
        self.viewModel.pickle_file_path.connect(self.view.update_pickle_file_path)

        self.view.ui.btnGetOutputDir.clicked.connect(self.view.get_output_dir_path)
        self.viewModel.output_file_path.connect(self.view.update_output_file_path)

        self.view.ui.checkBox_savepickle.clicked.connect(self.viewModel.on_changed_pickle_export_checked)
        self.viewModel.update_pickle_export_checked.connect(self.view.update_pickle_export_checked)

        self.view.ui.comboBox_time_format.activated[int].connect(self.viewModel.on_changed_time_format_mode)
        self.viewModel.export_plan_time_format.connect(self.view.update_time_format)

        self.view.ui.comboBox.activated[int].connect(self.viewModel.on_changed_create_plan_mode)
        self.viewModel.update_create_plan_mode.connect(self.view.update_create_plan_mode)

        self.view.ui.comboBox_direction.activated[int].connect(self.viewModel.on_changed_direction_mode)
        self.viewModel.update_direction_mode.connect(self.view.update_direction_mode)

        self.view.ui.AgenciesTableView.clicked.connect(self.view.get_selected_agency_table_record)
        self.view.ui.TripsTableView.clicked.connect(self.view.get_changed_selected_record_trip)
        self.view.ui.listDatesWeekday.clicked.connect(self.view.get_changed_selected_weekday)

        self.viewModel.update_agency_list.connect(self.view.update_agency_list)
        self.viewModel.update_routes_list_signal.connect(self.view.update_routes_list)
        self.viewModel.update_options_state_signal.connect(self.view.update_create_options_state)
        self.viewModel.update_select_data.connect(self.view.update_select_data)
        self.viewModel.set_up_create_tab_signal.connect(self.view.initialize_create_view_weekdaydate_option)
        self.viewModel.update_progress_value.connect(self.view.update_progress)
        self.viewModel.error_message.connect(self.view.send_message_box)

        self.view.ui.btnStart.clicked.connect(self.viewModel.start_create_table)
        self.viewModel.create_table_finshed.connect(self.view.update_create_table)

        self.view.ui.btnContinueCreate.clicked.connect(self.viewModel.create_table_continue)
        self.view.ui.btnStop.clicked.connect(self.viewModel.create_table_stop)

        self.view.ui.UseIndividualSorting.clicked.connect(self.viewModel.on_changed_individualsorting)
        self.viewModel.update_individualsorting.connect(self.view.update_individualsorting)
        self.viewModel.on_changed_individualsorting_table.connect(self.view.update_individualsorting_table)

        self.view.ui.dateEdit.editingFinished.connect(self.view.handle_selected_date)


    def init_signals(self):
        self.view.ui.lineInputPath.textChanged.connect(self.viewModel.input_file_path.emit)
        self.view.ui.lineOutputPath.textChanged.connect(self.viewModel.output_file_path.emit)
        self.view.ui.picklesavename.textChanged.connect(self.viewModel.pickle_file_path.emit)