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
from ProgressBar import ProgressBar

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class ImportData(Publisher, Subscriber):
    def __init__(self, events, name, progress: ProgressBar):
        super().__init__(events=events, name=name)
        self.reset_import = False
        self.notify_functions = {
            'ImportGTFS': [self.async_task_load_GTFS_data, False]
        }

        """ property """
        self.input_path = ""
        self.pickle_save_path = ""
        self.pickle_export_checked = False
        self.time_format = 1

        """ df property """
        self.df_date_range_in_gtfs_data = pd.DataFrame()

        """ visual internal property """
        self.progress = progress.progress

        """ loaded raw_gtfs_data """
        self.raw_gtfs_data = []

        """ """
        self.stops_dict = {}
        self.stop_times_dict = {}
        self.trip_dict = {}
        self.calendar_week_dict = {}
        self.calendar_dates_dict = {}
        self.routes_fahrt_dict = {}
        self.agency_fahrt_dict = {}

        """ dataframe data """
        self.df_stops = pd.DataFrame()
        self.df_stop_times = pd.DataFrame()
        self.df_trips = pd.DataFrame()
        self.df_week = pd.DataFrame()
        self.df_dates = pd.DataFrame()
        self.df_routes = pd.DataFrame()
        self.df_selected_routes = pd.DataFrame()
        self.df_agency = pd.DataFrame()
        self.df_feed_info = pd.DataFrame()

    @property
    def reset_import(self):
        return self._reset_import

    @reset_import.setter
    def reset_import(self, value):
        self._reset_import = value

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
        return self._pickle_export_checked

    @pickle_export_checked.setter
    def pickle_export_checked(self, value):
        self._pickle_export_checked = value

    @property
    def df_date_range_in_gtfs_data(self):
        return self._df_date_range_in_GTFS_data

    @df_date_range_in_gtfs_data.setter
    def df_date_range_in_gtfs_data(self, value):
        self._df_date_range_in_GTFS_data = value

    """ checks """
    def _check_input_fields_based_on_settings(self):
        if self._check_paths() is False:
            self.notify_error_message(f"could not read data from path: {self.input_path} ")
            return False

    def _check_paths(self) -> bool:
        ...

    """ main import methods """
    def import_gtfs(self) -> bool:

        if self.read_gtfs_data() is False:
            self.reset_data_cause_of_error()
            return False

        if self.pkl_loaded is False:
            self.read_gtfs_data_from_path()
            self.create_dfs()
            self.clean_dicts()
            return True
        else:
            logging.debug("Pickle Data Detected. Loading Pickle Data")
            self.clean_dicts()
            return True

    """ methods """

    """
    loads dicts and creates dicts.
    It also set indices, if possible -> to speed up search
    """
    def create_dfs(self):

        self.df_routes = pd.DataFrame.from_dict(self.routes_fahrt_dict)
        self.df_trips = pd.DataFrame.from_dict(self.trip_dict).set_index('trip_id')

        """ lets try to convert every column to speed computing """
        try:
            self.dfTrips['trip_id'] = self.dfTrips['trip_id'].astype('int8')
            self.dfTrips['direction_id'] = self.dfTrips['direction_id'].astype('int8')
            self.dfTrips['shape_id'] = self.dfTrips['shape_id'].astype('int8')
            self.dfTrips['wheelchair_accessible'] = self.dfTrips['wheelchair_accessible'].astype('int8')
            self.dfTrips['bikes_allowed'] = self.dfTrips['bikes_allowed'].astype('int8')

        except KeyError:
            logging.debug("can not convert dfTrips")

        # DataFrame with every stop (time)
        self.dfStopTimes = pd.DataFrame.from_dict(self.stopTimesdict).set_index('stop_id')

        try:
            self.dfStopTimes['stop_sequence'] = self.dfStopTimes['stop_sequence'].astype('int32')
            self.dfStopTimes['stop_id'] = self.dfStopTimes['stop_id'].astype('int32')
            self.dfStopTimes['trip_id'] = self.dfStopTimes['trip_id'].astype('string')
        except KeyError:
            logging.debug("can not convert dfStopTimes")
        except OverflowError:
            logging.debug("can not convert dfStopTimes")

        # DataFrame with every stop
        self.dfStops = pd.DataFrame.from_dict(self.stopsdict).set_index('stop_id')
        try:
            self.dfStops['stop_id'] = self.dfStops['stop_id'].astype('int32')
        except KeyError:
            logging.debug("can not convert dfStops: stop_id into int ")

        self.dfWeek = pd.DataFrame.from_dict(self.calendarWeekdict).set_index('service_id')
        self.dfWeek['start_date'] = self.dfWeek['start_date'].astype('string')
        self.dfWeek['end_date'] = self.dfWeek['end_date'].astype('string')
        self.dfDates = pd.DataFrame.from_dict(self.calendarDatesdict).set_index('service_id')
        self.dfDates['exception_type'] = self.dfDates['exception_type'].astype('int32')
        self.dfDates['date'] = pd.to_datetime(self.dfDates['date'], format='%Y%m%d')
        self.dfagency = pd.DataFrame.from_dict(self.agencyFahrtdict)

        if self.feed_infodict:
            self.dffeed_info = pd.DataFrame.from_dict(self.feed_infodict)

        return True

    def analyze_daterange_in_GTFS_data(self):
        if self.df_week is not None:
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

    """ reset methods """

    def clean_dicts(self) -> bool:
        self.stops_dict = {}
        self.stop_times_dict = {}
        self.trip_dict = {}
        self.calendar_week_dict = {}
        self.calendar_dates_dict = {}
        self.routes_fahrt_dict = {}
        self.agency_fahrt_dict = {}
        return True



