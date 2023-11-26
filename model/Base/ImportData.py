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

        self.df_gtfs_data = []


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
        os.path.isfile()
        os.path.exists()

    """ main import methods """
    def import_gtfs(self):
        imported_data = self.read_gtfs_data()
        if imported_data is None:
            self.reset_data_cause_of_error()
            return None

        if self.pkl_loaded is False:
            self.read_gtfs_data_from_path()
            return self.create_dfs()
        else:
            logging.debug("Pickle Data Detected. Loading Pickle Data")
            return

    """ methods """

    """
    loads dicts and creates dicts.
    It also set indices, if possible -> to speed up search
    """
    def create_dfs(self):

        if (self.raw_gtfs_data is None):
            return None

        df_routes = pd.DataFrame.from_dict(routes_fahrt_dict)
        df_trips = pd.DataFrame.from_dict(trip_dict).set_index('trip_id')

        """ lets try to convert every column to speed computing """
        try:
            df_trips['trip_id'] = df_trips['trip_id'].astype('int8')
            df_trips['direction_id'] = df_trips['direction_id'].astype('int8')
            df_trips['shape_id'] = df_trips['shape_id'].astype('int8')
            df_trips['wheelchair_accessible'] = df_trips['wheelchair_accessible'].astype('int8')
            df_trips['bikes_allowed'] = df_trips['bikes_allowed'].astype('int8')

        except KeyError:
            logging.debug("can not convert dfTrips")

        # DataFrame with every stop (time)
        df_stoptimes = pd.DataFrame.from_dict(stop_Timesdict).set_index('stop_id')

        try:
            df_stoptimes['stop_sequence'] = df_stoptimes['stop_sequence'].astype('int32')
            df_stoptimes['stop_id'] = df_stoptimes['stop_id'].astype('int32')
            df_stoptimes['trip_id'] = df_stoptimes['trip_id'].astype('string')
        except KeyError:
            logging.debug("can not convert df_stoptimes")
        except OverflowError:
            logging.debug("can not convert df_stoptimes")

        # DataFrame with every stop
        df_stops = pd.DataFrame.from_dict(stops_dict).set_index('stop_id')
        try:
            self.df_stops['stop_id'] = self.df_stops['stop_id'].astype('int32')
        except KeyError:
            logging.debug("can not convert df_Stops: stop_id into int ")

        df_week = pd.DataFrame.from_dict(calendar_week_dict).set_index('service_id')
        df_week['start_date'] = df_week['start_date'].astype('string')
        df_week['end_date'] = df_week['end_date'].astype('string')
        df_dates = pd.DataFrame.from_dict(calendar_dates_dict).set_index('service_id')
        df_dates['exception_type'] = df_dates['exception_type'].astype('int32')
        df_dates['date'] = pd.to_datetime(df_dates['date'], format='%Y%m%d')
        df_agency = pd.DataFrame.from_dict(agency_fahrt_dict)

        if feed_info_dict:
            df_feed_info = pd.DataFrame.from_dict(feed_info_dict)

        return True

    def analyze_daterange_in_GTFS_data(self, df_week):
        if df_week is not None:
            self.df_date_range_in_gtfs_data = df_week.groupby(['start_date', 'end_date']).size().reset_index()
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
        self.progress = 0
        """Todo: add the other values here """


    def read_gtfs_data(self):
        # try:
        with zipfile.ZipFile(self.input_path) as zf:
            logging.debug(zf.namelist())
            for file in zf.namelist():
                if file.endswith('pkl'):
                    self.pkl_loaded = True
                    break

            if self.pkl_loaded is True:
                with zf.open("Tmp/dfStops.pkl") as stops:
                    self.dfStops = pd.read_pickle(stops)
                with zf.open("Tmp/dfStopTimes.pkl") as stop_times:
                    self.dfStopTimes = pd.read_pickle(stop_times)
                with zf.open("Tmp/dfTrips.pkl") as trips:
                    self.dfTrips = pd.read_pickle(trips)
                with zf.open("Tmp/dfWeek.pkl") as calendar:
                    self.dfWeek = pd.read_pickle(calendar)
                with zf.open("Tmp/dfDates.pkl") as calendar_dates:
                    self.dfDates = pd.read_pickle(calendar_dates)
                with zf.open("Tmp/dfRoutes.pkl") as routes:
                    self.dfRoutes = pd.read_pickle(routes)
                with zf.open("Tmp/dfagency.pkl") as agency:
                    self.dfagency = pd.read_pickle(agency)

                try:
                    with zipfile.ZipFile(self.input_path) as zf:
                        with io.TextIOWrapper(zf.open("Tmp/dffeed_info.pkl")) as feed_info:
                            self.dffeed_info = pd.read_pickle(feed_info)
                except:
                    logging.debug('no feed info header')
                    feed_infoHeader = None

        # except:
        #     logging.debug('Error in Unzipping data ')
        #     return False

        if self.pkl_loaded is False:
            try:
                with zipfile.ZipFile(self.input_path) as zf:
                    with io.TextIOWrapper(zf.open("stops.txt"), encoding="utf-8") as stops:
                        stopsList = stops.readlines()[1:]
                    with io.TextIOWrapper(zf.open("stop_times.txt"), encoding="utf-8") as stop_times:
                        stopTimesList = stop_times.readlines()[1:]
                    with io.TextIOWrapper(zf.open("trips.txt"), encoding="utf-8") as trips:
                        tripsList = trips.readlines()[1:]
                    with io.TextIOWrapper(zf.open("calendar.txt"), encoding="utf-8") as calendar:
                        calendarList = calendar.readlines()[1:]
                    with io.TextIOWrapper(zf.open("calendar_dates.txt"), encoding="utf-8") as calendar_dates:
                        calendar_datesList = calendar_dates.readlines()[1:]
                    with io.TextIOWrapper(zf.open("routes.txt"), encoding="utf-8") as routes:
                        routesList = routes.readlines()[1:]
                    with io.TextIOWrapper(zf.open("agency.txt"), encoding="utf-8") as agency:
                        agencyList = agency.readlines()[1:]

            except:
                logging.debug('Error in Unzipping data ')
                return False

            try:
                with zipfile.ZipFile(self.input_path) as zf:
                    with io.TextIOWrapper(zf.open("stops.txt"), encoding="utf-8") as stops:
                        stopsHeader = stops.readlines()[0].rstrip()
                    with io.TextIOWrapper(zf.open("stop_times.txt"), encoding="utf-8") as stop_times:
                        stop_timesHeader = stop_times.readlines()[0].rstrip()
                    with io.TextIOWrapper(zf.open("trips.txt"), encoding="utf-8") as trips:
                        tripsHeader = trips.readlines()[0]
                    with io.TextIOWrapper(zf.open("calendar.txt"), encoding="utf-8") as calendar:
                        calendarHeader = calendar.readlines()[0].rstrip()
                    with io.TextIOWrapper(zf.open("calendar_dates.txt"), encoding="utf-8") as calendar_dates:
                        calendar_datesHeader = calendar_dates.readlines()[0].rstrip()
                    with io.TextIOWrapper(zf.open("routes.txt"), encoding="utf-8") as routes:
                        routesHeader = routes.readlines()[0].rstrip()
                    with io.TextIOWrapper(zf.open("agency.txt"), encoding="utf-8") as agency:
                        agencyHeader = agency.readlines()[0].rstrip()
            except:
                logging.debug('Error in Unzipping headers')
                return False

            try:
                with zipfile.ZipFile(self.input_path) as zf:
                    with io.TextIOWrapper(zf.open("feed_info.txt"), encoding="utf-8") as feed_info:
                        feed_infoHeader = feed_info.readlines()[0].rstrip()
            except:
                logging.debug('no feed info header')
                feed_infoHeader = None

            try:
                with zipfile.ZipFile(self.input_path) as zf:
                    with io.TextIOWrapper(zf.open("feed_info.txt"), encoding="utf-8") as feed_info:
                        feed_infoList = feed_info.readlines()[1:]
            except:
                logging.debug('no feed info data')
                feed_infoList = None

            self.printAllHeaders(stopsHeader, stop_timesHeader, tripsHeader, calendarHeader, calendar_datesHeader,
                                 routesHeader, agencyHeader, feed_infoHeader)
            self.raw_gtfs_data = [[stopsHeader, stopsList], [stop_timesHeader, stopTimesList], [tripsHeader, tripsList],
                                  [calendarHeader, calendarList], [calendar_datesHeader, calendar_datesList],
                                  [routesHeader, routesList], [agencyHeader, agencyList],
                                  [feed_infoHeader, feed_infoList]]
        return True

    def printAllHeaders(self, stopsHeader, stop_timesHeader, tripsHeader, calendarHeader, calendar_datesHeader,
                        routesHeader, agencyHeader, feed_infoHeader):
        logging.debug('stopsHeader          = {} \n'
                      'stop_timesHeader     = {} \n'
                      'tripsHeader          = {} \n'
                      'calendarHeader       = {} \n'
                      'calendar_datesHeader = {} \n'
                      'routesHeader         = {} \n'
                      'agencyHeader         = {} \n'
                      'feed_infoHeader      = {}'.format(stopsHeader, stop_timesHeader, tripsHeader, calendarHeader,
                                                         calendar_datesHeader, routesHeader, agencyHeader,
                                                         feed_infoHeader))

    def getDateRange(self):
        logging.debug('len stop_sequences {}'.format(self.dffeed_info))
        if not self.dffeed_info.empty:
            self.date_range = str(self.dffeed_info.iloc[0].feed_start_date) + '-' + str(
                self.dffeed_info.iloc[0].feed_end_date)
        else:
            self.date_range = self.analyzeDateRangeInGTFSData()

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



