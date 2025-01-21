# -*- coding: utf-8 -*-
import logging
import re
from datetime import datetime, timedelta

import pandas as pd
from PySide6.QtCore import Signal, QObject

from model.Dto.CreateSettingsForTableDto import CreateSettingsForTableDTO
from model.Dto.CreateTableDataframeDto import CreateTableDataframeDto
from model.Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto
from model.Enum.GTFSEnums import *

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class UmlaufPlaner(QObject):
    progress_Update = Signal(int)

    def __init__(self):
        super().__init__()
        self.create_settings_for_table_dto = CreateSettingsForTableDTO()
        self.create_dataframe = CreateTableDataframeDto()
        self.gtfs_data_frame_dto = None
        self.df_filtered_stop_names = None

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
        self.progress_Update.emit(self._progress)

    @property
    def gtfs_data_frame_dto(self):
        return self._gtfs_data_frame_dto

    @gtfs_data_frame_dto.setter
    def gtfs_data_frame_dto(self, value: GtfsDataFrameDto):
        self._gtfs_data_frame_dto = value

    def check_setting_data(self) -> bool:
        if not self.check_dates_input(self.create_settings_for_table_dto.dates):
            return False

        return True


    def create_table(self):
        if ((self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.date or self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_date)
              and self.create_settings_for_table_dto.individual_sorting):
            self.progress = 10
            self.dates_prepare_data_fahrplan()
            self.progress = 20
            self.datesWeekday_select_dates_for_date_range()
            self.progress = 30
            self.dates_select_dates_delete_exception_2()
            self.progress = 40
            self.datesWeekday_select_stops_for_trips()
            self.progress = 50
            self.datesWeekday_select_for_every_date_trips_stops()
            self.progress = 70
            self.datesWeekday_create_sort_stopnames()

        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.date or self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_date:
            self.progress = 10
            self.dates_prepare_data_fahrplan()
            self.progress = 20
            self.datesWeekday_select_dates_for_date_range()
            self.progress = 30
            self.dates_select_dates_delete_exception_2()
            self.progress = 40
            self.datesWeekday_select_stops_for_trips()
            self.progress = 50
            self.datesWeekday_select_for_every_date_trips_stops()
            self.progress = 70
            self.datesWeekday_create_sort_stopnames()
            self.progress = 80
            self.datesWeekday_create_fahrplan()
            self.progress = 90

        elif ((self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.weekday or self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_weekday)
              and self.create_settings_for_table_dto.individual_sorting):
            self.progress = 10
            self.weekday_prepare_data_fahrplan()
            self.progress = 20
            self.datesWeekday_select_dates_for_date_range()
            self.progress = 30
            self.weekday_select_weekday_exception_2()
            self.progress = 40
            self.datesWeekday_select_stops_for_trips()
            self.progress = 50
            self.datesWeekday_select_for_every_date_trips_stops()
            self.progress = 70
            self.datesWeekday_create_sort_stopnames()
            self.create_sorting.emit()

        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.weekday or self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_weekday:
            self.progress = 10
            self.weekday_prepare_data_fahrplan()
            self.progress = 20
            self.datesWeekday_select_dates_for_date_range()
            self.progress = 30
            self.weekday_select_weekday_exception_2()
            self.progress = 40
            self.datesWeekday_select_stops_for_trips()
            self.progress = 50
            self.datesWeekday_select_for_every_date_trips_stops()
            self.progress = 70
            self.datesWeekday_create_fahrplan()
            self.progress = 80


    def dates_prepare_data_fahrplan(self):
        # Create a dictionary for headers
        headers = {
            'Agency': [self.create_settings_for_table_dto.agency],
            'Route': [self.create_settings_for_table_dto.route['route_id']],
            'Dates': [self.create_settings_for_table_dto.dates]
        }

        # Convert headers dictionary to DataFrame
        df_header_for_export_data = pd.DataFrame(headers)

        # Simplify DataFrame creation for direction, dates, route, and agency
        self.create_dataframe = CreateTableDataframeDto()
        self.create_dataframe.Header = df_header_for_export_data
        self.create_dataframe.Direction = pd.DataFrame({'direction_id': [self.create_settings_for_table_dto.direction]})
        self.create_dataframe.RequestedDates = pd.DataFrame(
            {'date': pd.to_datetime([self.create_settings_for_table_dto.dates], format='%Y%m%d')})
        self.create_dataframe.SelectedRoute = self.create_settings_for_table_dto.route
        self.create_dataframe.SelectedAgency = self.create_settings_for_table_dto.agency

    def datesWeekday_select_dates_for_date_range(self):
        # conditions for searching in dfs
        dfTrips = self.gtfs_data_frame_dto.Trips
        dfWeek = self.gtfs_data_frame_dto.Calendarweeks
        dfRoutes = self.gtfs_data_frame_dto.Routes
        dfSelectedRoute = self.create_dataframe.SelectedRoute
        requested_directiondf = self.create_dataframe.Direction
        dfSelectedAgency = self.create_dataframe.SelectedAgency

        selected_columns = [
            'trip_id',
            'service_id',
            'route_id',
            'start_date',
            'end_date',
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday'
        ]

        if DfTripColumnEnum.direction_id.value in dfTrips.columns:
            result = (
                dfWeek
                .merge(dfTrips, on='service_id', how='inner')
                .merge(dfRoutes, on='route_id', how='inner')
                .merge(dfSelectedRoute, on=['route_id','route_short_name','agency_id', 'route_long_name'], how='inner')
                .merge(dfSelectedAgency, on='agency_id', how='inner')
                .merge(requested_directiondf, on='direction_id', how='inner')
                .sort_values('service_id')
            )
        else:
            result = (
                dfWeek
                .merge(dfTrips, on='service_id', how='inner')
                .merge(dfRoutes, on='route_id', how='inner')
                .merge(dfSelectedRoute, on=['route_id','route_short_name','agency_id', 'route_long_name'], how='inner')
                .merge(dfSelectedAgency, on='agency_id', how='inner')
                .sort_values('service_id')
            )
        result = result[selected_columns]

        if len(result) == 0:
            raise ValueError("fahrplan_dates is empty")

        # change format
        result_copy = result.copy()
        result_copy['start_date'] = pd.to_datetime(result_copy['start_date'], format='%Y%m%d')
        result_copy['end_date'] = pd.to_datetime(result_copy['end_date'], format='%Y%m%d')
        self.create_dataframe.FahrplanDates = result_copy

    def weekday_select_weekday_exception_2(self):
        dfDates = self.dfDates
        weekcond_df = self.weekcond_df
        dfTrips = self.dfTrips
        dfWeek = self.dfWeek
        dfRoutes = self.dfRoutes
        route_short_namedf = self.route_short_namedf
        varTestAgency = self.varTestAgency
        requested_directiondf = self.requested_directiondf

        """
        add date column for every date in date range
        for every date in range create
    
        fahrplan_dates_all_dates.date,
        fahrplan_dates_all_dates.trip_id,
        fahrplan_dates_all_dates.service_id,
        fahrplan_dates_all_dates.route_id, 
        fahrplan_dates_all_dates.start_date,
        fahrplan_dates_all_dates.end_date,
        fahrplan_dates_all_dates.monday,
        fahrplan_dates_all_dates.tuesday,
        fahrplan_dates_all_dates.wednesday,
        fahrplan_dates_all_dates.thursday,
        fahrplan_dates_all_dates.friday,
        fahrplan_dates_all_dates.saturday,
        fahrplan_dates_all_dates.sunday
        """

        fahrplan_dates_all_dates = pd.concat(
            [pd.DataFrame
             ({'date': pd.date_range(row.start_date, row.end_date, freq='D'),
               'trip_id': row.trip_id,
               'service_id': row.service_id,
               'route_id': row.route_id,
               'start_date': row.start_date,
               'end_date': row.end_date,
               'monday': row.monday,
               'tuesday': row.tuesday,
               'wednesday': row.wednesday,
               'thursday': row.thursday,
               'friday': row.friday,
               'saturday': row.saturday,
               'sunday': row.sunday
               }) for i, row in self.fahrplan_dates.iterrows()], ignore_index=True)

        # need to convert the date after using iterows (itertuples might be faster)
        self.fahrplan_dates = None
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y%m%d')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['day'] = fahrplan_dates_all_dates['date'].dt.day_name()

        # set value in column to day if 1 and and compare with day
        fahrplan_dates_all_dates['monday'] = ['Monday' if x == '1' else '-' for x in fahrplan_dates_all_dates['monday']]
        fahrplan_dates_all_dates['tuesday'] = ['Tuesday' if x == '1' else '-' for x in
                                               fahrplan_dates_all_dates['tuesday']]
        fahrplan_dates_all_dates['wednesday'] = ['Wednesday' if x == '1' else '-' for x in
                                                 fahrplan_dates_all_dates['wednesday']]
        fahrplan_dates_all_dates['thursday'] = ['Thursday' if x == '1' else '-' for x in
                                                fahrplan_dates_all_dates['thursday']]
        fahrplan_dates_all_dates['friday'] = ['Friday' if x == '1' else '-' for x in fahrplan_dates_all_dates['friday']]
        fahrplan_dates_all_dates['saturday'] = ['Saturday' if x == '1' else '-' for x in
                                                fahrplan_dates_all_dates['saturday']]
        fahrplan_dates_all_dates['sunday'] = ['Sunday' if x == '1' else '-' for x in fahrplan_dates_all_dates['sunday']]

        fahrplan_dates_all_dates = fahrplan_dates_all_dates.set_index('date')

        # delete exceptions = 2 or add exceptions = 1
        # Filter fahrplan_dates_all_dates to exclude dates with exception_type = 2 in dfDates
        excluded_dates_mask = ~fahrplan_dates_all_dates.apply(lambda row: (
                (fahrplan_dates_all_dates['service_id'] == dfDates['service_id']) &
                (fahrplan_dates_all_dates['date'] == dfDates['date']) &
                (dfDates['exception_type'] == 2)).any(), axis=1)

        fahrplan_dates_all_dates_filtered = fahrplan_dates_all_dates[~excluded_dates_mask]

        # Filter fahrplan_dates_all_dates_filtered to include dates that are either weekdays or have exception_type = 1 in dfDates
        included_dates_mask = fahrplan_dates_all_dates_filtered.apply(lambda row: (
                (row['day'] in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']) |
                ((fahrplan_dates_all_dates_filtered['service_id'] == dfDates['service_id']) &
                 (fahrplan_dates_all_dates_filtered['date'] == dfDates['date']) &
                 (dfDates['exception_type'] == 1)).any()), axis=1)

        fahrplan_dates_all_dates_final = fahrplan_dates_all_dates_filtered[included_dates_mask]

        # Filter fahrplan_dates_all_dates_final to include dates that are in weekcond_df
        final_dates_mask = fahrplan_dates_all_dates_final['day'].isin(weekcond_df['day'])
        fahrplan_dates_all_dates_final = fahrplan_dates_all_dates_final[final_dates_mask]

        # Order the final DataFrame by date
        ordered_fahrplan_dates_all_dates_final = fahrplan_dates_all_dates_final.sort_values('date')

        # Select the required columns
        selected_columns = ['date', 'day', 'trip_id', 'service_id', 'route_id', 'start_date', 'end_date', 'monday',
                            'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        fahrplan_dates_all_dates = ordered_fahrplan_dates_all_dates_final[selected_columns]

        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'],
                                                          format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'],
                                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'],
                                                              format='%Y-%m-%d %H:%M:%S.%f')

        self.fahrplan_dates_all_dates = fahrplan_dates_all_dates

    def dates_select_dates_delete_exception_2(self):

        dfDates = self.gtfs_data_frame_dto.Calendardates
        requested_datesdf = pd.DataFrame([self.create_settings_for_table_dto.dates], columns=['date'])
        requested_datesdf['date'] = pd.to_datetime(requested_datesdf['date'], format='%Y%m%d')
        fahrplan_dates = self.create_dataframe.FahrplanDates

        fahrplan_dates = pd.concat(
            [pd.DataFrame
             ({'date': pd.date_range(row.start_date, row.end_date, freq='D'),
               'trip_id': row.trip_id,
               'service_id': row.service_id,
               'route_id': row.route_id,
               'start_date': row.start_date,
               'end_date': row.end_date,
               'monday': row.monday,
               'tuesday': row.tuesday,
               'wednesday': row.wednesday,
               'thursday': row.thursday,
               'friday': row.friday,
               'saturday': row.saturday,
               'sunday': row.sunday
               }) for _, row in fahrplan_dates.iterrows()])

        # need to convert the date after using iterows (itertuples might be faster)
        fahrplan_dates['date'] = pd.to_datetime(fahrplan_dates['date'], format='%Y%m%d')
        fahrplan_dates['start_date'] = pd.to_datetime(fahrplan_dates['start_date'], format='%Y%m%d')
        fahrplan_dates['end_date'] = pd.to_datetime(fahrplan_dates['end_date'], format='%Y%m%d')
        fahrplan_dates['day'] = fahrplan_dates['date'].dt.day_name()

        # set value in column to day if 1 and compare with day
        fahrplan_dates['monday'] = ['Monday' if x == '1' else '-' for x in fahrplan_dates['monday']]
        fahrplan_dates['tuesday'] = ['Tuesday' if x == '1' else '-' for x in
                                     fahrplan_dates['tuesday']]
        fahrplan_dates['wednesday'] = ['Wednesday' if x == '1' else '-' for x in
                                       fahrplan_dates['wednesday']]
        fahrplan_dates['thursday'] = ['Thursday' if x == '1' else '-' for x in
                                      fahrplan_dates['thursday']]
        fahrplan_dates['friday'] = ['Friday' if x == '1' else '-' for x in fahrplan_dates['friday']]
        fahrplan_dates['saturday'] = ['Saturday' if x == '1' else '-' for x in
                                      fahrplan_dates['saturday']]
        fahrplan_dates['sunday'] = ['Sunday' if x == '1' else '-' for x in fahrplan_dates['sunday']]

        fahrplan_dates_df = fahrplan_dates[['date', 'day', 'trip_id', 'service_id', 'route_id', 'start_date', 'end_date','monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']]
        dfDates['date'] =  pd.to_datetime(dfDates['date'], format='%Y%m%d')
        exception_type_dates = dfDates[dfDates['service_id'].isin(fahrplan_dates_df['service_id'])]
        exception_type_dates = exception_type_dates[exception_type_dates['date'].isin(requested_datesdf['date'])]
        exception_type_1_dates = exception_type_dates[exception_type_dates['exception_type'] == 1]
        exception_type_2_dates = exception_type_dates[exception_type_dates['exception_type'] == 2]

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        fahrplan_dates_df_date = fahrplan_dates_df[(fahrplan_dates_df['date'].isin(requested_datesdf['date']))]

        #fahrplan_dates_df_date = fahrplan_dates_df_date[(fahrplan_dates_df_date['service_id'].isin(exception_type_1_dates['service_id']))]
        for _, row in exception_type_1_dates.iterrows():
            # Check if the record is not already in fahrplan_dates_df_date
            if row['service_id'] not in fahrplan_dates_df_date['service_id'].values:
                # Add the record to fahrplan_dates_df_date
                fahrplan_dates_df_date = pd.concat([fahrplan_dates_df_date, row.to_frame().T], ignore_index=True)

        fahrplan_dates_df_date = fahrplan_dates_df_date[(~fahrplan_dates_df_date['service_id'].isin(exception_type_2_dates['service_id']))]
        fahrplan_dates_df_date = fahrplan_dates_df_date[(fahrplan_dates_df_date['day'].isin(days))]

        fahrplan_dates_df = fahrplan_dates_df_date.drop_duplicates()

        fahrplan_dates_df['date'] = pd.to_datetime(fahrplan_dates_df['date'],
                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_df['start_date'] = pd.to_datetime(fahrplan_dates_df['start_date'],
                                                      format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_df['end_date'] = pd.to_datetime(fahrplan_dates_df['end_date'],
                                                    format='%Y-%m-%d %H:%M:%S.%f')
        self.create_dataframe.FahrplanDates = fahrplan_dates_df

    def datesWeekday_select_stops_for_trips(self):

        requested_datesdf = pd.DataFrame([self.create_settings_for_table_dto.dates], columns=['date'])
        requested_datesdf['date'] = pd.to_datetime(requested_datesdf['date'], format='%Y%m%d')

        dfselected_Route_Id = self.create_dataframe.SelectedRoute
        requested_directiondf = self.create_dataframe.Direction.astype('string')
        varTestAgency = self.create_dataframe.SelectedAgency

        dfRoutes = self.gtfs_data_frame_dto.Routes
        dfRoutes = pd.merge(left=dfRoutes, right=dfselected_Route_Id, how='inner', on=[DfRouteColumnEnum.route_id.value, DfRouteColumnEnum.route_short_name.value, DfRouteColumnEnum.agency_id.value, DfRouteColumnEnum.route_long_name.value])
        dfRoutes = pd.merge(left=dfRoutes, right=varTestAgency, how='inner', on=DfRouteColumnEnum.agency_id.value)
        dfTrip = self.gtfs_data_frame_dto.Trips
        if "direction_id" in dfTrip.columns:
            dfTrip['direction_id'] = dfTrip['direction_id'].astype('string')
            dfTrip = pd.merge(left=dfTrip, right=requested_directiondf, how='inner', on='direction_id')
        dfTrip = pd.merge(left=dfTrip, right=dfRoutes, how='inner', on='route_id')
        dfStopTimes = self.gtfs_data_frame_dto.Stoptimes
        dfTrip['trip_id'] = dfTrip['trip_id'].astype('string')
        dfStopTimes['trip_id'] = dfStopTimes['trip_id'].astype('string')
        dfStopTimes = pd.merge(left=dfStopTimes, right=dfTrip, how='inner', left_on='trip_id', right_on='trip_id')
        dfStops = self.gtfs_data_frame_dto.Stops

        joined_df = pd.merge(dfStopTimes, dfTrip[['trip_id', 'service_id']], left_on=['trip_id', 'service_id'],
                             right_on=['trip_id', 'service_id'])
        joined_df = pd.merge(joined_df, dfStops[['stop_id', 'stop_name']], left_on='stop_id', right_on='stop_id')

        min_stop_sequence = joined_df['stop_sequence'].min()
        first_stop_times = joined_df[joined_df['stop_sequence'] == min_stop_sequence][['arrival_time', 'trip_id']]

        merged_df = pd.merge(joined_df, first_stop_times.rename(columns={'arrival_time': 'start_time'}), on='trip_id',
                             how='left')

        selected_columns = ['start_time', 'trip_id', 'stop_name', 'stop_sequence', 'arrival_time', 'service_id',
                            'stop_id']
        cond_select_stops_for_trips_pandas = merged_df[selected_columns]

        if cond_select_stops_for_trips_pandas.empty:
            second_stop_times = joined_df[joined_df['stop_sequence'] == 1][['arrival_time', 'trip_id']]
            merged_df = pd.merge(joined_df, second_stop_times.rename(columns={'arrival_time': 'start_time'}),
                                 on='trip_id', how='left')
            selected_columns_one = ['start_time', 'trip_id', 'stop_name', 'stop_sequence', 'arrival_time', 'service_id',
                                    'stop_id']
            cond_select_stops_for_tripsOne_pandas = merged_df[selected_columns_one]
            self.create_dataframe.FahrplanStops = cond_select_stops_for_tripsOne_pandas
            return

        self.create_dataframe.FahrplanStops = cond_select_stops_for_trips_pandas

    def datesWeekday_select_for_every_date_trips_stops(self):

        fahrplan_calendar_weeks = self.create_dataframe.FahrplanStops.copy()
        fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype('string')
        fahrplan_dates_all_dates = self.create_dataframe.FahrplanDates
        fahrplan_dates_all_dates['trip_id'] = fahrplan_dates_all_dates['trip_id'].astype('string')

        joined_df = pd.merge(fahrplan_dates_all_dates, fahrplan_calendar_weeks, left_on=['trip_id', 'service_id'],
                             right_on=['trip_id', 'service_id'], how='left')
        joined_df = joined_df.dropna(subset=['stop_id'])

        ordered_df = joined_df.sort_values(by=['date', 'stop_sequence', 'start_time', 'trip_id'])
        selected_columns = ['date', 'day', 'start_time', 'trip_id', 'stop_name', 'stop_sequence', 'arrival_time',
                            'service_id', 'stop_id']
        ordered_df = ordered_df[selected_columns]
        ordered_df['arrival_time'] = ordered_df['arrival_time'].apply(
            lambda x: self.time_in_string(x))
        ordered_df['start_time'] = ordered_df['start_time'].apply(
            lambda x: self.time_in_string(x))
        sorted_df = ordered_df.sort_values(by=['trip_id', 'date', 'stop_sequence'])

        selected_columns = ['date', 'day', 'start_time', 'arrival_time', 'stop_name', 'stop_sequence', 'stop_id',
                            'trip_id']
        sorted_df = sorted_df[selected_columns]
        self.create_dataframe.SortedDataframe = sorted_df

    def datesWeekday_create_sort_stopnames(self):
        sorted_df = self.create_dataframe.SortedDataframe
        filtered_df = self.filterStopSequence(sorted_df)

        df_filtered_stop_names = pd.DataFrame.from_dict(filtered_df)
        df_filtered_stop_names["stop_sequence"] = df_filtered_stop_names["stop_sequence"].astype('int32')
        df_filtered_stop_names = df_filtered_stop_names.sort_index(axis=0)

        self.create_dataframe.FilteredStopNamesDataframe = df_filtered_stop_names

    def datesWeekday_create_fahrplan_continue(self):
        sortedDataframe = self.create_dataframe.SortedDataframe
        sortedDataframe.rename(columns=lambda x: f'sorted_{x}', inplace=True)
        df_filtered_stop_names = self.create_dataframe.FilteredStopNamesDataframe
        joined_df = pd.merge(sortedDataframe, df_filtered_stop_names, left_on='sorted_stop_id', right_on='stop_id',
                             how='left')

        grouped_df = joined_df.groupby(
            ['sorted_date', 'sorted_day', 'sorted_start_time', 'sorted_arrival_time', 'sorted_trip_id', 'sorted_stop_name', 'stop_sequence',
             'sorted_stop_sequence', 'sorted_stop_id'])


        aggregated_df = grouped_df.size().reset_index(name='count')
        ordered_df = aggregated_df.sort_values(by=['sorted_date', 'sorted_stop_sequence', 'sorted_start_time', 'sorted_trip_id'])

        selected_columns = ['sorted_date', 'sorted_day', 'sorted_start_time', 'sorted_trip_id', 'sorted_stop_name', 'stop_sequence',
                            'sorted_stop_sequence', 'sorted_arrival_time', 'sorted_stop_id']

        fahrplan_calendar_weeks = ordered_df[selected_columns].copy()
        fahrplan_calendar_weeks['sorted_date'] = pd.to_datetime(fahrplan_calendar_weeks['sorted_date'], format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_calendar_weeks['sorted_arrival_time'] = fahrplan_calendar_weeks['sorted_arrival_time'].astype('string')
        fahrplan_calendar_weeks['sorted_start_time'] = fahrplan_calendar_weeks['sorted_start_time'].astype('string')
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.drop(columns=['sorted_stop_sequence'])
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.groupby(
            ['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id', 'sorted_start_time',
             'sorted_trip_id']).first().reset_index()
        fahrplan_calendar_weeks['sorted_date'] = pd.to_datetime(fahrplan_calendar_weeks['sorted_date'], format='%Y-%m-%d')
        fahrplan_calendar_weeks['sorted_arrival_time'] = fahrplan_calendar_weeks['sorted_arrival_time'].astype('string')

        if self.create_settings_for_table_dto.timeformat == 1:
            fahrplan_calendar_weeks['sorted_arrival_time'] = fahrplan_calendar_weeks['sorted_arrival_time'].apply(
                lambda x: self.time_delete_seconds(x))

        fahrplan_calendar_weeks['sorted_start_time'] = fahrplan_calendar_weeks['sorted_start_time'].astype('string')

        self.create_dataframe.FahrplanCalendarFilterDaysPivot = fahrplan_calendar_weeks.pivot(
            index=['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id'], columns=['sorted_start_time', 'sorted_trip_id'],
            values='sorted_arrival_time')

        self.create_dataframe.FahrplanCalendarFilterDaysPivot = self.create_dataframe.FahrplanCalendarFilterDaysPivot.sort_index(
            axis=1)
        self.create_dataframe.FahrplanCalendarFilterDaysPivot = self.create_dataframe.FahrplanCalendarFilterDaysPivot.sort_index(
            axis=0)

    def datesWeekday_create_fahrplan(self):

        sortedDataframe = self.create_dataframe.SortedDataframe
        sortedDataframe.rename(columns=lambda x: f'sorted_{x}', inplace=True)
        df_filtered_stop_names = self.create_dataframe.FilteredStopNamesDataframe
        joined_df = pd.merge(sortedDataframe, df_filtered_stop_names, left_on='sorted_stop_id', right_on='stop_id',
                             how='left')
        grouped_df = joined_df.groupby(
            ['sorted_date', 'sorted_day', 'sorted_start_time', 'sorted_arrival_time', 'sorted_trip_id', 'sorted_stop_name', 'stop_sequence',
             'sorted_stop_sequence', 'sorted_stop_id'])
        aggregated_df = grouped_df.size().reset_index(name='count')
        ordered_df = aggregated_df.sort_values(by=['sorted_date', 'sorted_stop_sequence', 'sorted_start_time', 'sorted_trip_id'])
        selected_columns = ['sorted_date', 'sorted_day', 'sorted_start_time', 'sorted_trip_id', 'sorted_stop_name', 'stop_sequence',
                            'sorted_stop_sequence', 'sorted_arrival_time', 'sorted_stop_id']

        fahrplan_calendar_weeks = ordered_df[selected_columns].copy()
        fahrplan_calendar_weeks['sorted_date'] = pd.to_datetime(fahrplan_calendar_weeks['sorted_date'], format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_calendar_weeks['sorted_arrival_time'] = fahrplan_calendar_weeks['sorted_arrival_time'].astype('string')
        fahrplan_calendar_weeks['sorted_start_time'] = fahrplan_calendar_weeks['sorted_start_time'].astype('string')
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.groupby(
            ['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id', 'sorted_start_time',
             'sorted_trip_id']).first().reset_index()
        fahrplan_calendar_weeks['sorted_date'] = pd.to_datetime(fahrplan_calendar_weeks['sorted_date'], format='%Y-%m-%d')
        fahrplan_calendar_weeks['sorted_arrival_time'] = fahrplan_calendar_weeks['sorted_arrival_time'].astype('string')

        if self.create_settings_for_table_dto.timeformat == 1:
            fahrplan_calendar_weeks['sorted_arrival_time'] = fahrplan_calendar_weeks['sorted_arrival_time'].apply(
                lambda x: self.time_delete_seconds(x))

        fahrplan_calendar_weeks['sorted_start_time'] = fahrplan_calendar_weeks['sorted_start_time'].astype('string')

        self.create_dataframe.GftsTableData = fahrplan_calendar_weeks

        self.create_dataframe.FahrplanCalendarFilterDaysPivot = fahrplan_calendar_weeks.pivot(
            index=['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id'], columns=['sorted_start_time', 'sorted_trip_id'],
            values='sorted_arrival_time')

        self.create_dataframe.FahrplanCalendarFilterDaysPivot = self.create_dataframe.FahrplanCalendarFilterDaysPivot.sort_index(
            axis=1)
        self.create_dataframe.FahrplanCalendarFilterDaysPivot = self.create_dataframe.FahrplanCalendarFilterDaysPivot.sort_index(
            axis=0)

    def filterStopSequence(self, data):
        """
        take all stop ids and search for the earlist stoptime
        for each stop to determine sorting
        """
        stopsequence = {}
        sorted_stopsequence = {
            "stop_id": [],
            "stop_sequence": [],
            "stop_name": [],
            "start_time": []
        }

        for stop_name_i in data.itertuples():

            if not self.dictForEntry(stopsequence, "stop_id", stop_name_i.stop_id):
                temp = {"stop_sequence": -1, "stop_name": '', "trip_id": '', "start_time": '', "arrival_time": ''}
                temp["stop_sequence"] = stop_name_i.stop_sequence
                temp["stop_name"] = stop_name_i.stop_name
                temp["trip_id"] = stop_name_i.trip_id

                if self.check_hour_24(stop_name_i.start_time):
                    comparetime_i = str((stop_name_i.date.strftime(
                        '%Y-%m-%d'))) + ' 0' + str(int(stop_name_i.start_time.split(':')[0]) - 24) + ':' + \
                                    stop_name_i.start_time.split(':')[1] + ':' + \
                                    stop_name_i.start_time.split(':')[2]
                    time_i = datetime.strptime(comparetime_i, '%Y-%m-%d %H:%M:%S')
                    time_i = time_i + timedelta(days=1)
                else:
                    comparetime_i = str((stop_name_i.date.strftime(
                        '%Y-%m-%d'))) + ' ' + stop_name_i.start_time
                    time_i = datetime.strptime(comparetime_i, '%Y-%m-%d %H:%M:%S')

                if self.check_hour_24(stop_name_i.arrival_time):
                    time_arrival_i = str((stop_name_i.date.strftime(
                        '%Y-%m-%d'))) + ' 0' + str(int(stop_name_i.arrival_time.split(':')[0]) - 24) + ':' + \
                                     stop_name_i.arrival_time.split(':')[1] + ':' + \
                                     stop_name_i.arrival_time.split(':')[2]
                    time_arrival_i = datetime.strptime(time_arrival_i, '%Y-%m-%d %H:%M:%S')
                    time_arrival_i = time_arrival_i + timedelta(days=1)
                else:
                    time_arrival_i = str((stop_name_i.date.strftime(
                        '%Y-%m-%d'))) + ' ' + stop_name_i.arrival_time
                    time_arrival_i = datetime.strptime(time_arrival_i, '%Y-%m-%d %H:%M:%S')

                temp["start_time"] = time_i
                temp["arrival_time"] = time_arrival_i

                # search in data and compare the ids
                for stop_name_j in data.itertuples():
                    # if ids match continue comparison
                    if stop_name_i.stop_id == stop_name_j.stop_id:
                        # 23072022
                        # and stop_name_i.trip_id == stop_name_j.trip_id\
                        if self.check_hour_24(stop_name_j.start_time):
                            comparetime_j = str((stop_name_j.date.strftime(
                                '%Y-%m-%d'))) + ' 0' + str(
                                int(stop_name_j.start_time.split(':')[0]) - 24) + ':' + \
                                            stop_name_j.start_time.split(':')[1] + ':' + \
                                            stop_name_j.start_time.split(':')[2]

                            time_j = datetime.strptime(comparetime_j, '%Y-%m-%d %H:%M:%S')
                            time_j = time_j + timedelta(days=1)
                        else:
                            comparetime_j = str((stop_name_j.date.strftime(
                                '%Y-%m-%d'))) + ' ' + stop_name_j.start_time
                            time_j = datetime.strptime(comparetime_j, '%Y-%m-%d %H:%M:%S')

                        time_temp = temp["start_time"]

                        if self.check_hour_24(stop_name_j.arrival_time):
                            time_arrival_j = str((stop_name_j.date.strftime(
                                '%Y-%m-%d'))) + ' 0' + str(
                                int(stop_name_j.arrival_time.split(':')[0]) - 24) + ':' + \
                                             stop_name_j.arrival_time.split(':')[1] + ':' + \
                                             stop_name_j.arrival_time.split(':')[2]
                            time_arrival_j = datetime.strptime(time_arrival_j, '%Y-%m-%d %H:%M:%S')
                            time_arrival_j = time_arrival_j + timedelta(days=1)
                        else:
                            time_arrival_j = str((stop_name_j.date.strftime(
                                '%Y-%m-%d'))) + ' ' + stop_name_j.arrival_time
                            time_arrival_j = datetime.strptime(time_arrival_j, '%Y-%m-%d %H:%M:%S')

                        arrival_time_temp = temp["arrival_time"]

                        if time_j < time_i \
                                and time_j < time_temp \
                                and stop_name_j.stop_sequence > stop_name_i.stop_sequence \
                                and stop_name_j.stop_sequence > temp["stop_sequence"]:
                            temp["start_time"] = time_j
                            temp["arrival_time"] = time_arrival_j
                            # temp["arrival_time"] = stop_name_j.arrival_time
                            temp["stop_sequence"] = stop_name_j.stop_sequence


                stopsequence[stop_name_i.stop_id] = temp

        new_stopsequence = self.sortStopSequence(stopsequence)

        for stop_sequence in new_stopsequence.keys():
            sorted_stopsequence['stop_id'].append(new_stopsequence[stop_sequence]['stop_id'])
            sorted_stopsequence['stop_sequence'].append(stop_sequence)
            sorted_stopsequence['stop_name'].append(new_stopsequence[stop_sequence]['stop_name'])
            sorted_stopsequence['start_time'].append(new_stopsequence[stop_sequence]['start_time'])

        return sorted_stopsequence

    def sortStopSequence(self, stopsequence):
        """
        sort dict of stops (cust. bubble sort)
        """
        sequence_count = len(stopsequence)

        # init data structure
        d = {}
        for k in range(sequence_count):
            d[str(k)] = {"start_time": datetime.strptime('1901-01-01 23:59:00', '%Y-%m-%d %H:%M:%S').time(),
                         "arrival_time": datetime.strptime('1901-01-01 23:59:00', '%Y-%m-%d %H:%M:%S').time(),
                         "stop_name": '',
                         "stop_id": ''
                         }

        # fill new dict
        for k, j in enumerate(stopsequence):
            if d[str(k)]["stop_id"] == '':
                d[str(k)]["stop_id"] = j
                d[str(k)]["start_time"] = stopsequence[j]['start_time']
                d[str(k)]["arrival_time"] = stopsequence[j]['arrival_time']
                d[str(k)]["stop_sequence"] = stopsequence[j]['stop_sequence']
                d[str(k)]["stop_name"] = stopsequence[j]['stop_name']

        if self.create_settings_for_table_dto.individual_sorting == 1:
            # bubble sort
            for i in range(sequence_count - 1):
                for j in range(0, sequence_count - i - 1):
                    if d[str(j)]["stop_sequence"] > d[str(j + 1)]["stop_sequence"]:
                        d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
                    elif d[str(j)]["stop_sequence"] == d[str(j + 1)]["stop_sequence"]:
                        if d[str(j)]["start_time"] > d[str(j + 1)]["start_time"]:
                            d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]

        else:
            # bubble sort
            for i in range(sequence_count - 1):
                for j in range(0, sequence_count - i - 1):
                    if d[str(j)]["stop_sequence"] > d[str(j + 1)]["stop_sequence"]:
                        d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
                    elif d[str(j)]["stop_sequence"] == d[str(j + 1)]["stop_sequence"]:
                        if d[str(j)]["start_time"] > d[str(j + 1)]["start_time"]:
                            d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
        return d

    # checks if in dictonary
    def dictForEntry(self, temp, key, key_value):
        if key_value in temp:
            return True
        else:
            return False

    # the is the one way to add a 0 to the time hh:mm:ss, if 0 is missing like in 6:44:33
    def time_in_string(self, time):
        pattern = re.findall(r'^\d{1}:\d{2}:\d{2}$', time)

        if pattern:
            return '0' + time
        else:
            return time

    # the is the one way to add a 0 to the time hh:mm:ss, if 0 is missing like in 6:44:33
    def time_delete_seconds(self, time):
        return time[:-3]

    # checks if date string
    def check_dates_input(self, dates):
        pattern1 = re.findall(r'^\d{8}(?:\d{8})*(?:,\d{8})*$', dates)
        if pattern1:
            return True
        else:
            return False

    def check_KommaInText(self, dates):
        pattern1 = re.findall(r'"\w*,\w*"', dates)
        if pattern1:
            logging.debug(pattern1)
            return True
        else:
            return False

    # checks if time-string exceeds 24 hour format
    def check_hour_24(self, time):
        try:
            pattern1 = re.findall(r'^2{1}[4-9]{1}:[0-9]{2}', time)
            if pattern1:
                return True
            else:
                return False
        except:
            logging.debug(time)