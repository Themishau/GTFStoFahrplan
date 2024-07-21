# -*- coding: utf-8 -*-
import logging

from PyQt5.QtCore import pyqtSignal, QObject

from ..Base.AnalyzeData import AnalyzeData
from ..Base.CreatePlan import CreatePlan
from ..Base.ExportPlan import ExportPlan
from ..Base.GTFSEnums import *
from ..Base.ImportData import ImportData
from ..Base.SelectData import SelectData
from ..DTO.CreateSettingsForTableDTO import CreateSettingsForTableDTO
from ..DTO.General_Transit_Feed_Specification import GtfsDataFrameDto

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class SchedulePlaner(QObject):
    progress_Update = pyqtSignal(int)
    error_occured = pyqtSignal(str)
    import_finished = pyqtSignal(bool)
    create_finished = pyqtSignal(bool)
    update_routes_list_signal = pyqtSignal()
    update_options_state_signal = pyqtSignal(bool)
    create_sorting_signal = pyqtSignal()

    def __init__(self, app):
        super().__init__()
        self.gtfs_data_frame_dto = None
        self.app = app

        self.progress = 0
        self.create_plan = None
        self.export_plan = None
        self.analyze_data = None
        self.select_data = None

        self.import_Data = None
        self.create_settings_for_table_dto = CreateSettingsForTableDTO()

    """ methods """

    def notify_not_function(self, event):
        logging.debug('event not found in class gui: {}'.format(event))

    def sub_not_implemented(self):
        logging.debug("sub method not implemented")

    def update_progress_bar(self, value):
        self.progress = int(value)
        self.progress_Update.emit(self.progress)

    def update_routes_list(self):
        self.update_routes_list_signal.emit()

    def update_options_state(self, value):
        self.update_options_state_signal.emit(value)

    def update_create_settings_output(self):
        self.create_settings_for_table_dto.output_path = self.export_plan.create_settings_for_table_dto.output_path

    def update_create_settings_selected_data(self):
        self.create_settings_for_table_dto.agency = self.select_data.create_settings_for_table_dto.agency
        self.create_settings_for_table_dto.route = self.select_data.create_settings_for_table_dto.route
        self.create_settings_for_table_dto.weekday = self.select_data.create_settings_for_table_dto.weekday
        self.create_settings_for_table_dto.dates = self.select_data.create_settings_for_table_dto.dates
        self.create_settings_for_table_dto.direction = self.select_data.create_settings_for_table_dto.direction
        self.create_settings_for_table_dto.create_plan_mode = self.select_data.create_settings_for_table_dto.create_plan_mode

    def initilize_scheduler(self):
        self.initialize_import_data()
        self.initialize_analyze_data()
        self.initialize_select_data()
        self.initialize_export_plan()
        self.initialize_create_plan()

    def initialize_import_data(self):
        self.import_Data = ImportData(self.app, progress=self.progress)
        self.import_Data.progress_Update.connect(self.update_progress_bar)
        self.import_Data.error_occured.connect(self.sub_not_implemented)

    def initialize_select_data(self):
        self.select_data = SelectData(self.app, progress=self.progress)
        self.select_data.update_routes_list_signal.connect(self.update_routes_list)
        self.select_data.data_selected.connect(self.update_options_state)
        self.select_data.create_settings_for_table_dto_changed.connect(self.update_create_settings_selected_data)

    def update_settings_for_create_table(self):
        self.create_plan.create_settings_for_table_dto = self.create_settings_for_table_dto

    def initialize_analyze_data(self):
        self.analyze_data = AnalyzeData(self.app, progress=self.progress)

    def initialize_export_plan(self):
        self.export_plan = ExportPlan(self.app, progress=self.progress)
        self.export_plan.create_settings_for_table_dto_changed.connect(self.update_create_settings_output)

    def initialize_create_plan(self):
        self.create_plan = CreatePlan(self.app, progress=self.progress)
        self.create_plan.progress_Update.connect(self.update_progress_bar)
        self.create_plan.create_sorting.connect(self.create_sorting_start)

    def create_sorting_start(self):
        self.create_sorting_signal.emit()

    def set_paths(self, input_path, output_path, picklesavepath=""):
        self.import_Data.input_path = input_path
        self.import_Data.pickle_save_path_filename = picklesavepath
        self.export_plan.output_path = output_path

    def initialize_setting_dto(self):
        self.select_data.create_settings_for_table_dto = self.create_settings_for_table_dto

    def create_table(self) -> bool:
        #try:
        dataframe = self.create_plan.create_table()
        self.export_plan.export_plan(dataframe)
        self.create_finished.emit(True)
        return True
        #except AttributeError:
        #    self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
        #    return False

    def import_gtfs_data(self) -> bool:
        try:
            self.gtfs_data_frame_dto = self.import_Data.import_gtfs()

            if self.gtfs_data_frame_dto is None:
                self.error_occured.emit(ErrorMessageRessources.import_data_error.value)
                return False

            self.import_finished.emit(True)
        except AttributeError:
            self.error_occured.emit(ErrorMessageRessources.no_import_object_generated.value)
            return False

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value

    @property
    def export_plan(self):
        return self._exportPlan

    @export_plan.setter
    def export_plan(self, value):
        self._exportPlan = value

    @property
    def create_plan(self):
        return self._create_plan

    @create_plan.setter
    def create_plan(self, value):
        self._create_plan = value

    @property
    def select_data(self):
        return self._select_data

    @select_data.setter
    def select_data(self, value):
        self._select_data = value

    @property
    def import_Data(self):
        return self._import_Data

    @import_Data.setter
    def import_Data(self, value):
        self._import_Data = value

    @property
    def gtfs_data_frame_dto(self):
        return self._gtfs_data_frame_dto

    @gtfs_data_frame_dto.setter
    def gtfs_data_frame_dto(self, value: GtfsDataFrameDto):
        self._gtfs_data_frame_dto = value
        if value is not None:
            self.analyze_data.gtfs_data_frame_dto = value
            self.initialize_setting_dto()
            self.select_data.gtfs_data_frame_dto = value
            self.create_plan.gtfs_data_frame_dto = value
