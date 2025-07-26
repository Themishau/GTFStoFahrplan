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
        self.options_dates_weekday = ['Dates', 'Weekday']
        self.week_day_options = {0: [0, 'Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday'],
                                 1: [1, 'Monday, Tuesday, Wednesday, Thursday, Friday'],
                                 2: [2, 'Monday'],
                                 3: [3, 'Tuesday'],
                                 4: [4, 'Wednesday'],
                                 5: [5, 'Thursday'],
                                 6: [6, 'Friday'],
                                 7: [7, 'Saturday'],
                                 8: [8, 'Sunday'],
                                 }

        # Create DataFrame
        self.weekday_options_df = pd.DataFrame(self.week_day_options)

        self.week_day_options_list = ['0,Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday',
                                   '1,Monday, Tuesday, Wednesday, Thursday, Friday',
                                   '2,Monday',
                                   '3,Tuesday',
                                   '4,Wednesday',
                                   '5,Thursday',
                                   '6,Friday',
                                   '7,Saturday',
                                   '8,Sunday']

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
        # trip_available_dates_df = pd.DataFrame(columns=['route_id', 'start_date', 'end_date'])
        # trip_available_dates_df['start_date'] = pd.to_datetime(fahrplan_dates_df['start_date'],
        #                                                  format='%Y-%m-%d %H:%M:%S.%f')
        # trip_available_dates_df['end_date'] = pd.to_datetime(fahrplan_dates_df['end_date'],
        #                                                format='%Y-%m-%d %H:%M:%S.%f')

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






