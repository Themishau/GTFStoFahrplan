# -*- coding: utf-8 -*-
import logging

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal
import pandas as pd
from .Progress import ProgressSignal
from ..Dto.CreateSettingsForTableDto import CreateSettingsForTableDto
from ..Dto.gtfs_data_source import GtfsDataSource


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

    def read_gtfs_agencies(self, gtfs_data_frame_dto: GtfsDataSource):
        df_agency = gtfs_data_frame_dto.Agencies
        df_agency_ordered = df_agency.sort_values(by='agency_id')
        agency_list = df_agency_ordered.values.tolist()
        agency_str_list = [f'{row[0]},{row[1]}' for row in agency_list]
        return agency_str_list

    def get_date_range(self, gtfs_data_frame_dto: GtfsDataSource):
        feed_info = gtfs_data_frame_dto.Feedinfos
        if feed_info is None or feed_info.empty:
            return self.analyze_date_range_in_gtfs_data(gtfs_data_frame_dto)
        else:
            return str(feed_info.iloc[0].feed_start_date) + '-' + str(feed_info.iloc[0].feed_end_date)

    def get_date_range_based_on_selected_trip(self, gtfs_data_frame_dto: GtfsDataSource, create_settings_for_table_dto : CreateSettingsForTableDto):
        selected_route = create_settings_for_table_dto.route
        if selected_route is None or selected_route.empty:
            return
        trips_df = gtfs_data_frame_dto.get_trips(route_id=selected_route.iloc[0]['route_id'])
        calendar_dates_df = gtfs_data_frame_dto.Calendardates
        calendar_dates_df = calendar_dates_df[calendar_dates_df.service_id.isin(trips_df.service_id)]
        calendar = gtfs_data_frame_dto.Calendarweeks
        calendar = calendar[calendar.service_id.isin(trips_df.service_id)]
        starts = pd.concat([pd.to_datetime(calendar.start_date, format='%Y%m%d'), calendar_dates_df.date])
        ends = pd.concat([pd.to_datetime(calendar.end_date, format='%Y%m%d'), calendar_dates_df.date])
        if not starts.empty:
            start_date = starts.min()
            end_date = ends.max()
            trip_available_dates_df = pd.DataFrame({
                'route_id': [selected_route['route_id']],
                'start_date': [start_date],
                'end_date': [end_date]
            })
            create_settings_for_table_dto.date_range_df_format = trip_available_dates_df
            create_settings_for_table_dto.date = create_settings_for_table_dto.date_range_df_format.iloc[0].start_date.strftime('%Y%m%d')
            create_settings_for_table_dto.sample_date = create_settings_for_table_dto.date_range_df_format.iloc[
                0].start_date.strftime('%Y%m%d')

    def analyze_date_range_in_gtfs_data(self, gtfs_data_frame_dto: GtfsDataSource):
        if gtfs_data_frame_dto.Calendarweeks is not None:
            return gtfs_data_frame_dto.Calendarweeks.groupby(
                ['start_date', 'end_date']).size().reset_index()
        return None

    def analyze_date_range_string(self, date_range_df_format):
        if date_range_df_format is None or date_range_df_format.empty:
            return 'No date range available'
        return str(date_range_df_format.iloc[0].start_date) + '-' + str(
                date_range_df_format.iloc[0].end_date)
