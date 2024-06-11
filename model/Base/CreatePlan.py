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
from PyQt5.QtCore import pyqtSignal, QObject, QCoreApplication
import sys
import os
from ..Base.GTFSEnums import CreatePlanMode
from model.Base.ProgressBar import ProgressBar
from ..DTO.CreateSettingsForTableDTO import CreateSettingsForTableDTO
from ..DTO.General_Transit_Feed_Specification import GtfsListDto, GtfsDataFrameDto

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class CreatePlan(QObject):
    progress_Update = pyqtSignal(int)
    error_occured = pyqtSignal(str)
    create_sorting = pyqtSignal()
    def __init__(self, app, progress: int):
        super().__init__()
        self.reset_create = False
        self.create_plan_mode = None
        self.gtfs_data_frame_dto = None
        self.df_filtered_stop_names = None
        self.create_settings_for_table_dto = CreateSettingsForTableDTO()

        """ property """
        self.input_path = ""
        self.pickle_save_path = ""
        self.time_format = 1

        """ visual internal property """
        self.progress = progress

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

    def create_table(self):
        if self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.date and self.create_settings_for_table_dto.individual_sorting:
            self.progress = 0
            logging.debug(f"PREPARE intividual date ")
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
            self.progress = 60
            self.datesWeekday_select_stop_sequence_stop_name_sorted()
            self.progress = 70
            self.datesWeekday_create_sort_stopnames()
            self.create_sorting.emit()
        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.date:
            self.progress = 0
            logging.debug(f"PREPARE date ")
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
            self.progress = 60
            self.datesWeekday_select_stop_sequence_stop_name_sorted()
            self.progress = 70
            self.datesWeekday_create_fahrplan()
            self.progress = 80
            self.datesWeekday_create_output_fahrplan()
            self.progress = 100

        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.weekday and self.create_settings_for_table_dto.individual_sorting:
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
            self.progress = 60
            self.datesWeekday_select_stop_sequence_stop_name_sorted()
            self.progress = 70
            self.datesWeekday_create_sort_stopnames()
            self.create_sorting.emit()

        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.weekday:
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
            self.progress = 60
            self.datesWeekday_select_stop_sequence_stop_name_sorted()
            self.progress = 70
            self.datesWeekday_create_fahrplan()
            self.progress = 80
            self.datesWeekday_create_output_fahrplan()
            self.progress = 100

    def create_table_continue(self):
        self.datesWeekday_create_fahrplan_continue()
        self.progress = 80
        self.datesWeekday_create_output_fahrplan()
        self.progress = 100

    def dates_prepare_data_fahrplan(self):
        self.last_time = time.time()

        if not self.check_dates_input(self.selected_dates):
            return

        # DataFrame for header information
        self.header_for_export_data = {'Agency': [self.selectedAgency],
                                       'Route': [self.selectedRoute],
                                       'Dates': [self.selected_dates]
                                       }
        self.dfheader_for_export_data = pd.DataFrame.from_dict(self.header_for_export_data)

        dummy_direction = 0
        direction = [{'direction_id': dummy_direction}
                     ]
        self.dfdirection = pd.DataFrame(direction)

        # dataframe with requested data
        self.requested_dates = {'date': [self.selected_dates]}
        self.requested_datesdf = pd.DataFrame.from_dict(self.requested_dates)
        self.requested_datesdf['date'] = pd.to_datetime(self.requested_datesdf['date'], format='%Y%m%d')

        self.requested_direction = {'direction_id': [self.selected_direction]}
        self.requested_directiondf = pd.DataFrame.from_dict(self.requested_direction)

        inputVar = [{'route_short_name': self.selectedRoute}]
        self.route_short_namedf = pd.DataFrame(inputVar)

        inputVarAgency = [{'agency_id': self.selectedAgency}]
        self.varTestAgency = pd.DataFrame(inputVarAgency)

    def datesWeekday_select_dates_for_date_range(self):
        # conditions for searching in dfs
        dfTrips = self.gtfs_data_frame_dto.Trips
        dfWeek = self.gtfs_data_frame_dto.Calendarweeks
        dfRoutes = self.gtfs_data_frame_dto.Routes
        route_short_namedf = self.create_settings_for_table_dto.route
        varTestAgency = self.create_settings_for_table_dto.agency
        requested_directiondf = self.create_settings_for_table_dto.direction

        filtered_dfRoutes = dfRoutes[dfRoutes['route_short_name'].isin(route_short_namedf['route_short_name']) &
                                     dfRoutes['agency_id'].isin(varTestAgency['agency_id'])]

        # Filter dfTrips based on direction_id
        filtered_dfTrips = dfTrips[dfTrips['direction_id'].isin(requested_directiondf['direction_id'])]

        # Merge filtered_dfRoutes with filtered_dfTrips on route_id
        merged_df = pd.merge(filtered_dfTrips, filtered_dfRoutes[['route_id', 'service_id']], on='route_id')

        # Merge merged_df with dfWeek on service_id
        final_df = pd.merge(merged_df, dfWeek[['start_date', 'end_date', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'service_id']], left_on='service_id', right_on='service_id')

        # Order final_df by service_id
        final_df = final_df.sort_values(by=['service_id'])

        # Select columns as per the original SQL query
        selected_columns = ['trip_id', 'service_id', 'route_id', 'start_date', 'end_date', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        cond_select_dates_for_date_range_pandas = final_df[selected_columns]

        # change format
        self.fahrplan_dates['start_date'] = pd.to_datetime(self.fahrplan_dates['start_date'], format='%Y%m%d')
        self.fahrplan_dates['end_date'] = pd.to_datetime(self.fahrplan_dates['end_date'], format='%Y%m%d')

    def weekday_select_weekday_exception_2(self):
        dfDates = self.dfDates
        weekcond_df = self.weekcond_df
        dfTrips = self.dfTrips
        dfWeek = self.dfWeek
        dfRoutes = self.dfRoutes
        route_short_namedf = self.route_short_namedf
        varTestAgency = self.varTestAgency
        requested_directiondf = self.requested_directiondf

        cond_select_dates_delete_exception_2 = '''
                        select  
                                fahrplan_dates_all_dates.date,
                                fahrplan_dates_all_dates.day,
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
                        from fahrplan_dates_all_dates 
                              -- not has exception_type = 2
                        where fahrplan_dates_all_dates.date not in (select dfDates.date
                                                                      from dfDates                                                            
                                                                        where fahrplan_dates_all_dates.service_id = dfDates.service_id 
                                                                          and fahrplan_dates_all_dates.date = dfDates.date
                                                                          and dfDates.exception_type = 2
                                                                    )
                          -- and is marked as the day of the week or is has exception_type = 1                          
                          and (  (   fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.monday
                                  or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.tuesday
                                  or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.wednesday
                                  or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.thursday
                                  or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.friday
                                  or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.saturday
                                  or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.sunday
                                 )
                                 or 
                                 (   fahrplan_dates_all_dates.date in (select dfDates.date
                                                                      from dfDates                                                            
                                                                        where fahrplan_dates_all_dates.service_id = dfDates.service_id 
                                                                          and fahrplan_dates_all_dates.date = dfDates.date
                                                                          and dfDates.exception_type = 1
                                                                     )    
                                 )
                              )
                          -- and the day is requested   
                          and fahrplan_dates_all_dates.day in (select weekcond_df.day
                                                                      from weekcond_df                                                            
                                                                        where fahrplan_dates_all_dates.day = weekcond_df.day
                                                             )  
                        order by fahrplan_dates_all_dates.date;
                       '''

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
        fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_2, locals())
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'],
                                                          format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'],
                                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'],
                                                              format='%Y-%m-%d %H:%M:%S.%f')

        self.fahrplan_dates_all_dates = fahrplan_dates_all_dates

    def dates_select_dates_delete_exception_2(self):
        dfDates = self.dfDates
        dfTrips = self.dfTrips
        dfWeek = self.dfWeek
        dfRoutes = self.dfRoutes
        route_short_namedf = self.route_short_namedf
        varTestAgency = self.varTestAgency
        requested_directiondf = self.requested_directiondf
        requested_datesdf = self.requested_datesdf


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
        last_time = time.time()

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

        zeit = time.time() - last_time

        last_time = time.time()

        # need to convert the date after using iterows (itertuples might be faster)
        self.fahrplan_dates = None
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y%m%d')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['day'] = fahrplan_dates_all_dates['date'].dt.day_name()

        # set value in column to day if 1 and compare with day
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

        zeit = time.time() - last_time

        last_time = time.time()

        # Filter fahrplan_dates_all_dates to exclude dates with exception_type = 2 in dfDates
        excluded_dates_mask = ~fahrplan_dates_all_dates.apply(lambda row: (
            (fahrplan_dates_all_dates['date'] == dfDates.loc[(dfDates['service_id'] == row['service_id']) & (dfDates['exception_type'] == 2), 'date']).any()
        ), axis=1)

        fahrplan_dates_all_dates_filtered = fahrplan_dates_all_dates[~excluded_dates_mask]

        # Filter fahrplan_dates_all_dates_filtered to include dates in requested_datesdf
        included_dates_mask = fahrplan_dates_all_dates_filtered['date'].isin(requested_datesdf['date'])
        fahrplan_dates_all_dates_final = fahrplan_dates_all_dates_filtered[included_dates_mask]

        # Further filter to include dates with exception_type = 1 in dfDates
        dates_with_exception_type_1 = dfDates[dfDates['exception_type'] == 1]['date']
        fahrplan_dates_all_dates_final = fahrplan_dates_all_dates_final[fahrplan_dates_all_dates_final['date'].isin(dates_with_exception_type_1)]

        # Ensure the day column matches one of the days of the week
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        valid_days_mask = fahrplan_dates_all_dates_final['day'].isin(days_of_week)
        fahrplan_dates_all_dates_final = fahrplan_dates_all_dates_final[valid_days_mask]

        # Select columns as per the original SQL query
        selected_columns = ['date', 'day', 'trip_id', 'service_id', 'route_id', 'start_date', 'end_date', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        cond_select_dates_delete_exception_2_pandas = fahrplan_dates_all_dates_final[selected_columns]



        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'],
                                                          format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'],
                                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'],
                                                              format='%Y-%m-%d %H:%M:%S.%f')
        zeit = time.time() - last_time

        last_time = time.time()

        self.fahrplan_dates_all_dates = fahrplan_dates_all_dates

    def datesWeekday_select_stops_for_trips(self):


        route_short_namedf = self.route_short_namedf
        varTestAgency = self.varTestAgency
        requested_directiondf = self.requested_directiondf
        requested_directiondf['direction_id'] = requested_directiondf['direction_id'].astype('string')

        dfRoutes = self.dfRoutes
        dfRoutes = pd.merge(left=dfRoutes, right=route_short_namedf, how='inner', on='route_short_name')
        dfRoutes = pd.merge(left=dfRoutes, right=varTestAgency, how='inner', on='agency_id')
        dfTrip = self.dfTrips
        dfTrip['direction_id'] = dfTrip['direction_id'].astype('string')

        dfTrip['trip_id_dup'] = dfTrip.index
        dfTrip = dfTrip.reset_index(drop=True)
        dfTrip['trip_id_dup'] = dfTrip['trip_id_dup'].astype('string')
        dfTrip = pd.merge(left=dfTrip, right=requested_directiondf, how='inner', on='direction_id')
        # pd.concat([self.dfTrips, self.requested_directiondf], join='inner', keys='direction_id')
        dfTrip = pd.merge(left=dfTrip, right=dfRoutes, how='inner', on='route_id')
        dfStopTimes = self.dfStopTimes
        dfStopTimes['stop_id'] = dfStopTimes.index
        dfStopTimes = dfStopTimes.reset_index(drop=True)
        dfStopTimes['trip_id'] = dfStopTimes['trip_id'].astype('string')
        dfStopTimes = pd.merge(left=dfStopTimes, right=dfTrip, how='inner', left_on='trip_id', right_on='trip_id_dup')
        dfStops = self.dfStops
        last_time = time.time()


        # Join dfStopTimes with dfTrip and dfStops
        joined_df = pd.merge(dfStopTimes, dfTrip[['trip_id_dup', 'service_id']], left_on='trip_id', right_on='trip_id_dup')
        joined_df = pd.merge(joined_df, dfStops[['stop_id', 'stop_name']], left_on='stop_id', right_on='stop_id')

        # Select the arrival time at the first stop for each trip
        first_stop_times = joined_df[joined_df['stop_sequence'] == 0]['arrival_time']

        # Add the start_time column to the main DataFrame
        joined_df['start_time'] = first_stop_times.values

        # Select the required columns
        selected_columns = ['start_time', 'trip_id', 'stop_name', 'stop_sequence', 'arrival_time', 'service_id', 'stop_id']
        cond_select_stops_for_trips_pandas = joined_df[selected_columns]

        if not cond_select_stops_for_trips_pandas.empty:
            # Similar to cond_select_stops_for_trips but for the second stop
            second_stop_times = joined_df[joined_df['stop_sequence'] == 1]['arrival_time']

            # Add the start_time column to the main DataFrame for the second stop
            joined_df['start_time'] = second_stop_times.values

            # Select the required columns for the second stop
            selected_columns_one = ['start_time', 'trip_id', 'stop_name', 'stop_sequence', 'arrival_time', 'service_id', 'stop_id']
            cond_select_stops_for_tripsOne_pandas = joined_df[selected_columns_one]

        # get all stop_times and stops for every stop of one route

        dfTrip = dfTrip.drop('trip_id_dup', axis=1)
        zeit = time.time() - last_time
        last_time = time.time()

    def datesWeekday_select_for_every_date_trips_stops(self):

        fahrplan_calendar_weeks = self.fahrplan_calendar_weeks
        fahrplan_dates_all_dates = self.fahrplan_dates_all_dates
        # Perform a left join between fahrplan_dates_all_dates and fahrplan_calendar_weeks
        joined_df = pd.merge(fahrplan_dates_all_dates, fahrplan_calendar_weeks, left_on='trip_id', right_on='trip_id', how='left')

        # Order the resulting DataFrame by date, stop_sequence, start_time, and trip_id
        ordered_df = joined_df.sort_values(by=['date', 'stop_sequence', 'start_time', 'trip_id'])

        # Select the required columns
        selected_columns = ['date', 'day', 'start_time', 'trip_id', 'stop_name', 'stop_sequence', 'arrival_time', 'service_id', 'stop_id']
        self.fahrplan_calendar_weeks  = ordered_df[selected_columns]
        self.fahrplan_calendar_weeks['arrival_time'] = self.fahrplan_calendar_weeks['arrival_time'].apply(
            lambda x: self.time_in_string(x))
        self.fahrplan_calendar_weeks['start_time'] = self.fahrplan_calendar_weeks['start_time'].apply(
            lambda x: self.time_in_string(x))

        #########################

    def datesWeekday_select_stop_sequence_stop_name_sorted(self):

        fahrplan_calendar_weeks = self.fahrplan_calendar_weeks
        # Assuming fahrplan_calendar_weeks is already defined

        # Sort the DataFrame by trip_id, date, and stop_sequence
        sorted_df = fahrplan_calendar_weeks.sort_values(by=['trip_id', 'date', 'stop_sequence'])

        # Select the required columns
        selected_columns = ['date', 'day', 'start_time', 'arrival_time', 'stop_name', 'stop_sequence', 'stop_id', 'trip_id']
        self.fahrplan_sorted_stops = sorted_df[selected_columns]


    def datesWeekday_create_sort_stopnames(self):
        fahrplan_calendar_weeks = self.fahrplan_calendar_weeks
        self.filtered_stop_names = self.filterStopSequence(self.fahrplan_sorted_stops.copy())

        # create new def with filterStopSequence
        self.df_filtered_stop_names = pd.DataFrame.from_dict(self.filtered_stop_names)
        # df_deleted_dupl_stop_names["stop_name"] = df_deleted_dupl_stop_names["stop_name"].astype('string')
        self.df_filtered_stop_names["stop_sequence"] = self.df_filtered_stop_names["stop_sequence"].astype('int32')
        # self.df_filtered_stop_names = self.df_filtered_stop_names.set_index("stop_sequence")
        self.df_filtered_stop_names = self.df_filtered_stop_names.sort_index(axis=0)

    def datesWeekday_create_fahrplan_continue(self):


        fahrplan_calendar_weeks = self.fahrplan_calendar_weeks
        df_filtered_stop_names = self.df_filtered_stop_names

        # Assuming fahrplan_calendar_weeks and df_filtered_stop_names are already defined

        # Perform a left join between fahrplan_calendar_weeks and df_filtered_stop_names
        joined_df = pd.merge(fahrplan_calendar_weeks, df_filtered_stop_names, left_on='stop_id', right_on='stop_id', how='left')

        # Group the resulting DataFrame by the specified columns
        grouped_df = joined_df.groupby(['date', 'day', 'start_time', 'arrival_time', 'trip_id', 'stop_name', 'stop_sequence_sorted', 'stop_sequence', 'service_id', 'stop_id'])

        # Aggregate the grouped data (if needed, adjust the aggregation function as necessary)
        aggregated_df = grouped_df.size().reset_index(name='count')  # Example aggregation, adjust as needed

        # Order the aggregated DataFrame by date, stop_sequence, start_time, and trip_id
        ordered_df = aggregated_df.sort_values(by=['date', 'stop_sequence', 'start_time', 'trip_id'])

        # Select the required columns
        selected_columns = ['date', 'day', 'start_time', 'trip_id', 'stop_name', 'stop_sequence_sorted', 'stop_sequence', 'arrival_time', 'service_id', 'stop_id']
        fahrplan_calendar_weeks = ordered_df[selected_columns]

        ###########################

        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype('int32')
        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].astype('string')
        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].astype('string')

        # fahrplan_calendar_weeks = fahrplan_calendar_weeks.drop(columns=['stop_sequence', 'service_id', 'stop_id'])
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.drop(columns=['stop_sequence', 'service_id'])
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.groupby(
            ['date', 'day', 'stop_sequence_sorted', 'stop_name', 'stop_id', 'start_time',
             'trip_id']).first().reset_index()

        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d')
        # fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype('int32')

        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].astype('string')
        if self.timeformat == 1:
            fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].apply(
                lambda x: self.time_delete_seconds(x))

        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].astype('string')

        self.fahrplan_calendar_filter_days_pivot = fahrplan_calendar_weeks.pivot(
            index=['date', 'day', 'stop_sequence_sorted', 'stop_name', 'stop_id'], columns=['start_time', 'trip_id'],
            values='arrival_time')

        # fahrplan_calendar_filter_days_pivot['date'] = pd.to_datetime(fahrplan_calendar_filter_days_pivot['date'], format='%Y-%m-%d %H:%M:%S.%f')
        self.fahrplan_calendar_filter_days_pivot = self.fahrplan_calendar_filter_days_pivot.sort_index(axis=1)
        self.fahrplan_calendar_filter_days_pivot = self.fahrplan_calendar_filter_days_pivot.sort_index(axis=0)

        self.zeit = time.time() - self.last_time
        now = datetime.now()
        self.now = now.strftime("%Y_%m_%d_%H_%M_%S")

    def datesWeekday_create_fahrplan(self):


        fahrplan_calendar_weeks = self.fahrplan_calendar_weeks
        self.fahrplan_calendar_weeks = None
        self.filtered_stop_names = self.filterStopSequence(self.fahrplan_sorted_stops)

        """
        
        create new def with filterStopSequence
        
        """

        self.df_filtered_stop_names = pd.DataFrame.from_dict(self.filtered_stop_names)
        # df_deleted_dupl_stop_names["stop_name"] = df_deleted_dupl_stop_names["stop_name"].astype('string')
        self.df_filtered_stop_names["stop_sequence"] = self.df_filtered_stop_names["stop_sequence"].astype('int32')
        # self.df_filtered_stop_names = self.df_filtered_stop_names.set_index("stop_sequence")
        self.df_filtered_stop_names = self.df_filtered_stop_names.sort_index(axis=0)
        df_filtered_stop_names = self.df_filtered_stop_names


        # Assuming fahrplan_calendar_weeks and df_filtered_stop_names are already defined

        # Perform a left join between fahrplan_calendar_weeks and df_filtered_stop_names
        joined_df = pd.merge(fahrplan_calendar_weeks, df_filtered_stop_names, left_on='stop_id', right_on='stop_id', how='left')

        # Group the resulting DataFrame by the specified columns
        grouped_df = joined_df.groupby(['date', 'day', 'start_time', 'arrival_time', 'trip_id', 'stop_name', 'stop_sequence_sorted', 'stop_sequence', 'service_id', 'stop_id'])

        # Since the SQL query doesn't specify an aggregate function, we'll just keep the unique groups
        unique_groups_df = grouped_df.first().reset_index()

        # Order the DataFrame by date, stop_sequence, start_time, and trip_id
        ordered_df = unique_groups_df.sort_values(by=['date', 'stop_sequence', 'start_time', 'trip_id'])

        # Select the required columns
        selected_columns = ['date', 'day', 'start_time', 'trip_id', 'stop_name', 'stop_sequence_sorted', 'stop_sequence', 'arrival_time', 'service_id', 'stop_id']
        fahrplan_calendar_weeks = ordered_df[selected_columns]


        ###########################

        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype('int32')
        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].astype('string')
        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].astype('string')

        # fahrplan_calendar_weeks = fahrplan_calendar_weeks.drop(columns=['stop_sequence', 'service_id', 'stop_id'])
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.drop(columns=['stop_sequence', 'service_id'])
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.groupby(
            ['date', 'day', 'stop_sequence_sorted', 'stop_name', 'stop_id', 'start_time',
             'trip_id']).first().reset_index()

        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d')
        # fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype('int32')

        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].astype('string')
        if self.timeformat == 1:
            fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].apply(
                lambda x: self.time_delete_seconds(x))

        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].astype('string')

        self.fahrplan_calendar_filter_days_pivot = fahrplan_calendar_weeks.pivot(
            index=['date', 'day', 'stop_sequence_sorted', 'stop_name', 'stop_id'], columns=['start_time', 'trip_id'],
            values='arrival_time')

        # fahrplan_calendar_filter_days_pivot['date'] = pd.to_datetime(fahrplan_calendar_filter_days_pivot['date'], format='%Y-%m-%d %H:%M:%S.%f')
        self.fahrplan_calendar_filter_days_pivot = self.fahrplan_calendar_filter_days_pivot.sort_index(axis=1)
        self.fahrplan_calendar_filter_days_pivot = self.fahrplan_calendar_filter_days_pivot.sort_index(axis=0)

        self.zeit = time.time() - self.last_time
        now = datetime.now()
        self.now = now.strftime("%Y_%m_%d_%H_%M_%S")

        return fahrplan_calendar_weeks

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
        # data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d %H:%M:%S.%f')
        # data['date'] = data['date'].dt.strftime('%m-%Y-%d %Y')

        for stop_name_i in data.itertuples():

            if not self.dictForEntry(stopsequence, "stop_id", stop_name_i.stop_id):
                temp = {"stop_sequence": -1, "stop_name": '', "trip_id": '', "start_time": '', "arrival_time": ''}
                temp["stop_sequence"] = stop_name_i.stop_sequence
                temp["stop_name"] = stop_name_i.stop_name
                temp["trip_id"] = stop_name_i.trip_id

                if self.check_hour_24(stop_name_i.start_time):
                    comparetime_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime(
                        '%Y-%m-%d'))) + ' 0' + str(int(stop_name_i.start_time.split(':')[0]) - 24) + ':' + \
                                    stop_name_i.start_time.split(':')[1] + ':' + \
                                    stop_name_i.start_time.split(':')[2]
                    time_i = datetime.strptime(comparetime_i, '%Y-%m-%d %H:%M:%S')
                    time_i = time_i + timedelta(days=1)
                else:
                    comparetime_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime(
                        '%Y-%m-%d'))) + ' ' + stop_name_i.start_time
                    time_i = datetime.strptime(comparetime_i, '%Y-%m-%d %H:%M:%S')

                if self.check_hour_24(stop_name_i.arrival_time):
                    time_arrival_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime(
                        '%Y-%m-%d'))) + ' 0' + str(int(stop_name_i.arrival_time.split(':')[0]) - 24) + ':' + \
                                     stop_name_i.arrival_time.split(':')[1] + ':' + \
                                     stop_name_i.arrival_time.split(':')[2]
                    time_arrival_i = datetime.strptime(time_arrival_i, '%Y-%m-%d %H:%M:%S')
                    time_arrival_i = time_arrival_i + timedelta(days=1)
                else:
                    time_arrival_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime(
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
                            comparetime_j = str((datetime.strptime(stop_name_j.date,
                                                                   '%Y-%m-%d %H:%M:%S.%f').strftime(
                                '%Y-%m-%d'))) + ' 0' + str(
                                int(stop_name_j.start_time.split(':')[0]) - 24) + ':' + \
                                            stop_name_j.start_time.split(':')[1] + ':' + \
                                            stop_name_j.start_time.split(':')[2]

                            time_j = datetime.strptime(comparetime_j, '%Y-%m-%d %H:%M:%S')
                            time_j = time_j + timedelta(days=1)
                        else:
                            comparetime_j = str((datetime.strptime(stop_name_j.date,
                                                                   '%Y-%m-%d %H:%M:%S.%f').strftime(
                                '%Y-%m-%d'))) + ' ' + stop_name_j.start_time
                            time_j = datetime.strptime(comparetime_j, '%Y-%m-%d %H:%M:%S')

                        time_temp = temp["start_time"]

                        if self.check_hour_24(stop_name_j.arrival_time):
                            time_arrival_j = str((datetime.strptime(stop_name_j.date,
                                                                    '%Y-%m-%d %H:%M:%S.%f').strftime(
                                '%Y-%m-%d'))) + ' 0' + str(
                                int(stop_name_j.arrival_time.split(':')[0]) - 24) + ':' + \
                                             stop_name_j.arrival_time.split(':')[1] + ':' + \
                                             stop_name_j.arrival_time.split(':')[2]
                            time_arrival_j = datetime.strptime(time_arrival_j, '%Y-%m-%d %H:%M:%S')
                            time_arrival_j = time_arrival_j + timedelta(days=1)
                        else:
                            time_arrival_j = str((datetime.strptime(stop_name_j.date,
                                                                    '%Y-%m-%d %H:%M:%S.%f').strftime(
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

                        # if time_j < time_i \
                        # and time_j < time_temp \
                        # and time_arrival_j < time_arrival_i \
                        # and time_arrival_j < arrival_time_temp\
                        # and stop_name_j.stop_sequence > stop_name_i.stop_sequence:
                        #     temp["start_time"] = time_j
                        #     temp["arrival_time"] = time_arrival_j
                        #     # temp["arrival_time"] = stop_name_j.arrival_time
                        #     temp["stop_sequence"] = stop_name_j.stop_sequence

                stopsequence[stop_name_i.stop_id] = temp

        new_stopsequence = self.sortStopSequence(stopsequence)

        for stop_sequence in new_stopsequence.keys():
            sorted_stopsequence['stop_id'].append(new_stopsequence[stop_sequence]['stop_id'])
            sorted_stopsequence['stop_sequence'].append(stop_sequence)
            sorted_stopsequence['stop_name'].append(new_stopsequence[stop_sequence]['stop_name'])
            sorted_stopsequence['start_time'].append(new_stopsequence[stop_sequence]['start_time'])

        #
        # logging.debug('len stop_sequences {}'.format(sequence_count))
        # for stop_id in stopsequence.keys():
        #     if stop_id in new_stopsequence \
        #         and stopsequence[stop_id]['start_time'] < new_stopsequence[stop_id]['start_time'] \
        #         and stopsequence[stop_id]['arrival_time'] < new_stopsequence[stop_id]['arrival_time']:
        #         pass
        #     else:
        #         temp = {"stop_sequence": -1, "stop_name": '', "trip_id": '', "start_time": '', "arrival_time": ''}
        #         temp["start_time"] = stopsequence[stop_id]['start_time']
        #         temp["arrival_time"] = stopsequence[stop_id]['arrival_time']
        #         temp["stop_sequence"] = sequence_count - 1
        #         new_stopsequence[stop_id] = temp
        #
        #
        #
        #
        #
        #
        # logging.debug(stopsequence)
        # i = 0
        # for sequence in range(0, len(temp["stop_sequence"])):
        #     i += 1
        #     temp["stop_sequence"][sequence] = i

        return sorted_stopsequence