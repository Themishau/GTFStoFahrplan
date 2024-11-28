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
        filtered_first_stations_df = merged_df.groupby('trip_id')['sequence_number'].min().reset_index()
        filtered_last_station_sequence_df = merged_df.groupby('trip_id')['sequence_number'].max().reset_index()
        merged_filtered_df = pd.concat([filtered_first_stations_df, filtered_last_station_sequence_df], axis=0)
        test = self.assign_vehicle_numbers(merged_filtered_df)

    def assign_vehicle_numbers(self, df):

        # get the first trip_id with sequence 0 and set the vehicle_number to 1
        # get the next entry with same trip_id and sequence != 0 (there are only two entries)
        # use the last entry and look for the next fitting trip_id with sequence 0 based on start_time (trip_id 123 start_time : 04:26:00 -> trip_id 234 start_time: 04:46:00)
        # if found set also the vehicle number to 1 because we assume that it is the next trip and also search for the entry with same trip_id and sequence != 0
        # do it till no trip is found and continue with vehicle number 2 and then 3 and so on

        df = df.sort_values(by=['start_time', 'trip_id', 'sequence_number'])
        # Initialize variables
        current_trip_id = None
        current_vehicle_number = 1
        current_last_time_stop = None

        # Create a new DataFrame to store the result
        result_df = copy.deepcopy(df)
        result_df = result_df.sort_values(by=['start_time', 'trip_id', 'sequence_number'])

        for _, row in df.iterrows():
            trip_id = row['trip_id']
            sequence_number = row['sequence_number']
            # result_df[result_df['arrival_time']]
            current_last_time_stop = result_df[(result_df['trip_id'] == trip_id) & (result_df['trip_id'] != trip_id) ]

            if current_trip_id != trip_id:
                current_vehicle_number = 1

            vehicle_number = current_vehicle_number
            current_vehicle_number += 1

            result_df.loc[_, 'vehicle_number'] = vehicle_number

            current_trip_id = trip_id

        return result_df







