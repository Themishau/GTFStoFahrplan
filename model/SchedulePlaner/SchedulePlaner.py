# -*- coding: utf-8 -*-
from Event.ViewEvents import ProgressUpdateEvent
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
from Event.ViewEvents import *

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class SchedulePlaner(QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.progress = 0
        self.create_plan_direction_two = None
        self.create_plan_direction_one = None
        self.export_plan = None
        self.create_plan_direction_one = None
        self.create_plan_direction_two = None
        self.analyze_data = None
        self.prepare_data = None
        self.select_data = None

        self.imported_data = None
        self.import_Data = None

    """ methods """

    def notify_not_function(self, event):
        logging.debug('event not found in class gui: {}'.format(event))

    def sub_not_implemented(self):
        logging.debug("sub method not implemented")

    def update_progress_bar(self, value):
        self.progress = int(value)

    def initilize_scheduler(self):
        self.initialize_import_data()
        self.initialize_analyze_data()
        self.initialize_select_data()
        self.initialize_export_plan()

    def initialize_import_data(self):
        self.import_Data = ImportData(self.app, progress= self.progress)

    def initialize_select_data(self):
        self.select_data = SelectData(self.app,progress= self.progress)

    def initialize_analyze_data(self):
        self.analyze_data = AnalyzeData(self.app, progress= self.progress)

    def initialize_export_plan(self):
        self.export_plan = ExportPlan(self.app,progress= self.progress)

    def set_paths(self, input_path, output_path, picklesavepath=""):
        self.import_Data.input_path = input_path
        self.import_Data.pickle_save_path_filename = picklesavepath
        self.export_plan.output_path = output_path

    def import_gtfs_data(self) -> bool:
        try:
            imported_data = self.import_Data.import_gtfs()

            if imported_data is None:
                QCoreApplication.postEvent(self.app, ShowErrorMessageEvent(ErrorMessageRessources.import_data_error.value))
                return False

            self.imported_data = imported_data
            QCoreApplication.postEvent(self.app, ImportFinishedEvent())
        except AttributeError:
            QCoreApplication.postEvent(self.app, ShowErrorMessageEvent(ErrorMessageRessources.no_import_object_generated.value))
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
    def create_plan_direction_one(self):
        return self._createPlan_Direction_one

    @create_plan_direction_one.setter
    def create_plan_direction_one(self, value):
        self._createPlan_Direction_one = value

    @property
    def create_plan_direction_two(self):
        return self._createPlan_Direction_two

    @create_plan_direction_two.setter
    def create_plan_direction_two(self, value):
        self._createPlan_Direction_two = value

    @property
    def prepare_data(self):
        return self._prepare_data

    @prepare_data.setter
    def prepare_data(self, value):
        self._prepare_data = value

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
    def imported_data(self):
        return self._imported_data

    @imported_data.setter
    def imported_data(self, value):
        self._imported_data = value
        if value is not None:
            self.analyze_data.imported_data = value
            self.select_data.imported_data = value
            self.prepare_data.imported_data = value
            self.export_plan.imported_data = value
