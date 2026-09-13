import pandas as pd
from PySide6.QtCore import QObject

from model.enums import ErrorMessage


class VehicleCirculationPlanner(QObject):
    def __init__(self, plans):
        super().__init__()
        self.plans = plans

    def create_circulation_plan(self) -> None:
        if len(self.plans) != 2:
            raise ValueError(ErrorMessage.PLAN_CREATION_FAILED)
        self._merge_direction_plans()

    def _merge_direction_plans(self) -> None:
        merged_stops = self._add_vehicle_numbers()
        self._rebuild_direction_timetables(merged_stops)

    def _rebuild_direction_timetables(self, merged_stops: pd.DataFrame) -> None:
        direction_zero = merged_stops[merged_stops['direction'] == 0].reset_index(drop=True)
        direction_one = merged_stops[merged_stops['direction'] == 1].reset_index(drop=True)

        self.plans[0].timetable_data.timetable = direction_zero.pivot(
            index=['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id'],
            columns=['sorted_start_time', 'sorted_trip_id', 'vehicle_number'],
            values='sorted_arrival_time').sort_index(
            axis=1).sort_index(
            axis=0)

        self.plans[1].timetable_data.timetable = direction_one.pivot(
            index=['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id'],
            columns=['sorted_start_time', 'sorted_trip_id', 'vehicle_number'],
            values='sorted_arrival_time').sort_index(
            axis=1).sort_index(
            axis=0)

    def _add_vehicle_numbers(self) -> pd.DataFrame:
        self.plans[0].timetable_data.timetable_rows['vehicle_number'] = 0
        self.plans[1].timetable_data.timetable_rows['vehicle_number'] = 0
        self.plans[0].timetable_data.timetable_rows['direction'] = 0
        self.plans[1].timetable_data.timetable_rows['direction'] = 1
        self.plans[0].timetable_data.timetable_rows['first_vehicle_trip'] = ''
        self.plans[1].timetable_data.timetable_rows['first_vehicle_trip'] = ''
        merged_df = pd.concat(
            [self.plans[0].timetable_data.timetable_rows, self.plans[1].timetable_data.timetable_rows], axis=0)

        # get the first and last station of each trip id and merge these two dfs
        merged_df['trip_sequence_id'] = merged_df['sorted_trip_id'].astype(str) + '_' + merged_df[
            'sorted_stop_sequence'].astype(str)
        first_stops = merged_df.groupby('sorted_trip_id', as_index=False).agg(
            {'sorted_stop_sequence': 'min'})
        last_stops = merged_df.groupby('sorted_trip_id', as_index=False).agg(
            {'sorted_stop_sequence': 'max'})
        merged_filtered_df = pd.concat([first_stops, last_stops], axis=0)
        merged_filtered_df['trip_sequence_id'] = merged_filtered_df['sorted_trip_id'].astype(str) + '_' + \
                                                 merged_filtered_df['sorted_stop_sequence'].astype(str)
        filtered_df_mask = merged_df['trip_sequence_id'].isin(merged_filtered_df['trip_sequence_id'])
        filtered_df = merged_df[filtered_df_mask]
        return self._assign_vehicle_numbers(filtered_df, merged_df)

    def _assign_vehicle_numbers(
        self,
        trip_endpoints: pd.DataFrame,
        all_stops: pd.DataFrame,
    ) -> pd.DataFrame:
        trip_endpoints = trip_endpoints.sort_values(
            by=['sorted_start_time', 'sorted_trip_id', 'sorted_stop_sequence']
        )

        current_vehicle_number = 1
        assignments = trip_endpoints.copy(deep=True).sort_values(
            by=['sorted_start_time', 'sorted_stop_sequence', 'sorted_trip_id']
        )

        for _, trip in trip_endpoints.iterrows():
            if current_vehicle_number != 1 and self._has_assigned_vehicle(trip, assignments):
                continue

            current_trip = trip
            assignments.loc[
                (assignments['sorted_trip_id'] == current_trip['sorted_trip_id'])
                & (assignments['sorted_stop_sequence'] == 0),
                'first_vehicle_trip',
            ] = '*'
            all_stops.loc[(all_stops['sorted_trip_id'] == current_trip['sorted_trip_id']) & (
                    all_stops['sorted_stop_sequence'] == 0), 'first_vehicle_trip'] = '*'

            while True:
                assignments.loc[assignments['sorted_trip_id'] == current_trip[
                    'sorted_trip_id'], 'vehicle_number'] = current_vehicle_number
                all_stops.loc[all_stops['sorted_trip_id'] == current_trip[
                    'sorted_trip_id'], 'vehicle_number'] = current_vehicle_number

                last_stops = assignments[
                    (assignments['sorted_trip_id'] == current_trip['sorted_trip_id'])
                    & (assignments['sorted_stop_sequence'] != 0)
                ]
                if last_stops.empty:
                    break
                last_stop = last_stops.iloc[0]
                next_trips = assignments[
                    (assignments['sorted_trip_id'] != last_stop['sorted_trip_id'])
                    & (assignments['direction'] != last_stop['direction'])
                    & (assignments['sorted_stop_sequence'] == 0)
                    & (assignments['sorted_start_time'] >= last_stop['sorted_arrival_time'])
                    & (assignments['vehicle_number'] == 0)
                ]

                if next_trips.empty:
                    break

                current_trip = next_trips.sort_values('sorted_start_time').iloc[0]

            current_vehicle_number += 1

        return all_stops

    @staticmethod
    def _has_assigned_vehicle(trip, assignments: pd.DataFrame) -> bool:
        return assignments[
            (assignments['sorted_trip_id'] == trip['sorted_trip_id'])
            & (assignments['vehicle_number'] == 0)
        ].empty
