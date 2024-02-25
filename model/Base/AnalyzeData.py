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
from model.Base.ImportData import ImportData
from model.Base.GTFSEnums import GtfsColumnNames, GtfsDfNames

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class AnalyzeData(Publisher, Subscriber):
    def __init__(self, events, name, progress: int):
        super().__init__(events=events, name=name)
        self.imported_data = None
        self.progress = progress
        self.date_range = None
        self.notify_functions = {}

    """ subscriber methods """

    def notify_subscriber(self, event, message):
        logging.debug(f'class: ImportData, event: {event}, message {message}')
        notify_function, parameters = self.notify_functions.get(event, self.notify_not_function)
        if not parameters:
            notify_function()
        else:
            notify_function(message)

    def notify_not_function(self, event):
        logging.debug('event not found in class gui: {}'.format(event))

    def notify_error_message(self, message):
        self.notify_subscriber("error_in_import_class", message)

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.dispatch("update_progress_bar", "update_progress_bar routine started! Notify subscriber!")

    @property
    def imported_data(self):
        return self._imported_data

    @imported_data.setter
    def imported_data(self, value):
        self._imported_data = value
        if value is not None:
            self.getDateRange()

    def getDateRange(self):
        if not GtfsDfNames.Feedinfos in self.imported_data:
            self.date_range = self.analyzeDateRangeInGTFSData()
        else:
            self.date_range = str(self.imported_data[GtfsDfNames.Feedinfos].feed_start_date) + '-' + str(
                self.imported_data[GtfsDfNames.Feedinfos].feed_end_date)


    def analyzeDateRangeInGTFSData(self):
        if self.imported_data[GtfsDfNames.Calendarweeks] is not None:
            self.dfdateRangeInGTFSData = self.dfWeek.groupby(['start_date', 'end_date']).size().reset_index()
            return str(self.dfdateRangeInGTFSData.iloc[0].start_date) + '-' + str(
                self.dfdateRangeInGTFSData.iloc[0].end_date)