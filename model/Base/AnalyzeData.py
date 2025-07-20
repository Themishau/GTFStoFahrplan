# -*- coding: utf-8 -*-
import logging

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal
import pandas as pd
from .Progress import ProgressSignal
from ..Dto.CreateSettingsForTableDto import CreateSettingsForTableDto
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

        """ visual internal property """
        self.progress = ProgressSignal()

    def get_date_range(self, gtfs_data_frame_dto: GtfsDataFrameDto) -> str:
        if gtfs_data_frame_dto.Feedinfos is None:
            return self.analyze_date_range_in_gtfs_data(gtfs_data_frame_dto)
        else:
            return str(gtfs_data_frame_dto.Feedinfos.feed_start_date) + '-' + str(
                gtfs_data_frame_dto.Feedinfos.feed_end_date)

    def analyze_date_range_in_gtfs_data(self, gtfs_data_frame_dto: GtfsDataFrameDto):
        if gtfs_data_frame_dto.Calendarweeks is not None:
            return gtfs_data_frame_dto.Calendarweeks.groupby(
                ['start_date', 'end_date']).size().reset_index()
        return None

    def analyze_date_range_string(self, date_range_df_format):
        if date_range_df_format is None or date_range_df_format.empty:
            return 'No date range available'
        return str(date_range_df_format.iloc[0].start_date) + '-' + str(
                date_range_df_format.iloc[0].end_date)



    def get_date_range_based_on_selected_trip(self, gtfs_data_frame_dto: GtfsDataFrameDto, create_settings_for_table_dto : CreateSettingsForTableDto):
        selected_trip =
        trip_available_dates_df = pd.DataFrame(columns=['route_id', 'start_date', 'end_date'])
        trip_available_dates_df['start_date'] = pd.to_datetime(fahrplan_dates_df['start_date'],
                                                         format='%Y-%m-%d %H:%M:%S.%f')
        trip_available_dates_df['end_date'] = pd.to_datetime(fahrplan_dates_df['end_date'],
                                                       format='%Y-%m-%d %H:%M:%S.%f')




