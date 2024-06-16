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

    def check_setting_data(self) -> bool:
        if not self.check_dates_input(self.create_settings_for_table_dto.dates):
            return False

        return True

    def create_table(self):
        if self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.date and self.create_settings_for_table_dto.individual_sorting:
            self.progress = 0
            logging.debug(f"PREPARE intividual date ")
            self.progress = 10
            dataframe = self.dates_prepare_data_fahrplan()
            self.progress = 20
            dataframe = self.datesWeekday_select_dates_for_date_range(dataframe)
            self.progress = 30
            dataframe = self.dates_select_dates_delete_exception_2(dataframe)
            self.progress = 40
            dataframe = self.datesWeekday_select_stops_for_trips(dataframe)
            self.progress = 50
            dataframe = self.datesWeekday_select_for_every_date_trips_stops(dataframe)
            self.progress = 60
            dataframe = self.datesWeekday_select_stop_sequence_stop_name_sorted(dataframe)
            self.progress = 70
            dataframe = self.datesWeekday_create_sort_stopnames(dataframe)
            self.create_sorting.emit()
        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.date:
            self.progress = 0
            logging.debug(f"PREPARE date ")
            self.progress = 10
            dataframe = self.dates_prepare_data_fahrplan()
            self.progress = 20
            dataframe = self.datesWeekday_select_dates_for_date_range(dataframe)
            self.progress = 30
            dataframe = self.dates_select_dates_delete_exception_2(dataframe)
            self.progress = 40
            dataframe = self.datesWeekday_select_stops_for_trips(dataframe)
            self.progress = 50
            dataframe = self.datesWeekday_select_for_every_date_trips_stops(dataframe)
            self.progress = 60
            dataframe = self.datesWeekday_select_stop_sequence_stop_name_sorted(dataframe)
            self.progress = 70
            dataframe = self.datesWeekday_create_fahrplan(dataframe)
            self.progress = 80

        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.weekday and self.create_settings_for_table_dto.individual_sorting:
            self.progress = 10
            dataframe = self.weekday_prepare_data_fahrplan()
            self.progress = 20
            dataframe = self.datesWeekday_select_dates_for_date_range(dataframe)
            self.progress = 30
            dataframe = self.weekday_select_weekday_exception_2(dataframe)
            self.progress = 40
            dataframe = self.datesWeekday_select_stops_for_trips(dataframe)
            self.progress = 50
            dataframe = self.datesWeekday_select_for_every_date_trips_stops(dataframe)
            self.progress = 60
            dataframe = self.datesWeekday_select_stop_sequence_stop_name_sorted(dataframe)
            self.progress = 70
            dataframe = self.datesWeekday_create_sort_stopnames(dataframe)
            self.create_sorting.emit()

        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.weekday:
            self.progress = 10
            dataframe = self.weekday_prepare_data_fahrplan()
            self.progress = 20
            dataframe = self.datesWeekday_select_dates_for_date_range(dataframe)
            self.progress = 30
            dataframe = self.weekday_select_weekday_exception_2(dataframe)
            self.progress = 40
            dataframe = self.datesWeekday_select_stops_for_trips(dataframe)
            self.progress = 50
            dataframe = self.datesWeekday_select_for_every_date_trips_stops(dataframe)
            self.progress = 60
            dataframe = self.datesWeekday_select_stop_sequence_stop_name_sorted(dataframe)
            self.progress = 70
            dataframe = self.datesWeekday_create_fahrplan(dataframe)
            self.progress = 80

        return dataframe

    def create_table_continue(self, dataframe):
        dataframe = self.datesWeekday_create_fahrplan_continue(dataframe)
        self.progress = 80
        return dataframe


    def dates_prepare_data_fahrplan(self) -> dict:
        self.last_time = time.time()

        # Create a dictionary for headers
        headers = {
            'Agency': [self.create_settings_for_table_dto.agency],
            'Route': [self.create_settings_for_table_dto.route],
            'Dates': [self.create_settings_for_table_dto.dates]
        }

        # Convert headers dictionary to DataFrame
        df_header_for_export_data = pd.DataFrame(headers)

        # Simplify DataFrame creation for direction, dates, route, and agency
        dataframes = {
            'Header': df_header_for_export_data,
            'Direction': pd.DataFrame({'direction_id': [self.create_settings_for_table_dto.direction]}),
            'Requested Dates': pd.DataFrame({'date': pd.to_datetime([self.create_settings_for_table_dto.dates], format='%Y%m%d')}),
            'Route Short Name': pd.DataFrame({'route_short_name': [self.create_settings_for_table_dto.route]}),
            'Selected Agency': pd.DataFrame({'agency_id': [self.create_settings_for_table_dto.agency]})
        }
        return dataframes

    def datesWeekday_select_dates_for_date_range(self, dataframe):
        # conditions for searching in dfs
        dfTrips = self.gtfs_data_frame_dto.Trips
        dfWeek = self.gtfs_data_frame_dto.Calendarweeks
        dfRoutes = self.gtfs_data_frame_dto.Routes
        route_short_namedf = dataframe['Route Short Name']
        requested_directiondf = dataframe['Direction']
        varTestAgency = dataframe['Selected Agency']

        cond_select_dates_for_date_range = '''
                    select  
                            dfTrips.trip_id,
                            dfTrips.service_id,
                            dfTrips.route_id, 
                            dfWeek.start_date,
                            dfWeek.end_date,
                            dfWeek.monday,
                            dfWeek.tuesday,
                            dfWeek.wednesday,
                            dfWeek.thursday,
                            dfWeek.friday,
                            dfWeek.saturday,
                            dfWeek.sunday
                    from dfWeek 
                    inner join dfTrips on dfWeek.service_id = dfTrips.service_id
                    inner join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                    inner join route_short_namedf on dfRoutes.route_short_name = route_short_namedf.route_short_name
                    inner join varTestAgency on dfRoutes.agency_id = varTestAgency.agency_id
                    inner join requested_directiondf on dfTrips.direction_id = requested_directiondf.direction_id
                    where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                      and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                      and dfTrips.direction_id = requested_directiondf.direction_id -- shows the direction of the line 
                    order by dfTrips.service_id;
                   '''

        # get dates for start and end dates for date range function
        # TODO: Sortieren nach neue Spalte
        """
        dfTrips.trip_id,
        dfTrips.service_id,
        dfTrips.route_id, 
        dfWeek.start_date,
        dfWeek.end_date,
        dfWeek.monday,
        dfWeek.tuesday,
        dfWeek.wednesday,
        dfWeek.thursday,
        dfWeek.friday,
        dfWeek.saturday,
        dfWeek.sunday
        """
        fahrplan_dates = sqldf(cond_select_dates_for_date_range, locals())

        # change format
        fahrplan_dates['start_date'] = pd.to_datetime(fahrplan_dates['start_date'], format='%Y%m%d')
        fahrplan_dates['end_date'] = pd.to_datetime(fahrplan_dates['end_date'], format='%Y%m%d')
        dataframe['fahrplan_dates'] = fahrplan_dates
        return dataframe

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
        selected_columns = ['date', 'day', 'trip_id', 'service_id', 'route_id', 'start_date', 'end_date', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        fahrplan_dates_all_dates = ordered_fahrplan_dates_all_dates_final[selected_columns]

        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'],
                                                          format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'],
                                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'],
                                                              format='%Y-%m-%d %H:%M:%S.%f')

        self.fahrplan_dates_all_dates = fahrplan_dates_all_dates

    def dates_select_dates_delete_exception_2(self, dataframe):

        dfDates = self.gtfs_data_frame_dto.Calendardates
        requested_datesdf = pd.DataFrame([self.create_settings_for_table_dto.dates], columns=['date'])
        requested_datesdf['date'] = pd.to_datetime(requested_datesdf['date'], format='%Y%m%d')
        fahrplan_dates = dataframe['fahrplan_dates']
        cond_select_dates_delete_exception_2 = '''
                    select  
                            fahrplan_dates.date,
                            fahrplan_dates.day,
                            fahrplan_dates.trip_id,
                            fahrplan_dates.service_id,
                            fahrplan_dates.route_id, 
                            fahrplan_dates.start_date,
                            fahrplan_dates.end_date,
                            fahrplan_dates.monday,
                            fahrplan_dates.tuesday,
                            fahrplan_dates.wednesday,
                            fahrplan_dates.thursday,
                            fahrplan_dates.friday,
                            fahrplan_dates.saturday,
                            fahrplan_dates.sunday
                    from fahrplan_dates 
                    where fahrplan_dates.date not in (select dfDates.date 
                                                                  from dfDates                                                            
                                                                    where fahrplan_dates.service_id = dfDates.service_id
                                                                      and fahrplan_dates.date = dfDates.date 
                                                                      and dfDates.exception_type = 2 
                                                               )
                     and fahrplan_dates.date in (select requested_datesdf.date 
                                                                  from requested_datesdf                                                            
                                                                    where fahrplan_dates.date = requested_datesdf.date
                                                          )
                     and (   (   fahrplan_dates.day = fahrplan_dates.monday
                              or fahrplan_dates.day = fahrplan_dates.tuesday
                              or fahrplan_dates.day = fahrplan_dates.wednesday
                              or fahrplan_dates.day = fahrplan_dates.thursday
                              or fahrplan_dates.day = fahrplan_dates.friday
                              or fahrplan_dates.day = fahrplan_dates.saturday
                              or fahrplan_dates.day = fahrplan_dates.sunday
                             )
                             or 
                             (   fahrplan_dates.date in (select dfDates.date
                                                                   from dfDates                                                            
                                                                    where fahrplan_dates.service_id = dfDates.service_id 
                                                                      and fahrplan_dates.date = dfDates.date
                                                                      and dfDates.exception_type = 1
                                                                  )    
                             )
                        ) 
                    order by fahrplan_dates.date;
                   '''

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
               }) for i, row in fahrplan_dates.iterrows()], ignore_index=True)

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

        fahrplan_dates = fahrplan_dates.set_index('date')

        # delete exceptions = 2 or add exceptions = 1
        fahrplan_dates = sqldf(cond_select_dates_delete_exception_2, locals())
        fahrplan_dates['date'] = pd.to_datetime(fahrplan_dates['date'],
                                                          format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates['start_date'] = pd.to_datetime(fahrplan_dates['start_date'],
                                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates['end_date'] = pd.to_datetime(fahrplan_dates['end_date'],
                                                              format='%Y-%m-%d %H:%M:%S.%f')
        dataframe['fahrplan_dates'] = fahrplan_dates
        return dataframe

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


        return sorted_stopsequence

    def sortStopSequence(self, stopsequence):
        """
        sort dict of stops (cust. bubble sort)
        """
        # get all possible stops
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

        if self.sortmode == 1:
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
            # -> hier ist etwas komisch!
            # for i in range(sequence_count - 1):
            #     for j in range(0, sequence_count - i - 1):
            #         # 23072022
            #         # if d[str(j)]["arrival_time"] > d[str(j + 1)]["arrival_time"]:
            #         #     d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
            #         if d[str(j)]["stop_sequence"] > d[str(j + 1)]["stop_sequence"] \
            #                 and d[str(j)]["start_time"] > d[str(j + 1)]["start_time"]:
            #             d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
            #         elif d[str(j)]["stop_sequence"] == d[str(j + 1)]["stop_sequence"]:
            #             if d[str(j)]["start_time"] > d[str(j + 1)]["start_time"] \
            #                     and d[str(j)]["arrival_time"] > d[str(j + 1)]["arrival_time"]:
            #                 d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
        return d

    # checks if in dictonary
    def dictForEntry(self, temp, key, key_value):
        if key_value in temp:
            return True
        else:
            return False

    # the is the one way to add a 0 to the time hh:mm:ss, if 0 is missing like in 6:44:33
    def time_in_string(self, time):
        pattern = re.findall('^\d{1}:\d{2}:\d{2}$', time)

        if pattern:
            return '0' + time
        else:
            return time

    # the is the one way to add a 0 to the time hh:mm:ss, if 0 is missing like in 6:44:33
    def time_delete_seconds(self, time):
        return time[:-3]

    # checks if date string
    def check_dates_input(self, dates):
        pattern1 = re.findall('^\d{8}(?:\d{8})*(?:,\d{8})*$', dates)
        if pattern1:
            return True
        else:
            return False

    def check_KommaInText(self, dates):
        pattern1 = re.findall('"\w*,\w*"', dates)
        if pattern1:
            logging.debug(pattern1)
            return True
        else:
            return False

    # checks if time-string exceeds 24 hour
    def check_hour_24(self, time):
        try:
            pattern1 = re.findall('^2{1}[4-9]{1}:[0-9]{2}', time)
            if pattern1:
                return True
            else:
                return False
        except:
            logging.debug(time)