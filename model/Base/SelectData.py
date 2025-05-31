# -*- coding: utf-8 -*-
import logging
import time

from PySide6.QtCore import Signal, QObject
import pandas as pd

from .Progress import ProgressSignal
from ..Dto.CreateSettingsForTableDto import CreateSettingsForTableDTO
from ..Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto
from ..Enum.GTFSEnums import CreatePlanMode

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class SelectData(QObject):
    progress_Update = Signal(ProgressSignal)
    error_occured = Signal(str)
    select_agency_signal = Signal()
    update_routes_list_signal = Signal()
    data_selected = Signal(bool)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.gtfs_data_frame_dto = None
        self._agencies_list = None
        self._df_selected_routes = None

        self._selected_agency = None
        self._selected_route = None
        self._selected_weekday = None
        self._selected_dates = None
        self._selected_timeformat = 1
        self._selected_direction = None
        self._selected_create_plan_mode = None
        self._use_individual_sorting = False

        self.header_for_export_data = None
        self.df_header_for_export_data = None
        self.last_time = time.time()

        self.reset_select_data = False

        """ visual internal property """
        self.progress = ProgressSignal()

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

        # Create DataFrame
        self.weekday_options_df = pd.DataFrame(self.week_day_options)

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
    def selected_route(self):
        return self._selected_route

    @selected_route.setter
    def selected_route(self, value):
        self._selected_route = value
        self.data_selected.emit(value is not None)

    @property
    def selected_direction(self):
        return self._selected_direction

    @selected_direction.setter
    def selected_direction(self, value):
        self._selected_direction = value
        self.data_selected.emit(value is not None)

    @property
    def selected_agency(self):
        return self._selected_agency

    @selected_agency.setter
    def selected_agency(self, value):
        self._selected_agency = value
        self.get_routes_of_agency()

    @property
    def df_selected_routes(self):
        return self._df_selected_routes

    @df_selected_routes.setter
    def df_selected_routes(self, value):
        self._df_selected_routes = value
        self.update_routes_list_signal.emit()

    @property
    def use_individual_sorting(self):
        return self._use_individual_sorting

    @use_individual_sorting.setter
    def use_individual_sorting(self, value):
        self._use_individual_sorting = value


    @property
    def selected_dates(self):
        return self._selected_dates

    @selected_dates.setter
    def selected_dates(self, value):
        self._selected_dates = value
        self.data_selected.emit(value is not None)

    @property
    def selected_create_plan_mode(self):
        return self._selected_create_plan_mode

    @selected_create_plan_mode.setter
    def selected_create_plan_mode(self, value):
        self._selected_create_plan_mode = value
        self.data_selected.emit(value is not None)

    @property
    def selected_weekday(self):
        return self._selected_weekday

    @selected_weekday.setter
    def selected_weekday(self, value):
        self._selected_weekday = value
        self.data_selected.emit(value is not None)

    @property
    def agencies_list(self):
        return self._agencies_list

    @agencies_list.setter
    def agencies_list(self, value):
        self._agencies_list = value
        self.select_agency_signal.emit()

    @property
    def selected_timeformat(self):
        return self._selected_timeformat

    @selected_timeformat.setter
    def selected_timeformat(self, value):
        self._selected_timeformat = value
        self.data_selected.emit(value is not None)
        logging.debug(value)

    @property
    def gtfs_data_frame_dto(self):
        return self._gtfs_data_frame_dto

    @gtfs_data_frame_dto.setter
    def gtfs_data_frame_dto(self, value: GtfsDataFrameDto):
        self._gtfs_data_frame_dto = value
        if value is not None:
            self.read_gtfs_agencies()

    def initialize_select_data(self):
        self.selected_agency = None
        self.selected_route = None
        self.selected_weekday = None
        self.selected_dates = None
        self.selected_timeformat = 1
        self.selected_direction = 0
        self.use_individual_sorting = False
        self.create_plan_mode = CreatePlanMode.date

    def get_routes_of_agency(self) -> None:
        if self.selected_agency is not None:
            self.find_routes_from_agency()

    def find_routes_from_agency(self):
        self.df_selected_routes = self.gtfs_data_frame_dto.Routes[self.gtfs_data_frame_dto.Routes['agency_id'].isin(self.selected_agency['agency_id'])]
        return True

    def read_gtfs_agencies(self):
        df_agency = self.gtfs_data_frame_dto.Agencies
        df_agency_ordered = df_agency.sort_values(by='agency_id')
        agency_list = df_agency_ordered.values.tolist()
        agency_str_list = [f'{row[0]},{row[1]}' for row in agency_list]
        self.agencies_list = agency_str_list
        return True
