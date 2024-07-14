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


# noinspection SqlResolve
class gtfs(Publisher, Subscriber):
    def __init__(self, events, name):
        super().__init__(events=events, name=name)
        self.notify_functions = {
            'ImportGTFS': [self.async_task_load_GTFS_data, False],
            'fill_agency_list': [self.get_routes_of_agency, False],
            'create_table_date': [self.sub_worker_create_output_fahrplan_date, False],
            'create_table_weekday': [self.sub_worker_create_output_fahrplan_weekday, False],
        }

        """ property """
        self.input_path = ""
        self._output_path = ""
        self.date_range = ""
        self._gtfs_name = ""
        self._pickleSavePath = ""
        self._progress = 0
        self._agenciesList = None
        self._routesList = None
        self.pkl_loaded = False
        self._individualsorting = False
        self._pickleExport_checked = False
        self.options_dates_weekday = ['Dates', 'Weekday']
        self.weekDayOptions = {0: [0, 'Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday'],
                               1: [1, 'Monday, Tuesday, Wednesday, Thursday, Friday'],
                               2: [2, 'Monday'],
                               3: [3, 'Tuesday'],
                               4: [4, 'Wednesday'],
                               5: [5, 'Thursday'],
                               6: [6, 'Friday'],
                               7: [7, 'Saturday'],
                               8: [8, 'Sunday'],
                               }
        self.weekDayOptionsList = ['0,Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday',
                                   '1,Monday, Tuesday, Wednesday, Thursday, Friday',
                                   '2,Monday',
                                   '3,Tuesday',
                                   '4,Wednesday',
                                   '5,Thursday',
                                   '6,Friday',
                                   '7,Saturday',
                                   '8,Sunday']

        self.selected_option_dates_weekday = 1
        self.selected_direction = 0
        self.sortmode = 1
        self.timeformat = 1
        self.dfdateRangeInGTFSData = None
        self.STRdateRangeInGTFSData = None

        self.time = None
        self.processing = None
        self.runningAsync = 0

        """ dicts for create and listbox """
        self.stopsdict = {}
        self.stopTimesdict = {}
        self.tripdict = {}
        self.calendarWeekdict = {}
        self.calendarDatesdict = {}
        self.routesFahrtdict = {}
        self.agencyFahrtdict = {}

        self.feed_infodict = {}

        """ loaded raw_gtfs_data """
        self.raw_gtfs_data = []

        """ all stops for given trips """
        self.filtered_stop_names = ""

        """ df-data """
        self.dfStops = pd.DataFrame()
        self.dfStopTimes = pd.DataFrame()
        self.dfTrips = pd.DataFrame()
        self.dfWeek = pd.DataFrame()
        self.dfDates = pd.DataFrame()
        self.dfRoutes = pd.DataFrame()
        self.dfSelectedRoutes = pd.DataFrame()
        self.dfagency = pd.DataFrame()
        self.dffeed_info = pd.DataFrame()
        self.now = None

        """ loaded data for listbox """

        self.weekdayList = None
        self.serviceslist = None

        """ loaded data for create tables """
        self.selectedAgency = None
        self.selectedRoute = None
        self.selected_weekday = None
        self.selected_dates = None
        self.header_for_export_data = None
        self.dfheader_for_export_data = None
        self.last_time = time.time()
        self.dfdirection = None

        # dataframe with requested data (options)
        self.requested_dates = None
        self.requested_datesdf = None
        self.requested_direction = None
        self.requested_directiondf = None
        self.route_short_namedf = None
        self.varTestAgency = None

        self.weekcond_df = None
        self.varTestService = None

        self.fahrplan_dates = None
        self.fahrplan_calendar_weeks = None
        self.fahrplan_dates_all_dates = None
        self.fahrplan_sorted_stops = None
        self.fahrplan_calendar_filter_days_pivot = None

    @property
    def individualsorting(self):
        return self._individualsorting

    @individualsorting.setter
    def individualsorting(self, value):
        self._individualsorting = value

    @property
    def progress(self):
        return self._progress

    @property
    def input_path(self):
        return self._input_path

    @input_path.setter
    def input_path(self, value):
        self._input_path = value

    @property
    def pickleSavePath(self):
        return self._pickleSavePath

    @pickleSavePath.setter
    def pickleSavePath(self, value):
        if value is not None:
            self._pickleSavePath = value
        else:
            self.dispatch("message",
                          "Folder not found. Please check!")

    @property
    def gtfs_name(self):
        return self._gtfs_name

    @gtfs_name.setter
    def gtfs_name(self, value):
        self._gtfs_name = value
        # self.dispatch("message",
        #               "Folder not found. Please check!")

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.dispatch("update_progress_bar", "update_progress_bar routine started! Notify subscriber!")

    @property
    def agenciesList(self):
        return self._agenciesList

    @agenciesList.setter
    def agenciesList(self, value):
        self._agenciesList = value
        self.dispatch("update_agency_list",
                      "update_agency_list routine started! Notify subscriber!")

    @property
    def pickleExport_checked(self):
        return self._pickleExport_checked

    @pickleExport_checked.setter
    def pickleExport_checked(self, value):
        self._pickleExport_checked = value

    @property
    def dfSelectedRoutes(self):
        return self._dfSelectedRoutes

    @dfSelectedRoutes.setter
    def dfSelectedRoutes(self, value):
        self._dfSelectedRoutes = value
        self.dispatch("update_routes_list",
                      "update_routes_list routine started! Notify subscriber!")

    def notify_subscriber(self, event, message):
        logging.debug(f'event: {event}, message {message}')
        notify_function, parameters = self.notify_functions.get(event, self.notify_not_function)
        if not parameters:
            notify_function()
        else:
            notify_function(message)

    def notify_not_function(self, event):
        logging.debug('event not found in class gui: {}'.format(event))

    # loads data from zip
    def async_task_load_GTFS_data(self):
        self.progress = 20
        self.import_gtfs()
        self.progress = 60
        self.getDateRange()
        self.progress = 100

    # import routine and
    def import_gtfs(self) -> bool:
        self.processing = "import_gtfs started"

        if self.read_paths() is True:
            if self.read_gtfs_data() is True:
                if self.pkl_loaded is False:
                    logging.debug("read_gtfs_data")
                    self.read_gtfs_data_from_path()
                    logging.debug("read_gtfs_data_from_path")
                    self.create_dfs()
                    logging.debug("create_dfs ")
                    self.cleandicts()
                    return True
                else:
                    logging.debug("Pickle Data Detected. Loading Pickle Data")
                    self.cleandicts()
                    return True
        return False

    def set_paths(self, input_path, output_path, picklesavepath=""):
        self.input_path = input_path
        self.output_path = output_path
        self.pickleSavePath = picklesavepath

    def get_routes_of_agency(self) -> None:
        if self.selectedAgency is not None:
            self.select_gtfs_routes_from_agency()

    def set_routes(self, route) -> None:
        self.selectedRoute = route

    def sub_worker_create_output_fahrplan_weekday(self):
        self.progress = 10
        self.weekday_prepare_data_fahrplan()
        self.progress = 20
        self.datesWeekday_select_dates_for_date_range()
        self.progress = 30
        self.weekday_select_weekday_exception_2()
        self.progress = 40
        self.datesWeekday_select_stops_for_trips()
        self.progress = 50
        self.datesWeekday_select_for_every_date_trips_stops()
        self.progress = 60
        self.datesWeekday_select_stop_sequence_stop_name_sorted()
        self.progress = 70
        self.datesWeekday_create_fahrplan()
        self.progress = 80
        self.datesWeekday_create_output_fahrplan()
        self.progress = 100

    def sub_worker_create_output_fahrplan_date(self):
        self.progress = 0
        logging.debug(f"PREPARE date ")
        self.progress = 10
        self.dates_prepare_data_fahrplan()
        self.progress = 20
        self.datesWeekday_select_dates_for_date_range()
        self.progress = 30
        self.dates_select_dates_delete_exception_2()
        self.progress = 40
        self.datesWeekday_select_stops_for_trips()
        self.progress = 50
        self.datesWeekday_select_for_every_date_trips_stops()
        self.progress = 60
        self.datesWeekday_select_stop_sequence_stop_name_sorted()
        self.progress = 70
        self.datesWeekday_create_fahrplan()
        self.progress = 80
        self.datesWeekday_create_output_fahrplan()
        self.progress = 100

    def sub_worker_create_output_fahrplan_date_indi(self):
        self.progress = 0
        logging.debug(f"PREPARE intividual date ")
        self.progress = 10
        self.dates_prepare_data_fahrplan()
        self.progress = 20
        self.datesWeekday_select_dates_for_date_range()
        self.progress = 30
        self.dates_select_dates_delete_exception_2()
        self.progress = 40
        self.datesWeekday_select_stops_for_trips()
        self.progress = 50
        self.datesWeekday_select_for_every_date_trips_stops()
        self.progress = 60
        self.datesWeekday_select_stop_sequence_stop_name_sorted()
        self.progress = 70
        self.datesWeekday_create_sort_stopnames()
        self.dispatch("update_stopname_create_list",
                      "update_stopname_create_list routine started! Notify subscriber!")

    def sub_worker_create_output_fahrplan_date_indi_continue(self):
        logging.debug(f"continue to create table with individual sorting")
        self.datesWeekday_create_fahrplan_continue()
        self.progress = 80
        self.datesWeekday_create_output_fahrplan()
        self.progress = 100

    def create_dfs(self):
        """
        loads dicts and creates dicts.
        It also set indices, if possible to speed up search
        """

        last_time = time.time()

        # DataFrame for every route
        #  self.dfRoutes = pd.DataFrame.from_dict(self.routesFahrtdict).set_index('route_id')
        self.dfRoutes = pd.DataFrame.from_dict(self.routesFahrtdict)

        # DataFrame with every trip
        self.dfTrips = pd.DataFrame.from_dict(self.tripdict).set_index('trip_id')
        try:
            # dfTrips['trip_id'] = pd.to_numeric(dfTrips['trip_id'])
            self.dfTrips['trip_id'] = self.dfTrips['trip_id'].astype('int8')
            self.dfTrips['direction_id'] = self.dfTrips['direction_id'].astype('int8')
            self.dfTrips['shape_id'] = self.dfTrips['shape_id'].astype('int8')
            self.dfTrips['wheelchair_accessible'] = self.dfTrips['wheelchair_accessible'].astype('int8')
            self.dfTrips['bikes_allowed'] = self.dfTrips['bikes_allowed'].astype('int8')

        except KeyError:
            logging.debug("can not convert dfTrips: trip_id into string")

        # DataFrame with every stop (time)
        self.dfStopTimes = pd.DataFrame.from_dict(self.stopTimesdict).set_index('stop_id')
        # try:
        #
        #     self.dfStopTimes['arrival_time'] = self.dfStopTimes['arrival_time'].apply(lambda x: self.time_in_string(x))
        #
        # except KeyError:
        #     logging.debug("can not convert dfStopTimes: arrival_time into string and change time")

        try:
            self.dfStopTimes['stop_sequence'] = self.dfStopTimes['stop_sequence'].astype('int32')
        except KeyError:
            logging.debug("can not convert dfStopTimes: stop_sequence into int")
        try:
            self.dfStopTimes['stop_id'] = self.dfStopTimes['stop_id'].astype('int32')
        except KeyError:
            logging.debug("can not convert dfStopTimes: stop_id into int")
        except OverflowError:
            logging.debug("can not convert dfStopTimes: stop_id into int")
        try:
            self.dfStopTimes['trip_id'] = self.dfStopTimes['trip_id'].astype('string')
        except KeyError:
            logging.debug("can not convert dfStopTimes: trip_id into string")

        # DataFrame with every stop
        self.dfStops = pd.DataFrame.from_dict(self.stopsdict).set_index('stop_id')
        try:
            self.dfStops['stop_id'] = self.dfStops['stop_id'].astype('int32')
        except KeyError:
            logging.debug("can not convert dfStops: stop_id into int ")

        # DataFrame with every service weekly
        self.dfWeek = pd.DataFrame.from_dict(self.calendarWeekdict).set_index('service_id')
        self.dfWeek['start_date'] = self.dfWeek['start_date'].astype('string')
        self.dfWeek['end_date'] = self.dfWeek['end_date'].astype('string')

        # DataFrame with every service dates
        self.dfDates = pd.DataFrame.from_dict(self.calendarDatesdict).set_index('service_id')
        self.dfDates['exception_type'] = self.dfDates['exception_type'].astype('int32')
        self.dfDates['date'] = pd.to_datetime(self.dfDates['date'], format='%Y%m%d')

        # DataFrame with every agency
        self.dfagency = pd.DataFrame.from_dict(self.agencyFahrtdict)

        if self.feed_infodict:
            self.dffeed_info = pd.DataFrame.from_dict(self.feed_infodict)

        zeit = time.time() - last_time
        logging.debug("time: {} ".format(zeit))

        return True

    def save_pickle(self):
        self.dfStops.to_pickle(self.output_path + "dfStops.pkl")
        self.dfStopTimes.to_pickle(self.output_path + "dfStopTimes.pkl")
        self.dfTrips.to_pickle(self.output_path + "dfTrips.pkl")
        self.dfWeek.to_pickle(self.output_path + "dfWeek.pkl")
        self.dfDates.to_pickle(self.output_path + "dfDates.pkl")
        self.dfRoutes.to_pickle(self.output_path + "dfRoutes.pkl")
        self.dfagency.to_pickle(self.output_path + "dfagency.pkl")

        if not self.dffeed_info.empty:
            self.dffeed_info.to_pickle(self.output_path + "dffeed_info.pkl")

        with zipfile.ZipFile(self.pickleSavePath, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(self.output_path + "dfStops.pkl")
            zf.write(self.output_path + "dfStopTimes.pkl")
            zf.write(self.output_path + "dfTrips.pkl")
            zf.write(self.output_path + "dfWeek.pkl")
            zf.write(self.output_path + "dfDates.pkl")
            zf.write(self.output_path + "dfRoutes.pkl")
            zf.write(self.output_path + "dfagency.pkl")

        os.remove(self.output_path + "dfStops.pkl")
        os.remove(self.output_path + "dfStopTimes.pkl")
        os.remove(self.output_path + "dfTrips.pkl")
        os.remove(self.output_path + "dfWeek.pkl")
        os.remove(self.output_path + "dfDates.pkl")
        os.remove(self.output_path + "dfRoutes.pkl")
        os.remove(self.output_path + "dfagency.pkl")
        if not self.dffeed_info.empty:
            os.remove(self.output_path + "dffeed_info.pkl")

    def getDateRange(self):
        logging.debug('len stop_sequences {}'.format(self.dffeed_info))
        if not self.dffeed_info.empty:
            self.date_range = str(self.dffeed_info.iloc[0].feed_start_date) + '-' + str(
                self.dffeed_info.iloc[0].feed_end_date)
        else:
            self.date_range = self.analyzeDateRangeInGTFSData()

    # reads the files
    def read_paths(self):
        if self.input_path is None \
                or self.output_path is None:
            return False
        return True

    def cleandicts(self) -> bool:
        self.stopsdict = None
        self.stopTimesdict = None
        self.tripdict = None
        self.calendarWeekdict = None
        self.calendarDatesdict = None
        self.routesFahrtdict = None
        self.agencyFahrtdict = None
        return True

    # checks if all data is avalibale before creation
    def data_loaded_and_available(self) -> bool:
        if (self.stopsdict is None
                or self.stopTimesdict is None
                or self.tripdict is None
                or self.calendarWeekdict is None
                or self.calendarDatesdict is None
                or self.routesFahrtdict is None
                or self.selectedRoute is None
                or self.selected_direction is None):
            return False
        else:
            return True

    def filterStopSequence(self, data):
        """
        take all stop ids and search for the earlist stoptime
        for each stop to determine sorting
        """
        stopsequence = {}
        sorted_stopsequence = {
            "stop_id": [],
            "stop_sequence": [],
            "stop_name": [],
            "start_time": []
        }
        # data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d %H:%M:%S.%f')
        # data['date'] = data['date'].dt.strftime('%m-%Y-%d %Y')

        for stop_name_i in data.itertuples():

            if not self.dictForEntry(stopsequence, "stop_id", stop_name_i.stop_id):
                temp = {"stop_sequence": -1, "stop_name": '', "trip_id": '', "start_time": '', "arrival_time": ''}
                temp["stop_sequence"] = stop_name_i.stop_sequence
                temp["stop_name"] = stop_name_i.stop_name
                temp["trip_id"] = stop_name_i.trip_id

                if self.check_hour_24(stop_name_i.start_time):
                    comparetime_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime(
                        '%Y-%m-%d'))) + ' 0' + str(int(stop_name_i.start_time.split(':')[0]) - 24) + ':' + \
                                    stop_name_i.start_time.split(':')[1] + ':' + \
                                    stop_name_i.start_time.split(':')[2]
                    time_i = datetime.strptime(comparetime_i, '%Y-%m-%d %H:%M:%S')
                    time_i = time_i + timedelta(days=1)
                else:
                    comparetime_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime(
                        '%Y-%m-%d'))) + ' ' + stop_name_i.start_time
                    time_i = datetime.strptime(comparetime_i, '%Y-%m-%d %H:%M:%S')

                if self.check_hour_24(stop_name_i.arrival_time):
                    time_arrival_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime(
                        '%Y-%m-%d'))) + ' 0' + str(int(stop_name_i.arrival_time.split(':')[0]) - 24) + ':' + \
                                     stop_name_i.arrival_time.split(':')[1] + ':' + \
                                     stop_name_i.arrival_time.split(':')[2]
                    time_arrival_i = datetime.strptime(time_arrival_i, '%Y-%m-%d %H:%M:%S')
                    time_arrival_i = time_arrival_i + timedelta(days=1)
                else:
                    time_arrival_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime(
                        '%Y-%m-%d'))) + ' ' + stop_name_i.arrival_time
                    time_arrival_i = datetime.strptime(time_arrival_i, '%Y-%m-%d %H:%M:%S')

                temp["start_time"] = time_i
                temp["arrival_time"] = time_arrival_i

                # search in data and compare the ids
                for stop_name_j in data.itertuples():
                    # if ids match continue comparison
                    if stop_name_i.stop_id == stop_name_j.stop_id:
                        # 23072022
                        # and stop_name_i.trip_id == stop_name_j.trip_id\
                        if self.check_hour_24(stop_name_j.start_time):
                            comparetime_j = str((datetime.strptime(stop_name_j.date,
                                                                   '%Y-%m-%d %H:%M:%S.%f').strftime(
                                '%Y-%m-%d'))) + ' 0' + str(
                                int(stop_name_j.start_time.split(':')[0]) - 24) + ':' + \
                                            stop_name_j.start_time.split(':')[1] + ':' + \
                                            stop_name_j.start_time.split(':')[2]

                            time_j = datetime.strptime(comparetime_j, '%Y-%m-%d %H:%M:%S')
                            time_j = time_j + timedelta(days=1)
                        else:
                            comparetime_j = str((datetime.strptime(stop_name_j.date,
                                                                   '%Y-%m-%d %H:%M:%S.%f').strftime(
                                '%Y-%m-%d'))) + ' ' + stop_name_j.start_time
                            time_j = datetime.strptime(comparetime_j, '%Y-%m-%d %H:%M:%S')

                        time_temp = temp["start_time"]

                        if self.check_hour_24(stop_name_j.arrival_time):
                            time_arrival_j = str((datetime.strptime(stop_name_j.date,
                                                                    '%Y-%m-%d %H:%M:%S.%f').strftime(
                                '%Y-%m-%d'))) + ' 0' + str(
                                int(stop_name_j.arrival_time.split(':')[0]) - 24) + ':' + \
                                             stop_name_j.arrival_time.split(':')[1] + ':' + \
                                             stop_name_j.arrival_time.split(':')[2]
                            time_arrival_j = datetime.strptime(time_arrival_j, '%Y-%m-%d %H:%M:%S')
                            time_arrival_j = time_arrival_j + timedelta(days=1)
                        else:
                            time_arrival_j = str((datetime.strptime(stop_name_j.date,
                                                                    '%Y-%m-%d %H:%M:%S.%f').strftime(
                                '%Y-%m-%d'))) + ' ' + stop_name_j.arrival_time
                            time_arrival_j = datetime.strptime(time_arrival_j, '%Y-%m-%d %H:%M:%S')

                        arrival_time_temp = temp["arrival_time"]

                        if time_j < time_i \
                                and time_j < time_temp \
                                and stop_name_j.stop_sequence > stop_name_i.stop_sequence \
                                and stop_name_j.stop_sequence > temp["stop_sequence"]:
                            temp["start_time"] = time_j
                            temp["arrival_time"] = time_arrival_j
                            # temp["arrival_time"] = stop_name_j.arrival_time
                            temp["stop_sequence"] = stop_name_j.stop_sequence

                        # if time_j < time_i \
                        # and time_j < time_temp \
                        # and time_arrival_j < time_arrival_i \
                        # and time_arrival_j < arrival_time_temp\
                        # and stop_name_j.stop_sequence > stop_name_i.stop_sequence:
                        #     temp["start_time"] = time_j
                        #     temp["arrival_time"] = time_arrival_j
                        #     # temp["arrival_time"] = stop_name_j.arrival_time
                        #     temp["stop_sequence"] = stop_name_j.stop_sequence

                stopsequence[stop_name_i.stop_id] = temp

        new_stopsequence = self.sortStopSequence(stopsequence)

        for stop_sequence in new_stopsequence.keys():
            sorted_stopsequence['stop_id'].append(new_stopsequence[stop_sequence]['stop_id'])
            sorted_stopsequence['stop_sequence'].append(stop_sequence)
            sorted_stopsequence['stop_name'].append(new_stopsequence[stop_sequence]['stop_name'])
            sorted_stopsequence['start_time'].append(new_stopsequence[stop_sequence]['start_time'])

        #
        # logging.debug('len stop_sequences {}'.format(sequence_count))
        # for stop_id in stopsequence.keys():
        #     if stop_id in new_stopsequence \
        #         and stopsequence[stop_id]['start_time'] < new_stopsequence[stop_id]['start_time'] \
        #         and stopsequence[stop_id]['arrival_time'] < new_stopsequence[stop_id]['arrival_time']:
        #         pass
        #     else:
        #         temp = {"stop_sequence": -1, "stop_name": '', "trip_id": '', "start_time": '', "arrival_time": ''}
        #         temp["start_time"] = stopsequence[stop_id]['start_time']
        #         temp["arrival_time"] = stopsequence[stop_id]['arrival_time']
        #         temp["stop_sequence"] = sequence_count - 1
        #         new_stopsequence[stop_id] = temp
        #
        #
        #
        #
        #
        #
        # logging.debug(stopsequence)
        # i = 0
        # for sequence in range(0, len(temp["stop_sequence"])):
        #     i += 1
        #     temp["stop_sequence"][sequence] = i

        return sorted_stopsequence

    def sortStopSequence(self, stopsequence):
        """
        sort dict of stops (cust. bubble sort)
        """
        # get all possible stops
        sequence_count = len(stopsequence)

        # init data structure
        d = {}
        for k in range(sequence_count):
            d[str(k)] = {"start_time": datetime.strptime('1901-01-01 23:59:00', '%Y-%m-%d %H:%M:%S').time(),
                         "arrival_time": datetime.strptime('1901-01-01 23:59:00', '%Y-%m-%d %H:%M:%S').time(),
                         "stop_name": '',
                         "stop_id": ''
                         }

        # fill new dict
        for k, j in enumerate(stopsequence):
            if d[str(k)]["stop_id"] == '':
                d[str(k)]["stop_id"] = j
                d[str(k)]["start_time"] = stopsequence[j]['start_time']
                d[str(k)]["arrival_time"] = stopsequence[j]['arrival_time']
                d[str(k)]["stop_sequence"] = stopsequence[j]['stop_sequence']
                d[str(k)]["stop_name"] = stopsequence[j]['stop_name']

        if self.sortmode == 1:
            # bubble sort
            for i in range(sequence_count - 1):
                for j in range(0, sequence_count - i - 1):
                    if d[str(j)]["stop_sequence"] > d[str(j + 1)]["stop_sequence"]:
                        d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
                    elif d[str(j)]["stop_sequence"] == d[str(j + 1)]["stop_sequence"]:
                        if d[str(j)]["start_time"] > d[str(j + 1)]["start_time"]:
                            d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]

        else:
            # bubble sort
            for i in range(sequence_count - 1):
                for j in range(0, sequence_count - i - 1):
                    if d[str(j)]["stop_sequence"] > d[str(j + 1)]["stop_sequence"]:
                        d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
                    elif d[str(j)]["stop_sequence"] == d[str(j + 1)]["stop_sequence"]:
                        if d[str(j)]["start_time"] > d[str(j + 1)]["start_time"]:
                            d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
            # -> hier ist etwas komisch!
            # for i in range(sequence_count - 1):
            #     for j in range(0, sequence_count - i - 1):
            #         # 23072022
            #         # if d[str(j)]["arrival_time"] > d[str(j + 1)]["arrival_time"]:
            #         #     d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
            #         if d[str(j)]["stop_sequence"] > d[str(j + 1)]["stop_sequence"] \
            #                 and d[str(j)]["start_time"] > d[str(j + 1)]["start_time"]:
            #             d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
            #         elif d[str(j)]["stop_sequence"] == d[str(j + 1)]["stop_sequence"]:
            #             if d[str(j)]["start_time"] > d[str(j + 1)]["start_time"] \
            #                     and d[str(j)]["arrival_time"] > d[str(j + 1)]["arrival_time"]:
            #                 d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
        return d

    # checks if in dictonary
    def dictForEntry(self, temp, key, key_value):
        if key_value in temp:
            return True
        else:
            return False

    # the is the one way to add a 0 to the time hh:mm:ss, if 0 is missing like in 6:44:33
    def time_in_string(self, time):
        pattern = re.findall('^\d{1}:\d{2}:\d{2}$', time)

        if pattern:
            return '0' + time
        else:
            return time

    # the is the one way to add a 0 to the time hh:mm:ss, if 0 is missing like in 6:44:33
    def time_delete_seconds(self, time):
        return time[:-3]

    # checks if date string
    def check_dates_input(self, dates):
        pattern1 = re.findall('^\d{8}(?:\d{8})*(?:,\d{8})*$', dates)
        if pattern1:
            return True
        else:
            return False

    def check_KommaInText(self, dates):
        pattern1 = re.findall('"\w*,\w*"', dates)
        if pattern1:
            logging.debug(pattern1)
            return True
        else:
            return False

    # checks if time-string exceeds 24 hour
    def check_hour_24(self, time):
        try:
            pattern1 = re.findall('^2{1}[4-9]{1}:[0-9]{2}', time)
            if pattern1:
                return True
            else:
                return False
        except:
            logging.debug(time)

    # read zip-data
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

    def get_gtfs_trip(self):
        tripdict = {
        }

        headers = self.raw_gtfs_data[2][0].replace('"', "").split(",")
        itripDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            tripdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        for data in self.raw_gtfs_data[2][1]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            tripDate = data.split(",")
            for idx in range(itripDate):
                tripdict[header_names[idx]].append(tripDate[idx])

        self.tripdict = tripdict
        return True

    def get_gtfs_stop(self):

        stopsdict = {
        }
        headers = self.raw_gtfs_data[0][0].replace('"', "").split(",")
        istopDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            stopsdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        for haltestellen in self.raw_gtfs_data[0][1]:
            haltestellen = haltestellen.replace(", ", " ")
            haltestellen = haltestellen.replace('"', "")
            haltestellen = haltestellen.replace('\n', "")
            stopData = haltestellen.split(",")

            for idx in range(istopDate):
                stopsdict[header_names[idx]].append(stopData[idx])

        self.stopsdict = stopsdict
        return True

    def get_gtfs_stoptime(self):
        stopTimesdict = {
        }

        headers = self.raw_gtfs_data[1][0].replace('"', "").split(",")
        istopTimeData = len(headers)
        header_names = []
        for haltestellen_header in headers:
            stopTimesdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        for data in self.raw_gtfs_data[1][1]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            stopTimeData = data.split(",")

            for idx in range(istopTimeData):
                stopTimesdict[header_names[idx]].append(stopTimeData[idx])

        self.stopTimesdict = stopTimesdict
        return True

    def get_gtfs_calendarWeek(self):
        calendarWeekdict = {
        }

        headers = self.raw_gtfs_data[3][0].replace('"', "").split(",")
        icalendarDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            calendarWeekdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        for data in self.raw_gtfs_data[3][1]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            calendarDate = data.split(",")

            for idx in range(icalendarDate):
                calendarWeekdict[header_names[idx]].append(calendarDate[idx])

        self.calendarWeekdict = calendarWeekdict
        return True

    def get_gtfs_calendarDates(self):
        calendarDatesdict = {
        }

        headers = self.raw_gtfs_data[4][0].replace('"', "").split(",")
        icalendarDate = len(headers)
        header_names = []
        for haltestellen_header in headers:
            calendarDatesdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        for data in self.raw_gtfs_data[4][1]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            calendarDatesDate = data.split(",")
            for idx in range(icalendarDate):
                calendarDatesdict[header_names[idx]].append(calendarDatesDate[idx])

        self.calendarDatesdict = calendarDatesdict
        return True

    def get_gtfs_routes(self):
        routesFahrtdict = {
        }

        headers = self.raw_gtfs_data[5][0].replace('"', "").split(",")
        iroutesFahrt = len(headers)
        header_names = []
        for haltestellen_header in headers:
            routesFahrtdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        for data in self.raw_gtfs_data[5][1]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            routesFahrtData = data.split(",")
            for idx in range(iroutesFahrt):
                routesFahrtdict[header_names[idx]].append(routesFahrtData[idx])

        self.routesFahrtdict = routesFahrtdict
        return True

    def get_gtfs_feed_info(self):
        feed_infodict = {
        }

        headers = self.raw_gtfs_data[7][0].replace('"', "").split(",")
        ifeed_infodict = len(headers)
        header_names = []
        for haltestellen_header in headers:
            feed_infodict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        for data in self.raw_gtfs_data[7][1]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            feed_infodictData = data.split(",")
            for idx in range(ifeed_infodict):
                feed_infodict[header_names[idx]].append(feed_infodictData[idx])

        self.feed_infodict = feed_infodict
        return True

    def get_gtfs_agencies(self):

        agencyFahrtdict = {
        }

        headers = self.raw_gtfs_data[6][0].replace('"', "").split(",")
        iagencyData = len(headers)
        header_names = []
        for haltestellen_header in headers:
            agencyFahrtdict[haltestellen_header] = []
            header_names.append(haltestellen_header)

        for data in self.raw_gtfs_data[6][1]:
            data = data.replace(", ", " ")
            data = data.replace('"', "")
            data = data.replace('\n', "")
            agencyData = data.split(",")
            for idx in range(iagencyData):
                agencyFahrtdict[header_names[idx]].append(agencyData[idx])

        self.agencyFahrtdict = agencyFahrtdict
        return True

    def read_gtfs_data_from_path(self):
        """ Creating and starting 10 tasks.
        tasks = get_gtfs_stop(inputgtfsData[0]),\
                get_gtfs_stoptime(inputgtfsData[1]),\
                get_gtfs_trip(inputgtfsData[2]),\
                get_gtfs_calendarWeek(inputgtfsData[3]),\
                get_gtfs_calendarDates(inputgtfsData[4]),\
                get_gtfs_routes(inputgtfsData[5])

        """

        self.get_gtfs_stop()
        self.get_gtfs_stoptime()
        self.get_gtfs_trip()
        self.get_gtfs_calendarWeek()
        self.get_gtfs_calendarDates()
        self.get_gtfs_routes()
        self.get_gtfs_agencies()
        if self.raw_gtfs_data[7][0] is not None:
            self.get_gtfs_feed_info()
        self.raw_gtfs_data = None
        return True

    def select_gtfs_routes_from_agency(self):
        dfRoutes = self.dfRoutes
        inputVar = [{'agency_id': self.selectedAgency}]
        varTest = pd.DataFrame(inputVar).set_index('agency_id')
        cond_routes_of_agency = '''
                    select *
                    from dfRoutes 
                    left join varTest
                    where varTest.agency_id = dfRoutes.agency_id
                    order by dfRoutes.route_short_name;
                   '''
        routes_list = sqldf(cond_routes_of_agency, locals())
        """
        todo
        """
        self.dfSelectedRoutes = routes_list

        # routes_list = routes_list.values.tolist()
        # routes_str_list = []
        # for lists in routes_list:
        #     routes_str_list.append('{},{}'.format(lists[0], lists[1]))
        # self.routesList = routes_str_list
        return True

    def select_gtfs_services_from_routes(self, route, tripdict, calendarWeekdict):
        inputVar = [{'route_id': route[1]}]
        varTest = pd.DataFrame(inputVar).set_index('route_id')

        dfTrips = pd.DataFrame.from_dict(tripdict).set_index('trip_id')

        # DataFrame with every service weekly
        dfWeek = pd.DataFrame.from_dict(calendarWeekdict).set_index('service_id')
        try:
            dfWeek['service_id'] = dfWeek['service_id'].astype(int)
        except:
            logging.debug('dfWeek service_id: can not convert into int')

        cond_services_from_routes = '''
                    select dfWeek.service_id, dfWeek.monday, dfWeek.tuesday, dfWeek.wednesday, dfWeek.thursday, dfWeek.friday, dfWeek.saturday, dfWeek.sunday
                    from dfWeek 
                    inner join dfTrips on dfWeek.service_id = dfTrips.service_id
                    inner join varTest on varTest.route_id = dfTrips.route_id             
                    group by dfWeek.service_id
                    order by dfWeek.service_id;
                   '''
        services_list = sqldf(cond_services_from_routes, locals())
        self.serviceslist = services_list.values.tolist()
        return True

    def read_gtfs_agencies(self):
        dfagency = self.dfagency
        cond_agencies = '''
                    select *
                    from dfagency 
                    order by dfagency.agency_id;
                   '''
        agency_list = sqldf(cond_agencies, locals())
        agency_list = agency_list.values.tolist()
        agency_str_list = []
        for lists in agency_list:
            agency_str_list.append('{},{}'.format(lists[0], lists[1]))
        self.agenciesList = agency_str_list
        # print (agency_list.values.tolist())
        return True

    def weekday_prepare_data_fahrplan(self):

        self.last_time = time.time()

        # DataFrame for header information
        self.header_for_export_data = {'Agency': [self.selectedAgency],
                                       'Route': [self.selectedRoute],
                                       'WeekdayOption': [self.selected_weekday]
                                       }

        self.dfheader_for_export_data = pd.DataFrame.from_dict(self.header_for_export_data)

        dummy_direction = 0
        direction = [{'direction_id': dummy_direction}
                     ]
        self.dfdirection = pd.DataFrame(direction)

        self.requested_direction = {'direction_id': [self.selected_direction]}
        self.requested_directiondf = pd.DataFrame.from_dict(self.requested_direction)

        inputVar = [{'route_short_name': self.selectedRoute}]
        self.route_short_namedf = pd.DataFrame(inputVar)

        inputVarAgency = [{'agency_id': self.selectedAgency}]
        self.varTestAgency = pd.DataFrame(inputVarAgency)

        weekDayOption_1 = {'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
        weekDayOption_2 = {'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
        weekDayOption_monday = {'day': ['Monday']}
        weekDayOption_tuesday = {'day': ['Tuesday']}
        weekDayOption_wednesday = {'day': ['Wednesday']}
        weekDayOption_thursday = {'day': ['Thursday']}
        weekDayOption_friday = {'day': ['Friday']}
        weekDayOption_saturday = {'day': ['Saturday']}
        weekDayOption_sunday = {'day': ['Sunday']}

        weekDay_1_df = pd.DataFrame.from_dict(weekDayOption_1).set_index('day')
        weekDay_2_df = pd.DataFrame.from_dict(weekDayOption_2).set_index('day')
        weekDayOption_monday_df = pd.DataFrame.from_dict(weekDayOption_monday).set_index('day')
        weekDayOption_tuesday_df = pd.DataFrame.from_dict(weekDayOption_tuesday).set_index('day')
        weekDayOption_wednesday_df = pd.DataFrame.from_dict(weekDayOption_wednesday).set_index('day')
        weekDayOption_thursday_df = pd.DataFrame.from_dict(weekDayOption_thursday).set_index('day')
        weekDayOption_friday_df = pd.DataFrame.from_dict(weekDayOption_friday).set_index('day')
        weekDayOption_saturday_df = pd.DataFrame.from_dict(weekDayOption_saturday).set_index('day')
        weekDayOption_sunday_df = pd.DataFrame.from_dict(weekDayOption_sunday).set_index('day')

        weekDayOptionList = [weekDay_1_df,
                             weekDay_2_df,
                             weekDayOption_monday_df,
                             weekDayOption_tuesday_df,
                             weekDayOption_wednesday_df,
                             weekDayOption_thursday_df,
                             weekDayOption_friday_df,
                             weekDayOption_saturday_df,
                             weekDayOption_sunday_df]

        self.weekcond_df = weekDayOptionList[int(self.selected_weekday)]
        dummy_direction = 0

        inputVarService = [{'weekdayOption': int(self.selected_weekday)}]
        self.varTestService = pd.DataFrame(inputVarService).set_index('weekdayOption')

    def dates_prepare_data_fahrplan(self):
        self.last_time = time.time()

        if not self.check_dates_input(self.selected_dates):
            return

        # DataFrame for header information
        self.header_for_export_data = {'Agency': [self.selectedAgency],
                                       'Route': [self.selectedRoute],
                                       'Dates': [self.selected_dates]
                                       }
        self.dfheader_for_export_data = pd.DataFrame.from_dict(self.header_for_export_data)

        dummy_direction = 0
        direction = [{'direction_id': dummy_direction}
                     ]
        self.dfdirection = pd.DataFrame(direction)

        # dataframe with requested data
        self.requested_dates = {'date': [self.selected_dates]}
        self.requested_datesdf = pd.DataFrame.from_dict(self.requested_dates)
        self.requested_datesdf['date'] = pd.to_datetime(self.requested_datesdf['date'], format='%Y%m%d')

        self.requested_direction = {'direction_id': [self.selected_direction]}
        self.requested_directiondf = pd.DataFrame.from_dict(self.requested_direction)

        inputVar = [{'route_short_name': self.selectedRoute}]
        self.route_short_namedf = pd.DataFrame(inputVar)

        inputVarAgency = [{'agency_id': self.selectedAgency}]
        self.varTestAgency = pd.DataFrame(inputVarAgency)

    """checks for first and last date in data and returns it """

    def analyzeDateRangeInGTFSData(self):
        if self.dfWeek is not None:
            self.dfdateRangeInGTFSData = self.dfWeek.groupby(['start_date', 'end_date']).size().reset_index()
            return str(self.dfdateRangeInGTFSData.iloc[0].start_date) + '-' + str(
                self.dfdateRangeInGTFSData.iloc[0].end_date)

    def datesWeekday_select_dates_for_date_range(self):
        # conditions for searching in dfs
        dfTrips = self.dfTrips
        dfWeek = self.dfWeek
        dfRoutes = self.dfSelectedRoutes
        route_short_namedf = self.route_short_namedf
        varTestAgency = self.varTestAgency
        requested_directiondf = self.requested_directiondf
        cond_select_dates_for_date_range = '''
                    select  
                            dfTrips.trip_id,
                            dfTrips.service_id,
                            dfTrips.route_id, 
                            dfWeek.start_date,
                            dfWeek.end_date,
                            dfWeek.monday,
                            dfWeek.tuesday,
                            dfWeek.wednesday,
                            dfWeek.thursday,
                            dfWeek.friday,
                            dfWeek.saturday,
                            dfWeek.sunday
                    from dfWeek 
                    inner join dfTrips on dfWeek.service_id = dfTrips.service_id
                    inner join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                    inner join route_short_namedf on dfRoutes.route_short_name = route_short_namedf.route_short_name
                    inner join varTestAgency on dfRoutes.agency_id = varTestAgency.agency_id
                    inner join requested_directiondf on dfTrips.direction_id = requested_directiondf.direction_id
                    where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                      and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                      and dfTrips.direction_id = requested_directiondf.direction_id -- shows the direction of the line 
                    order by dfTrips.service_id;
                   '''

        # get dates for start and end dates for date range function
        # TODO: Sortieren nach neue Spalte
        """
        dfTrips.trip_id,
        dfTrips.service_id,
        dfTrips.route_id, 
        dfWeek.start_date,
        dfWeek.end_date,
        dfWeek.monday,
        dfWeek.tuesday,
        dfWeek.wednesday,
        dfWeek.thursday,
        dfWeek.friday,
        dfWeek.saturday,
        dfWeek.sunday
        """

        self.fahrplan_dates = None
        self.fahrplan_dates = sqldf(cond_select_dates_for_date_range, locals())

        # change format
        self.fahrplan_dates['start_date'] = pd.to_datetime(self.fahrplan_dates['start_date'], format='%Y%m%d')
        self.fahrplan_dates['end_date'] = pd.to_datetime(self.fahrplan_dates['end_date'], format='%Y%m%d')

    def weekday_select_weekday_exception_2(self):
        dfDates = self.dfDates
        weekcond_df = self.weekcond_df
        dfTrips = self.dfTrips
        dfWeek = self.dfWeek
        dfRoutes = self.dfRoutes
        route_short_namedf = self.route_short_namedf
        varTestAgency = self.varTestAgency
        requested_directiondf = self.requested_directiondf

        cond_select_dates_delete_exception_2 = '''
                    select  
                            fahrplan_dates_all_dates.date,
                            fahrplan_dates_all_dates.day,
                            fahrplan_dates_all_dates.trip_id,
                            fahrplan_dates_all_dates.service_id,
                            fahrplan_dates_all_dates.route_id, 
                            fahrplan_dates_all_dates.start_date,
                            fahrplan_dates_all_dates.end_date,
                            fahrplan_dates_all_dates.monday,
                            fahrplan_dates_all_dates.tuesday,
                            fahrplan_dates_all_dates.wednesday,
                            fahrplan_dates_all_dates.thursday,
                            fahrplan_dates_all_dates.friday,
                            fahrplan_dates_all_dates.saturday,
                            fahrplan_dates_all_dates.sunday
                    from fahrplan_dates_all_dates 
                          -- not has exception_type = 2
                    where fahrplan_dates_all_dates.date not in (select dfDates.date
                                                                  from dfDates                                                            
                                                                    where fahrplan_dates_all_dates.service_id = dfDates.service_id 
                                                                      and fahrplan_dates_all_dates.date = dfDates.date
                                                                      and dfDates.exception_type = 2
                                                                )
                      -- and is marked as the day of the week or is has exception_type = 1                          
                      and (  (   fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.monday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.tuesday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.wednesday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.thursday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.friday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.saturday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.sunday
                             )
                             or 
                             (   fahrplan_dates_all_dates.date in (select dfDates.date
                                                                  from dfDates                                                            
                                                                    where fahrplan_dates_all_dates.service_id = dfDates.service_id 
                                                                      and fahrplan_dates_all_dates.date = dfDates.date
                                                                      and dfDates.exception_type = 1
                                                                 )    
                             )
                          )
                      -- and the day is requested   
                      and fahrplan_dates_all_dates.day in (select weekcond_df.day
                                                                  from weekcond_df                                                            
                                                                    where fahrplan_dates_all_dates.day = weekcond_df.day
                                                         )  
                    order by fahrplan_dates_all_dates.date;
                   '''

        """
        add date column for every date in date range
        for every date in range create

        fahrplan_dates_all_dates.date,
        fahrplan_dates_all_dates.trip_id,
        fahrplan_dates_all_dates.service_id,
        fahrplan_dates_all_dates.route_id, 
        fahrplan_dates_all_dates.start_date,
        fahrplan_dates_all_dates.end_date,
        fahrplan_dates_all_dates.monday,
        fahrplan_dates_all_dates.tuesday,
        fahrplan_dates_all_dates.wednesday,
        fahrplan_dates_all_dates.thursday,
        fahrplan_dates_all_dates.friday,
        fahrplan_dates_all_dates.saturday,
        fahrplan_dates_all_dates.sunday
        """

        fahrplan_dates_all_dates = pd.concat(
            [pd.DataFrame
             ({'date': pd.date_range(row.start_date, row.end_date, freq='D'),
               'trip_id': row.trip_id,
               'service_id': row.service_id,
               'route_id': row.route_id,
               'start_date': row.start_date,
               'end_date': row.end_date,
               'monday': row.monday,
               'tuesday': row.tuesday,
               'wednesday': row.wednesday,
               'thursday': row.thursday,
               'friday': row.friday,
               'saturday': row.saturday,
               'sunday': row.sunday
               }) for i, row in self.fahrplan_dates.iterrows()], ignore_index=True)

        # need to convert the date after using iterows (itertuples might be faster)
        self.fahrplan_dates = None
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y%m%d')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['day'] = fahrplan_dates_all_dates['date'].dt.day_name()

        # set value in column to day if 1 and and compare with day
        fahrplan_dates_all_dates['monday'] = ['Monday' if x == '1' else '-' for x in fahrplan_dates_all_dates['monday']]
        fahrplan_dates_all_dates['tuesday'] = ['Tuesday' if x == '1' else '-' for x in
                                               fahrplan_dates_all_dates['tuesday']]
        fahrplan_dates_all_dates['wednesday'] = ['Wednesday' if x == '1' else '-' for x in
                                                 fahrplan_dates_all_dates['wednesday']]
        fahrplan_dates_all_dates['thursday'] = ['Thursday' if x == '1' else '-' for x in
                                                fahrplan_dates_all_dates['thursday']]
        fahrplan_dates_all_dates['friday'] = ['Friday' if x == '1' else '-' for x in fahrplan_dates_all_dates['friday']]
        fahrplan_dates_all_dates['saturday'] = ['Saturday' if x == '1' else '-' for x in
                                                fahrplan_dates_all_dates['saturday']]
        fahrplan_dates_all_dates['sunday'] = ['Sunday' if x == '1' else '-' for x in fahrplan_dates_all_dates['sunday']]

        fahrplan_dates_all_dates = fahrplan_dates_all_dates.set_index('date')

        # delete exceptions = 2 or add exceptions = 1
        fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_2, locals())
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'],
                                                          format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'],
                                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'],
                                                              format='%Y-%m-%d %H:%M:%S.%f')

        self.fahrplan_dates_all_dates = fahrplan_dates_all_dates

    def dates_select_dates_delete_exception_2(self):
        dfDates = self.dfDates
        dfTrips = self.dfTrips
        dfWeek = self.dfWeek
        dfRoutes = self.dfRoutes
        route_short_namedf = self.route_short_namedf
        varTestAgency = self.varTestAgency
        requested_directiondf = self.requested_directiondf
        requested_datesdf = self.requested_datesdf

        cond_select_dates_delete_exception_2 = '''
                    select  
                            fahrplan_dates_all_dates.date,
                            fahrplan_dates_all_dates.day,
                            fahrplan_dates_all_dates.trip_id,
                            fahrplan_dates_all_dates.service_id,
                            fahrplan_dates_all_dates.route_id, 
                            fahrplan_dates_all_dates.start_date,
                            fahrplan_dates_all_dates.end_date,
                            fahrplan_dates_all_dates.monday,
                            fahrplan_dates_all_dates.tuesday,
                            fahrplan_dates_all_dates.wednesday,
                            fahrplan_dates_all_dates.thursday,
                            fahrplan_dates_all_dates.friday,
                            fahrplan_dates_all_dates.saturday,
                            fahrplan_dates_all_dates.sunday
                    from fahrplan_dates_all_dates 
                    where fahrplan_dates_all_dates.date not in (select dfDates.date 
                                                                  from dfDates                                                            
                                                                    where fahrplan_dates_all_dates.service_id = dfDates.service_id
                                                                      and fahrplan_dates_all_dates.date = dfDates.date 
                                                                      and dfDates.exception_type = 2 
                                                               )
                     and fahrplan_dates_all_dates.date in (select requested_datesdf.date 
                                                                  from requested_datesdf                                                            
                                                                    where fahrplan_dates_all_dates.date = requested_datesdf.date
                                                          )
                     and (   (   fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.monday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.tuesday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.wednesday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.thursday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.friday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.saturday
                              or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.sunday
                             )
                             or 
                             (   fahrplan_dates_all_dates.date in (select dfDates.date
                                                                   from dfDates                                                            
                                                                    where fahrplan_dates_all_dates.service_id = dfDates.service_id 
                                                                      and fahrplan_dates_all_dates.date = dfDates.date
                                                                      and dfDates.exception_type = 1
                                                                  )    
                             )
                        ) 
                    order by fahrplan_dates_all_dates.date;
                   '''

        fahrplan_dates_all_dates = pd.concat(
            [pd.DataFrame
             ({'date': pd.date_range(row.start_date, row.end_date, freq='D'),
               'trip_id': row.trip_id,
               'service_id': row.service_id,
               'route_id': row.route_id,
               'start_date': row.start_date,
               'end_date': row.end_date,
               'monday': row.monday,
               'tuesday': row.tuesday,
               'wednesday': row.wednesday,
               'thursday': row.thursday,
               'friday': row.friday,
               'saturday': row.saturday,
               'sunday': row.sunday
               }) for i, row in self.fahrplan_dates.iterrows()], ignore_index=True)

        # need to convert the date after using iterows (itertuples might be faster)
        self.fahrplan_dates = None
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y%m%d')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['day'] = fahrplan_dates_all_dates['date'].dt.day_name()

        # set value in column to day if 1 and compare with day
        fahrplan_dates_all_dates['monday'] = ['Monday' if x == '1' else '-' for x in fahrplan_dates_all_dates['monday']]
        fahrplan_dates_all_dates['tuesday'] = ['Tuesday' if x == '1' else '-' for x in
                                               fahrplan_dates_all_dates['tuesday']]
        fahrplan_dates_all_dates['wednesday'] = ['Wednesday' if x == '1' else '-' for x in
                                                 fahrplan_dates_all_dates['wednesday']]
        fahrplan_dates_all_dates['thursday'] = ['Thursday' if x == '1' else '-' for x in
                                                fahrplan_dates_all_dates['thursday']]
        fahrplan_dates_all_dates['friday'] = ['Friday' if x == '1' else '-' for x in fahrplan_dates_all_dates['friday']]
        fahrplan_dates_all_dates['saturday'] = ['Saturday' if x == '1' else '-' for x in
                                                fahrplan_dates_all_dates['saturday']]
        fahrplan_dates_all_dates['sunday'] = ['Sunday' if x == '1' else '-' for x in fahrplan_dates_all_dates['sunday']]

        fahrplan_dates_all_dates = fahrplan_dates_all_dates.set_index('date')

        # delete exceptions = 2 or add exceptions = 1
        fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_2, locals())
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'],
                                                          format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'],
                                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'],
                                                              format='%Y-%m-%d %H:%M:%S.%f')

        self.fahrplan_dates_all_dates = fahrplan_dates_all_dates

    def datesWeekday_select_stops_for_trips(self):

        cond_select_stops_for_trips = '''
                    select 
                            (select st_dfStopTimes.arrival_time 
                                from dfStopTimes st_dfStopTimes
                                where st_dfStopTimes.stop_sequence = 0
                                  and dfStopTimes.trip_id = st_dfStopTimes.trip_id) as start_time,                         
                            dfStopTimes.trip_id,
                            dfStops.stop_name,
                            dfStopTimes.stop_sequence, 
                            dfStopTimes.arrival_time, 
                            dfTrip.service_id, 
                            dfStops.stop_id                        
                    from dfStopTimes 
                    inner join dfTrip on dfStopTimes.trip_id = dfTrip.trip_id_dup
                    inner join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                    ;
                   '''
        cond_Test_SequenceStart = '''select st_dfStopTimes.arrival_time 
                                       from dfStopTimes st_dfStopTimes
                                      where st_dfStopTimes.stop_sequence = 0'''

        cond_select_stops_for_tripsOne = '''
                    select 
                            (select st_dfStopTimes.arrival_time 
                                from dfStopTimes st_dfStopTimes
                                where st_dfStopTimes.stop_sequence = 1
                                  and dfStopTimes.trip_id = st_dfStopTimes.trip_id) as start_time,                         
                            dfStopTimes.trip_id,
                            dfStops.stop_name,
                            dfStopTimes.stop_sequence, 
                            dfStopTimes.arrival_time, 
                            dfTrip.service_id, 
                            dfStops.stop_id                        
                    from dfStopTimes 
                    inner join dfTrip on dfStopTimes.trip_id = dfTrip.trip_id_dup
                    inner join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                    ;
                   '''
        route_short_namedf = self.route_short_namedf
        varTestAgency = self.varTestAgency
        requested_directiondf = self.requested_directiondf
        requested_directiondf['direction_id'] = requested_directiondf['direction_id'].astype('string')

        dfRoutes = self.dfRoutes
        dfRoutes = pd.merge(left=dfRoutes, right=route_short_namedf, how='inner', on='route_short_name')
        dfRoutes = pd.merge(left=dfRoutes, right=varTestAgency, how='inner', on='agency_id')
        dfTrip = self.dfTrips
        dfTrip['direction_id'] = dfTrip['direction_id'].astype('string')

        dfTrip['trip_id_dup'] = dfTrip.index
        dfTrip = dfTrip.reset_index(drop=True)
        dfTrip['trip_id_dup'] = dfTrip['trip_id_dup'].astype('string')
        dfTrip = pd.merge(left=dfTrip, right=requested_directiondf, how='inner', on='direction_id')
        # pd.concat([self.dfTrips, self.requested_directiondf], join='inner', keys='direction_id')
        dfTrip = pd.merge(left=dfTrip, right=dfRoutes, how='inner', on='route_id')
        dfStopTimes = self.dfStopTimes
        dfStopTimes['stop_id'] = dfStopTimes.index
        dfStopTimes = dfStopTimes.reset_index(drop=True)
        dfStopTimes['trip_id'] = dfStopTimes['trip_id'].astype('string')
        dfStopTimes = pd.merge(left=dfStopTimes, right=dfTrip, how='inner', left_on='trip_id', right_on='trip_id_dup')
        dfStops = self.dfStops
        last_time = time.time()

        # get all stop_times and stops for every stop of one route
        IsSequenceNumberStartAtZERO = sqldf(cond_Test_SequenceStart, locals())
        if IsSequenceNumberStartAtZERO.empty:
            self.fahrplan_calendar_weeks = sqldf(cond_select_stops_for_tripsOne, locals())
        else:
            self.fahrplan_calendar_weeks = sqldf(cond_select_stops_for_trips, locals())
        dfTrip = dfTrip.drop('trip_id_dup', axis=1)
        zeit = time.time() - last_time
        last_time = time.time()

    def datesWeekday_select_for_every_date_trips_stops(self):

        fahrplan_calendar_weeks = self.fahrplan_calendar_weeks
        fahrplan_dates_all_dates = self.fahrplan_dates_all_dates
        cond_select_for_every_date_trips_stops = '''
                    select  fahrplan_dates_all_dates.date,
                            fahrplan_dates_all_dates.day,
                            fahrplan_calendar_weeks.start_time, 
                            fahrplan_dates_all_dates.trip_id,
                            fahrplan_calendar_weeks.stop_name,
                            fahrplan_calendar_weeks.stop_sequence, 
                            fahrplan_calendar_weeks.arrival_time, 
                            fahrplan_dates_all_dates.service_id, 
                            fahrplan_calendar_weeks.stop_id                        
                    from fahrplan_dates_all_dates 
                    left join fahrplan_calendar_weeks on fahrplan_calendar_weeks.trip_id = fahrplan_dates_all_dates.trip_id             
                    order by fahrplan_dates_all_dates.date, fahrplan_calendar_weeks.stop_sequence, fahrplan_calendar_weeks.start_time, fahrplan_calendar_weeks.trip_id;
                   '''

        # combine dates and trips to get a df with trips for every date
        self.fahrplan_calendar_weeks = sqldf(cond_select_for_every_date_trips_stops, locals())
        self.fahrplan_calendar_weeks['arrival_time'] = self.fahrplan_calendar_weeks['arrival_time'].apply(
            lambda x: self.time_in_string(x))
        self.fahrplan_calendar_weeks['start_time'] = self.fahrplan_calendar_weeks['start_time'].apply(
            lambda x: self.time_in_string(x))

        #########################

    def datesWeekday_select_stop_sequence_stop_name_sorted(self):

        fahrplan_calendar_weeks = self.fahrplan_calendar_weeks
        cond_select_stop_sequence_stop_name_sorted_ = '''
                    select  fahrplan_calendar_weeks.date,
                            fahrplan_calendar_weeks.day,
                            fahrplan_calendar_weeks.start_time,
                            fahrplan_calendar_weeks.arrival_time,
                            fahrplan_calendar_weeks.stop_name,
                            fahrplan_calendar_weeks.stop_sequence,
                            fahrplan_calendar_weeks.stop_id,
                            fahrplan_calendar_weeks.trip_id             
                    from fahrplan_calendar_weeks     
                    order by fahrplan_calendar_weeks.trip_id, fahrplan_calendar_weeks.date, fahrplan_calendar_weeks.stop_sequence;
                   '''
        # group stop_sequence and stop_names, so every stop_name appears only once
        self.fahrplan_sorted_stops = None
        self.fahrplan_sorted_stops = sqldf(cond_select_stop_sequence_stop_name_sorted_, locals())

        # fahrplan_sorted_stops.to_csv('C:Temp/' + 'routeName' + 'nameprefix' + 'pivot_table.csv', header=True, quotechar=' ',
        #                       index=True, sep=';', mode='a', encoding='utf8')

    # tried to get all data in one variable but then I need to create a new index for every dict again
    # maybe I try to get change it later

    def datesWeekday_create_sort_stopnames(self):
        fahrplan_calendar_weeks = self.fahrplan_calendar_weeks
        self.filtered_stop_names = self.filterStopSequence(self.fahrplan_sorted_stops.copy())

        # create new def with filterStopSequence
        self.df_filtered_stop_names = pd.DataFrame.from_dict(self.filtered_stop_names)
        # df_deleted_dupl_stop_names["stop_name"] = df_deleted_dupl_stop_names["stop_name"].astype('string')
        self.df_filtered_stop_names["stop_sequence"] = self.df_filtered_stop_names["stop_sequence"].astype('int32')
        # self.df_filtered_stop_names = self.df_filtered_stop_names.set_index("stop_sequence")
        self.df_filtered_stop_names = self.df_filtered_stop_names.sort_index(axis=0)

    def datesWeekday_create_fahrplan_continue(self):
        cond_stop_name_sorted_trips_with_dates = '''
                    select  fahrplan_calendar_weeks.date,
                            fahrplan_calendar_weeks.day,
                            fahrplan_calendar_weeks.start_time, 
                            fahrplan_calendar_weeks.trip_id,
                            fahrplan_calendar_weeks.stop_name,
                            df_filtered_stop_names.stop_sequence as stop_sequence_sorted,
                            fahrplan_calendar_weeks.stop_sequence,
                            fahrplan_calendar_weeks.arrival_time, 
                            fahrplan_calendar_weeks.service_id, 
                            fahrplan_calendar_weeks.stop_id                        
                    from fahrplan_calendar_weeks 
                    left join df_filtered_stop_names on fahrplan_calendar_weeks.stop_id = df_filtered_stop_names.stop_id  
                    group by fahrplan_calendar_weeks.date,
                             fahrplan_calendar_weeks.day,
                             fahrplan_calendar_weeks.start_time,
                             fahrplan_calendar_weeks.arrival_time, 
                             fahrplan_calendar_weeks.trip_id,
                             fahrplan_calendar_weeks.stop_name,
                             stop_sequence_sorted,
                             fahrplan_calendar_weeks.stop_sequence,
                             fahrplan_calendar_weeks.service_id,
                             fahrplan_calendar_weeks.stop_id
    
                    order by fahrplan_calendar_weeks.date,
                             fahrplan_calendar_weeks.stop_sequence,
                             fahrplan_calendar_weeks.start_time,
                             fahrplan_calendar_weeks.trip_id;
                   '''
        fahrplan_calendar_weeks = self.fahrplan_calendar_weeks
        df_filtered_stop_names = self.df_filtered_stop_names

        fahrplan_calendar_weeks = sqldf(cond_stop_name_sorted_trips_with_dates, locals())

        ###########################

        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype('int32')
        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].astype('string')
        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].astype('string')

        # fahrplan_calendar_weeks = fahrplan_calendar_weeks.drop(columns=['stop_sequence', 'service_id', 'stop_id'])
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.drop(columns=['stop_sequence', 'service_id'])
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.groupby(
            ['date', 'day', 'stop_sequence_sorted', 'stop_name', 'stop_id', 'start_time',
             'trip_id']).first().reset_index()

        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d')
        # fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype('int32')

        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].astype('string')
        if self.timeformat == 1:
            fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].apply(
                lambda x: self.time_delete_seconds(x))

        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].astype('string')

        self.fahrplan_calendar_filter_days_pivot = fahrplan_calendar_weeks.pivot(
            index=['date', 'day', 'stop_sequence_sorted', 'stop_name', 'stop_id'], columns=['start_time', 'trip_id'],
            values='arrival_time')

        # fahrplan_calendar_filter_days_pivot['date'] = pd.to_datetime(fahrplan_calendar_filter_days_pivot['date'], format='%Y-%m-%d %H:%M:%S.%f')
        self.fahrplan_calendar_filter_days_pivot = self.fahrplan_calendar_filter_days_pivot.sort_index(axis=1)
        self.fahrplan_calendar_filter_days_pivot = self.fahrplan_calendar_filter_days_pivot.sort_index(axis=0)

        self.zeit = time.time() - self.last_time
        now = datetime.now()
        self.now = now.strftime("%Y_%m_%d_%H_%M_%S")

    def datesWeekday_create_fahrplan(self):

        cond_stop_name_sorted_trips_with_dates = '''
                    select  fahrplan_calendar_weeks.date,
                            fahrplan_calendar_weeks.day,
                            fahrplan_calendar_weeks.start_time, 
                            fahrplan_calendar_weeks.trip_id,
                            fahrplan_calendar_weeks.stop_name,
                            df_filtered_stop_names.stop_sequence as stop_sequence_sorted,
                            fahrplan_calendar_weeks.stop_sequence,
                            fahrplan_calendar_weeks.arrival_time, 
                            fahrplan_calendar_weeks.service_id, 
                            fahrplan_calendar_weeks.stop_id                        
                    from fahrplan_calendar_weeks 
                    left join df_filtered_stop_names on fahrplan_calendar_weeks.stop_id = df_filtered_stop_names.stop_id  
                    group by fahrplan_calendar_weeks.date,
                             fahrplan_calendar_weeks.day,
                             fahrplan_calendar_weeks.start_time,
                             fahrplan_calendar_weeks.arrival_time, 
                             fahrplan_calendar_weeks.trip_id,
                             fahrplan_calendar_weeks.stop_name,
                             stop_sequence_sorted,
                             fahrplan_calendar_weeks.stop_sequence,
                             fahrplan_calendar_weeks.service_id,
                             fahrplan_calendar_weeks.stop_id
    
                    order by fahrplan_calendar_weeks.date,
                             fahrplan_calendar_weeks.stop_sequence,
                             fahrplan_calendar_weeks.start_time,
                             fahrplan_calendar_weeks.trip_id;
                   '''

        fahrplan_calendar_weeks = self.fahrplan_calendar_weeks
        self.fahrplan_calendar_weeks = None
        self.filtered_stop_names = self.filterStopSequence(self.fahrplan_sorted_stops)

        """
        
        create new def with filterStopSequence
        
        """

        self.df_filtered_stop_names = pd.DataFrame.from_dict(self.filtered_stop_names)
        # df_deleted_dupl_stop_names["stop_name"] = df_deleted_dupl_stop_names["stop_name"].astype('string')
        self.df_filtered_stop_names["stop_sequence"] = self.df_filtered_stop_names["stop_sequence"].astype('int32')
        # self.df_filtered_stop_names = self.df_filtered_stop_names.set_index("stop_sequence")
        self.df_filtered_stop_names = self.df_filtered_stop_names.sort_index(axis=0)
        df_filtered_stop_names = self.df_filtered_stop_names

        fahrplan_calendar_weeks = sqldf(cond_stop_name_sorted_trips_with_dates, locals())

        ###########################

        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype('int32')
        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].astype('string')
        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].astype('string')

        # fahrplan_calendar_weeks = fahrplan_calendar_weeks.drop(columns=['stop_sequence', 'service_id', 'stop_id'])
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.drop(columns=['stop_sequence', 'service_id'])
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.groupby(
            ['date', 'day', 'stop_sequence_sorted', 'stop_name', 'stop_id', 'start_time',
             'trip_id']).first().reset_index()

        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d')
        # fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype('int32')

        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].astype('string')
        if self.timeformat == 1:
            fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].apply(
                lambda x: self.time_delete_seconds(x))

        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].astype('string')

        self.fahrplan_calendar_filter_days_pivot = fahrplan_calendar_weeks.pivot(
            index=['date', 'day', 'stop_sequence_sorted', 'stop_name', 'stop_id'], columns=['start_time', 'trip_id'],
            values='arrival_time')

        # fahrplan_calendar_filter_days_pivot['date'] = pd.to_datetime(fahrplan_calendar_filter_days_pivot['date'], format='%Y-%m-%d %H:%M:%S.%f')
        self.fahrplan_calendar_filter_days_pivot = self.fahrplan_calendar_filter_days_pivot.sort_index(axis=1)
        self.fahrplan_calendar_filter_days_pivot = self.fahrplan_calendar_filter_days_pivot.sort_index(axis=0)

        self.zeit = time.time() - self.last_time
        now = datetime.now()
        self.now = now.strftime("%Y_%m_%d_%H_%M_%S")



