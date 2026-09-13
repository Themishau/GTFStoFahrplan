import re
from datetime import datetime, timedelta

import pandas as pd

from model.domain.gtfs_data_source import GtfsDataSource
from model.domain.planning_settings import PlanningSettings
from model.domain.timetable_data import TimetableData
from model.enums import ErrorMessage, RouteColumn, TimeFormat
from model.services.gtfs_time import gtfs_time_to_seconds


class TimetablePlanner:
    def __init__(self):
        super().__init__()
        self.planning_settings = PlanningSettings()
        self.timetable_data = TimetableData()
        self.gtfs_data = None

    @property
    def gtfs_data(self):
        return self._gtfs_data

    @gtfs_data.setter
    def gtfs_data(self, value: GtfsDataSource):
        self._gtfs_data = value

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

    def select_dates_for_range(self):
        trips = self.gtfs_data.get_trips(
            route_id=self.planning_settings.route.iloc[0]['route_id'],
            direction_id=self.planning_settings.direction)
        calendar = self.gtfs_data.calendar
        calendar = calendar[calendar.service_id.isin(trips.service_id)]
        routes = self.gtfs_data.routes
        selected_route = self.planning_settings.route
        requested_direction = pd.DataFrame({'direction_id': [self.planning_settings.direction]})
        selected_agency = self.planning_settings.agency

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

        if result.empty:
            raise ValueError("timetable_dates is empty")

        # change format
        result_copy = result.copy()
        result_copy['start_date'] = pd.to_datetime(result_copy['start_date'], format='%Y%m%d')
        result_copy['end_date'] = pd.to_datetime(result_copy['end_date'], format='%Y%m%d')
        self.timetable_data.service_dates = result_copy

    def apply_weekday_exceptions(self):

        calendar_dates = self.gtfs_data.calendar_dates
        timetable_dates = self.timetable_data.service_dates
        weekdays = self.planning_settings.weekday

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

        timetable_dates = timetable_dates[
            ['date', 'day', 'trip_id', 'service_id', 'route_id', 'start_date', 'end_date', 'monday', 'tuesday',
             'wednesday', 'thursday', 'friday', 'saturday', 'sunday']]
        calendar_dates = calendar_dates.assign(date=pd.to_datetime(calendar_dates['date'], format='%Y%m%d'))
        exception_dates = calendar_dates[calendar_dates['service_id'].isin(timetable_dates['service_id'])]

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

        selected_timetable_dates = selected_timetable_dates[
            (~selected_timetable_dates['service_id'].isin(removed_dates['service_id']))]

        selected_timetable_dates = selected_timetable_dates.drop_duplicates(subset=['service_id'])
        timetable_dates = selected_timetable_dates.drop_duplicates()

        timetable_dates['date'] = pd.to_datetime(timetable_dates['date'],
                                                 format='%Y-%m-%d %H:%M:%S.%f')
        timetable_dates['start_date'] = pd.to_datetime(timetable_dates['start_date'],
                                                       format='%Y-%m-%d %H:%M:%S.%f')
        timetable_dates['end_date'] = pd.to_datetime(timetable_dates['end_date'],
                                                     format='%Y-%m-%d %H:%M:%S.%f')
        self.timetable_data.service_dates = timetable_dates

    def apply_date_exceptions(self):
        calendar_dates = self.gtfs_data.calendar_dates
        requested_dates = pd.DataFrame([self.planning_settings.date], columns=['date'])
        requested_dates['date'] = pd.to_datetime(requested_dates['date'], format='%Y%m%d')
        timetable_dates = self.timetable_data.service_dates

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
        if not added_dates.empty:
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

        selected_timetable_dates = selected_timetable_dates[
            (selected_timetable_dates['date'].isin(requested_dates['date']))]
        selected_timetable_dates = selected_timetable_dates[
            (~selected_timetable_dates['service_id'].isin(removed_dates['service_id']))]

        selected_timetable_dates = selected_timetable_dates.drop_duplicates(subset=['trip_id'])
        timetable_dates = selected_timetable_dates.drop_duplicates()

        timetable_dates['date'] = pd.to_datetime(timetable_dates['date'],
                                                 format='%Y-%m-%d %H:%M:%S.%f')
        timetable_dates['start_date'] = pd.to_datetime(timetable_dates['start_date'],
                                                       format='%Y-%m-%d %H:%M:%S.%f')
        timetable_dates['end_date'] = pd.to_datetime(timetable_dates['end_date'],
                                                     format='%Y-%m-%d %H:%M:%S.%f')
        self.timetable_data.service_dates = timetable_dates

    def select_stops_for_trips(self):

        selected_route = self.planning_settings.route
        requested_direction = pd.DataFrame({'direction_id': [self.planning_settings.direction]})
        # pd.DataFrame({'direction_id': [self.planning_settings.direction]})
        selected_agency = self.planning_settings.agency

        routes = self.gtfs_data.routes
        routes = pd.merge(left=routes, right=selected_route, how='inner',
                          on=[RouteColumn.ROUTE_ID, RouteColumn.SHORT_NAME, RouteColumn.AGENCY_ID,
                              RouteColumn.LONG_NAME])
        routes = pd.merge(left=routes, right=selected_agency, how='inner', on=RouteColumn.AGENCY_ID)
        trips = self.gtfs_data.get_trips(
            route_id=selected_route.iloc[0]['route_id'],
            direction_id=self.planning_settings.direction)
        trips = pd.merge(left=trips, right=requested_direction, how='inner', on='direction_id')
        trips = pd.merge(left=trips, right=routes, how='inner', on='route_id')
        trips = trips[trips.trip_id.isin(self.timetable_data.service_dates.trip_id)]
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
            self.timetable_data.trip_stops = fallback_trip_stops
            return

        self.timetable_data.trip_stops = trip_stops

    def build_daily_trip_stops(self):

        timetable_rows = self.timetable_data.trip_stops.copy()
        timetable_rows['trip_id'] = timetable_rows['trip_id'].astype('string')
        all_timetable_dates = self.timetable_data.service_dates.copy()
        all_timetable_dates['trip_id'] = all_timetable_dates['trip_id'].astype('string')

        joined_df = pd.merge(all_timetable_dates, timetable_rows, left_on=['trip_id', 'service_id'],
                             right_on=['trip_id', 'service_id'], how='left')
        joined_df = joined_df.dropna(subset=['stop_id'])

        ordered_df = joined_df.sort_values(by=['date', 'stop_sequence', 'start_time', 'trip_id'])
        selected_columns = ['date', 'day', 'start_time', 'trip_id', 'stop_name', 'stop_sequence', 'arrival_time',
                            'service_id', 'stop_id']
        ordered_df = ordered_df[selected_columns]
        ordered_df['arrival_time'] = ordered_df['arrival_time'].map(self.normalize_time)
        ordered_df['start_time'] = ordered_df['start_time'].map(self.normalize_time)
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

        self.timetable_data.ordered_stops = filtered_stop_names

    def create_timetable_after_sorting(self) -> None:
        self._build_timetable(keep_source_rows=False)

    def create_timetable(self) -> None:
        self._build_timetable(keep_source_rows=True)

    def _build_timetable(self, *, keep_source_rows: bool) -> None:
        sorted_stops = self.timetable_data.sorted_stops
        filtered_stop_names = self.timetable_data.ordered_stops

        if (
            sorted_stops is None
            or filtered_stop_names is None
            or sorted_stops.empty
            or filtered_stop_names.empty
        ):
            raise ValueError(ErrorMessage.NO_TRIPS_IN_DATE_RANGE)

        prefixed_stops = sorted_stops.add_prefix('sorted_')
        joined_df = pd.merge(
            prefixed_stops,
            filtered_stop_names,
            left_on='sorted_stop_id',
            right_on='stop_id',
            how='left',
        )
        grouped_df = joined_df.groupby(
            ['sorted_date', 'sorted_day', 'sorted_start_time', 'sorted_arrival_time', 'sorted_trip_id',
             'sorted_stop_name', 'stop_sequence',
             'sorted_stop_sequence', 'sorted_stop_id'])
        aggregated_df = grouped_df.size().reset_index(name='count')
        ordered_df = aggregated_df.sort_values(
            by=['sorted_date', 'sorted_stop_sequence', 'sorted_start_time', 'sorted_trip_id'])
        selected_columns = ['sorted_date', 'sorted_day', 'sorted_start_time', 'sorted_trip_id', 'sorted_stop_name',
                            'stop_sequence',
                            'sorted_stop_sequence', 'sorted_arrival_time', 'sorted_stop_id']

        timetable_rows = ordered_df[selected_columns].copy()
        timetable_rows['sorted_date'] = pd.to_datetime(timetable_rows['sorted_date'], format='%Y-%m-%d %H:%M:%S.%f')
        timetable_rows['sorted_arrival_time'] = timetable_rows['sorted_arrival_time'].astype('string')
        timetable_rows['sorted_start_time'] = timetable_rows['sorted_start_time'].astype('string')
        if not keep_source_rows:
            timetable_rows = timetable_rows.drop(columns=['sorted_stop_sequence'])
        timetable_rows = timetable_rows.groupby(
            ['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id', 'sorted_start_time',
             'sorted_trip_id']).first().reset_index()
        timetable_rows['sorted_date'] = pd.to_datetime(timetable_rows['sorted_date'], format='%Y-%m-%d')
        timetable_rows['sorted_arrival_time'] = timetable_rows['sorted_arrival_time'].astype('string')

        if self.planning_settings.time_format == TimeFormat.HOURS_MINUTES:
            timetable_rows['sorted_arrival_time'] = timetable_rows['sorted_arrival_time'].map(
                self.remove_seconds
            )

        timetable_rows['sorted_start_time'] = timetable_rows['sorted_start_time'].astype('string')

        if keep_source_rows:
            self.timetable_data.timetable_rows = timetable_rows

        self.timetable_data.timetable = timetable_rows.pivot(
            index=['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id'],
            columns=['sorted_start_time', 'sorted_trip_id'],
            values='sorted_arrival_time')

        self.timetable_data.timetable = self.timetable_data.timetable.sort_index(axis=1).sort_index(axis=0)

    def filter_stop_sequence(self, data: pd.DataFrame) -> dict[str, list]:
        stop_sequence: dict[str, dict] = {}
        sorted_stop_sequence = {
            "stop_id": [],
            "stop_sequence": [],
            "stop_name": [],
            "start_time": [],
        }
        rows = list(data.itertuples())

        for initial_stop in rows:
            if initial_stop.stop_id in stop_sequence:
                continue

            initial_start = self._service_datetime(initial_stop.date, initial_stop.start_time)
            candidate = {
                "stop_sequence": initial_stop.stop_sequence,
                "stop_name": initial_stop.stop_name,
                "trip_id": initial_stop.trip_id,
                "start_time": initial_start,
                "arrival_time": self._service_datetime(
                    initial_stop.date,
                    initial_stop.arrival_time,
                ),
            }

            for compared_stop in rows:
                if initial_stop.stop_id != compared_stop.stop_id:
                    continue

                compared_start = self._service_datetime(
                    compared_stop.date,
                    compared_stop.start_time,
                )
                if (
                        compared_start < initial_start
                        and compared_start < candidate["start_time"]
                        and compared_stop.stop_sequence > initial_stop.stop_sequence
                        and compared_stop.stop_sequence > candidate["stop_sequence"]
                ):
                    candidate["start_time"] = compared_start
                    candidate["arrival_time"] = self._service_datetime(
                        compared_stop.date,
                        compared_stop.arrival_time,
                    )
                    candidate["stop_sequence"] = compared_stop.stop_sequence

            stop_sequence[initial_stop.stop_id] = candidate

        ordered_stops = self._sort_stop_sequence(stop_sequence)

        for sequence, stop in ordered_stops.items():
            sorted_stop_sequence["stop_id"].append(stop["stop_id"])
            sorted_stop_sequence["stop_sequence"].append(sequence)
            sorted_stop_sequence["stop_name"].append(stop["stop_name"])
            sorted_stop_sequence["start_time"].append(stop["start_time"])

        return sorted_stop_sequence

    @staticmethod
    def _sort_stop_sequence(stop_sequence: dict[str, dict]) -> dict[str, dict]:
        stops = (
            {"stop_id": stop_id, **values}
            for stop_id, values in stop_sequence.items()
        )
        ordered = sorted(
            stops,
            key=lambda stop: (stop["stop_sequence"], stop["start_time"]),
        )
        return {str(index): stop for index, stop in enumerate(ordered)}

    @staticmethod
    def _service_datetime(service_date, value: str) -> datetime:
        seconds = gtfs_time_to_seconds(value)
        if seconds is None:
            raise ValueError("A stop time cannot be empty")
        service_day = pd.Timestamp(service_date).normalize().to_pydatetime()
        return service_day + timedelta(seconds=seconds)

    @staticmethod
    def normalize_time(value: str) -> str:
        """Pad a one-digit GTFS hour for stable lexical sorting."""
        return f"0{value}" if re.fullmatch(r"\d:\d{2}:\d{2}", value) else value

    @staticmethod
    def remove_seconds(value: str) -> str:
        return value[:-3]
