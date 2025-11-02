import logging
import os
from PySide6.QtCore import Signal, QObject
from model.Base.Progress import ProgressSignal
from model.Enum.GTFSEnums import *

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
delimiter = " "
lineend = '\n'


class ViewModelImportData(QObject):
    input_file_path = Signal(str)
    pickle_file_path = Signal(str)
    output_file_path = Signal(str)
    update_pickle_export_checked = Signal(bool)
    update_progress_value = Signal(ProgressSignal)
    update_warning_table_view = Signal()
    export_plan_time_format = Signal(str)
    error_message = Signal(str)
    update_agency_list_signal = Signal()
    set_up_create_tab_signal = Signal()

    def __init__(self, app, model):
        super().__init__()
        self.app = app
        self.model = model

    def on_changed_progress_value(self, progress_data: ProgressSignal):
        self.update_progress_value.emit(progress_data)

    def on_changed_pickle_export_checked(self, checked):
        self.model.planer.import_settings_dto.pickle_export_checked = checked
        self.update_pickle_export_checked.emit(checked)

    def on_change_input_file_path(self, path):
        self.model.planer.import_settings_dto.input_path = path[0]
        self.input_file_path.emit(path[0])

    def on_changed_pickle_path(self, path):
        if len(path) == 0:
            return
        self.model.planer.import_settings_dto.pickle_save_path_filename = path[0]
        self.pickle_file_path.emit(path[0])

    def on_import_gtfs_data_finished(self):
        self.update_agency_list_signal.emit()
        self.set_up_create_tab_signal.emit()


    def start_import_gtfs_data(self):
        if (self.find(self.model.planer.import_settings_dto.input_path.split('/')[-1],
                      self.model.planer.import_settings_dto.input_path.replace(
                          self.model.planer.import_settings_dto.input_path.split('/')[-1], ''))
        ):
            self.model.start_function_async(ModelTriggerActionsEnum.planer_start_load_data.value)
        else:
            self.send_error_message(ErrorMessageRessources.error_path_not_valid)

        self.update_warning_table_view.emit()


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