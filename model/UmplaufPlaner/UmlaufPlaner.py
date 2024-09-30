# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal
import logging
from pandasql import sqldf
import re
from datetime import datetime, timedelta
import pandas as pd
from model.Enum.GTFSEnums import CreatePlanMode
from ..Dto.CreateSettingsForTableDto import CreateSettingsForTableDTO
from ..Dto.CreateTableDataframeDto import CreateTableDataframeDto
from ..Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class UmlaufPlaner(QObject):
    progress_Update = pyqtSignal(int)
    error_occured = pyqtSignal(str)
    create_sorting = pyqtSignal()

    def __init__(self, progress: int):
        super().__init__()
        self.reset_create = False
        self.create_plan_direction_two = None
        self.create_plan_direction_one = None
        self.create_plan_direction_one = None
        self.create_plan_direction_two = None

        self.create_settings_for_table_dto = CreateSettingsForTableDTO()
        self.create_dataframe = CreateTableDataframeDto()

        """ visual internal property """
        self.progress = progress

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

    @property
    def gtfs_data_frame_dto(self):
        return self._gtfs_data_frame_dto

    @gtfs_data_frame_dto.setter
    def gtfs_data_frame_dto(self, value: GtfsDataFrameDto):
        self._gtfs_data_frame_dto = value

    def check_setting_data(self) -> bool:
        if not self.check_dates_input(self.create_settings_for_table_dto.dates):
            return False

        return True