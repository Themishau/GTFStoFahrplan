# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal, QObject, QCoreApplication
import logging
from ..DTO.General_Transit_Feed_Specification import GtfsListDto, GtfsDataFrameDto
from ..DTO.CreateSettingsForTableDTO import CreateSettingsForTableDTO

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class ExportPlan(QObject):
    progress_update = pyqtSignal(int)
    create_settings_for_table_dto_changed = pyqtSignal()
    def __init__(self, app, progress: int):
        super().__init__()
        self.app = app
        self.reset_create = False
        self.create_settings_for_table_dto = CreateSettingsForTableDTO()
        self.create_plan_mode = None
        self.output_path = ""
        self.progress = progress

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.progress_update.emit(self.progress)

    def sub_worker_create_output_fahrplan_date(self):
        NotImplementedError

    @property
    def output_path(self):
        return self._output_path

    @output_path.setter
    def output_path(self, value):
        self._output_path = value
        self.create_settings_for_table_dto.output_path = value
        self.create_settings_for_table_dto_changed.emit()
        logging.debug(value)

    def export_plan(self):
        self.datesWeekday_create_output_fahrplan()

    def datesWeekday_create_output_fahrplan(self, dataframe):
        # save as csv
        self.dfheader_for_export_data.to_csv(
            self.output_path + str(self.route_short_namedf.route_short_name[0]) + 'dates_' + str(
                self.now) + 'pivot_table.csv', header=True,
            quotechar=' ', sep=';', mode='w', encoding='utf8')
        self.fahrplan_calendar_filter_days_pivot.to_csv(
            self.output_path + str(self.route_short_namedf.route_short_name[0]) + 'dates_' + str(
                self.now) + 'pivot_table.csv', header=True, quotechar=' ',
            index=True, sep=';', mode='a', encoding='utf8')