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

        self.create_plan_direction_two = None
        self.create_plan_direction_one = None
        self.export_plan = None
        self.create_plan_direction_one = None
        self.create_plan_direction_two = None
        self.prepare_data = None
        self.select_data = None
        self.import_Data = None

        self.notify_functions = {
            'ImportGTFS': [self.async_task_load_GTFS_data, False],
        }

    @property
    def export_plan(self):
        return self._exportPlan

    @export_plan.setter
    def export_plan(self, value):
        self._exportPlan = value

    @property
    def create_plan_direction_one(self):
        return self._createPlan_Direction_one

    @create_plan_direction_one.setter
    def create_plan_direction_one(self, value):
        self._createPlan_Direction_one = value

    @property
    def create_plan_direction_two(self):
        return self._createPlan_Direction_two

    @create_plan_direction_two.setter
    def create_plan_direction_two(self, value):
        self._createPlan_Direction_two = value

    @property
    def prepare_data(self):
        return self._prepare_data

    @prepare_data.setter
    def prepare_data(self, value):
        self._prepare_data = value

    @property
    def select_data(self):
        return self._select_data

    @select_data.setter
    def _select_data(self, value):
        self._select_data = value

    @property
    def import_Data(self):
        return self._import_Data

    @import_Data.setter
    def import_Data(self, value):
        self._import_Data = value
