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
from model.Base.ProgressBar import ProgressBar

from threading import Thread
import concurrent.futures

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class ImportData(Publisher, Subscriber):
    def __init__(self, events, name, progress: int):
        super().__init__(events=events, name=name)
        self._pkl_loaded = False
        self.reset_import = False
        """ property """
        self.input_path = ""
        self.pickle_save_path = ""
        self.pickle_export_checked = False
        self.time_format = 1

        """ df property """
        self.df_date_range_in_gtfs_data = pd.DataFrame()

        """ visual internal property """
        self.progress = progress

        self.notify_functions = {
            'ImportGTFS': [self.import_gtfs, False]
        }

    """ subscriber methods """

    def notify_subscriber(self, event, message):
        logging.debug(f'class: ImportData, event: {event}, message {message}')
        notify_function, parameters = self.notify_functions.get(event, self.notify_not_function)
        if not parameters:
            notify_function()
        else:
            notify_function(message)

    def notify_not_function(self, event):
        logging.debug('event not found in class gui: {}'.format(event))

    def notify_error_message(self, message):
        self.notify_subscriber("error_in_import_class", message)
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
        self.dispatch("update_progress_bar", f"{value}")

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

    def _check_paths(self):
        os.path.isfile()
        os.path.exists()

    """ main import methods """

    def pre_checks(self):
        return self.input_path is not None

    def import_gtfs(self):
        self.progress = 0
        if not self.pre_checks():
            self.progress = 20
            self.reset_data_cause_of_error()
            return None
        imported_data = self.read_gtfs_data()

        if imported_data is None:
            self.reset_data_cause_of_error()
            return None
        self.progress = 100
        return imported_data

    """ methods """

    def read_gtfs_data(self):

        """
        reads data from self.input_path. Data needs to be formatted as gtfs data
        :return: dict of raw_gtfs_data and creates a pandas dataframe
        """
        with zipfile.ZipFile(self.input_path) as zf:
            logging.debug(zf.namelist())
            for file in zf.namelist():
                if file.endswith('pkl'):
                    self._pkl_loaded = True
                    break

            if self._pkl_loaded is True:
                logging.debug('pickle data detected')
                df_gtfs_data = {}

                with zf.open("Tmp/dfStops.pkl") as stops:
                    df_gtfs_data["dfStops"] = pd.read_pickle(stops)
                with zf.open("Tmp/dfStopTimes.pkl") as stop_times:
                    df_gtfs_data["dfStopTimes"] = pd.read_pickle(stop_times)
                with zf.open("Tmp/dfTrips.pkl") as trips:
                    df_gtfs_data["dfTrips"] = pd.read_pickle(trips)
                with zf.open("Tmp/dfWeek.pkl") as calendar:
                    df_gtfs_data["dfWeek"] = pd.read_pickle(calendar)
                with zf.open("Tmp/dfDates.pkl") as calendar_dates:
                    df_gtfs_data["dfDates"] = pd.read_pickle(calendar_dates)
                with zf.open("Tmp/dfRoutes.pkl") as routes:
                    df_gtfs_data["dfRoutes"] = pd.read_pickle(routes)
                with zf.open("Tmp/dfagency.pkl") as agency:
                    df_gtfs_data["dfagency"] = pd.read_pickle(agency)

                self.progress = 80
                try:
                    with zipfile.ZipFile(self.input_path) as zf:
                        with io.TextIOWrapper(zf.open("Tmp/dffeed_info.pkl")) as feed_info:
                            df_gtfs_data["dffeed_info"] = pd.read_pickle(feed_info)
                except:
                    logging.debug('no feed info header')
                return df_gtfs_data

        if self._pkl_loaded is False:
            raw_data = {}
            self.progress = 30
            try:
                with zipfile.ZipFile(self.input_path) as zf:
                    with io.TextIOWrapper(zf.open("stops.txt"), encoding="utf-8") as stops:
                        raw_data["stopsList"] = [stops.readlines()[0].rstrip()]
                    with io.TextIOWrapper(zf.open("stop_times.txt"), encoding="utf-8") as stop_times:
                        raw_data["stopTimesList"] = [stop_times.readlines()[0].rstrip()]
                    with io.TextIOWrapper(zf.open("trips.txt"), encoding="utf-8") as trips:
                        raw_data["tripsList"] = [trips.readlines()[0].rstrip()]
                    with io.TextIOWrapper(zf.open("calendar.txt"), encoding="utf-8") as calendar:
                        raw_data["calendarList"] = [calendar.readlines()[0].rstrip()]
                    with io.TextIOWrapper(zf.open("calendar_dates.txt"), encoding="utf-8") as calendar_dates:
                        raw_data["calendar_datesList"] = [calendar_dates.readlines()[0].rstrip()]
                    with io.TextIOWrapper(zf.open("routes.txt"), encoding="utf-8") as routes:
                        raw_data["routesList"] = [routes.readlines()[0].rstrip()]
                    with io.TextIOWrapper(zf.open("agency.txt"), encoding="utf-8") as agency:
                        raw_data["agencyList"] = [agency.readlines()[0].rstrip()]
            except:
                logging.debug('Error in Unzipping headers')
                return None
            self.progress = 40
            try:
                with zipfile.ZipFile(self.input_path) as zf:
                    with io.TextIOWrapper(zf.open("stops.txt"), encoding="utf-8") as stops:
                        raw_data["stopsList"] += stops.readlines()[1:]
                    with io.TextIOWrapper(zf.open("stop_times.txt"), encoding="utf-8") as stop_times:
                        raw_data["stopTimesList"] += stop_times.readlines()[1:]
                    with io.TextIOWrapper(zf.open("trips.txt"), encoding="utf-8") as trips:
                        raw_data["tripsList"] += trips.readlines()[1:]
                    with io.TextIOWrapper(zf.open("calendar.txt"), encoding="utf-8") as calendar:
                        raw_data["calendarList"] += calendar.readlines()[1:]
                    with io.TextIOWrapper(zf.open("calendar_dates.txt"), encoding="utf-8") as calendar_dates:
                        raw_data["calendar_datesList"] += calendar_dates.readlines()[1:]
                    with io.TextIOWrapper(zf.open("routes.txt"), encoding="utf-8") as routes:
                        raw_data["routesList"] += routes.readlines()[1:]
                    with io.TextIOWrapper(zf.open("agency.txt"), encoding="utf-8") as agency:
                        raw_data["agencyList"] += agency.readlines()[1:]

            except:
                logging.debug('Error in Unzipping data ')
                return None

            try:
                with zipfile.ZipFile(self.input_path) as zf:
                    with io.TextIOWrapper(zf.open("feed_info.txt"), encoding="utf-8") as feed_info:
                        raw_data["feed_infoHeader"] = [feed_info.readlines()[0].rstrip()]
            except:
                logging.debug('no feed info header')
                raw_data["feed_infoHeader"] = []

            try:
                with zipfile.ZipFile(self.input_path) as zf:
                    with io.TextIOWrapper(zf.open("feed_info.txt"), encoding="utf-8") as feed_info:
                        raw_data["feed_info"] += feed_info.readlines()[1:]
            except:
                logging.debug('no feed info data')
                raw_data["feed_infoHeader"] = []

            logging.debug(f"raw_data keys: {raw_data.keys()}")

            return self.create_dfs(raw_data)

    def print_all_headers(self, stopsHeader, stop_timesHeader, tripsHeader, calendarHeader, calendar_datesHeader,
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

    def create_dfs(self, raw_data):

        """
        loads dicts and creates dicts.
        It also set indices, if possible -> to speed up search

        :param raw_data:
        dictonary with these keys
            stopsList
            stopTimesList
            tripsList
            calendarList
            calendar_datesList
            routesList
            agencyList
            feed_info (optional)
        :return: dict (df)
        """
        self.progress = 50
        if raw_data is None:
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            processes = [executor.submit(self.get_gtfs_routes, raw_data),
                         executor.submit(self.get_gtfs_trips, raw_data),
                         executor.submit(self.get_gtfs_stop_times, raw_data),
                         executor.submit(self.get_gtfs_stops, raw_data),
                         executor.submit(self.get_gtfs_week, raw_data),
                         executor.submit(self.get_gtfs_dates, raw_data),
                         executor.submit(self.get_gtfs_agency, raw_data)]
            if raw_data.get('feed_info') is not None:
                processes.append(executor.submit(self.get_gtfs_feed_info, raw_data))

            results = concurrent.futures.as_completed(processes)
            raw_dict_data = {}
            for result in results:
                temp_result = result.result()
                raw_dict_data[temp_result[0]] = temp_result[1]
        logging.debug(f"raw_dict_data creation: {raw_dict_data.keys()}")
        self.progress = 60
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            processes = [executor.submit(self.create_df_routes, raw_dict_data),
                         executor.submit(self.create_df_trips, raw_dict_data),
                         executor.submit(self.create_df_stop_times, raw_dict_data),
                         executor.submit(self.create_df_stops, raw_dict_data),
                         executor.submit(self.create_df_week, raw_dict_data),
                         executor.submit(self.create_df_dates, raw_dict_data),
                         executor.submit(self.create_df_agency, raw_dict_data)]
            if raw_dict_data.get('feed_info') is not None:
                processes.append(executor.submit(self.create_df_feed, raw_dict_data))

            results = concurrent.futures.as_completed(processes)
            df_collection = {}
            for result in results:
                temp_result = result.result()
                df_collection[temp_result.name] = temp_result
        self.progress = 90
        logging.debug(f"df_collection creation: {df_collection.keys()}")
        return df_collection

    def get_gtfs_trips(self, raw_data):
        tripdict = {
        }

        headers = raw_data["tripsList"][0].replace('"', "").split(",")
        itripDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            tripdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data["tripsList"].remove(raw_data["tripsList"][0])

        for data in raw_data["tripsList"]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            tripDate = data.split(",")
            for idx in range(itripDate):
                tripdict[header_names[idx]].append(tripDate[idx])

        return "Trips", tripdict

    def get_gtfs_stops(self, raw_data):

        stopsdict = {
        }
        headers = raw_data["stopsList"][0].replace('"', "").split(",")
        istopDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            stopsdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data["stopsList"].remove(raw_data["stopsList"][0])

        for haltestellen in raw_data["stopsList"]:
            haltestellen = haltestellen.replace(", ", " ")
            haltestellen = haltestellen.replace('"', "")
            haltestellen = haltestellen.replace('\n', "")
            stopData = haltestellen.split(",")

            for idx in range(istopDate):
                stopsdict[header_names[idx]].append(stopData[idx])

        return "Stops", stopsdict

    def get_gtfs_stop_times(self, raw_data):
        stopTimesdict = {
        }

        headers = raw_data["stopTimesList"][0].replace('"', "").split(",")
        istopTimeData = len(headers)
        header_names = []
        for haltestellen_header in headers:
            stopTimesdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data["stopTimesList"].remove(raw_data["stopTimesList"][0])

        for data in raw_data["stopTimesList"]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            stopTimeData = data.split(",")

            for idx in range(istopTimeData):
                stopTimesdict[header_names[idx]].append(stopTimeData[idx])

        return "Stoptimes", stopTimesdict

    def get_gtfs_week(self, raw_data):
        calendarWeekdict = {
        }

        headers = raw_data["calendarList"][0].replace('"', "").split(",")
        icalendarDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            calendarWeekdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data["calendarList"].remove(raw_data["calendarList"][0])

        for data in raw_data["calendarList"]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            calendarDate = data.split(",")

            for idx in range(icalendarDate):
                calendarWeekdict[header_names[idx]].append(calendarDate[idx])

        return "Calendarweeks", calendarWeekdict

    def get_gtfs_dates(self, raw_data):
        calendarDatesdict = {
        }

        headers = raw_data["calendar_datesList"][0].replace('"', "").split(",")
        icalendarDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            calendarDatesdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data["calendar_datesList"].remove(raw_data["calendar_datesList"][0])

        for data in raw_data["calendar_datesList"]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            calendarDatesDate = data.split(",")
            for idx in range(icalendarDate):
                calendarDatesdict[header_names[idx]].append(calendarDatesDate[idx])

        return "Calendardates", calendarDatesdict

    def get_gtfs_routes(self, raw_data):
        routesFahrtdict = {
        }

        headers = raw_data["routesList"][0].replace('"', "").split(",")
        iroutesFahrt = len(headers)
        header_names = []
        for haltestellen_header in headers:
            routesFahrtdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data["routesList"].remove(raw_data["routesList"][0])

        for data in raw_data["routesList"]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            routesFahrtData = data.split(",")
            for idx in range(iroutesFahrt):
                routesFahrtdict[header_names[idx]].append(routesFahrtData[idx])

        return "Routes", routesFahrtdict

    def get_gtfs_feed_info(self, raw_data):
        feed_infodict = {
        }

        headers = raw_data["feed_infoHeader"][0].replace('"', "").split(",")
        ifeed_infodict = len(headers)
        header_names = []
        for haltestellen_header in headers:
            feed_infodict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data["feed_infoHeader"].remove(raw_data["feed_infoHeader"][0])

        for data in raw_data["feed_infoHeader"]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            feed_infodictData = data.split(",")
            for idx in range(ifeed_infodict):
                feed_infodict[header_names[idx]].append(feed_infodictData[idx])

        return "Feedinfos", feed_infodict

    def get_gtfs_agency(self, raw_data):

        agencyFahrtdict = {
        }

        headers = raw_data["agencyList"][0].replace('"', "").split(",")
        iagencyData = len(headers)
        header_names = []
        for haltestellen_header in headers:
            agencyFahrtdict[haltestellen_header] = []
            header_names.append(haltestellen_header)
        raw_data["agencyList"].remove(raw_data["agencyList"][0])

        for data in raw_data["agencyList"]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            agencyData = data.split(",")
            for idx in range(iagencyData):
                agencyFahrtdict[header_names[idx]].append(agencyData[idx])

        return "Agencies", agencyFahrtdict

    # region creation dataframes

    def create_df_routes(self, raw_data):
        logging.debug("convert to df: create_df_routes")
        df_routes = pd.DataFrame.from_dict(raw_data["Routes"])
        df_routes.name = "Routes"
        return df_routes

    def create_df_trips(self, raw_data):
        logging.debug("convert to df: create_df_trips")
        df_trips = pd.DataFrame.from_dict(raw_data["Trips"]).set_index('trip_id')
        df_trips.name = "Trips"
        """ lets try to convert every column to speed computing """
        try:
            df_trips['trip_id'] = df_trips['trip_id'].astype('int8')
            df_trips['direction_id'] = df_trips['direction_id'].astype('int8')
            df_trips['shape_id'] = df_trips['shape_id'].astype('int8')
            df_trips['wheelchair_accessible'] = df_trips['wheelchair_accessible'].astype('int8')
            df_trips['bikes_allowed'] = df_trips['bikes_allowed'].astype('int8')

        except KeyError:
            logging.debug("can not convert dfTrips")
        logging.debug("convert to df: create_df_trips finished")
        return df_trips

    def create_df_stop_times(self, raw_data):
        logging.debug("convert to df: create_df_stop_times")
        # DataFrame with every stop (time)
        df_stoptimes = pd.DataFrame.from_dict(raw_data["Stoptimes"]).set_index('stop_id')
        df_stoptimes.name = "Stoptimes"
        try:
            df_stoptimes['stop_sequence'] = df_stoptimes['stop_sequence'].astype('int32')
            df_stoptimes['stop_id'] = df_stoptimes['stop_id'].astype('int32')
            df_stoptimes['trip_id'] = df_stoptimes['trip_id'].astype('string')
        except KeyError:
            logging.debug("can not convert df_stoptimes")
        except OverflowError:
            logging.debug("can not convert df_stoptimes")
        logging.debug("convert to df: create_df_stop_times finished")
        return df_stoptimes

    def create_df_stops(self, raw_data):
        logging.debug("convert to df: create_df_stops")
        # DataFrame with every stop
        df_stops = pd.DataFrame.from_dict(raw_data["Stops"]).set_index('stop_id')
        df_stops.name = "Stops"
        try:
            df_stops['stop_id'] = df_stops['stop_id'].astype('int32')
        except KeyError:
            logging.debug("can not convert df_Stops: stop_id into int ")
        logging.debug("convert to df: create_df_stops finished")
        return df_stops

    def create_df_week(self, raw_data):
        logging.debug("convert to df: create_df_week")
        df_week = pd.DataFrame.from_dict(raw_data["Calendarweeks"]).set_index('service_id')
        df_week.name = "Calendarweeks"
        try:
            df_week['start_date'] = df_week['start_date'].astype('string')
            df_week['end_date'] = df_week['end_date'].astype('string')
        except KeyError:
            logging.debug("can not convert df_week")
        logging.debug("convert to df: df_week finished")
        return df_week

    def create_df_dates(self, raw_data):
        logging.debug("convert to df: create_df_dates")

        df_dates = pd.DataFrame.from_dict(raw_data["Calendardates"]).set_index('service_id')
        df_dates.name = "Calendardates"
        try:
            df_dates['exception_type'] = df_dates['exception_type'].astype('int32')
            df_dates['date'] = pd.to_datetime(df_dates['date'], format='%Y%m%d')
        except KeyError:
            logging.debug("can not convert df_dateS")
            logging.debug("convert to df: create_df_dates finished")
        return df_dates

    def create_df_agency(self, raw_data):
        logging.debug("convert to df: create_df_agency")
        df_agencies = pd.DataFrame.from_dict(raw_data["Agencies"])
        df_agencies.name = "Agencies"
        return df_agencies

    def create_df_feed(self, raw_data):
        logging.debug("convert to df: create_df_feed")
        if raw_data["feed_info"]:
            df_feedinfo = pd.DataFrame.from_dict(raw_data["Feedinfos"])
            df_feedinfo.name = "Feedinfos"
            return df_feedinfo
        return None

    # region end

    def get_daterange_in_gtfs_data(self, df_week):
        if df_week is not None:
            self.df_date_range_in_gtfs_data = df_week.groupby(['start_date', 'end_date']).size().reset_index()
            return str(self.df_date_range_in_gtfs_data.iloc[0].start_date) + '-' + str(
                self.df_date_range_in_gtfs_data.iloc[0].end_date)

    def read_gtfs_data_from_path(self):
        ...

    def reset_data_cause_of_error(self):
        self.progress = 0
        """Todo: add the other values here """
