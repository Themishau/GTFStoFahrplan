import logging
import os
from PySide6.QtCore import Signal, QObject
from model.Base.Progress import ProgressSignal
from model.history_store import ImportHistoryEntry, ImportHistoryStore
from model.Enum.GTFSEnums import *
import pandas as pd
delimiter = " "
lineend = '\n'


class ViewModelImportData(QObject):
    input_file_path = Signal(str)
    pickle_file_path = Signal(str)
    output_file_path = Signal(str)
    update_pickle_export_checked = Signal(bool)
    update_archive_input_checked = Signal(bool)
    update_progress_value = Signal(ProgressSignal)
    update_warning_table_view = Signal()
    export_plan_time_format = Signal(str)
    error_message = Signal(str)
    update_agency_list_signal = Signal()
    set_up_create_tab_signal = Signal()
    update_history_table_signal = Signal()

    def __init__(self, app, model, parent=None):
        super().__init__(parent)
        self.app = app
        self.model = model
        self.history_store = ImportHistoryStore()

    def on_changed_progress_value(self, progress_data: ProgressSignal):
        self.update_progress_value.emit(progress_data)

    def get_missing_columns_df(self):
        return self.model.planer.import_Data.missing_columns_in_gtfs_file

    def has_missing_columns(self):
        missing_columns_df = self.get_missing_columns_df()
        return missing_columns_df is not None and not missing_columns_df.empty

    def get_agencies_df(self):
        gtfs_data = self.model.planer.gtfs_data_frame_dto
        if gtfs_data is None:
            return None
        return gtfs_data.Agencies

    def get_time_format(self):
        return self.model.planer.create_settings_for_table_dto.timeformat

    def get_sample_date(self):
        return self.model.planer.create_settings_for_table_dto.sample_date

    def get_history_df(self):
        history_df = self.history_store.to_dataframe()
        if history_df.empty:
            return history_df
        return history_df.iloc[::-1].reset_index(drop=True)

    def save_import_history(self):
        gtfs_data = self.model.planer.gtfs_data_frame_dto
        import_settings = self.model.planer.import_settings_dto
        create_settings = self.model.planer.create_settings_for_table_dto
        input_path = import_settings.input_path or ""
        imported_at = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        file_name = os.path.basename(input_path) if input_path else ""
        try:
            file_size_mb = round(os.path.getsize(input_path) / (1024 * 1024), 2) if input_path else 0.0
        except OSError:
            file_size_mb = 0.0

        archived_copy_path = ""
        if bool(import_settings.archive_input_file_checked):
            archived_copy_path = self.history_store.archive_import_file(input_path, imported_at)

        feed_start_date = ""
        feed_end_date = ""
        if gtfs_data is not None and gtfs_data.Feedinfos is not None and not gtfs_data.Feedinfos.empty:
            feed_info = gtfs_data.Feedinfos.iloc[0]
            feed_start_date = str(feed_info.get("feed_start_date", ""))
            feed_end_date = str(feed_info.get("feed_end_date", ""))

        entry = ImportHistoryEntry(
            imported_at=imported_at,
            file_name=file_name,
            input_path=input_path,
            archived_copy_path=archived_copy_path,
            file_size_mb=file_size_mb,
            output_path=create_settings.output_path or "",
            pickle_export_checked=bool(import_settings.pickle_export_checked),
            pickle_file_path=import_settings.pickle_save_path_filename or "",
            agencies=len(gtfs_data.Agencies.index) if gtfs_data is not None and gtfs_data.Agencies is not None else 0,
            routes=len(gtfs_data.Routes.index) if gtfs_data is not None and gtfs_data.Routes is not None else 0,
            trips=len(gtfs_data.Trips.index) if gtfs_data is not None and gtfs_data.Trips is not None else 0,
            feed_start_date=feed_start_date,
            feed_end_date=feed_end_date,
        )
        self.history_store.append_entry(entry)

    def on_changed_pickle_export_checked(self, checked):
        self.model.planer.import_settings_dto.pickle_export_checked = checked
        self.update_pickle_export_checked.emit(checked)

    def on_changed_archive_input_checked(self, checked):
        self.model.planer.import_settings_dto.archive_input_file_checked = checked
        self.update_archive_input_checked.emit(checked)

    def on_change_input_file_path(self, path):
        self.model.planer.import_settings_dto.input_path = path[0]
        self.input_file_path.emit(path[0])

    def on_changed_pickle_path(self, path):
        if len(path) == 0:
            return
        self.model.planer.import_settings_dto.pickle_save_path_filename = path[0]
        self.pickle_file_path.emit(path[0])

    def on_import_gtfs_data_finished(self):
        self.save_import_history()
        self.update_warning_table_view.emit()
        self.update_agency_list_signal.emit()
        self.set_up_create_tab_signal.emit()
        self.update_history_table_signal.emit()


    def start_import_gtfs_data(self):
        if (self.find(self.model.planer.import_settings_dto.input_path.split('/')[-1],
                      self.model.planer.import_settings_dto.input_path.replace(
                          self.model.planer.import_settings_dto.input_path.split('/')[-1], ''))
        ):
            self.model.start_function_async(ModelTriggerActionsEnum.planer_start_load_data.value)
        else:
            self.send_error_message(ErrorMessageRessources.error_path_not_valid.value)


    def on_change_output_file_path(self, path):
        self.model.planer.create_settings_for_table_dto.output_path = path
        self.output_file_path.emit(path)

    def on_changed_time_format_mode(self, text):
        logging.debug(f'time format {text}')
        if text == 0:
            self.model.planer.create_settings_for_table_dto.timeformat = 1
        elif text == 1:
            self.model.planer.create_settings_for_table_dto.timeformat = 2
        self.export_plan_time_format.emit(text)

    def send_error_message(self, message):
        self.error_message.emit(message)

    @staticmethod
    def find(name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return True
            return None
        return None
