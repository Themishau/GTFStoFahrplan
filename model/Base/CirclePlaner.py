# -*- coding: utf-8 -*-
from copy import deepcopy

from PyQt5.QtCore import QObject, pyqtSignal
import logging
import copy
from pandasql import sqldf
import re
from datetime import datetime, timedelta
import pandas as pd
from model.Enum.GTFSEnums import CreatePlanMode, ErrorMessageRessources
from model.Dto.CreateSettingsForTableDto import CreateSettingsForTableDTO
from model.Dto.CreateTableDataframeDto import CreateTableDataframeDto
from model.Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto
from model.SchedulePlaner.UmplaufPlaner.UmlaufPlaner import UmlaufPlaner

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class CirclePlaner(QObject):
    progress_Update = pyqtSignal(int)
    error_occured = pyqtSignal(str)

    def __init__(self, plans, app, progress: int):
        super().__init__()
        self.app = app
        self.create_settings_for_table_dto = CreateSettingsForTableDTO()
        self.plans =  plans
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
        self.add_vehicle_number()

        NotImplementedError()

    def add_vehicle_number(self):
        self.plans[0].create_dataframe.SortedDataframe['vehicle_number'] = 0
        self.plans[1].create_dataframe.SortedDataframe['vehicle_number'] = 0
        merged_df = pd.concat([self.plans[0].create_dataframe.SortedDataframe, self.plans[1].create_dataframe.SortedDataframe], axis=0)

        # get the first and last station of each trip id and merge these two dfs
        merged_df['trip_sequence_id'] = merged_df['sorted_trip_id'].astype(str) + '_' + merged_df['sorted_stop_sequence'].astype(str)
        filtered_first_stations_df = merged_df.groupby('sorted_trip_id', as_index=False).agg({'sorted_stop_sequence': 'min'}).rename(columns={'sorted_stop_sequence': 'sorted_stop_sequence'})
        filtered_last_station_sequence_df = merged_df.groupby('sorted_trip_id', as_index=False).agg({'sorted_stop_sequence': 'max'}).rename(columns={'sorted_stop_sequence': 'sorted_stop_sequence'})
        merged_filtered_df = pd.concat([filtered_first_stations_df, filtered_last_station_sequence_df], axis=0)
        merged_filtered_df['trip_sequence_id'] = merged_filtered_df['sorted_trip_id'].astype(str) + '_' + merged_filtered_df['sorted_stop_sequence'].astype(str)

        # add ['trip_sequence_id'] also to the concat series and use it with isin to filter


        filtered_df_mask = merged_df['trip_sequence_id'].isin(merged_filtered_df['trip_sequence_id'])
        filtered_df = merged_df[filtered_df_mask]
        test = self.assign_vehicle_numbers(filtered_df)

    def assign_vehicle_numbers(self, df):

        # given is a df with trip_id, arrival_time (at a station), sequence_number (number in order of stops), vehicle_number and  start_time (of the trip)
        # vehicle_number is init with 0
        # get the first trip_id with sequence 0 and set the vehicle_number to int: x
        # get the next entry with same trip_id and sequence != 0 (there are only two entries) use the last entry and set also vehicle_number to int: x
        # look for the next fitting trip_id with sequence 0 based on arrival_time (trip_id 123 start_time : 04:26:00 -> trip_id 234 start_time: 04:46:00)
        # if found set also the vehicle number to 1 because we assume that it is the next trip and also search for the entry with same trip_id and sequence != 0
        # do it till no trip is found
        # set int: x + 1 and continue with next entry with vehicle_number = 0

        df = df.sort_values(by=['sorted_start_time', 'sorted_trip_id', 'sorted_stop_sequence'])
        # Initialize variables
        current_vehicle_number = 1

        # Create a new DataFrame to store the result
        result_df = copy.deepcopy(df)
        result_df = result_df.sort_values(by=['sorted_start_time','sorted_stop_sequence', 'sorted_trip_id'])

        for _, row in df.iterrows():

            if current_vehicle_number != 1 and self.has_records_with_vehicle_number(row, result_df):
                continue

            current_trip_id = row

            while True:

                result_df.loc[result_df['sorted_trip_id'] == current_trip_id['sorted_trip_id'], 'vehicle_number'] = current_vehicle_number

                current_last_time_stop = result_df[(result_df['sorted_trip_id'] == current_trip_id['sorted_trip_id']) & (result_df['sorted_stop_sequence'] != 0)]
                current_last_time_stop = current_last_time_stop.iloc[0] if not current_last_time_stop.empty else None
                current_trip_id = result_df[
                    (result_df['sorted_trip_id'] != current_last_time_stop['sorted_trip_id'])  &
                    (result_df['sorted_stop_sequence'] == 0) &
                    (result_df['sorted_start_time'] >= current_last_time_stop['sorted_arrival_time']) &
                    (result_df['vehicle_number'] == 0)
                    ]

                if current_trip_id.empty:
                    break

                current_trip_id = current_trip_id.sort_values('sorted_start_time').iloc[0]


            current_vehicle_number += 1


        return result_df

    def has_records_with_vehicle_number(self, row, result_df):
        return result_df[(result_df['sorted_trip_id'] == row['sorted_trip_id']) & (result_df['vehicle_number'] == 0)].empty







