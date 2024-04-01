# -*- coding: utf-8 -*-
from PyQt5.QtCore import QCoreApplication, QObject
import logging
from model.Base.GTFSEnums import GtfsDfNames
from Event.ViewEvents import *
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class AnalyzeData(QObject):
    def __init__(self, app, progress: int):
        super().__init__()
        self.app = app
        self.imported_data = None
        self.progress = progress
        self.date_range = None
        self.date_range_df_format = None
        self.notify_functions = {}

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        QCoreApplication.postEvent(self.app, ProgressUpdateEvent(self._progress))

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
            self.date_range_df_format = self.imported_data[GtfsDfNames.Calendarweeks].groupby(['start_date', 'end_date']).size().reset_index()
            return str(self.date_range_df_format.iloc[0].start_date) + '-' + str(
                self.date_range_df_format.iloc[0].end_date)