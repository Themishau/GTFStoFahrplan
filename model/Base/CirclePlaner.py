# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal
import logging
from pandasql import sqldf
import re
from datetime import datetime, timedelta
import pandas as pd
from model.Enum.GTFSEnums import CreatePlanMode
from model.Dto.CreateSettingsForTableDto import CreateSettingsForTableDTO
from model.Dto.CreateTableDataframeDto import CreateTableDataframeDto
from model.Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto
from model.SchedulePlaner.UmplaufPlaner.UmlaufPlaner import UmlaufPlaner

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class CirclePlaner(QObject):
    progress_Update = pyqtSignal(int)

    def __init__(self, plans):
        super().__init__()
        self.create_settings_for_table_dto = CreateSettingsForTableDTO()
        self.plans =  plans

        self.weekDayOptionsList = ['0,Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday',
                                   '1,Monday, Tuesday, Wednesday, Thursday, Friday',
                                   '2,Monday',
                                   '3,Tuesday',
                                   '4,Wednesday',
                                   '5,Thursday',
                                   '6,Friday',
                                   '7,Saturday',
                                   '8,Sunday']

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.progress_Update.emit(self._progress)


    def ReadCreatedSchedulePlans(self):
        NotImplementedError()

    def CreateCirclePlan(self):
        self.MergePlans()

    def MergePlans(self):
        NotImplementedError()