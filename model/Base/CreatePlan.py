# -*- coding: utf-8 -*-
import copy
import logging
import re

from PySide6.QtCore import Signal, QObject
import pandas as pd
from model.Enum.GTFSEnums import CreatePlanMode
from .Progress import ProgressSignal
from ..Dto.CreateSettingsForTableDto import CreateSettingsForTableDto
from ..Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto
from ..SchedulePlaner.CreationStrategy.ParallelTableCreationStrategy import ParallelTableCreationStrategy
from ..SchedulePlaner.CreationStrategy.SequentialTableCreationStrategy import SequentialTableCreationStrategy
from ..SchedulePlaner.CreationStrategy.TableCreationContext import TableCreationContext

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class CreatePlan(QObject):
    progress_Update = Signal(ProgressSignal)
    error_occured = Signal(str)
    data_selected = Signal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.gtfs_data_frame_dto = None
        self.create_settings_for_table_dto = CreateSettingsForTableDto()
        self.strategy = None

        """ visual internal property """
        self.progress = ProgressSignal()

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
        if not self.check_dates_input(self.create_settings_for_table_dto.date):
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

        if self.create_settings_for_table_dto.individual_sorting:
            self.data_selected.emit()

        self.strategy.progress_Update.connect(self.update_progress)
        context = TableCreationContext(self.strategy)
        context.create_table()

    def create_table_continue(self):
        self.strategy.create_table_continue()

        # checks if date string
    def check_dates_input(self, dates):
        pattern1 = re.findall(r'^\d{8}(?:\d{8})*(?:,\d{8})*$', dates)
        if pattern1:
            return True
        else:
            return False
