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
import sys
import os
from enum import Enum, auto
from model.Base.ProgressBar import ProgressBar

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class CreatePlan(Publisher, Subscriber):
    def __init__(self, events, name, progress: ProgressBar):
        super().__init__(events=events, name=name)
        self.reset_create = False
        self.create_plan_mode = None
        self.notify_functions = {
            'create_table': [self.sub_worker_create_output_fahrplan_date, False]
        }

        class CreatePlanMode(Enum):
            """ Types of methods """
            date = 'date'
            weekday = 'weekday'

        """ property """
        self.input_path = ""
        self.pickle_save_path = ""
        self.pickle_export_checked = False
        self.time_format = 1

        """ visual internal property """
        self.progress = progress.progress

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

    def get_date_range(self, dffeed_info):
        logging.debug('len stop_sequences {}'.format(dffeed_info))
        if not dffeed_info.empty:
            self.date_range = str(dffeed_info.iloc[0].feed_start_date) + '-' + str(
                dffeed_info.iloc[0].feed_end_date)
        else:
            self.date_range = self.analyze_date_range_in_gtfs_data()

    def analyze_date_range_in_gtfs_data(self):
        if self.dfWeek is not None:
            self.dfdateRangeInGTFSData = self.dfWeek.groupby(['start_date', 'end_date']).size().reset_index()
            return str(self.dfdateRangeInGTFSData.iloc[0].start_date) + '-' + str(
                self.dfdateRangeInGTFSData.iloc[0].end_date)
