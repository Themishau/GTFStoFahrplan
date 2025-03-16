# -*- coding: utf-8 -*-
import concurrent.futures
import copy
import logging
import re

from PySide6.QtCore import Signal, QObject
import pandas as pd
from model.Enum.GTFSEnums import CreatePlanMode
from .Progress import ProgressSignal
from ..Dto.CreateSettingsForTableDto import CreateSettingsForTableDTO
from ..Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto
from ..SchedulePlaner.CreationStrategy.ParallelTableCreationStrategy import ParallelTableCreationStrategy
from ..SchedulePlaner.CreationStrategy.SequentialTableCreationStrategy import SequentialTableCreationStrategy
from ..SchedulePlaner.CreationStrategy.TableCreationContext import TableCreationContext
from ..SchedulePlaner.UmplaufPlaner.UmlaufPlaner import UmlaufPlaner

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class CreatePlan(QObject):
    progress_Update = Signal(ProgressSignal)
    error_occured = Signal(str)
    create_sorting = Signal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.reset_create = False
        self.create_plan_mode = None
        self.gtfs_data_frame_dto = None
        self.create_settings_for_table_dto = CreateSettingsForTableDTO()
        self.strategy = None

        """ visual internal property """
        self.progress = ProgressSignal()

        #self.weekend = ['Saturday', 'Sunday']
        #self.weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Create DataFrames with category information
        self.df_all = pd.DataFrame(['All Days'], columns=['day']).assign(category='All Days')
        self.df_weekend = pd.DataFrame(['Weekend'], columns=['day']).assign(category='Weekend')
        self.df_weekdays = pd.DataFrame(['Weekdays'], columns=['day']).assign(category='Weekdays')
        self.df_days_only = pd.DataFrame({
            'day': self.days,
            'category': [f'{day} only' for day in self.days]
        })

        self.weekdays_df = pd.concat([
            self.df_all,
            self.df_weekend,
            self.df_weekdays,
            self.df_days_only
        ])

        for day in self.days:
            weekend_days = ['Saturday', 'Sunday']
            weekday_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

            self.weekdays_df[day] = (
                    (self.weekdays_df['day'] == day.capitalize()) |
                    ((self.weekdays_df['category'] == 'Weekend') &
                     (day.capitalize() in weekend_days)) |
                    ((self.weekdays_df['category'] == 'Weekdays') &
                     (day.capitalize() in weekday_days)) |
                    (self.weekdays_df['category'] == 'All Days')
            ).map({True: day.capitalize(), False: '-'})

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

    def update_progress(self, value):
        self.progress_Update.emit(copy.deepcopy(value))

    def create_table(self):
        if (self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_date or
                self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_weekday):
            self.strategy = ParallelTableCreationStrategy(self.app,
                self.create_settings_for_table_dto,
                self.gtfs_data_frame_dto
            )
        elif (self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.date or
              self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.weekday):
            self.strategy = SequentialTableCreationStrategy(self.app,
                self.create_settings_for_table_dto,
                self.gtfs_data_frame_dto
            )
        # Add other strategy selection logic as needed
        self.strategy.progress_Update.connect(self.update_progress)
        # Create context with selected strategy
        context = TableCreationContext(self.strategy)
        context.create_table()

        if self.create_settings_for_table_dto.individual_sorting:
            self.create_sorting.emit()


    def create_table_continue(self):
        self.strategy.datesWeekday_create_fahrplan_continue()

        # checks if date string
    def check_dates_input(self, dates):
        pattern1 = re.findall(r'^\d{8}(?:\d{8})*(?:,\d{8})*$', dates)
        if pattern1:
            return True
        else:
            return False
