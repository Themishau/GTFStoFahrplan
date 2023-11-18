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
from ..Base.ImportData import ImportData
from ..Base.SelectData import SelectData
from ..Base.PrepareData import PrepareData
from ..Base.CreatePlan import CreatePlan
from ..Base.ExportPlan import ExportPlan

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

class SchedulePlaner(Publisher, Subscriber):
    def __init__(self,
                 events,
                 name,
                 importData: ImportData,
                 selectData: SelectData,
                 prepareData: PrepareData,
                 createPlan: CreatePlan,
                 exportPlan: ExportPlan):

        super().__init__(events=events, name=name)

        self.exportPlan = exportPlan
        self.createPlan = createPlan
        self.prepareData = prepareData
        self.selectData = selectData
        self.importData = importData

        self.notify_functions = {
            'ImportGTFS': [self.async_task_load_GTFS_data, False],
            'ImportGTFS': [self.async_task_load_GTFS_data, False],

        }
