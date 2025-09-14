import copy
from PySide6.QtCore import QObject
from PySide6.QtCore import Signal, Slot
import pandas as pd

class ImportSettingsDto(QObject):
    import_settings_changed = Signal()

    def __init__(self, other=None):
        super().__init__()
        self._input_path = ""
        self._pickle_save_path_filename = ""
        self._pickle_save_path = ""
        self._pickle_export_checked = False
        self._time_format = 1
        self._df_date_range_in_gtfs_data = pd.DataFrame()


    def __deepcopy__(self, memo):
        copied = ImportSettingsDto()
        copied._input_path = copy.deepcopy(self._input_path, memo)
        copied._pickle_save_path_filename = copy.deepcopy(self._pickle_save_path_filename, memo)
        copied._pickle_export_checked = copy.deepcopy(self._pickle_export_checked, memo)
        copied._time_format = copy.deepcopy(self._time_format, memo)
        copied._pickle_save_path = copy.deepcopy(self._pickle_save_path, memo)
        copied._df_date_range_in_gtfs_data = copy.deepcopy(self._df_date_range_in_gtfs_data, memo)

        return copied
    @property
    def input_path(self):
        return self._input_path

    @input_path.setter
    def input_path(self, value):
        self._input_path = value
        self.import_settings_changed.emit()

    @property
    def pickle_save_path_filename(self):
        return self._pickle_save_path_filename

    @pickle_save_path_filename.setter
    def pickle_save_path_filename(self, value):
        if value is not None:
            self._pickle_save_path_filename = value
            self._pickle_save_path = value.replace(value.split('/')[-1], '')

    @property
    def pickle_save_path(self):
        return self._pickle_save_path

    @pickle_save_path.setter
    def pickle_save_path(self, value):
        self._pickle_save_path = value
        self.import_settings_changed.emit()

    @property
    def pickle_export_checked(self):
        return self._pickle_export_checked

    @pickle_export_checked.setter
    def pickle_export_checked(self, value):
        self._pickle_export_checked = value
        self.import_settings_changed.emit()

    @property
    def time_format(self):
        return self._time_format

    @time_format.setter
    def time_format(self, value):
        self._time_format = value
        self.import_settings_changed.emit()

    @property
    def df_date_range_in_gtfs_data(self):
        return self._df_date_range_in_gtfs_data

    @df_date_range_in_gtfs_data.setter
    def df_date_range_in_gtfs_data(self, value):
        self._df_date_range_in_gtfs_data = value
        self.import_settings_changed.emit()