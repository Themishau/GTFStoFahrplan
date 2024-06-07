# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal, QObject, QCoreApplication

from model.observer import Publisher, Subscriber
import time
import pandas as pd
from pandasql import sqldf
import zipfile
import io
from datetime import datetime, timedelta
import re
import logging
import sys
import os
from model.Base.GTFSEnums import *
from model.Base.ProgressBar import ProgressBar
from model.Base.ImportData import ImportData
from ..DTO.CreateSettingsForTableDTO import CreateSettingsForTableDTO
from ..DTO.General_Transit_Feed_Specification import GtfsListDto, GtfsDataFrameDto

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class SelectData(QObject):
    progress_update = pyqtSignal(int)
    select_agency_signal = pyqtSignal()
    update_routes_list_signal = pyqtSignal()
    error_occured = pyqtSignal(str)
    data_selected = pyqtSignal(bool)
    create_settings_for_table_dto_changed = pyqtSignal()

    def __init__(self, app, progress: int):
        super().__init__()
        self.app = app
        self.gtfs_data_frame_dto = None
        self.create_settings_for_table_dto = CreateSettingsForTableDTO()
        self.agencies_list = None
        self.df_selected_routes = None

        self.selected_agency = None
        self.selected_route = None
        self.selected_weekday = None
        self.selected_dates = None
        self.selected_timeformat = 1

        self.header_for_export_data = None
        self.df_header_for_export_data = None
        self.last_time = time.time()
        self.df_direction = None

        self.reset_select_data = False
        self.create_plan_mode = None
        self.progress = progress

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
        self.week_day_options_list = ['0,Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday',
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
        self.progress_update.emit(self.progress)

    @property
    def selected_route(self):
        return self._selected_route

    @selected_route.setter
    def selected_route(self, value):
        self._selected_route = value
        self.create_settings_for_table_dto.route = value
        self.create_settings_for_table_dto_changed.emit()
        self.data_selected.emit(value is not None)

    @property
    def selected_agency(self):
        return self._selected_agency

    @selected_agency.setter
    def selected_agency(self, value):
        self._selected_agency = value
        self.create_settings_for_table_dto.agency = value
        self.create_settings_for_table_dto_changed.emit()
        self.get_routes_of_agency()

    @property
    def df_selected_routes(self):
        return self._df_selected_routes

    @df_selected_routes.setter
    def df_selected_routes(self, value):
        self._df_selected_routes = value
        self.update_routes_list_signal.emit()


    @property
    def agencies_list(self):
        return self._agencies_list

    @agencies_list.setter
    def agencies_list(self, value):
        self._agencies_list = value
        if value is not None:
            self.select_agency_signal.emit()

    @property
    def selected_timeformat(self):
        return self._selected_timeformat

    @selected_timeformat.setter
    def selected_timeformat(self, value):
        self._selected_timeformat = value
        self.create_settings_for_table_dto.timeformat = value
        self.create_settings_for_table_dto_changed.emit()
        logging.debug(value)

    @property
    def gtfs_data_frame_dto(self):
        return self._gtfs_data_frame_dto

    @gtfs_data_frame_dto.setter
    def gtfs_data_frame_dto(self, value: GtfsDataFrameDto):
        self._gtfs_data_frame_dto = value
        if value is not None:
            self.read_gtfs_agencies()

    def get_routes_of_agency(self) -> None:
        if self.selected_agency is not None:
            self.find_routes_from_agency()

    def find_routes_from_agency(self):
        # df_routes = self.imported_data[GtfsDfNames.Routes]
        # input_var = [{'agency_id': self.selected_agency}]
        # var_test = pd.DataFrame(input_var).set_index('agency_id')
        # cond_routes_of_agency = '''
        #             select *
        #             from df_routes
        #             left join var_test
        #             where var_test.agency_id = df_routes.agency_id
        #             order by df_routes.route_short_name;
        #            '''
        # routes_list = sqldf(cond_routes_of_agency, locals())
        #
        # self.df_selected_routes = routes_list

        df_routes = self.gtfs_data_frame_dto.Routes

        # Create a DataFrame from input_var and set 'agency_id' as the index
        input_var = [{'agency_id': self.selected_agency}]
        var_test = pd.DataFrame(input_var).set_index('agency_id')

        # Perform a left join between df_routes and var_test on 'agency_id'
        # Filter rows where 'agency_id' in var_test matches 'agency_id' in df_routes
        # Order the result by 'route_short_name'
        routes_list = df_routes.merge(var_test, left_on='agency_id', right_index=True, how='left')
        routes_list = routes_list[routes_list['agency_id'].notna()].sort_values(by='route_short_name')

        # Assign the filtered and sorted DataFrame to self.df_selected_routes
        self.df_selected_routes = routes_list
        return True

    def read_gtfs_agencies(self):
        # df_agency = self.imported_data[GtfsDfNames.Agencies]
        # cond_agencies = '''
        #             select *
        #             from df_agency
        #             order by df_agency.agency_id;
        #            '''
        # agency_list = sqldf(cond_agencies, locals())
        # agency_list = agency_list.values.tolist()
        # agency_str_list = []

        # for lists in agency_list:
        #     agency_str_list.append('{},{}'.format(lists[0], lists[1]))
        # self.agencies_list = agency_str_list
        # print (agency_list.values.tolist())

        df_agency = self.gtfs_data_frame_dto.Agencies
        # Order the DataFrame by agency_id
        df_agency_ordered = df_agency.sort_values(by='agency_id')
        # Convert the DataFrame to a list of lists
        agency_list = df_agency_ordered.values.tolist()
        # Format each row into a string and store in agency_str_list
        agency_str_list = [f'{row[0]},{row[1]}' for row in agency_list]
        # Assign the list of strings to self.agencies_list
        self.agencies_list = agency_str_list
        return True
