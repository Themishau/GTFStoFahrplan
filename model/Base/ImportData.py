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

from PyQt5.QtCore import QAbstractTableModel

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class ImportData(Publisher, Subscriber):
    def __init__(self, events, name):
        super().__init__(events=events, name=name)
        self.notify_functions = {
            'ImportGTFS': [self.async_task_load_GTFS_data, False]
        }

        """ property """
        self.input_path = ""
        self.pickle_save_path = ""
        self.pickle_export_checked = False
        self.time_format = 1

        """ visual internal property """
        # TODO: create a own class for progress
        self.progress = 0

        """ loaded raw_gtfs_data """
        self.raw_gtfs_data = []

        """ dataframe data """
        self.df_Stops = pd.DataFrame()
        self.df_Stop_times = pd.DataFrame()
        self.df_Trips = pd.DataFrame()
        self.df_Week = pd.DataFrame()
        self.df_Dates = pd.DataFrame()
        self.df_Routes = pd.DataFrame()
        self.df_Selected_routes = pd.DataFrame()
        self.df_agency = pd.DataFrame()
        self.df_feed_info = pd.DataFrame()

        """ df property """
        self.df_date_range_in_gtfs_data = pd.DataFrame()

    @property
    def input_path(self):
        return self._input_path

    @input_path.setter
    def input_path(self, value):
        self._input_path = value

    @property
    def pickle_save_path(self):
        return self._pickleSavePath

    @pickle_save_path.setter
    def pickle_save_path(self, value):
        if value is not None:
            self._pickleSavePath = value
        else:
            self.dispatch("message",
                          "Folder not found. Please check!")

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value

    @property
    def pickle_export_checked(self):
        return self._progress

    @pickle_export_checked.setter
    def pickle_export_checked(self, value):
        self._pickleExport_checked = value

    @property
    def time_format(self):
        return self._time_format

    @time_format.setter
    def time_format(self, value):
        self._time_format = value

    @property
    def df_date_range_in_gtfs_data(self):
        return self._df_date_range_in_GTFS_data

    @df_date_range_in_gtfs_data.setter
    def df_date_range_in_gtfs_data(self, value):
        self._df_date_range_in_GTFS_data = value

    """ checks """
    def _check_input_fields_based_on_settings(self):
        ...

    def _check_paths(self):
        ...

    """ main import methods """
    def import_gtfs(self) -> bool:

        if self.read_gtfs_data() is False:
            self.notify_error_message(f"could not read data from path: {self.input_path} ")
            self.reset_data_cause_of_error()
            return False

        if self.pkl_loaded is False:
            logging.debug("read_gtfs_data")
            self.read_gtfs_data_from_path()
            logging.debug("read_gtfs_data_from_path")
            self.create_dfs()
            logging.debug("create_dfs ")
            self.clean_dicts()
            return True
        else:
            logging.debug("Pickle Data Detected. Loading Pickle Data")
            self.clean_dicts()
            return True

    """ methods """
    def analyze_daterange_in_GTFS_data(self):
        if self.df_Week is not None:
            self.df_date_range_in_gtfs_data = self.dfWeek.groupby(['start_date', 'end_date']).size().reset_index()
            return str(self.df_date_range_in_gtfs_data.iloc[0].start_date) + '-' + str(
                self.df_date_range_in_gtfs_data.iloc[0].end_date)

    def read_gtfs_data_from_path(self):
        ...

    """ subscriber methods """
    def notify_subscriber(self, event, message):
        logging.debug(f'event: {event}, message {message}')
        notify_function, parameters = self.notify_functions.get(event, self.notify_not_function)
        if not parameters:
            notify_function()
        else:
            notify_function(message)

    def notify_not_function(self, event):
        logging.debug('event not found in class gui: {}'.format(event))

    def notify_error_message(self, message):
        self.notify_subscriber("error_in_import_class", message)

    def read_gtfs_data(self):
        pass

    def reset_data_cause_of_error(self):
        pass





