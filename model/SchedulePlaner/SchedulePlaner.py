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
from ..Dto.CreateSettingsForTableDto import CreateSettingsForTableDto
from ..Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto
from ..Dto.ImportSettingsDto import ImportSettingsDto

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class SchedulePlaner(QObject):
    progress_Update = Signal(ProgressSignal)
    error_occured = Signal(str)
    import_finished = Signal(bool)
    create_finished = Signal(bool)
    settings_changed = Signal()
    update_options_state_signal = Signal(bool)
    create_sorting_signal = Signal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.progress = 0

        self.circle_plan = None
        self.create_plan = None
        self.export_plan = None
        self.analyze_data = None
        self.select_data = None
        self.import_Data = None

        self.gtfs_data_frame_dto = None
        self.import_settings_dto = ImportSettingsDto()
        self.create_settings_for_table_dto = CreateSettingsForTableDto()

    def send_error(self, e):
        self.error_occured.emit(e)

    def update_progress(self, value):
        self.progress_Update.emit(copy.deepcopy(value))

    def update_options_state(self, value):
        self.update_options_state_signal.emit(value)

    def initialize_signals_settings_dto(self):
        self.create_settings_for_table_dto.settingsChanged.connect(self.settings_changed.emit)

    def initilize_scheduler(self):
        self.initialize_import_data()
        self.initialize_analyze_data()
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

    def initialize_analyze_data(self):
        self.analyze_data = AnalyzeData(self.app)

    def initialize_export_plan(self):
        self.export_plan = ExportPlan(self.app)
        self.export_plan.progress_Update.connect(self.update_progress)
        self.export_plan.error_occured.connect(self.send_error)

    def initialize_create_plan(self):
        self.create_plan = CreatePlan(self.app)
        self.create_plan.progress_Update.connect(self.update_progress)
        self.create_plan.error_occured.connect(self.send_error)

        self.create_plan.create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
        self.create_plan.gtfs_data_frame_dto = self.gtfs_data_frame_dto

    def update_settings_for_create_table(self):
        self.initialize_create_plan()

    def create_sorting_start(self):
        self.create_sorting_signal.emit()

    def create_table(self) -> bool:
        try:
            self.create_plan.create_table()
            self.export_plan.export_plan(self.create_settings_for_table_dto,
                                         self.create_plan.strategy.plans.create_dataframe)
            self.create_finished.emit(True)
            return True

        except AttributeError as e:
            logging.error(f'create_table: {e}')
            self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
            return False
        except ValueError as e:
            logging.error(f"create_table: {e}")
            self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
            return False
        except Exception as e:
            logging.error(f"create_table: {e}")
            self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
            return False

    def create_table_individual_sorting(self) -> bool:
        self.create_plan.create_table()
        self.create_sorting_signal.emit()
        return True

    def create_table_continue(self):
        try:
            self.create_plan.create_table_continue()
            self.export_plan.export_plan(self.create_settings_for_table_dto,
                                         self.create_plan.strategy.plans.create_dataframe)
            self.create_finished.emit(True)
        except AttributeError as e:
            logging.error(f"create_table_continue: {e}")
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
            logging.error(f"create_umlaufplan: {e}")
            self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
            return False
        except ValueError as e:
            logging.error(f"create_umlaufplan: {e}")
            self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
            return False
        except Exception as e:
            logging.error(f"create_umlaufplan: {e}")
            self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)

    def create_umlaufplan_continue(self):
        try:
            self.create_plan.create_table_continue()
            self.export_plan.export_plan(self.create_settings_for_table_dto, self.create_plan.plans.create_dataframe)
            self.create_finished.emit(True)
        except AttributeError as e:
            logging.error(f"create_umlaufplan_continue: {e}")
            self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
            return False

    def import_gtfs_data(self):
        try:
            self.gtfs_data_frame_dto = self.import_Data.import_gtfs(self.import_settings_dto)

            if self.gtfs_data_frame_dto is None:
                self.error_occured.emit(ErrorMessageRessources.import_data_error.value)
                return False
            return self.import_finished.emit(True)

        except AttributeError as e:
            logging.error(f"import_gtfs_data: {e}")
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
