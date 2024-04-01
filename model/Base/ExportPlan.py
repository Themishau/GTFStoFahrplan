# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, QCoreApplication
from Event.ViewEvents import ProgressUpdateEvent, ShowErrorMessageEvent
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class ExportPlan(QObject):
    def __init__(self, app, progress: int):
        super().__init__()
        self.app = app
        self.reset_create = False
        self.create_plan_mode = None
        self.output_path = ""
        self.notify_functions = {
            'create_table': [self.sub_worker_create_output_fahrplan_date, False]
        }
        self.progress = progress

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        event = ProgressUpdateEvent(self._progress)
        QCoreApplication.postEvent(self.app, event)

    def sub_worker_create_output_fahrplan_date(self):
        NotImplementedError

    @property
    def output_path(self):
        return self._output_path

    @output_path.setter
    def output_path(self, value):
        self._output_path = value
        logging.debug(value)