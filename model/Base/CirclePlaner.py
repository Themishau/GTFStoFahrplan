# -*- coding: utf-8 -*-
from copy import deepcopy

from PySide6.QtCore import Signal, QObject
import logging
import copy
import pandas as pd
from model.Enum.GTFSEnums import ErrorMessageRessources
from model.Dto.CreateSettingsForTableDto import CreateSettingsForTableDTO

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class CirclePlaner(QObject):
    progress_Update = Signal(int)
    error_occured = Signal(str)

    def __init__(self, plans, app, progress: int):
        super().__init__()
        self.app = app
        self.create_settings_for_table_dto = CreateSettingsForTableDTO()
        self.plans = plans
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

    def ReadCreatedSchedulePlans(self):
        NotImplementedError()

    def CreateCirclePlan(self):
        if self.CheckintegrityPlans() is False:
            return False
        self.MergePlans()

    def CheckintegrityPlans(self) -> False:
        if len(self.plans) != 2:
            self.error_occured.emit(ErrorMessageRessources.no_create_object_generated.value)
            return False

    def MergePlans(self):
        merged_plans = self.add_vehicle_number()
        self.create_updated_pivot_tables(merged_plans)

    def create_updated_pivot_tables(self, merged_df):
        df_direction_0 = merged_df[merged_df['direction'] == 0].reset_index(drop=True)
        df_direction_1 = merged_df[merged_df['direction'] == 1].reset_index(drop=True)

        self.plans[0].create_dataframe.FahrplanCalendarFilterDaysPivot = df_direction_0.pivot(
            index=['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id'],
            columns=['sorted_start_time', 'sorted_trip_id', 'vehicle_number'],
            values='sorted_arrival_time').sort_index(
            axis=1).sort_index(
            axis=0)

        self.plans[1].create_dataframe.FahrplanCalendarFilterDaysPivot = df_direction_1.pivot(
            index=['sorted_date', 'sorted_day', 'stop_sequence', 'sorted_stop_name', 'sorted_stop_id'],
            columns=['sorted_start_time', 'sorted_trip_id', 'vehicle_number'],
            values='sorted_arrival_time').sort_index(
            axis=1).sort_index(
            axis=0)

    def add_vehicle_number(self):
        self.plans[0].create_dataframe.GftsTableData['vehicle_number'] = 0
        self.plans[1].create_dataframe.GftsTableData['vehicle_number'] = 0
        self.plans[0].create_dataframe.GftsTableData['direction'] = 0
        self.plans[1].create_dataframe.GftsTableData['direction'] = 1
        self.plans[0].create_dataframe.GftsTableData['first_vehicle_trip'] = ''
        self.plans[1].create_dataframe.GftsTableData['first_vehicle_trip'] = ''
        merged_df = pd.concat(
            [self.plans[0].create_dataframe.GftsTableData, self.plans[1].create_dataframe.GftsTableData], axis=0)

        # get the first and last station of each trip id and merge these two dfs
        merged_df['trip_sequence_id'] = merged_df['sorted_trip_id'].astype(str) + '_' + merged_df[
            'sorted_stop_sequence'].astype(str)
        filtered_first_stations_df = merged_df.groupby('sorted_trip_id', as_index=False).agg(
            {'sorted_stop_sequence': 'min'}).rename(columns={'sorted_stop_sequence': 'sorted_stop_sequence'})
        filtered_last_station_sequence_df = merged_df.groupby('sorted_trip_id', as_index=False).agg(
            {'sorted_stop_sequence': 'max'}).rename(columns={'sorted_stop_sequence': 'sorted_stop_sequence'})
        merged_filtered_df = pd.concat([filtered_first_stations_df, filtered_last_station_sequence_df], axis=0)
        merged_filtered_df['trip_sequence_id'] = merged_filtered_df['sorted_trip_id'].astype(str) + '_' + \
                                                 merged_filtered_df['sorted_stop_sequence'].astype(str)
        filtered_df_mask = merged_df['trip_sequence_id'].isin(merged_filtered_df['trip_sequence_id'])
        filtered_df = merged_df[filtered_df_mask]
        merged_df = self.assign_vehicle_numbers(filtered_df, merged_df)
        return merged_df

    def assign_vehicle_numbers(self, df, all_df):
        df = df.sort_values(by=['sorted_start_time', 'sorted_trip_id', 'sorted_stop_sequence'])

        current_vehicle_number = 1

        result_df = copy.deepcopy(df)
        result_df = result_df.sort_values(by=['sorted_start_time', 'sorted_stop_sequence', 'sorted_trip_id'])

        for _, row in df.iterrows():

            if current_vehicle_number != 1 and self.has_records_with_vehicle_number(row, result_df):
                continue

            current_trip_id = row
            result_df.loc[(result_df['sorted_trip_id'] == current_trip_id['sorted_trip_id']) & (
                        result_df['sorted_stop_sequence'] == 0), 'first_vehicle_trip'] = '*'
            all_df.loc[(all_df['sorted_trip_id'] == current_trip_id['sorted_trip_id']) & (
                        all_df['sorted_stop_sequence'] == 0), 'first_vehicle_trip'] = '*'

            while True:

                result_df.loc[result_df['sorted_trip_id'] == current_trip_id[
                    'sorted_trip_id'], 'vehicle_number'] = current_vehicle_number
                all_df.loc[all_df['sorted_trip_id'] == current_trip_id[
                    'sorted_trip_id'], 'vehicle_number'] = current_vehicle_number

                current_last_time_stop = result_df[
                    (result_df['sorted_trip_id'] == current_trip_id['sorted_trip_id']) & (
                                result_df['sorted_stop_sequence'] != 0)]
                current_last_time_stop = current_last_time_stop.iloc[0] if not current_last_time_stop.empty else None
                current_trip_id = result_df[
                    (result_df['sorted_trip_id'] != current_last_time_stop['sorted_trip_id']) &
                    (result_df['direction'] != current_last_time_stop['direction']) &
                    (result_df['sorted_stop_sequence'] == 0) &
                    (result_df['sorted_start_time'] >= current_last_time_stop['sorted_arrival_time']) &
                    (result_df['vehicle_number'] == 0)
                    ]

                if current_trip_id.empty:
                    break

                current_trip_id = current_trip_id.sort_values('sorted_start_time').iloc[0]

            current_vehicle_number += 1

        return all_df

    def has_records_with_vehicle_number(self, row, result_df):
        return result_df[
            (result_df['sorted_trip_id'] == row['sorted_trip_id']) & (result_df['vehicle_number'] == 0)].empty
