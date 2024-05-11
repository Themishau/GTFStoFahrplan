# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal, QObject, QCoreApplication
import logging
from model.Base.GTFSEnums import GtfsDfNames
from ..DTO.General_Transit_Feed_Specification import GtfsListDto, GtfsDataFrameDto


logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class AnalyzeData(QObject):
    progress_Update = pyqtSignal(int)
    error_occured = pyqtSignal(str)
    def __init__(self, app, progress: int):
        super().__init__()
        self.app = app
        self.gtfs_data_frame_dto = None
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
        self.progress_Update.emit(self._progress)

    @property
    def gtfs_data_frame_dto(self):
        return self._gtfs_data_frame_dto

    @gtfs_data_frame_dto.setter
    def gtfs_data_frame_dto(self, value: GtfsDataFrameDto):
        self._gtfs_data_frame_dto = value
        if value is not None:
            self.getDateRange()

    def getDateRange(self):
        if self.gtfs_data_frame_dto.Feedinfos is None:
            self.date_range = self.analyzeDateRangeInGTFSData()
        else:
            self.date_range = str(self.gtfs_data_frame_dto.Feedinfos.feed_start_date) + '-' + str(
                self.gtfs_data_frame_dto.Feedinfos.feed_end_date)


    def analyzeDateRangeInGTFSData(self):
        if self.gtfs_data_frame_dto.Calendarweeks is not None:
            self.date_range_df_format = self.gtfs_data_frame_dto.Calendarweeks.groupby(['start_date', 'end_date']).size().reset_index()
            return str(self.date_range_df_format.iloc[0].start_date) + '-' + str(
                self.date_range_df_format.iloc[0].end_date)