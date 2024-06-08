# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal, QObject, QCoreApplication, QDate
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
        self.sample_date = None
        self.date_range_df_format = None
        self.notify_functions = {}

    @property
    def progress(self):
        """
        Getter method for the progress value.

        Returns:
            int: The current progress value.
        """
        return self._progress

    @progress.setter
    def progress(self, value):
        """
        Setter method for the progress attribute.

        Args:
            value (int): The value to set for the progress attribute.
        """
        self._progress = value
        self.progress_Update.emit(self._progress)

    @property
    def gtfs_data_frame_dto(self):
        """
        Getter method for the GTFS data frame DTO.
        Returns:
            GtfsDataFrameDto: The GTFS data frame DTO.
        """
        return self._gtfs_data_frame_dto

    @gtfs_data_frame_dto.setter
    def gtfs_data_frame_dto(self, value: GtfsDataFrameDto):
        """
        Setter method for the GTFS data frame DTO.

        Args:
            value (GtfsDataFrameDto): The value to set for the GTFS data frame DTO.
        """
        self._gtfs_data_frame_dto = value
        if value is not None:
            self.get_date_range()

    def get_date_range(self):
        """
        Gets the date range based on the GTFS data frame.

        If Feedinfos is None, analyzes the date range in the GTFS data.
        Otherwise, constructs the date range string from feed_start_date and feed_end_date.
        """
        if self.gtfs_data_frame_dto.Feedinfos is None:
            self.date_range = self.analyze_date_range_in_gtfs_data()
        else:
            self.date_range = str(self.gtfs_data_frame_dto.Feedinfos.feed_start_date) + '-' + str(
                self.gtfs_data_frame_dto.Feedinfos.feed_end_date)

    def analyze_date_range_in_gtfs_data(self):
        """
         Analyzes the date range in the GTFS data.

         Returns:
         str: A string representing the start and end date of the date range.
         """
        if self.gtfs_data_frame_dto.Calendarweeks is not None:
            self.date_range_df_format = self.gtfs_data_frame_dto.Calendarweeks.groupby(['start_date', 'end_date']).size().reset_index()
            self.sample_date = str(self.date_range_df_format.iloc[0].start_date)
            return str(self.date_range_df_format.iloc[0].start_date) + '-' + str(
                self.date_range_df_format.iloc[0].end_date)

