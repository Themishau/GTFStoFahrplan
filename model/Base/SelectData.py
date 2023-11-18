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
from ProgressBar import ProgressBar

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class SelectData(Publisher, Subscriber):
    def __init__(self, events, name, progress: ProgressBar):
        super().__init__(events=events, name=name)
        self.reset_select_data = False
        self.create_plan_mode = None
        self.progress = progress

        self.notify_functions = {
            'create_table': [self.sub_worker_create_output_fahrplan_date, False]
        }

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value