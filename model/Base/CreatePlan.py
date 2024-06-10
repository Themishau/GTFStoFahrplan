# -*- coding: utf-8 -*-
from model.observer import Publisher, Subscriber
import time
import pandas as pd
from pandasql import sqldf
import zipfile
import io
from datetime import datetime, timedelta
import re
import logging
from PyQt5.QtCore import pyqtSignal, QObject, QCoreApplication
import sys
import os
from ..Base.GTFSEnums import CreatePlanMode
from model.Base.ProgressBar import ProgressBar
from ..DTO.CreateSettingsForTableDTO import CreateSettingsForTableDTO
from ..DTO.General_Transit_Feed_Specification import GtfsListDto, GtfsDataFrameDto

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class CreatePlan(QObject):
    progress_Update = pyqtSignal(int)
    error_occured = pyqtSignal(str)
    create_sorting = pyqtSignal()
    def __init__(self, app, progress: int):
        super().__init__()
        self.reset_create = False
        self.create_plan_mode = None
        self.gtfs_data_frame_dto = None
        self.df_filtered_stop_names = None
        self.create_settings_for_table_dto = CreateSettingsForTableDTO()

        """ property """
        self.input_path = ""
        self.pickle_save_path = ""
        self.time_format = 1

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

    def create_table(self):
        if self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.date and self.create_settings_for_table_dto.individual_sorting:
            self.progress = 0
            logging.debug(f"PREPARE intividual date ")
            self.progress = 10
            self.dates_prepare_data_fahrplan()
            self.progress = 20
            self.datesWeekday_select_dates_for_date_range()
            self.progress = 30
            self.dates_select_dates_delete_exception_2()
            self.progress = 40
            self.datesWeekday_select_stops_for_trips()
            self.progress = 50
            self.datesWeekday_select_for_every_date_trips_stops()
            self.progress = 60
            self.datesWeekday_select_stop_sequence_stop_name_sorted()
            self.progress = 70
            self.datesWeekday_create_sort_stopnames()
            self.create_sorting.emit()

    def create_table_continue(self):
        self.datesWeekday_create_fahrplan_continue()
        self.progress = 80
        self.datesWeekday_create_output_fahrplan()
        self.progress = 100

