# -*- coding: utf-8 -*-
import concurrent.futures
import copy
import logging

from PySide6.QtCore import Signal, QObject
import pandas as pd
from model.Enum.GTFSEnums import CreatePlanMode
from ..Dto.CreateSettingsForTableDto import CreateSettingsForTableDTO
from ..Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto
from ..SchedulePlaner.UmplaufPlaner.UmlaufPlaner import UmlaufPlaner

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class CreatePlan(QObject):
    progress_Update = Signal(int)
    error_occured = Signal(str)
    create_sorting = Signal()

    def __init__(self, app, progress: int):
        super().__init__()
        self.app = app
        self.reset_create = False
        self.create_plan_mode = None
        self.gtfs_data_frame_dto = None
        self.create_settings_for_table_dto = CreateSettingsForTableDTO()
        self.plans = None

        """ visual internal property """
        self.progress = progress

        self.weekend = ['Saturday', 'Sunday']
        self.weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Create DataFrames with category information
        self.df_all = pd.DataFrame(self.days, columns=['day']).assign(category='All Days')
        self.df_weekend = pd.DataFrame(self.weekend, columns=['day']).assign(category='Weekend')
        self.df_weekdays = pd.DataFrame(self.weekdays, columns=['day']).assign(category='Weekdays')
        self.df_weekdays_only = pd.DataFrame({
            'day': self.weekdays,
            'category': [f'{day} only' for day in self.weekdays]  # Create unique category for each day
        })
        self.weekdays_df = pd.concat([
            self.df_all,
            self.df_weekend,
            self.df_weekdays,
            self.df_weekdays_only
        ])

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
        self.progress = 0
        if self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_date and self.create_settings_for_table_dto.individual_sorting:
            self.plans = [UmlaufPlaner(), UmlaufPlaner()]
            self.plans[0].create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
            self.plans[0].gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)

            self.plans[1].create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
            self.plans[1].create_settings_for_table_dto.direction = 1
            self.plans[1].gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)

            logging.debug(f"plans: {self.plans[0].create_settings_for_table_dto.direction}\n"
                          f"       {self.plans[1].create_settings_for_table_dto.direction}")

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                processes = [executor.submit(self.plans[0].create_table),
                             executor.submit(self.plans[1].create_table)]

                test = concurrent.futures.as_completed(processes)

            self.create_sorting.emit()

        elif (self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.date
               and self.create_settings_for_table_dto.individual_sorting):
            self.plans = UmlaufPlaner()
            self.plans.create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
            self.plans.gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)
            self.plans.create_table()
            self.create_sorting.emit()

        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_date or self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_weekday:
            self.plans = [UmlaufPlaner(), UmlaufPlaner()]
            self.plans[0].create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
            self.plans[0].create_settings_for_table_dto.direction = 0
            self.plans[0].gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)

            self.plans[1].create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
            self.plans[1].create_settings_for_table_dto.direction = 1
            self.plans[1].gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)

            logging.debug(f"plans: Direction {self.plans[0].create_settings_for_table_dto.direction}\n"
                          f"       Direction {self.plans[1].create_settings_for_table_dto.direction}")

            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [executor.submit(self.plans[0].create_table),
                               executor.submit(self.plans[1].create_table)]

                for future in concurrent.futures.as_completed(futures):
                    try:
                        _ = future.result()
                    except Exception as exc:
                        logging.debug(f'Thread generated an exception: {exc}')
            except Exception as exc:
                logging.debug(f'An error occurred during execution: {exc}')




        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.date:
            self.plans = UmlaufPlaner()
            self.plans.create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
            self.plans.gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)
            self.progress = 10
            self.plans.dates_prepare_data_fahrplan()
            self.progress = 20
            self.plans.datesWeekday_select_dates_for_date_range()
            self.progress = 30
            self.plans.dates_select_dates_delete_exception_2()
            self.progress = 40
            self.plans.datesWeekday_select_stops_for_trips()
            self.progress = 50
            self.plans.datesWeekday_select_for_every_date_trips_stops()
            self.progress = 70
            self.plans.datesWeekday_create_sort_stopnames()
            self.progress = 80
            self.plans.datesWeekday_create_fahrplan()
            self.progress = 90

        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.weekday and self.create_settings_for_table_dto.individual_sorting:
            self.plans = UmlaufPlaner()
            self.plans.create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
            self.plans.gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)
            self.progress = 10
            self.plans.weekday_prepare_data_fahrplan()
            self.progress = 20
            self.plans.datesWeekday_select_dates_for_date_range()
            self.progress = 30
            self.plans.weekday_select_weekday_exception_2()
            self.progress = 40
            self.plans.datesWeekday_select_stops_for_trips()
            self.progress = 50
            self.plans.datesWeekday_select_for_every_date_trips_stops()
            self.progress = 70
            self.plans.datesWeekday_create_sort_stopnames()
            self.create_sorting.emit()

        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.weekday:
            self.plans = UmlaufPlaner()
            self.plans.create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
            self.plans.gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)
            self.progress = 10
            self.plans.weekday_prepare_data_fahrplan()
            self.progress = 20
            self.plans.datesWeekday_select_dates_for_date_range()
            self.progress = 30
            self.plans.weekday_select_weekday_exception_2()
            self.progress = 40
            self.plans.datesWeekday_select_stops_for_trips()
            self.progress = 50
            self.plans.datesWeekday_select_for_every_date_trips_stops()
            self.progress = 70
            self.plans.datesWeekday_create_fahrplan()
            self.progress = 80

        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_weekday and self.create_settings_for_table_dto.individual_sorting:
            self.plans = UmlaufPlaner()
            self.plans.create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
            self.plans.gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)
            self.progress = 10
            self.plans.weekday_prepare_data_fahrplan()
            self.progress = 20
            self.plans.datesWeekday_select_dates_for_date_range()
            self.progress = 30
            self.plans.weekday_select_weekday_exception_2()
            self.progress = 40
            self.plans.datesWeekday_select_stops_for_trips()
            self.progress = 50
            self.plans.datesWeekday_select_for_every_date_trips_stops()
            self.progress = 70
            self.plans.datesWeekday_create_sort_stopnames()
            self.create_sorting.emit()

        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_weekday:
            self.plans = UmlaufPlaner()
            self.plans.create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
            self.plans.gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)
            self.progress = 10
            self.plans.weekday_prepare_data_fahrplan()
            self.progress = 20
            self.plans.datesWeekday_select_dates_for_date_range()
            self.progress = 30
            self.plans.weekday_select_weekday_exception_2()
            self.progress = 40
            self.plans.datesWeekday_select_stops_for_trips()
            self.progress = 50
            self.plans.datesWeekday_select_for_every_date_trips_stops()
            self.progress = 70
            self.plans.datesWeekday_create_fahrplan()
            self.progress = 80

    def create_table_continue(self):
        self.plans.datesWeekday_create_fahrplan_continue()
        self.progress = 80


