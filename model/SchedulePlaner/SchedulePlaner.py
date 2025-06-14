# -*- coding: utf-8 -*-
import logging
import copy
from PySide6.QtCore import QObject
from PySide6.QtCore import Signal

from model.Enum.GTFSEnums import *
from ..Base.Progress import ProgressSignal
from ..Base.AnalyzeData import AnalyzeData
from model.SchedulePlaner.UmplaufPlaner.CirclePlaner import CirclePlaner
from ..Base.CreatePlan import CreatePlan
from ..Base.ExportPlan import ExportPlan
from ..Base.ImportData import ImportData
from ..Base.SelectData import SelectData
from ..Dto.CreateSettingsForTableDto import CreateSettingsForTableDTO
from ..Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class SchedulePlaner(QObject):
    progress_Update = Signal(ProgressSignal)
    error_occured = Signal(str)
    import_finished = Signal(bool)
    create_finished = Signal(bool)
    settings_changed = Signal()
    update_routes_list_signal = Signal()
    update_options_state_signal = Signal(bool)
    create_sorting_signal = Signal()

    def __init__(self, app):
        super().__init__()
        self.gtfs_data_frame_dto = None
        self.app = app
        self.progress = 0

        self.circle_plan = None
        self.create_plan = None
        self.export_plan = None
        self.analyze_data = None
        self.select_data = None
        self.import_Data = None

        self.create_settings_for_table_dto = CreateSettingsForTableDTO()

    def send_error(self, e):
        self.error_occured.emit(e)

    def update_progress(self, value):
        self.progress_Update.emit(copy.deepcopy(value))

    def update_routes_list(self):
        self.update_routes_list_signal.emit()

    def update_options_state(self, value):
        self.update_options_state_signal.emit(value)

    def update_create_settings_analyze_data(self):
        self.create_settings_for_table_dto.dates = self.analyze_data.sample_date

    def update_create_settings_create_plan(self):
        self.create_settings_for_table_dto.create_plan_mode = self.create_plan.create_plan_mode

    def update_create_settings_export_plan(self):
        self.create_settings_for_table_dto.output_path = self.export_plan.output_path

    def update_create_settings_selected_data(self):
        self.create_settings_for_table_dto.agency = self.select_data.selected_agency
        self.create_settings_for_table_dto.route = self.select_data.selected_route
        self.create_settings_for_table_dto.weekday = self.select_data.selected_weekday
        self.create_settings_for_table_dto.dates = self.select_data.selected_dates
        self.create_settings_for_table_dto.direction = self.select_data.selected_direction
        self.create_settings_for_table_dto.individual_sorting = self.select_data.use_individual_sorting
        self.create_settings_for_table_dto.timeformat = self.select_data.selected_timeformat
        self.create_settings_for_table_dto.create_plan_mode = self.select_data.selected_create_plan_mode


    def initialize_signals_settings_dto(self):
        self.create_settings_for_table_dto.settingsChanged.connect(self.settings_changed.emit)

    def initilize_scheduler(self):
        self.initialize_import_data()
        self.initialize_analyze_data()
        self.initialize_select_data()
        self.initialize_export_plan()
        self.initialize_create_plan()

    def initialize_import_data(self):
        self.import_Data = ImportData(self.app)
        self.import_Data.progress_Update.connect(self.update_progress)
        self.import_Data.error_occured.connect(self.send_error)

    def initialize_cirle_planer(self):
        self.circle_plan = CirclePlaner(plans=self.create_plan.strategy.plans, app=self.app)
        self.circle_plan.progress_Update.connect(self.update_progress)
        self.circle_plan.error_occured.connect(self.send_error)

    def initialize_select_data(self):
        self.select_data = SelectData(self.app)
        self.select_data.update_routes_list_signal.connect(self.update_routes_list)
        self.select_data.data_selected.connect(self.update_create_settings_selected_data)
        self.select_data.data_selected.connect(self.update_options_state)

    def initialize_analyze_data(self):
        self.analyze_data = AnalyzeData(self.app)
        self.analyze_data.data_selected.connect(self.update_create_settings_analyze_data)

    def initialize_export_plan(self):
        self.export_plan = ExportPlan(self.app)
        self.export_plan.data_selected.connect(self.update_create_settings_export_plan)
        self.export_plan.progress_Update.connect(self.update_progress)

    def initialize_create_plan(self):
        self.create_plan = CreatePlan(self.app)
        self.create_plan.progress_Update.connect(self.update_progress)
        self.create_plan.data_selected.connect(self.update_create_settings_create_plan)

        self.create_plan.create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
        self.create_plan.gtfs_data_frame_dto = self.gtfs_data_frame_dto

    def initialize_setting_dto(self):
        self.select_data.initialize_select_data()

    def update_settings_for_create_table(self):
        self.initialize_create_plan()

    def create_sorting_start(self):
        self.create_sorting_signal.emit()

    def set_paths(self, input_path, output_path, picklesavepath=""):
        self.import_Data.input_path = input_path
        self.import_Data.pickle_save_path_filename = picklesavepath
        self.export_plan.output_path = output_path

    def create_table(self) -> bool:
        #try:
            self.create_plan.create_table()
            self.export_plan.export_plan(self.create_settings_for_table_dto, self.create_plan.strategy.plans.create_dataframe)
            self.create_finished.emit(True)
            return True
        # except AttributeError as e:
        #    self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
        #    return False
        # except ValueError as e:
        #    self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
        #    return False

    def create_table_individual_sorting(self) -> bool:
        self.create_plan.create_table()
        self.create_sorting_signal.emit()
        return True

    def create_table_continue(self):
        try:
            self.create_plan.create_table_continue()
            self.export_plan.export_plan(self.create_settings_for_table_dto, self.create_plan.strategy.plans.create_dataframe)
            self.create_finished.emit(True)
        except AttributeError as e:
            self.error_occured.emit(ErrorMessageRessources.no_import_object_generated.value)
            return False

    def create_umlaufplan(self):
        try:
            self.create_plan.create_table()
            self.initialize_cirle_planer()
            self.circle_plan.CreateCirclePlan()
            self.export_plan.export_circle_plan(self.create_settings_for_table_dto, self.circle_plan.plans)
            self.create_finished.emit(True)
            return True

        except AttributeError as e:
           self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
           return False
        except ValueError as e:
           self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
           return False

    def create_umlaufplan_continue(self):
        try:
            self.create_plan.create_table_continue()
            self.export_plan.export_plan(self.create_settings_for_table_dto, self.create_plan.plans.create_dataframe)
            self.create_finished.emit(True)
        except AttributeError as e:
            self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
            return False

    def import_gtfs_data(self) -> bool:
        try:
            self.gtfs_data_frame_dto = self.import_Data.import_gtfs()
            # if self.import_Data.evaluate_imported_data():
            #     self.error_occured.emit(ErrorMessageRessources.missing_import_object_generated.value)

            if self.gtfs_data_frame_dto is None:
                self.error_occured.emit(ErrorMessageRessources.import_data_error.value)
                return False

            self.import_finished.emit(True)
            return True

        except AttributeError as e:
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
