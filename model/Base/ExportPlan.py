# -*- coding: utf-8 -*-
from datetime import datetime

from PyQt5.QtCore import pyqtSignal, QObject
import logging

from ..Dto import CreateTableDataframeDto
from ..Dto.CreateSettingsForTableDto import CreateSettingsForTableDTO

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class ExportPlan(QObject):
    progress_Update = pyqtSignal(int)
    create_settings_for_table_dto_changed = pyqtSignal()

    def __init__(self, app, progress: int):
        super().__init__()
        self.app = app
        self.reset_create = False
        self.create_settings_for_table_dto = CreateSettingsForTableDTO()
        self.create_plan_mode = None
        self.output_path = ""
        self.full_output_path = ""
        self.progress = progress

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.progress_Update.emit(self.progress)

    @property
    def output_path(self):
        return self._output_path

    @output_path.setter
    def output_path(self, value):
        self._output_path = value
        self.create_settings_for_table_dto.output_path = value
        self.create_settings_for_table_dto_changed.emit()
        logging.debug(value)

    def export_plan(self, exportSettings, createTableDto: CreateTableDataframeDto):
        self.datesWeekday_create_output_fahrplan(createTableDto)
        self.progress = 100

    def export_circle_plan(self, exportSettings, createTableDto: list[CreateTableDataframeDto]):
        self.datesWeekday_create_output_circleplan(createTableDto)
        self.progress = 100

    def datesWeekday_create_output_fahrplan(self, createTableDto: CreateTableDataframeDto):
        # save as csv
        now = datetime.now()
        now = now.strftime("%Y_%m_%d_%H_%M_%S")
        self.full_output_path = self.output_path + '/' + str(
            createTableDto.RouteShortName['route_short_name'][0]) + 'dates_' + str(now) + 'pivot_table.csv'
        createTableDto.Header.to_csv(self.full_output_path, header=True, quotechar=' ', sep=';', mode='w',
                                     encoding='utf8')
        createTableDto.FahrplanCalendarFilterDaysPivot.to_csv(self.full_output_path, header=True, quotechar=' ',
                                                              index=True, sep=';', mode='a', encoding='utf8')

    def datesWeekday_create_output_circleplan(self, CreateTableDataframeDto):
        # save as csv
        now = datetime.now()
        now = now.strftime("%Y_%m_%d_%H_%M_%S")
        self.full_output_path = self.output_path + '/' + str(
            CreateTableDataframeDto[0].create_settings_for_table_dto.route) + 'circle_plan_dates_' + str(now) + 'pivot_table.csv'
        CreateTableDataframeDto[0].create_dataframe.Header.to_csv(self.full_output_path, header=True, quotechar=' ', sep=';', mode='w',
                                     encoding='utf8')
        CreateTableDataframeDto[0].create_dataframe.FahrplanCalendarFilterDaysPivot.to_csv(self.full_output_path, header=True, quotechar=' ',
                                                              index=True, sep=';', mode='a', encoding='utf8')
        CreateTableDataframeDto[1].create_dataframe.Header.to_csv(self.full_output_path, header=True, quotechar=' ', sep=';', mode='a',
                                        encoding='utf8')
        CreateTableDataframeDto[1].create_dataframe.FahrplanCalendarFilterDaysPivot.to_csv(self.full_output_path, header=True, quotechar=' ',
                                                             index=True, sep=';', mode='a', encoding='utf8')
