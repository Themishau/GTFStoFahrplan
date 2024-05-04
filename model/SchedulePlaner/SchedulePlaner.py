# -*- coding: utf-8 -*-
from model.observer import Publisher, Subscriber
from PyQt5.QtCore import pyqtSignal, QObject, QCoreApplication
import time
import pandas as pd
from pandasql import sqldf
import zipfile
import io
from datetime import datetime, timedelta
import re
import logging
import sys
import os
from ..Base.ImportData import ImportData
from ..Base.AnalyzeData import AnalyzeData
from ..Base.SelectData import SelectData
from ..Base.CreatePlan import CreatePlan
from ..Base.ExportPlan import ExportPlan
from ..Base.GTFSEnums import *
from ..DTO.General_Transit_Feed_Specification import GtfsListDto, GtfsDataFrameDto

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class SchedulePlaner(QObject):
    progress_Update = pyqtSignal(int)
    error_occured = pyqtSignal(str)
    import_finished = pyqtSignal(bool)
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

    """ methods """

    def notify_not_function(self, event):
        logging.debug('event not found in class gui: {}'.format(event))

    def sub_not_implemented(self):
        logging.debug("sub method not implemented")

    def update_progress_bar(self, value):
        self.progress = int(value)
        self.progress_Update.emit(self.progress)

    def initilize_scheduler(self):
        self.initialize_import_data()
        self.initialize_analyze_data()
        self.initialize_select_data()
        self.initialize_export_plan()
        self.initialize_create_plan()

    def initialize_import_data(self):
        self.import_Data = ImportData(self.app, progress= self.progress)
        self.import_Data.progress_Update.connect(self.update_progress_bar)
        self.import_Data.error_occured.connect(self.sub_not_implemented)

    def initialize_select_data(self):
        self.select_data = SelectData(self.app,progress= self.progress)

    def initialize_analyze_data(self):
        self.analyze_data = AnalyzeData(self.app, progress= self.progress)

    def initialize_export_plan(self):
        self.export_plan = ExportPlan(self.app,progress= self.progress)

    def initialize_create_plan(self):
        self.create_plan = CreatePlan(self.app,progress= self.progress)

    def set_paths(self, input_path, output_path, picklesavepath=""):
        self.import_Data.input_path = input_path
        self.import_Data.pickle_save_path_filename = picklesavepath
        self.export_plan.output_path = output_path

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
            self.select_data.gtfs_data_frame_dto = value
            self.create_plan.gtfs_data_frame_dto = value


