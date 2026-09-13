import re
from datetime import datetime

import pandas as pd

from model.domain.gtfs_data_source import GtfsDataSource
from model.domain.planning_settings import PlanningSettings
from model.domain.timetable_data import TimetableData
from model.enums import ErrorMessages, RouteColumns
from model.planning.progress import ProgressUpdate


class TimetablePlanner:
    def __init__(self):
        super().__init__()
        self.planning_settings = PlanningSettings()
        self.timetable_data = TimetableData()
        self.gtfs_data = None
        self.progress = ProgressUpdate()


    @property
    def gtfs_data(self):
        return self._gtfs_data

    @gtfs_data.setter
    def gtfs_data(self, value: GtfsDataSource):
        self._gtfs_data = value

    def validate_settings(self) -> bool:
        if not self.is_valid_date_input(self.planning_settings.date):
            return False

        return True

    def prepare_date_data(self):
        # Create a dictionary for headers
        headers = {
            'Agency': [self.planning_settings.agency],
            'Route': [self.planning_settings.route['route_id']],
            'Dates': [self.planning_settings.date]
        }

        # Convert headers dictionary to DataFrame
        header = pd.DataFrame(headers)

        # Simplify DataFrame creation for direction, dates, route, and agency
        self.timetable_data = TimetableData()
        self.timetable_data.header = header
        self.timetable_data.direction = pd.DataFrame({'direction_id': [self.planning_settings.direction]})
        self.timetable_data.requested_dates = pd.DataFrame(
            {'date': pd.to_datetime([self.planning_settings.date], format='%Y%m%d')})
        self.timetable_data.selected_route = self.planning_settings.route
        self.timetable_data.selected_agency = self.planning_settings.agency

    def prepare_weekday_data(self):
        # DataFrame for header information
        headers = {'Agency': [self.planning_settings.agency],
                   'Route': [self.planning_settings.route['route_id']],
                   'WeekdayOption': [self.planning_settings.weekday]}

        # Convert headers dictionary to DataFrame
        header = pd.DataFrame(headers)

        # Simplify DataFrame creation for direction, dates, route, and agency
        self.timetable_data = TimetableData()
        self.timetable_data.header = header
        self.timetable_data.direction = pd.DataFrame({'direction_id': [self.planning_settings.direction]})
        self.timetable_data.requested_weekdays = self.planning_settings.weekday
        self.timetable_data.selected_route = self.planning_settings.route
        self.timetable_data.selected_agency = self.planning_settings.agency


    def select_dates_for_range(self):
        trips = self.gtfs_data.get_trips(
            route_id=self.timetable_data.selected_route.iloc[0]['route_id'],
            direction_id=self.planning_settings.direction)
        calendar = self.gtfs_data.calendar
        calendar = calendar[calendar.service_id.isin(trips.service_id)]
        routes = self.gtfs_data.routes
        selected_route = self.timetable_data.selected_route
        requested_direction = self.timetable_data.direction
        selected_agency = self.timetable_data.selected_agency

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


        result = (
            calendar
            .merge(trips, on='service_id', how='inner')
            .merge(routes, on='route_id', how='inner')
            .merge(selected_route, on=['route_id', 'agency_id'], how='inner', suffixes=('', '_duplicate'))
            .merge(selected_agency, on='agency_id', how='inner', suffixes=('', '_duplicate'))
            .merge(requested_direction, on='direction_id', how='inner')
            .sort_values('service_id')
        )

        result = result[selected_columns]

        if len(result) == 0:
            raise ValueError("timetable_dates is empty")

        # change format
        result_copy = result.copy()
        result_copy['start_date'] = pd.to_datetime(result_copy['start_date'], format='%Y%m%d')
        result_copy['end_date'] = pd.to_datetime(result_copy['end_date'], format='%Y%m%d')
        self.timetable_data.timetable_dates = result_copy

    def apply_weekday_exceptions(self):

        calendar_dates = self.gtfs_data.calendar_dates
        timetable_dates = self.timetable_data.timetable_dates
        weekdays = self.timetable_data.requested_weekdays

        timetable_dates = pd.concat(
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
               }) for _, row in timetable_dates.iterrows()])

        # need to convert the date after using iterows (itertuples might be faster)
        timetable_dates['date'] = pd.to_datetime(timetable_dates['date'], format='%Y%m%d')
        timetable_dates['start_date'] = pd.to_datetime(timetable_dates['start_date'], format='%Y%m%d')
        timetable_dates['end_date'] = pd.to_datetime(timetable_dates['end_date'], format='%Y%m%d')
        timetable_dates['day'] = timetable_dates['date'].dt.day_name()

        # set value in column to day if 1 and compare with day
        timetable_dates['monday'] = ['Monday' if x == '1' else '-' for x in timetable_dates['monday']]
        timetable_dates['tuesday'] = ['Tuesday' if x == '1' else '-' for x in
                                     timetable_dates['tuesday']]
        timetable_dates['wednesday'] = ['Wednesday' if x == '1' else '-' for x in
                                       timetable_dates['wednesday']]
        timetable_dates['thursday'] = ['Thursday' if x == '1' else '-' for x in
                                      timetable_dates['thursday']]
        timetable_dates['friday'] = ['Friday' if x == '1' else '-' for x in timetable_dates['friday']]
        timetable_dates['saturday'] = ['Saturday' if x == '1' else '-' for x in
                                      timetable_dates['saturday']]
        timetable_dates['sunday'] = ['Sunday' if x == '1' else '-' for x in timetable_dates['sunday']]

        timetable_dates = timetable_dates[['date', 'day', 'trip_id', 'service_id', 'route_id', 'start_date', 'end_date','monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']]
        calendar_dates = calendar_dates.assign(date=pd.to_datetime(calendar_dates['date'], format='%Y%m%d'))
        exception_dates = calendar_dates[calendar_dates['service_id'].isin(timetable_dates['service_id'])]

        added_dates = exception_dates[exception_dates['exception_type'] == 1]
        removed_dates = exception_dates[exception_dates['exception_type'] == 2]

        selected_timetable_dates = timetable_dates[(
                timetable_dates['day'].isin(weekdays['Monday']) |
                timetable_dates['day'].isin(weekdays['Tuesday']) |
                timetable_dates['day'].isin(weekdays['Wednesday']) |
                timetable_dates['day'].isin(weekdays['Thursday']) |
                timetable_dates['day'].isin(weekdays['Friday']) |
                timetable_dates['day'].isin(weekdays['Saturday']) |
                timetable_dates['day'].isin(weekdays['Sunday'])
        )]

        selected_timetable_dates = selected_timetable_dates[(~selected_timetable_dates['service_id'].isin(removed_dates['service_id']))]

        selected_timetable_dates = selected_timetable_dates.drop_duplicates(subset=['service_id'])
        timetable_dates = selected_timetable_dates.drop_duplicates()

        timetable_dates['date'] = pd.to_datetime(timetable_dates['date'],
                                                   format='%Y-%m-%d %H:%M:%S.%f')
        timetable_dates['start_date'] = pd.to_datetime(timetable_dates['start_date'],
                                                         format='%Y-%m-%d %H:%M:%S.%f')
        timetable_dates['end_date'] = pd.to_datetime(timetable_dates['end_date'],
                                                       format='%Y-%m-%d %H:%M:%S.%f')
        self.timetable_data.timetable_dates = timetable_dates

    def apply_date_exceptions(self):
        calendar_dates = self.gtfs_data.calendar_dates
        requested_dates = pd.DataFrame([self.planning_settings.date], columns=['date'])
        requested_dates['date'] = pd.to_datetime(requested_dates['date'], format='%Y%m%d')
        timetable_dates = self.timetable_data.timetable_dates

        timetable_dates = pd.concat(
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
               }) for _, row in timetable_dates.iterrows()])

        timetable_dates['date'] = pd.to_datetime(timetable_dates['date'], format='%Y%m%d')
        timetable_dates['start_date'] = pd.to_datetime(timetable_dates['start_date'], format='%Y%m%d')
        timetable_dates['end_date'] = pd.to_datetime(timetable_dates['end_date'], format='%Y%m%d')
        timetable_dates['day'] = timetable_dates['date'].dt.day_name()

        # # set value in column to day if 1 and compare with day
        # timetable_dates['monday'] = ['Monday' if x == '1' else '-' for x in timetable_dates['monday']]
        # timetable_dates['tuesday'] = ['Tuesday' if x == '1' else '-' for x in
        #                              timetable_dates['tuesday']]
        # timetable_dates['wednesday'] = ['Wednesday' if x == '1' else '-' for x in
        #                                timetable_dates['wednesday']]
        # timetable_dates['thursday'] = ['Thursday' if x == '1' else '-' for x in
        #                               timetable_dates['thursday']]
        # timetable_dates['friday'] = ['Friday' if x == '1' else '-' for x in timetable_dates['friday']]
        # timetable_dates['saturday'] = ['Saturday' if x == '1' else '-' for x in
        #                               timetable_dates['saturday']]
        # timetable_dates['sunday'] = ['Sunday' if x == '1' else '-' for x in timetable_dates['sunday']]

        timetable_dates = timetable_dates[
            ['date', 'day', 'trip_id', 'service_id', 'route_id', 'start_date', 'end_date', 'monday', 'tuesday',
             'wednesday', 'thursday', 'friday', 'saturday', 'sunday']]

        calendar_dates = calendar_dates.assign(date=pd.to_datetime(calendar_dates['date'], format='%Y%m%d'))
        exception_dates = calendar_dates[calendar_dates['service_id'].isin(timetable_dates['service_id'])]
        exception_dates = exception_dates[exception_dates['date'].isin(requested_dates['date'])]
        added_dates = exception_dates[exception_dates['exception_type'] == 1]
        removed_dates = exception_dates[exception_dates['exception_type'] == 2]

        # add exceptions first!
        if added_dates.empty == False:
            selected_timetable_dates = timetable_dates[(timetable_dates['service_id'].isin(added_dates['service_id']))]
        else:
            date_weekday = requested_dates['date'].dt.day_name()
            weekday_columns = {
                'Monday': 'monday',
                'Tuesday': 'tuesday',
                'Wednesday': 'wednesday',
                'Thursday': 'thursday',
                'Friday': 'friday',
                'Saturday': 'saturday',
                'Sunday': 'sunday'
            }
            weekday_column = weekday_columns[date_weekday[0]]
            selected_service_ids = self.gtfs_data.calendar[self.gtfs_data.calendar[weekday_column] == '1']
            selected_timetable_dates = timetable_dates[
                (timetable_dates['service_id'].isin(selected_service_ids['service_id']))]

        selected_timetable_dates = selected_timetable_dates[(selected_timetable_dates['date'].isin(requested_dates['date']))]
        selected_timetable_dates = selected_timetable_dates[(~selected_timetable_dates['service_id'].isin(removed_dates['service_id']))]



        selected_timetable_dates = selected_timetable_dates.drop_duplicates(subset=['trip_id'])
        timetable_dates = selected_timetable_dates.drop_duplicates()

        timetable_dates['date'] = pd.to_datetime(timetable_dates['date'],
                                                format='%Y-%m-%d %H:%M:%S.%f')
        timetable_dates['start_date'] = pd.to_datetime(timetable_dates['start_date'],
                                                      format='%Y-%m-%d %H:%M:%S.%f')
        timetable_dates['end_date'] = pd.to_datetime(timetable_dates['end_date'],
                                                    format='%Y-%m-%d %H:%M:%S.%f')
        self.timetable_data.timetable_dates = timetable_dates

    def select_stops_for_trips(self):

        selected_route = self.timetable_data.selected_route
        requested_direction = self.timetable_data.direction
        #pd.DataFrame({'direction_id': [self.planning_settings.direction]})
        selected_agency = self.timetable_data.selected_agency

        routes = self.gtfs_data.routes
        routes = pd.merge(left=routes, right=selected_route, how='inner', on=[RouteColumns.ROUTE_ID.value, RouteColumns.SHORT_NAME.value, RouteColumns.AGENCY_ID.value, RouteColumns.LONG_NAME.value])
        routes = pd.merge(left=routes, right=selected_agency, how='inner', on=RouteColumns.AGENCY_ID.value)
        trips = self.gtfs_data.get_trips(
            route_id=selected_route.iloc[0]['route_id'],
            direction_id=self.planning_settings.direction)
        trips = pd.merge(left=trips, right=requested_direction, how='inner', on='direction_id')
        trips = pd.merge(left=trips, right=routes, how='inner', on='route_id')
        trips = trips[trips.trip_id.isin(self.timetable_data.timetable_dates.trip_id)]
        stop_times = self.gtfs_data.get_stop_times_for_trips(trips.trip_id.unique())
        trips['trip_id'] = trips['trip_id'].astype('string')
        stop_times = stop_times.assign(trip_id=stop_times['trip_id'].astype('string'))
        stop_times = pd.merge(left=stop_times, right=trips, how='inner', left_on='trip_id', right_on='trip_id')
        stops = self.gtfs_data.get_stops(stop_times.stop_id.unique())

        joined_df = pd.merge(stop_times, trips[['trip_id', 'service_id']], left_on=['trip_id', 'service_id'],
                             right_on=['trip_id', 'service_id'])
        joined_df = pd.merge(joined_df, stops[['stop_id', 'stop_name']], left_on='stop_id', right_on='stop_id')

        min_stop_sequence = joined_df['stop_sequence'].min()
        first_stop_times = joined_df[joined_df['stop_sequence'] == min_stop_sequence][['arrival_time', 'trip_id']]

        merged_df = pd.merge(joined_df, first_stop_times.rename(columns={'arrival_time': 'start_time'}), on='trip_id',
                             how='left')

        selected_columns = ['start_time', 'trip_id', 'stop_name', 'stop_sequence', 'arrival_time', 'service_id',
                            'stop_id']
        trip_stops = merged_df[selected_columns]

        if trip_stops.empty:
            second_stop_times = joined_df[joined_df['stop_sequence'] == 1][['arrival_time', 'trip_id']]
            merged_df = pd.merge(joined_df, second_stop_times.rename(columns={'arrival_time': 'start_time'}),
                                 on='trip_id', how='left')
            selected_columns_one = ['start_time', 'trip_id', 'stop_name', 'stop_sequence', 'arrival_time', 'service_id',
                                    'stop_id']
            fallback_trip_stops = merged_df[selected_columns_one]
            self.timetable_data.timetable_stops = fallback_trip_stops
            return

        self.timetable_data.timetable_stops = trip_stops

    def build_daily_trip_stops(self):

        timetable_rows = self.timetable_data.timetable_stops.copy()
        timetable_rows['trip_id'] = timetable_rows['trip_id'].astype('string')
        all_timetable_dates = self.timetable_data.timetable_dates.copy()
        all_timetable_dates['trip_id'] = all_timetable_dates['trip_id'].astype('string')

        joined_df = pd.merge(all_timetable_dates, timetable_rows, left_on=['trip_id', 'service_id'],
                             right_on=['trip_id', 'service_id'], how='left')
        joined_df = joined_df.dropna(subset=['stop_id'])

        ordered_df = joined_df.sort_values(by=['date', 'stop_sequence', 'start_time', 'trip_id'])
        selected_columns = ['date', 'day', 'start_time', 'trip_id', 'stop_name', 'stop_sequence', 'arrival_time',
                            'service_id', 'stop_id']
        ordered_df = ordered_df[selected_columns]
        ordered_df['arrival_time'] = ordered_df['arrival_time'].apply(
            lambda x: self.normalize_time(x))
        ordered_df['start_time'] = ordered_df['start_time'].apply(
            lambda x: self.normalize_time(x))
        sorted_df = ordered_df.sort_values(by=['trip_id', 'date', 'stop_sequence'])

        selected_columns = ['date', 'day', 'start_time', 'arrival_time', 'stop_name', 'stop_sequence', 'stop_id',
                            'trip_id']
        sorted_df = sorted_df[selected_columns]
        self.timetable_data.sorted_stops = sorted_df

    def prepare_stop_sorting(self):
        sorted_df = self.timetable_data.sorted_stops
        filtered_df = self.filter_stop_sequence(sorted_df)

        filtered_stop_names = pd.DataFrame.from_dict(filtered_df)
        filtered_stop_names["stop_sequence"] = filtered_stop_names["stop_sequence"].astype('int32')
        filtered_stop_names = filtered_stop_names.sort_index(axis=0)

        self.timetable_data.filtered_stop_names = filtered_stop_names

    def create_timetable_after_sorting(self):
        sorted_stops = self.timetable_data.sorted_stops
        sorted_stops.rename(columns=lambda x: f'sorted_{x}', inplace=True)
        filtered_stop_names = self.timetable_data.filtered_stop_names
        joined_df = pd.merge(sorted_stops, filtered_stop_names, left_on='sorted_stop_id', right_on='stop_id',
                             how='left')

        grouped_df = joined_df.groupby(
            ['sorted_date', 'sorted_day', 'sorted_start_time', 'sorted_arrival_time', 'sorted_trip_id', 'sorted_stop_name', 'stop_sequence',
             'sorted_stop_sequence', 'sorted_stop_id'])


        aggregated_df = grouped_df.size().reset_index(name='count')
        ordered_df = aggregated_df.sort_values(by=['sorted_date', 'sorted_stop_sequence', 'sorted_start_time', 'sorted_trip_id'])

        selected_columns = ['sorted_date', 'sorted_day', 'sorted_start_time', 'sorted_trip_id', 'sorted_stop_name', 'stop_sequence',
                            'sorted_stop_sequence', 'sorted_arrival_time', 'sorted_stop_id']

        timetable_rows = ordered_df[selected_columns].copy()
        timetable_rows['sorted_date'] = pd.to_datetime(timetable_rows['sorted_date'], format='%Y-%m-%d %H:%M:%S.%f')
        timetable_rows['sorted_arrival_time'] = timetable_rows['sorted_arrival_time'].astype('string')
        timetable_rows['sorted_start_time'] = timetable_rows['sorted_start_time'].astype('string')
        timetable_rows = timetable_rows.drop(columns=['sorted_stop_sequence'])
        timetable_rows = timetable_rows.groupby(
            ['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id', 'sorted_start_time',
             'sorted_trip_id']).first().reset_index()
        timetable_rows['sorted_date'] = pd.to_datetime(timetable_rows['sorted_date'], format='%Y-%m-%d')
        timetable_rows['sorted_arrival_time'] = timetable_rows['sorted_arrival_time'].astype('string')

        if self.planning_settings.time_format == 1:
            timetable_rows['sorted_arrival_time'] = timetable_rows['sorted_arrival_time'].apply(
                lambda x: self.remove_seconds(x))

        timetable_rows['sorted_start_time'] = timetable_rows['sorted_start_time'].astype('string')

        self.timetable_data.timetable = timetable_rows.pivot(
            index=['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id'], columns=['sorted_start_time', 'sorted_trip_id'],
            values='sorted_arrival_time')

        self.timetable_data.timetable = self.timetable_data.timetable.sort_index(
            axis=1)
        self.timetable_data.timetable = self.timetable_data.timetable.sort_index(
            axis=0)

    def create_timetable(self):

        sorted_stops = self.timetable_data.sorted_stops
        sorted_stops.rename(columns=lambda x: f'sorted_{x}', inplace=True)
        filtered_stop_names = self.timetable_data.filtered_stop_names

        if sorted_stops.empty:
            raise Exception(ErrorMessages.NO_TRIPS_IN_DATE_RANGE.value)
        if filtered_stop_names.empty:
            raise Exception(ErrorMessages.NO_TRIPS_IN_DATE_RANGE.value)

        joined_df = pd.merge(sorted_stops, filtered_stop_names, left_on='sorted_stop_id', right_on='stop_id',
                             how='left')
        grouped_df = joined_df.groupby(
            ['sorted_date', 'sorted_day', 'sorted_start_time', 'sorted_arrival_time', 'sorted_trip_id', 'sorted_stop_name', 'stop_sequence',
             'sorted_stop_sequence', 'sorted_stop_id'])
        aggregated_df = grouped_df.size().reset_index(name='count')
        ordered_df = aggregated_df.sort_values(by=['sorted_date', 'sorted_stop_sequence', 'sorted_start_time', 'sorted_trip_id'])
        selected_columns = ['sorted_date', 'sorted_day', 'sorted_start_time', 'sorted_trip_id', 'sorted_stop_name', 'stop_sequence',
                            'sorted_stop_sequence', 'sorted_arrival_time', 'sorted_stop_id']

        timetable_rows = ordered_df[selected_columns].copy()
        timetable_rows['sorted_date'] = pd.to_datetime(timetable_rows['sorted_date'], format='%Y-%m-%d %H:%M:%S.%f')
        timetable_rows['sorted_arrival_time'] = timetable_rows['sorted_arrival_time'].astype('string')
        timetable_rows['sorted_start_time'] = timetable_rows['sorted_start_time'].astype('string')
        timetable_rows = timetable_rows.groupby(
            ['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id', 'sorted_start_time',
             'sorted_trip_id']).first().reset_index()
        timetable_rows['sorted_date'] = pd.to_datetime(timetable_rows['sorted_date'], format='%Y-%m-%d')
        timetable_rows['sorted_arrival_time'] = timetable_rows['sorted_arrival_time'].astype('string')

        if self.planning_settings.time_format == 1:
            timetable_rows['sorted_arrival_time'] = timetable_rows['sorted_arrival_time'].apply(
                lambda x: self.remove_seconds(x))

        timetable_rows['sorted_start_time'] = timetable_rows['sorted_start_time'].astype('string')

        self.timetable_data.gtfs_table_data = timetable_rows

        self.timetable_data.timetable = timetable_rows.pivot(
            index=['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id'], columns=['sorted_start_time', 'sorted_trip_id'],
            values='sorted_arrival_time')

        self.timetable_data.timetable = self.timetable_data.timetable.sort_index(
            axis=1)
        self.timetable_data.timetable = self.timetable_data.timetable.sort_index(
            axis=0)

    def filter_stop_sequence(self, data):
        stop_sequence = {}
        sorted_stop_sequence = {
            "stop_id": [],
            "stop_sequence": [],
            "stop_name": [],
            "start_time": []
        }

        for stop_name_i in data.itertuples():

            if not self.contains_entry(stop_sequence, "stop_id", stop_name_i.stop_id):
                temp = {"stop_sequence": -1, "stop_name": '', "trip_id": '', "start_time": '', "arrival_time": ''}
                temp["stop_sequence"] = stop_name_i.stop_sequence
                temp["stop_name"] = stop_name_i.stop_name
                temp["trip_id"] = stop_name_i.trip_id

                if self.is_after_midnight(stop_name_i.start_time):
                    comparison_time_i = str((stop_name_i.date.strftime(
                        '%Y-%m-%d'))) + ' 0' + str(int(stop_name_i.start_time.split(':')[0]) - 24) + ':' + \
                                    stop_name_i.start_time.split(':')[1] + ':' + \
                                    stop_name_i.start_time.split(':')[2]
                    time_i = datetime.strptime(comparison_time_i, '%Y-%m-%d %H:%M:%S')
                    time_i = time_i + timedelta(days=1)
                else:
                    comparison_time_i = str((stop_name_i.date.strftime(
                        '%Y-%m-%d'))) + ' ' + stop_name_i.start_time
                    time_i = datetime.strptime(comparison_time_i, '%Y-%m-%d %H:%M:%S')

                if self.is_after_midnight(stop_name_i.arrival_time):
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
                        if self.is_after_midnight(stop_name_j.start_time):
                            comparison_time_j = str((stop_name_j.date.strftime(
                                '%Y-%m-%d'))) + ' 0' + str(
                                int(stop_name_j.start_time.split(':')[0]) - 24) + ':' + \
                                            stop_name_j.start_time.split(':')[1] + ':' + \
                                            stop_name_j.start_time.split(':')[2]

                            time_j = datetime.strptime(comparison_time_j, '%Y-%m-%d %H:%M:%S')
                            time_j = time_j + timedelta(days=1)
                        else:
                            comparison_time_j = str((stop_name_j.date.strftime(
                                '%Y-%m-%d'))) + ' ' + stop_name_j.start_time
                            time_j = datetime.strptime(comparison_time_j, '%Y-%m-%d %H:%M:%S')

                        current_start_time = temp["start_time"]

                        if self.is_after_midnight(stop_name_j.arrival_time):
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

                        current_arrival_time = temp["arrival_time"]

                        if time_j < time_i \
                                and time_j < current_start_time \
                                and stop_name_j.stop_sequence > stop_name_i.stop_sequence \
                                and stop_name_j.stop_sequence > temp["stop_sequence"]:
                            temp["start_time"] = time_j
                            temp["arrival_time"] = time_arrival_j
                            # temp["arrival_time"] = stop_name_j.arrival_time
                            temp["stop_sequence"] = stop_name_j.stop_sequence


                stop_sequence[stop_name_i.stop_id] = temp

        new_stop_sequence = self.sort_stop_sequence(stop_sequence)

        for stop_sequence in new_stop_sequence.keys():
            sorted_stop_sequence['stop_id'].append(new_stop_sequence[stop_sequence]['stop_id'])
            sorted_stop_sequence['stop_sequence'].append(stop_sequence)
            sorted_stop_sequence['stop_name'].append(new_stop_sequence[stop_sequence]['stop_name'])
            sorted_stop_sequence['start_time'].append(new_stop_sequence[stop_sequence]['start_time'])

        return sorted_stop_sequence

    def sort_stop_sequence(self, stop_sequence):
        sequence_count = len(stop_sequence)

        # init data structure
        d = {}
        for k in range(sequence_count):
            d[str(k)] = {"start_time": datetime.strptime('1901-01-01 23:59:00', '%Y-%m-%d %H:%M:%S').time(),
                         "arrival_time": datetime.strptime('1901-01-01 23:59:00', '%Y-%m-%d %H:%M:%S').time(),
                         "stop_name": '',
                         "stop_id": ''
                         }

        # fill new dict
        for k, j in enumerate(stop_sequence):
            if d[str(k)]["stop_id"] == '':
                d[str(k)]["stop_id"] = j
                d[str(k)]["start_time"] = stop_sequence[j]['start_time']
                d[str(k)]["arrival_time"] = stop_sequence[j]['arrival_time']
                d[str(k)]["stop_sequence"] = stop_sequence[j]['stop_sequence']
                d[str(k)]["stop_name"] = stop_sequence[j]['stop_name']

        if self.planning_settings.use_individual_sorting:
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
    def contains_entry(self, temp, key, key_value):
        return key_value in temp

    # the is the one way to add a 0 to the time hh:mm:ss, if 0 is missing like in 6:44:33
    def normalize_time(self, time):
        return f"0{time}" if re.fullmatch(r"\d:\d{2}:\d{2}", time) else time

    # the is the one way to add a 0 to the time hh:mm:ss, if 0 is missing like in 6:44:33
    def remove_seconds(self, time):
        return time[:-3]

    # checks if date string
    def is_valid_date_input(self, dates):
        return isinstance(dates, str) and re.fullmatch(r"\d{8}(?:,\d{8})*", dates) is not None

    def escape_commas(self, dates):
        return re.search(r'"\w*,\w*"', dates) is not None

    # checks if time-string exceeds 24 hour format
    def is_after_midnight(self, time):
        return isinstance(time, str) and re.match(r"^2[4-9]:[0-9]{2}", time) is not None
