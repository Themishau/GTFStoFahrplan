# -*- coding: utf-8 -*-
from PySide6.QtCore import Signal
from PySide6.QtCore import QObject
import pandas as pd
import zipfile
import io
import logging
import os
from model.Enum.GTFSEnums import *
from ..Dto.GeneralTransitFeedSpecificationDto import GtfsDataFrameDto

import concurrent.futures

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class ImportData(QObject):
    progress_Update = Signal(int)
    error_occured = Signal(str)

    def __init__(self, app, progress: int):
        super().__init__()
        self.app = app
        self._pkl_loaded = False
        self._pickle_save_path = ""
        self.reset_import = False
        """ property """
        self.input_path = ""
        self.pickle_save_path_filename = ""
        self.pickle_export_checked = False
        self.time_format = 1

        """ df property """
        self.df_date_range_in_gtfs_data = pd.DataFrame()

        """ visual internal property """
        self.progress = progress
        self.current_process_string = ""

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
    def pickle_save_path_filename(self):
        return self._pickleSavePath

    @pickle_save_path_filename.setter
    def pickle_save_path_filename(self, value):
        if value is not None:
            self._pickleSavePath = value
            self._pickle_save_path = value.replace(value.split('/')[-1], '')
            logging.debug(value)
        else:
            self.error_occured("Folder not found. Please check!")

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.progress_Update.emit(self._progress)

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
            self.error_occured(f"could not read data from path: {self.input_path}")
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
        if imported_data.get(GtfsDfNames.Feedinfos) is not None:
            gtfsDataFrameDto = GtfsDataFrameDto(imported_data[GtfsDfNames.Routes], imported_data[GtfsDfNames.Trips], imported_data[GtfsDfNames.Stoptimes], imported_data[GtfsDfNames.Stops], imported_data[GtfsDfNames.Calendarweeks], imported_data[GtfsDfNames.Calendardates], imported_data[GtfsDfNames.Agencies], imported_data[GtfsDfNames.Feedinfos])
        else:
            gtfsDataFrameDto = GtfsDataFrameDto(imported_data[GtfsDfNames.Routes], imported_data[GtfsDfNames.Trips], imported_data[GtfsDfNames.Stoptimes], imported_data[GtfsDfNames.Stops], imported_data[GtfsDfNames.Calendarweeks], imported_data[GtfsDfNames.Calendardates], imported_data[GtfsDfNames.Agencies], None)

        if imported_data is None:
            self.reset_data_cause_of_error()
            return None

        if self.pickle_export_checked is True and self.pickle_save_path_filename is not None:
            self.save_pickle(imported_data)
        self.progress = 100
        return gtfsDataFrameDto

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
                    df_gtfs_data[GtfsDfNames.Stops] = pd.read_pickle(stops)
                with zf.open("Tmp/dfStopTimes.pkl") as stop_times:
                    df_gtfs_data[GtfsDfNames.Stoptimes] = pd.read_pickle(stop_times)
                with zf.open("Tmp/dfTrips.pkl") as trips:
                    df_gtfs_data[GtfsDfNames.Trips] = pd.read_pickle(trips)
                with zf.open("Tmp/dfWeek.pkl") as calendar:
                    df_gtfs_data[GtfsDfNames.Calendarweeks] = pd.read_pickle(calendar)
                with zf.open("Tmp/dfDates.pkl") as calendar_dates:
                    df_gtfs_data[GtfsDfNames.Calendardates] = pd.read_pickle(calendar_dates)
                with zf.open("Tmp/dfRoutes.pkl") as routes:
                    df_gtfs_data[GtfsDfNames.Routes] = pd.read_pickle(routes)
                with zf.open("Tmp/dfagency.pkl") as agency:
                    df_gtfs_data[GtfsDfNames.Agencies] = pd.read_pickle(agency)

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
                        raw_data[GtfsColumnNames.stopsList] = [stops.readlines()[0].rstrip()]
                    with io.TextIOWrapper(zf.open("stop_times.txt"), encoding="utf-8") as stop_times:
                        raw_data[GtfsColumnNames.stopTimesList] = [stop_times.readlines()[0].rstrip()]
                    with io.TextIOWrapper(zf.open("trips.txt"), encoding="utf-8") as trips:
                        raw_data[GtfsColumnNames.tripsList] = [trips.readlines()[0].rstrip()]
                    with io.TextIOWrapper(zf.open("calendar.txt"), encoding="utf-8") as calendar:
                        raw_data[GtfsColumnNames.calendarList] = [calendar.readlines()[0].rstrip()]
                    with io.TextIOWrapper(zf.open("calendar_dates.txt"), encoding="utf-8") as calendar_dates:
                        raw_data[GtfsColumnNames.calendar_datesList] = [calendar_dates.readlines()[0].rstrip()]
                    with io.TextIOWrapper(zf.open("routes.txt"), encoding="utf-8") as routes:
                        raw_data[GtfsColumnNames.routesList] = [routes.readlines()[0].rstrip()]
                    with io.TextIOWrapper(zf.open("agency.txt"), encoding="utf-8") as agency:
                        raw_data[GtfsColumnNames.agencyList] = [agency.readlines()[0].rstrip()]
            except:
                logging.debug('Error in Unzipping headers')
                return None

            self.progress = 40

            try:
                with zipfile.ZipFile(self.input_path) as zf:
                    with io.TextIOWrapper(zf.open("stops.txt"), encoding="utf-8") as stops:
                        raw_data[GtfsColumnNames.stopsList] += stops.readlines()[1:]
                    with io.TextIOWrapper(zf.open("stop_times.txt"), encoding="utf-8") as stop_times:
                        raw_data[GtfsColumnNames.stopTimesList] += stop_times.readlines()[1:]
                    with io.TextIOWrapper(zf.open("trips.txt"), encoding="utf-8") as trips:
                        raw_data[GtfsColumnNames.tripsList] += trips.readlines()[1:]
                    with io.TextIOWrapper(zf.open("calendar.txt"), encoding="utf-8") as calendar:
                        raw_data[GtfsColumnNames.calendarList] += calendar.readlines()[1:]
                    with io.TextIOWrapper(zf.open("calendar_dates.txt"), encoding="utf-8") as calendar_dates:
                        raw_data[GtfsColumnNames.calendar_datesList] += calendar_dates.readlines()[1:]
                    with io.TextIOWrapper(zf.open("routes.txt"), encoding="utf-8") as routes:
                        raw_data[GtfsColumnNames.routesList] += routes.readlines()[1:]
                    with io.TextIOWrapper(zf.open("agency.txt"), encoding="utf-8") as agency:
                        raw_data[GtfsColumnNames.agencyList] += agency.readlines()[1:]

            except:
                logging.debug('Error in Unzipping data ')
                return None

            try:
                with zipfile.ZipFile(self.input_path) as zf:
                    with io.TextIOWrapper(zf.open("feed_info.txt"), encoding="utf-8") as feed_info:
                        raw_data[GtfsColumnNames.feed_info] = [feed_info.readlines()[0].rstrip()]
            except:
                logging.debug('no feed info header')

            try:
                with zipfile.ZipFile(self.input_path) as zf:
                    with io.TextIOWrapper(zf.open("feed_info.txt"), encoding="utf-8") as feed_info:
                        raw_data[GtfsColumnNames.feed_info] += feed_info.readlines()[1:]
            except:
                logging.debug('no feed info data')

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
            if raw_data.get(GtfsColumnNames.feed_info) is not None:
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
            if raw_dict_data.get(GtfsColumnNames.feed_info) is not None:
                processes.append(executor.submit(self.create_df_feed, raw_dict_data))

            results = concurrent.futures.as_completed(processes)
            df_collection = {}
            for result in results:
                try:
                    temp_result = result.result()
                    df_collection[temp_result.name] = temp_result
                except Exception as e:
                    logging.debug(f"An error occurred for: {str(e)}:")
                    return None

        self.progress = 90

        logging.debug(f"df_collection creation: {df_collection.keys()}")
        return df_collection

    def get_gtfs_trips(self, raw_data):
        tripdict = {
        }

        headers = raw_data[GtfsColumnNames.tripsList][0].replace('"', "").split(",")
        itripDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            tripdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.tripsList].remove(raw_data[GtfsColumnNames.tripsList][0])

        for data in raw_data[GtfsColumnNames.tripsList]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            tripDate = data.split(",")
            for idx in range(itripDate):
                tripdict[header_names[idx]].append(tripDate[idx])

        return GtfsDfNames.Trips, tripdict

    def get_gtfs_stops(self, raw_data):

        stopsdict = {
        }
        headers = raw_data[GtfsColumnNames.stopsList][0].replace('"', "").split(",")
        istopDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            stopsdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.stopsList].remove(raw_data[GtfsColumnNames.stopsList][0])

        for haltestellen in raw_data[GtfsColumnNames.stopsList]:
            haltestellen = haltestellen.replace(", ", " ")
            haltestellen = haltestellen.replace('"', "")
            haltestellen = haltestellen.replace('\n', "")
            stopData = haltestellen.split(",")

            for idx in range(istopDate):
                stopsdict[header_names[idx]].append(stopData[idx])

        return GtfsDfNames.Stops, stopsdict

    def get_gtfs_stop_times(self, raw_data):
        stopTimesdict = {
        }

        headers = raw_data[GtfsColumnNames.stopTimesList][0].replace('"', "").split(",")
        istopTimeData = len(headers)
        header_names = []
        for haltestellen_header in headers:
            stopTimesdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.stopTimesList].remove(raw_data[GtfsColumnNames.stopTimesList][0])

        for data in raw_data[GtfsColumnNames.stopTimesList]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            stopTimeData = data.split(",")

            for idx in range(istopTimeData):
                stopTimesdict[header_names[idx]].append(stopTimeData[idx])

        return GtfsDfNames.Stoptimes, stopTimesdict

    def get_gtfs_week(self, raw_data):
        calendarWeekdict = {
        }

        headers = raw_data[GtfsColumnNames.calendarList][0].replace('"', "").split(",")
        icalendarDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            calendarWeekdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.calendarList].remove(raw_data[GtfsColumnNames.calendarList][0])

        for data in raw_data[GtfsColumnNames.calendarList]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            calendarDate = data.split(",")

            for idx in range(icalendarDate):
                calendarWeekdict[header_names[idx]].append(calendarDate[idx])

        return GtfsDfNames.Calendarweeks, calendarWeekdict

    def get_gtfs_dates(self, raw_data):
        calendarDatesdict = {
        }

        headers = raw_data[GtfsColumnNames.calendar_datesList][0].replace('"', "").split(",")
        icalendarDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            calendarDatesdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.calendar_datesList].remove(raw_data[GtfsColumnNames.calendar_datesList][0])

        for data in raw_data[GtfsColumnNames.calendar_datesList]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            calendarDatesDate = data.split(",")
            for idx in range(icalendarDate):
                calendarDatesdict[header_names[idx]].append(calendarDatesDate[idx])

        return GtfsDfNames.Calendardates, calendarDatesdict

    def get_gtfs_routes(self, raw_data):
        routesFahrtdict = {
        }

        headers = raw_data[GtfsColumnNames.routesList][0].replace('"', "").split(",")
        iroutesFahrt = len(headers)
        header_names = []
        for haltestellen_header in headers:
            routesFahrtdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.routesList].remove(raw_data[GtfsColumnNames.routesList][0])

        for data in raw_data[GtfsColumnNames.routesList]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            routesFahrtData = data.split(",")
            for idx in range(iroutesFahrt):
                routesFahrtdict[header_names[idx]].append(routesFahrtData[idx])

        return GtfsDfNames.Routes, routesFahrtdict

    def get_gtfs_feed_info(self, raw_data):
        feed_infodict = {
        }

        headers = raw_data[GtfsColumnNames.feed_info][0].replace('"', "").split(",")
        ifeed_infodict = len(headers)
        header_names = []
        for haltestellen_header in headers:
            feed_infodict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        raw_data[GtfsColumnNames.feed_info].remove(raw_data[GtfsColumnNames.feed_info][0])

        for data in raw_data[GtfsColumnNames.feed_info]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            feed_infodictData = data.split(",")
            for idx in range(ifeed_infodict):
                feed_infodict[header_names[idx]].append(feed_infodictData[idx])

        return GtfsDfNames.Feedinfos, feed_infodict

    def get_gtfs_agency(self, raw_data):

        agencyFahrtdict = {
        }

        headers = raw_data[GtfsColumnNames.agencyList][0].replace('"', "").split(",")
        iagencyData = len(headers)
        header_names = []
        for haltestellen_header in headers:
            agencyFahrtdict[haltestellen_header] = []
            header_names.append(haltestellen_header)
        raw_data[GtfsColumnNames.agencyList].remove(raw_data[GtfsColumnNames.agencyList][0])

        for data in raw_data[GtfsColumnNames.agencyList]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            agencyData = data.split(",")
            for idx in range(iagencyData):
                agencyFahrtdict[header_names[idx]].append(agencyData[idx])

        return GtfsDfNames.Agencies, agencyFahrtdict

    # region creation dataframes

    def create_df_routes(self, raw_data):
        logging.debug("convert to df: create_df_routes")
        df_routes = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Routes])
        df_routes = self.drop_columns_by_enum(df_routes, DfRouteColumnEnum)
        df_routes.name = GtfsDfNames.Routes
        try:
            df_routes['route_long_name'] = df_routes['route_long_name'].astype('string')
            df_routes['agency_id'] = df_routes['agency_id'].astype('string')
            df_routes['route_type'] = df_routes['route_type'].astype('string')
            df_routes['route_id'] = df_routes['route_id'].astype('string')
        except KeyError:
            logging.debug("can not convert df_routes: stop_id into int ")
        except ValueError:
            logging.debug("can not convert df_routes")
        except AttributeError:
            logging.debug("can not convert df_routes Attribute")
        logging.debug("convert to df: df_routes finished")

        return df_routes

    def create_df_trips(self, raw_data):
        logging.debug("convert to df: create_df_trips")
        df_trips = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Trips])
        df_trips = self.drop_columns_by_enum(df_trips, DfTripColumnEnum)
        df_trips.name = GtfsDfNames.Trips
        """ lets try to convert every column to speed computing """
        try:
            df_trips['trip_id'] = df_trips['trip_id'].astype('string')
        except KeyError:
            logging.debug("can not convert dfTrips")
        except ValueError:
            logging.debug("can not convert dfTrips")
        try:
            df_trips['service_id'] = df_trips['service_id'].astype('string')
        except KeyError:
            logging.debug("can not convert service_id")
        except ValueError:
            logging.debug("can not convert service_id")
        try:
            df_trips['route_id'] = df_trips['route_id'].astype('string')
        except KeyError:
            logging.debug("can not convert route_id")
        except ValueError:
            logging.debug("can not convert route_id")
        try:
            df_trips['direction_id'] = pd.to_numeric(df_trips['direction_id'], errors='coerce').fillna(0).astype(int)
        except KeyError:
            logging.debug("can not convert direction_id in  dfTrips")
        except ValueError:
            logging.debug("can not convert direction_id in  dfTrips")

        logging.debug("convert to df: create_df_trips finished")

        return df_trips

    def create_df_stop_times(self, raw_data):
        logging.debug("convert to df: create_df_stop_times")
        # DataFrame with every stop (time)
        df_stoptimes = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Stoptimes])
        df_stoptimes = self.drop_columns_by_enum(df_stoptimes, DfStopTimesColumnEnum)
        df_stoptimes.name = GtfsDfNames.Stoptimes
        try:
            df_stoptimes['stop_sequence'] = df_stoptimes['stop_sequence'].astype('int32')
            df_stoptimes['arrival_time'] = df_stoptimes['arrival_time'].astype('string')
            df_stoptimes['departure_time'] = df_stoptimes['departure_time'].astype('string')
            df_stoptimes['stop_id'] = df_stoptimes['stop_id'].astype('string')
            df_stoptimes['trip_id'] = df_stoptimes['trip_id'].astype('string')
        except KeyError:
            logging.debug("can not convert df_stoptimes")
        except OverflowError:
            logging.debug("can not convert df_stoptimes")
        except ValueError:
            logging.debug("can not convert df_stoptimes")
        except AttributeError:
            logging.debug("can not convert df_stoptimes Attribute")

        logging.debug("convert to df: create_df_stop_times finished")

        return df_stoptimes

    def create_df_stops(self, raw_data):
        logging.debug("convert to df: create_df_stops")
        # DataFrame with every stop
        df_stops = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Stops])
        df_stops = self.drop_columns_by_enum(df_stops, DfStopColumnEnum)
        df_stops.name = GtfsDfNames.Stops
        try:
            df_stops['stop_id'] = df_stops['stop_id'].astype('string')
            df_stops['parent_station'] = df_stops['parent_station'].astype('string')
            df_stops['stop_name'] = df_stops['stop_name'].astype('string')
        except KeyError:
            logging.debug("can not convert df_Stops: stop_id into int ")
        except ValueError:
            logging.debug("can not convert df_Stops")
        except AttributeError:
            logging.debug("can not convert df_Stops Attribute")
        logging.debug("convert to df: create_df_stops finished")

        return df_stops

    def create_df_week(self, raw_data):
        logging.debug("convert to df: create_df_week")
        df_week = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Calendarweeks])
        df_week = self.drop_columns_by_enum(df_week, DfCalendarweekColumnEnum)
        df_week.name = GtfsDfNames.Calendarweeks
        try:
            df_week['start_date'] = df_week['start_date'].astype('string')
            df_week['end_date'] = df_week['end_date'].astype('string')
        except KeyError:
            logging.debug("can not convert df_week")

        logging.debug("convert to df: df_week finished")

        return df_week

    def create_df_dates(self, raw_data):
        logging.debug("convert to df: create_df_dates")
        df_dates = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Calendardates])
        df_dates.name = GtfsDfNames.Calendardates
        try:
            df_dates['exception_type'] = df_dates['exception_type'].astype('int32')
            df_dates['date_day_format'] = pd.to_datetime(df_dates['date'])
            df_dates['day'] = df_dates['date_day_format'].dt.day_name()
            df_dates['date'] = pd.to_datetime(df_dates['date'], format='%Y%m%d')
        except KeyError:
            logging.debug("can not convert df_dateS")
        logging.debug("convert to df: create_df_dates finished")
        df_dates = self.drop_columns_by_enum(df_dates, DfCalendardateColumnEnum)
        return df_dates

    def create_df_agency(self, raw_data):
        logging.debug("convert to df: create_df_agency")
        df_agencies = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Agencies])
        df_agencies = self.drop_columns_by_enum(df_agencies, DfAgencyColumnEnum)
        df_agencies.name = GtfsDfNames.Agencies

        return df_agencies

    def create_df_feed(self, raw_data):
        logging.debug("convert to df: create_df_feed")
        if raw_data["feed_info"]:
            df_feedinfo = pd.DataFrame.from_dict(raw_data[GtfsDfNames.Feedinfos])
            df_feedinfo.name = GtfsDfNames.Feedinfos
            self.drop_columns_by_enum(df_feedinfo, DfFeedinfoColumnEnum)
            return df_feedinfo
        return None

    def drop_columns_by_enum(self, df, enum_class):
        columns_to_keep = [col.value for col in enum_class]
        columns_to_drop = [col for col in df.columns if col not in columns_to_keep]

        if len(columns_to_drop) > 0:
            return df.drop(columns=columns_to_drop)
        return df

    # region end

    def read_gtfs_data_from_path(self):
        ...

    def reset_data_cause_of_error(self):
        self.progress = 0
        """Todo: add the other values here """

    def save_pickle(self, imported_df_data):
        """
        Save the imported dataframes as pickle files and create a zip file containing all pickled dataframes.
        :param imported_df_data: Dictionary containing dataframes to be saved
        :return: None
        """

        # Save individual dataframes as pickle files
        imported_df_data[GtfsDfNames.Stops].to_pickle(self._pickle_save_path + "dfStops.pkl")
        imported_df_data[GtfsDfNames.Stoptimes].to_pickle(self._pickle_save_path + "dfStopTimes.pkl")
        imported_df_data[GtfsDfNames.Trips].to_pickle(self._pickle_save_path + "dfTrips.pkl")
        imported_df_data[GtfsDfNames.Calendarweeks].to_pickle(self._pickle_save_path + "dfWeek.pkl")
        imported_df_data[GtfsDfNames.Calendardates].to_pickle(self._pickle_save_path + "dfDates.pkl")
        imported_df_data[GtfsDfNames.Routes].to_pickle(self._pickle_save_path + "dfRoutes.pkl")
        imported_df_data[GtfsDfNames.Agencies].to_pickle(self._pickle_save_path + "dfagency.pkl")

        # Save feed info dataframe if available
        if GtfsDfNames.Feedinfos in imported_df_data:
            imported_df_data[GtfsDfNames.Stops].to_pickle(self._pickle_save_path + "dffeed_info.pkl")

        # Create a zip file containing all pickled dataframes
        with zipfile.ZipFile(self.pickle_save_path_filename, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(self._pickle_save_path + "dfStops.pkl")
            zf.write(self._pickle_save_path + "dfStopTimes.pkl")
            zf.write(self._pickle_save_path + "dfTrips.pkl")
            zf.write(self._pickle_save_path + "dfWeek.pkl")
            zf.write(self._pickle_save_path + "dfDates.pkl")
            zf.write(self._pickle_save_path + "dfRoutes.pkl")
            zf.write(self._pickle_save_path + "dfagency.pkl")

        # Remove individual pickle files after zipping
        os.remove(self._pickle_save_path + "dfStops.pkl")
        os.remove(self._pickle_save_path + "dfStopTimes.pkl")
        os.remove(self._pickle_save_path + "dfTrips.pkl")
        os.remove(self._pickle_save_path + "dfWeek.pkl")
        os.remove(self._pickle_save_path + "dfDates.pkl")
        os.remove(self._pickle_save_path + "dfRoutes.pkl")
        os.remove(self._pickle_save_path + "dfagency.pkl")
        # Remove feed info pickle file if available
        if GtfsDfNames.Feedinfos in imported_df_data:
            os.remove(self._pickle_save_path + "dffeed_info.pkl")
