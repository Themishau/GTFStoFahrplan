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


    def get_routes_of_agency(self, gtfs_data_frame_dto, selected_agency):
        if selected_agency is not None:
            return self.find_routes_from_agency(gtfs_data_frame_dto, selected_agency)
        return None

    def find_routes_from_agency(self, gtfs_data_frame_dto, selected_agency):
        return gtfs_data_frame_dto.Routes[gtfs_data_frame_dto.Routes['agency_id'].isin(selected_agency['agency_id'])]

    def read_gtfs_agencies(self, gtfs_data_frame_dto : GtfsDataFrameDto):
        df_agency = gtfs_data_frame_dto.Agencies
        df_agency_ordered = df_agency.sort_values(by='agency_id')
        agency_list = df_agency_ordered.values.tolist()
        agency_str_list = [f'{row[0]},{row[1]}' for row in agency_list]
        return agency_str_list

    def get_date_range(self, gtfs_data_frame_dto: GtfsDataFrameDto) -> str:
        if gtfs_data_frame_dto.Feedinfos is None:
            return self.analyze_date_range_in_gtfs_data(gtfs_data_frame_dto)
        else:
            return str(gtfs_data_frame_dto.Feedinfos.feed_start_date) + '-' + str(
                gtfs_data_frame_dto.Feedinfos.feed_end_date)

    def get_date_range_based_on_selected_trip(self, gtfs_data_frame_dto: GtfsDataFrameDto, create_settings_for_table_dto : CreateSettingsForTableDto):
        selected_route = create_settings_for_table_dto.route
        if selected_route is None or selected_route.empty:
            return
        trips_df = gtfs_data_frame_dto.Trips[gtfs_data_frame_dto.Trips['route_id'].isin(selected_route['route_id'])]
        calendar_dates_df = gtfs_data_frame_dto.Calendardates[gtfs_data_frame_dto.Calendardates['service_id'].isin(trips_df['service_id'].unique())]
        if not calendar_dates_df.empty:
            start_date = pd.to_datetime(calendar_dates_df['date'].min(),format='%Y-%m-%d %H:%M:%S.%f')
            end_date = pd.to_datetime(calendar_dates_df['date'].max(),format='%Y-%m-%d %H:%M:%S.%f')
            trip_available_dates_df = pd.DataFrame({
                'route_id': [selected_route['route_id']],
                'start_date': [start_date],
                'end_date': [end_date]
            })
            create_settings_for_table_dto.date_range_df_format = trip_available_dates_df
            create_settings_for_table_dto.date = create_settings_for_table_dto.date_range_df_format.iloc[0].start_date.strftime('%Y%m%d')
            create_settings_for_table_dto.sample_date = create_settings_for_table_dto.date_range_df_format.iloc[
                0].start_date.strftime('%Y%m%d')

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