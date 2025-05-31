# -*- coding: utf-8 -*-
import logging

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal

from .Progress import ProgressSignal
from ..Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class AnalyzeData(QObject):
    progress_Update = Signal(ProgressSignal)
    error_occured = Signal(str)
    data_selected = Signal(bool)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.gtfs_data_frame_dto = None
        self.progress_information = ""
        self.date_range = None
        self._sample_date = None
        self.date_range_df_format = None
        self.notify_functions = {}

        """ visual internal property """
        self.progress = ProgressSignal()

    @property
    def sample_date(self):
        return self._sample_date

    @sample_date.setter
    def sample_date(self, value):
        self._sample_date = value
        self.data_selected.emit(value is not None)


    @property
    def gtfs_data_frame_dto(self):
        return self._gtfs_data_frame_dto

    @gtfs_data_frame_dto.setter
    def gtfs_data_frame_dto(self, value: GtfsDataFrameDto):
        self._gtfs_data_frame_dto = value
        if value is not None:
            self.get_date_range()

    def get_date_range(self):
        if self.gtfs_data_frame_dto.Feedinfos is None:
            self.date_range = self.analyze_date_range_in_gtfs_data()
        else:
            self.date_range = str(self.gtfs_data_frame_dto.Feedinfos.feed_start_date) + '-' + str(
                self.gtfs_data_frame_dto.Feedinfos.feed_end_date)

    def analyze_date_range_in_gtfs_data(self):
        if self.gtfs_data_frame_dto.Calendarweeks is not None:
            self.date_range_df_format = self.gtfs_data_frame_dto.Calendarweeks.groupby(
                ['start_date', 'end_date']).size().reset_index()
            self.sample_date = str(self.date_range_df_format.iloc[0].start_date)
            return str(self.date_range_df_format.iloc[0].start_date) + '-' + str(
                self.date_range_df_format.iloc[0].end_date)
        return None
