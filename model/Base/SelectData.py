# -*- coding: utf-8 -*-
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
from enum import Enum, auto
from model.Base.ProgressBar import ProgressBar
from model.Base.ImportData import ImportData

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class SelectData(Publisher, Subscriber):
    def __init__(self, events, name, progress: ProgressBar, imported_data: ImportData):
        super().__init__(events=events, name=name)
        self.imported_data = imported_data

        self.reset_select_data = False
        self.create_plan_mode = None
        self.progress = progress

        self.notify_functions = {
            'fill_agency_list': [self.get_routes_of_agency, False],
        }

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value


    def get_routes_of_agency(self) -> None:
        if self.selectedAgency is not None:
            self.select_gtfs_routes_from_agency()