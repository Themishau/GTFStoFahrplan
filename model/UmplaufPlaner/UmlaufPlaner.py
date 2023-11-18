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


class UmlaufPlaner(Publisher, Subscriber):
    def __init__(self, events, name):
        super().__init__(events=events, name=name)

        self.createPlan_Direction_two = None
        self.createPlan_Direction_one = None
        self.exportPlan = None

        self.notify_functions = {
            'ImportGTFS': [self.async_task_load_GTFS_data, False],
            'ImportGTFS': [self.async_task_load_GTFS_data, False],

        }

    @property
    def exportPlan(self):
        return self._exportPlan

    @exportPlan.setter
    def exportPlan(self, value):
        self._exportPlan = value

    @property
    def createPlan_Direction_one(self):
        return self._createPlan_Direction_one

    @createPlan_Direction_one.setter
    def createPlan_Direction_one(self, value):
        self.createPlan_Direction_one = value

    @property
    def createPlan_Direction_two(self):
        return self._createPlan_Direction_two

    @createPlan_Direction_two.setter
    def createPlan_Direction_two(self, value):
        self._createPlan_Direction_two = value


    @property
    def prepareData(self):
        return self.

    @prepareData.setter
    def prepareData(self):

        @property
        def selectData(self):
            return self.

    @selectData.setter
    def selectData(self):

    @property
    def importData(self):
        return self.

    @importData.setter
    def importData(self):
        return self.
