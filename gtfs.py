# -*- coding: utf-8 -*-

import time
import pandas as pd
from pandasql import sqldf
import zipfile
import io
from datetime import datetime, timedelta
import re


# noinspection SqlResolve
class gtfs:
    input_path: str
    output_path: str
    gtfs_data_list: list[list[str]]
    options_dates_weekday: list[str]
    selected_direction: int
    runningAsync: int

    def __init__(self):
        self.noError = False
        self.input_path = ""
        self.output_path = ""
        self.progress = 0
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
        self.time = None
        self.processing = None
        self.runningAsync = 0

        """ dicts for create and listbox """
        self.stopsdict = None
        self.stopTimesdict = None
        self.tripdict = None
        self.calendarWeekdict = None
        self.calendarDatesdict = None
        self.routesFahrtdict = None
        self.agencyFahrtdict = None

        """ loaded raw_gtfs_data """
        self.raw_gtfs_data = None

        """ df-data """
        self.dfStops = None
        self.dfStopTimes = None
        self.dfTrips = None
        self.dfWeek = None
        self.dfDates = None
        self.dfRoutes = None
        self.dfagency = None
        self.now = None

        # self.stops_df = None
        # self.stopTimes_df = None
        # self.trip_df = None
        # self.calendarWeek_df = None
        # self.calendarDates_df = None
        # self.routesFahrt_df = None
        # self.agencyFahrt_df = None

        """ loaded data for listbox """
        self.agenciesList = None
        self.routesList = None
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
        # dataframe with requested data
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

    # loads data from zip
    def async_task_load_GTFS_data(self) -> bool:
        return self.import_gtfs()

    # import routine and
    def import_gtfs(self) -> bool:
        self.processing = "import_gtfs started"
        print('import_gtfs')
        if self.read_paths() is True:
            if self.read_gtfs_data() is True:
                self.noError = self.read_gtfs_data_from_path()
        if self.noError is True:
            self.noError = self.create_dfs()
        if self.noError is True:
            self.noError = self.cleandicts()
        return self.noError

    def set_paths(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path



    def get_routes_of_agency(self) -> None:
        if self.selectedAgency is not None:
            self.select_gtfs_routes_from_agency()

    def set_routes(self, route) -> None:
        self.selectedRoute = route

    def create_dfs(self):

        last_time = time.time()

        # DataFrame for every route
        self.dfRoutes = pd.DataFrame.from_dict(self.routesFahrtdict).set_index(['route_id', 'agency_id'])

        # DataFrame with every trip
        self.dfTrips = pd.DataFrame.from_dict(self.tripdict).set_index('trip_id')

        try:
            # dfTrips['trip_id'] = pd.to_numeric(dfTrips['trip_id'])
            self.dfTrips['trip_id'] = self.dfTrips['trip_id'].astype('int32')
        except KeyError:
            print("can not convert dfTrips: trip_id into int")

        # DataFrame with every stop (time)
        self.dfStopTimes = pd.DataFrame.from_dict(self.stopTimesdict).set_index(['trip_id', 'stop_id'])
        try:
            self.dfStopTimes['arrival_time'] = self.dfStopTimes['arrival_time'].apply(lambda x: self.time_in_string(x))
            self.dfStopTimes['arrival_time'] = self.dfStopTimes['arrival_time'].astype('string')
        except KeyError:
            print("can not convert dfStopTimes: arrival_time into string and change time")

        try:
            self.dfStopTimes['stop_sequence'] = self.dfStopTimes['stop_sequence'].astype('int32')
        except KeyError:
            print("can not convert dfStopTimes: stop_sequence into int")
        try:
            self.dfStopTimes['stop_id'] = self.dfStopTimes['stop_id'].astype('int32')
        except KeyError:
            print("can not convert dfStopTimes: stop_id into int")
        except OverflowError:
            print("can not convert dfStopTimes: stop_id into int")
        try:
            self.dfStopTimes['trip_id'] = self.dfStopTimes['trip_id'].astype('int32')
        except KeyError:
            print("can not convert dfStopTimes: trip_id into int")

        # DataFrame with every stop
        self.dfStops = pd.DataFrame.from_dict(self.stopsdict).set_index('stop_id')
        try:
            self.dfStops['stop_id'] = self.dfStops['stop_id'].astype('int32')
        except KeyError:
            print("can not convert dfStops: stop_id into int ")

        # DataFrame with every service weekly
        self.dfWeek = pd.DataFrame.from_dict(self.calendarWeekdict).set_index('service_id')

        # DataFrame with every service dates
        self.dfDates = pd.DataFrame.from_dict(self.calendarDatesdict).set_index('service_id')
        self.dfDates['exception_type'] = self.dfDates['exception_type'].astype('int32')
        self.dfDates['date'] = pd.to_datetime(self.dfDates['date'], format='%Y%m%d')

        # DataFrame with every agency
        self.dfagency = pd.DataFrame.from_dict(self.agencyFahrtdict).set_index('agency_id')

        zeit = time.time() - last_time
        print("time: {} ".format(zeit))

        return True

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
        stopsequence = {}
        sorted_stopsequence = {
            "stop_id": [],
            "stop_sequence": [],
            "start_time": []
        }

        for stop_name_i in data.itertuples():
            # check for stop_id not for stop_name!
            if not self.dictForEntry(stopsequence, "stop_id", stop_name_i.stop_id):
                temp = {"stop_sequence": -1, "stop_name": '', "trip_id": '', "start_time": '', "arrival_time": ''}
                temp["stop_sequence"] = stop_name_i.stop_sequence
                temp["stop_name"] = stop_name_i.stop_name
                temp["trip_id"] = stop_name_i.trip_id

                if self.check_hour_24(stop_name_i.start_time):
                    comparetime_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime(
                        '%Y-%m-%d'))) + ' 0' + str(int(stop_name_i.start_time.split(':')[0]) - 24) + ':' + \
                                    stop_name_i.start_time.split(':')[1]
                    time_i = datetime.strptime(comparetime_i, '%Y-%m-%d %H:%M')
                    time_i = time_i + timedelta(days=1)
                else:
                    comparetime_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime(
                        '%Y-%m-%d'))) + ' ' + stop_name_i.start_time
                    time_i = datetime.strptime(comparetime_i, '%Y-%m-%d %H:%M')

                if self.check_hour_24(stop_name_i.arrival_time):
                    time_arrival_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime(
                        '%Y-%m-%d'))) + ' 0' + str(int(stop_name_i.arrival_time.split(':')[0]) - 24) + ':' + \
                                     stop_name_i.arrival_time.split(':')[1]
                    time_arrival_i = datetime.strptime(time_arrival_i, '%Y-%m-%d %H:%M')
                    time_arrival_i = time_arrival_i + timedelta(days=1)
                else:
                    time_arrival_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime(
                        '%Y-%m-%d'))) + ' ' + stop_name_i.arrival_time
                    time_arrival_i = datetime.strptime(time_arrival_i, '%Y-%m-%d %H:%M')

                temp["start_time"] = time_i
                temp["arrival_time"] = time_arrival_i

                # search in data and compare the ids
                for stop_name_j in data.itertuples():
                    # if ids match continue comparison
                    if self.sortmode == 1:
                        if stop_name_i.stop_id == stop_name_j.stop_id:

                            if self.check_hour_24(stop_name_j.start_time):
                                comparetime_j = str((datetime.strptime(stop_name_j.date,
                                                                       '%Y-%m-%d %H:%M:%S.%f').strftime(
                                    '%Y-%m-%d'))) + ' 0' + str(int(stop_name_j.start_time.split(':')[0]) - 24) + ':' + \
                                                stop_name_j.start_time.split(':')[1]
                                time_j = datetime.strptime(comparetime_j, '%Y-%m-%d %H:%M')
                                time_j = time_j + timedelta(days=1)
                            else:
                                comparetime_j = str((datetime.strptime(stop_name_j.date,
                                                                       '%Y-%m-%d %H:%M:%S.%f').strftime(
                                    '%Y-%m-%d'))) + ' ' + stop_name_j.start_time
                                time_j = datetime.strptime(comparetime_j, '%Y-%m-%d %H:%M')

                            time_temp = temp["start_time"]

                            if self.check_hour_24(stop_name_j.arrival_time):
                                time_arrival_j = str((datetime.strptime(stop_name_j.date,
                                                                        '%Y-%m-%d %H:%M:%S.%f').strftime(
                                    '%Y-%m-%d'))) + ' 0' + str(int(stop_name_j.arrival_time.split(':')[0]) - 24) + ':' + \
                                                 stop_name_j.arrival_time.split(':')[1]
                                time_arrival_j = datetime.strptime(time_arrival_j, '%Y-%m-%d %H:%M')
                                time_arrival_j = time_arrival_j + timedelta(days=1)
                            else:
                                time_arrival_j = str((datetime.strptime(stop_name_j.date,
                                                                        '%Y-%m-%d %H:%M:%S.%f').strftime(
                                    '%Y-%m-%d'))) + ' ' + stop_name_j.arrival_time
                                time_arrival_j = datetime.strptime(time_arrival_j, '%Y-%m-%d %H:%M')

                            arrival_time_temp = temp["arrival_time"]

                            # if time_j < time_i \
                            # and time_j < time_temp \
                            # and time_arrival_j < time_arrival_i \
                            # and time_arrival_j < arrival_time_temp\
                            # and stop_name_j.stop_sequence > stop_name_i.stop_sequence:
                            if time_j < time_i \
                                    and time_j < time_temp \
                                    and stop_name_j.stop_sequence > stop_name_i.stop_sequence \
                                    and stop_name_j.stop_sequence > temp["stop_sequence"]:
                                temp["start_time"] = time_j
                                temp["arrival_time"] = time_arrival_j
                                # temp["arrival_time"] = stop_name_j.arrival_time
                                temp["stop_sequence"] = stop_name_j.stop_sequence
                    else:
                        if stop_name_i.stop_id == stop_name_j.stop_id \
                                and stop_name_i.trip_id == stop_name_j.trip_id:

                            if self.check_hour_24(stop_name_j.start_time):
                                comparetime_j = str((datetime.strptime(stop_name_j.date,
                                                                       '%Y-%m-%d %H:%M:%S.%f').strftime(
                                    '%Y-%m-%d'))) + ' 0' + str(
                                    int(stop_name_j.start_time.split(':')[0]) - 24) + ':' + \
                                                stop_name_j.start_time.split(':')[1]
                                time_j = datetime.strptime(comparetime_j, '%Y-%m-%d %H:%M')
                                time_j = time_j + timedelta(days=1)
                            else:
                                comparetime_j = str((datetime.strptime(stop_name_j.date,
                                                                       '%Y-%m-%d %H:%M:%S.%f').strftime(
                                    '%Y-%m-%d'))) + ' ' + stop_name_j.start_time
                                time_j = datetime.strptime(comparetime_j, '%Y-%m-%d %H:%M')

                            time_temp = temp["start_time"]

                            if self.check_hour_24(stop_name_j.arrival_time):
                                time_arrival_j = str((datetime.strptime(stop_name_j.date,
                                                                        '%Y-%m-%d %H:%M:%S.%f').strftime(
                                    '%Y-%m-%d'))) + ' 0' + str(
                                    int(stop_name_j.arrival_time.split(':')[0]) - 24) + ':' + \
                                                 stop_name_j.arrival_time.split(':')[1]
                                time_arrival_j = datetime.strptime(time_arrival_j, '%Y-%m-%d %H:%M')
                                time_arrival_j = time_arrival_j + timedelta(days=1)
                            else:
                                time_arrival_j = str((datetime.strptime(stop_name_j.date,
                                                                        '%Y-%m-%d %H:%M:%S.%f').strftime(
                                    '%Y-%m-%d'))) + ' ' + stop_name_j.arrival_time
                                time_arrival_j = datetime.strptime(time_arrival_j, '%Y-%m-%d %H:%M')

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

        print(self.sortmode)

        new_stopsequence = self.sortStopSequence(stopsequence)

        for stop_sequence in new_stopsequence.keys():
            sorted_stopsequence['stop_id'].append(new_stopsequence[stop_sequence]['stop_id'])
            sorted_stopsequence['stop_sequence'].append(stop_sequence)
            sorted_stopsequence['start_time'].append(new_stopsequence[stop_sequence]['start_time'])

        #
        # print('len stop_sequences {}'.format(sequence_count))
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
        # print(stopsequence)
        # i = 0
        # for sequence in range(0, len(temp["stop_sequence"])):
        #     i += 1
        #     temp["stop_sequence"][sequence] = i

        return sorted_stopsequence

    def sortStopSequence(self, stopsequence):

        # get all possible stops
        sequence_count = len(stopsequence)

        # init data structure
        d = {}
        for k in range(sequence_count):
            d[str(k)] = {"start_time": datetime.strptime('1901-01-01 23:59', '%Y-%m-%d %H:%M').time(),
                         "arrival_time": datetime.strptime('1901-01-01 23:59', '%Y-%m-%d %H:%M').time(),
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
                    if d[str(j)]["arrival_time"] > d[str(j + 1)]["arrival_time"]:
                        d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
                    elif d[str(j)]["stop_sequence"] > d[str(j + 1)]["stop_sequence"] \
                            and d[str(j)]["start_time"] > d[str(j + 1)]["start_time"]:
                        d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
                    elif d[str(j)]["stop_sequence"] == d[str(j + 1)]["stop_sequence"]:
                        if d[str(j)]["start_time"] > d[str(j + 1)]["start_time"] \
                                and d[str(j)]["arrival_time"] > d[str(j + 1)]["arrival_time"]:
                            d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
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
            return '0' + time[:-3]
        else:
            return time[:-3]

    # checks if date string
    def check_dates_input(self, dates):
        pattern1 = re.findall('^\d{8}(?:\d{8})*(?:,\d{8})*$', dates)
        if pattern1:
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
            print(time)

    # read zip-data
    def read_gtfs_data(self):
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
            return False
        self.raw_gtfs_data = [stopsList, stopTimesList, tripsList, calendarList, calendar_datesList, routesList,
                              agencyList]
        return True

    def get_gtfs_trip(self):
        tripdict = {
            "route_id": [],
            "service_id": [],
            "trip_id": [],
            "trip_headsign": [],
            "trip_short_name": [],
            "direction_id": [],
            "block_id": [],
            "shape_id": [],
            "wheelchair_accessible": [],
            "bikes_allowed": []
        }
        for trip in self.raw_gtfs_data[2]:
            trip = trip.replace(", ", " ")
            trip = trip.replace('"', "")
            trip = trip.replace('\n', "")
            data = trip.split(",")
            idata = len(data)
            if idata > 9:
                tripdict["route_id"].append(data[0])
                tripdict["service_id"].append(data[1])
                tripdict["trip_id"].append(data[2])
                tripdict["trip_headsign"].append(data[3])
                tripdict["trip_short_name"].append(data[4])
                tripdict["direction_id"].append(data[5])
                tripdict["block_id"].append(data[6])
                tripdict["shape_id"].append(data[7])
                tripdict["wheelchair_accessible"].append(data[8])
                tripdict["bikes_allowed"].append(data[9])
            else:
                tripdict["route_id"].append(data[0])
                tripdict["service_id"].append(data[1])
                tripdict["trip_id"].append(data[2])
                tripdict["shape_id"].append(data[3])
                tripdict["trip_headsign"].append(data[4])
                tripdict["trip_short_name"].append(data[5])
                tripdict["direction_id"].append(data[6])
                tripdict["wheelchair_accessible"].append(data[7])
                tripdict["block_id"].append('')
                tripdict["bikes_allowed"].append('')
        self.tripdict = tripdict
        return True

    def get_gtfs_stop(self):

        stopsdict = {
            "stop_id": [],
            "stop_code": [],
            "stop_name": [],
            "stop_desc": [],
            "stop_lat": [],
            "stop_lon": [],
            "location_type": [],
            "parent_station": [],
            "wheelchair_accessible": [],
            "platform_code": [],
            "zone_id": []
        }
        for haltestellen in self.raw_gtfs_data[0]:
            haltestellen = haltestellen.replace(", ", " ")
            haltestellen = haltestellen.replace('"', "")
            haltestellen = haltestellen.replace('\n', "")
            stopData = haltestellen.split(",")
            istopDate = len(stopData)

            stopsdict["stop_id"].append(stopData[0])
            stopsdict["stop_code"].append(stopData[1])
            stopsdict["stop_name"].append(stopData[2])
            stopsdict["stop_desc"].append(stopData[3])
            stopsdict["stop_lat"].append(stopData[4])
            stopsdict["stop_lon"].append(stopData[5])
            stopsdict["location_type"].append(stopData[6])
            stopsdict["parent_station"].append(stopData[7])
            stopsdict["wheelchair_accessible"].append(stopData[8])
            stopsdict["platform_code"].append(stopData[9])
            if istopDate > 10:
                stopsdict["zone_id"].append(stopData[10])
            else:
                stopsdict["zone_id"].append('')

        self.stopsdict = stopsdict
        return True

    def get_gtfs_stoptime(self):
        stopTimesdict = {
            "trip_id": [],
            "arrival_time": [],
            "departure_time": [],
            "stop_id": [],
            "stop_sequence": [],
            "pickup_type": [],
            "drop_off_type": [],
            "stop_headsign": [],
            "shape_dist_traveled": []
        }
        for stopTime in self.raw_gtfs_data[1]:
            stopTime = stopTime.replace(", ", " ")
            stopTime = stopTime.replace('"', "")
            stopTime = stopTime.replace('\n', "")
            stopTimeData = stopTime.split(",")
            istopTimeData = len(stopTimeData)
            if istopTimeData == 8:
                stopTimesdict["trip_id"].append(stopTimeData[0])
                stopTimesdict["arrival_time"].append(stopTimeData[1])
                stopTimesdict["departure_time"].append(stopTimeData[2])
                stopTimesdict["stop_id"].append(stopTimeData[3])
                stopTimesdict["stop_sequence"].append(stopTimeData[4])
                stopTimesdict["pickup_type"].append(stopTimeData[5])
                stopTimesdict["drop_off_type"].append(stopTimeData[6])
                stopTimesdict["stop_headsign"].append(stopTimeData[7])
                stopTimesdict["shape_dist_traveled"].append('')
            else:
                stopTimesdict["trip_id"].append(stopTimeData[0])
                stopTimesdict["arrival_time"].append(stopTimeData[1])
                stopTimesdict["departure_time"].append(stopTimeData[2])
                stopTimesdict["stop_id"].append(stopTimeData[3])
                stopTimesdict["stop_sequence"].append(str(int(stopTimeData[4]) - 1))
                stopTimesdict["stop_headsign"].append(stopTimeData[5])
                stopTimesdict["pickup_type"].append(stopTimeData[6])
                stopTimesdict["drop_off_type"].append(stopTimeData[7])
                stopTimesdict["shape_dist_traveled"].append(stopTimeData[8])

        self.stopTimesdict = stopTimesdict
        return True

    def get_gtfs_calendarWeek(self):
        calendarWeekdict = {
            "service_id": [],
            "monday": [],
            "tuesday": [],
            "wednesday": [],
            "thursday": [],
            "friday": [],
            "saturday": [],
            "sunday": [],
            "start_date": [],
            "end_date": []
        }
        for calendarDate in self.raw_gtfs_data[3]:
            calendarDate = calendarDate.replace(", ", " ")
            calendarDate = calendarDate.replace('"', "")
            calendarDate = calendarDate.replace('\n', "")
            calendarData = calendarDate.split(",")
            calendarWeekdict["service_id"].append(calendarData[0])
            calendarWeekdict["monday"].append(calendarData[1])
            calendarWeekdict["tuesday"].append(calendarData[2])
            calendarWeekdict["wednesday"].append(calendarData[3])
            calendarWeekdict["thursday"].append(calendarData[4])
            calendarWeekdict["friday"].append(calendarData[5])
            calendarWeekdict["saturday"].append(calendarData[6])
            calendarWeekdict["sunday"].append(calendarData[7])
            calendarWeekdict["start_date"].append(calendarData[8])
            calendarWeekdict["end_date"].append(calendarData[9])

        self.calendarWeekdict = calendarWeekdict
        return True

    def get_gtfs_calendarDates(self):
        calendarDatesdict = {
            "service_id": [],
            "date": [],
            "exception_type": [],
        }
        for calendarDate in self.raw_gtfs_data[4]:
            calendarDate = calendarDate.replace(", ", " ")
            calendarDate = calendarDate.replace('"', "")
            calendarDate = calendarDate.replace('\n', "")
            calendarDatesData = calendarDate.split(",")
            calendarDatesdict["service_id"].append(calendarDatesData[0])
            calendarDatesdict["date"].append(calendarDatesData[1])
            calendarDatesdict["exception_type"].append(calendarDatesData[2])

        self.calendarDatesdict = calendarDatesdict
        return True

    def get_gtfs_routes(self):
        routesFahrtdict = {
            "route_id": [],
            "agency_id": [],
            "route_short_name": [],
            "route_long_name": [],
            "route_type": [],
            "route_color": [],
            "route_text_color": [],
            "route_desc": []
        }
        for routes in self.raw_gtfs_data[5]:
            routes = routes.replace(", ", " ")
            routes = routes.replace('"', "")
            routes = routes.replace('\n', "")
            routesData = routes.split(",")
            iroutesDate = len(routesData)
            if iroutesDate > 7:
                routesFahrtdict["route_id"].append(routesData[0])
                routesFahrtdict["agency_id"].append(routesData[1])
                routesFahrtdict["route_short_name"].append(routesData[2])
                routesFahrtdict["route_long_name"].append(routesData[3])
                routesFahrtdict["route_type"].append(routesData[4])
                routesFahrtdict["route_color"].append(routesData[5])
                routesFahrtdict["route_text_color"].append(routesData[6])
                routesFahrtdict["route_desc"].append(routesData[7])
            else:
                routesFahrtdict["route_id"].append(routesData[0])
                routesFahrtdict["agency_id"].append(routesData[1])
                routesFahrtdict["route_short_name"].append(routesData[2])
                routesFahrtdict["route_long_name"].append(routesData[3])
                routesFahrtdict["route_type"].append(routesData[4])
                routesFahrtdict["route_color"].append(routesData[5])
                routesFahrtdict["route_text_color"].append(routesData[6])
                routesFahrtdict["route_desc"].append('')

        self.routesFahrtdict = routesFahrtdict
        return True

    def get_gtfs_agencies(self):

        agencyFahrtdict = {
            "agency_id": [],
            "agency_name": [],
            "agency_url": [],
            "agency_timezone": [],
            "agency_lang": [],
            "agency_phone": [],
            "agency_fare_url": [],
            "agency_email": []
        }
        for agency in self.raw_gtfs_data[6]:
            agency = agency.replace(", ", " ")
            agency = agency.replace('"', "")
            agency = agency.replace('\n', "")
            agencyData = agency.split(",")
            iagencyData = len(agencyData)
            if iagencyData == 6:
                agencyFahrtdict["agency_id"].append(agencyData[0])
                agencyFahrtdict["agency_name"].append(agencyData[1])
                agencyFahrtdict["agency_url"].append(agencyData[2])
                agencyFahrtdict["agency_timezone"].append(agencyData[3])
                agencyFahrtdict["agency_lang"].append(agencyData[4])
                agencyFahrtdict["agency_phone"].append(agencyData[5])
                agencyFahrtdict["agency_fare_url"].append('')
                agencyFahrtdict["agency_email"].append('')
            else:
                agencyFahrtdict["agency_id"].append(agencyData[0])
                agencyFahrtdict["agency_name"].append(agencyData[1])
                agencyFahrtdict["agency_url"].append(agencyData[2])
                agencyFahrtdict["agency_timezone"].append(agencyData[3])
                agencyFahrtdict["agency_lang"].append(agencyData[4])
                agencyFahrtdict["agency_phone"].append(agencyData[5])
                agencyFahrtdict["agency_fare_url"].append(agencyData[6])
                agencyFahrtdict["agency_email"].append(agencyData[7])

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
        self.raw_gtfs_data = None
        return True

    def select_gtfs_routes_from_agency(self):
        dfRoutes = self.dfRoutes
        inputVar = [{'agency_id': self.selectedAgency}]
        varTest = pd.DataFrame(inputVar).set_index('agency_id')
        cond_routes_of_agency = '''
                    select dfRoutes.route_id, dfRoutes.route_short_name
                    from dfRoutes 
                    left join varTest
                    where varTest.agency_id = dfRoutes.agency_id
                    order by dfRoutes.route_short_name;
                   '''
        routes_list = sqldf(cond_routes_of_agency, locals())
        routes_list = routes_list.values.tolist()
        routes_str_list = []
        for lists in routes_list:
            routes_str_list.append('{},{}'.format(lists[0], lists[1]))
        self.routesList = routes_str_list
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
            print('dfWeek service_id: can not convert into int')

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
                    select dfagency.agency_id, dfagency.agency_name
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

    def datesWeekday_select_dates_for_date_range(self):
        # conditions for searching in dfs
        dfTrips = self.dfTrips
        dfWeek = self.dfWeek
        dfRoutes = self.dfRoutes
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
                            route_id, 
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

        fahrplan_dates_all_dates['monday'] = ['Monday' if x == '1' else '-' for x in fahrplan_dates_all_dates['monday']]
        fahrplan_dates_all_dates['tuesday'] = ['Tuesday' if x == '1' else '-' for x  in fahrplan_dates_all_dates['tuesday']]
        fahrplan_dates_all_dates['wednesday'] = ['Wednesday' if x == '1' else '-' for x  in fahrplan_dates_all_dates['wednesday']]
        fahrplan_dates_all_dates['thursday'] = ['Thursday' if x == '1' else '-' for x  in fahrplan_dates_all_dates['thursday']]
        fahrplan_dates_all_dates['friday'] = ['Friday' if x == '1' else '-' for x  in fahrplan_dates_all_dates['friday']]
        fahrplan_dates_all_dates['saturday'] = ['Saturday' if x == '1' else '-' for x  in fahrplan_dates_all_dates['saturday']]
        fahrplan_dates_all_dates['sunday'] = ['Sunday' if x == '1' else '-' for x  in fahrplan_dates_all_dates['sunday']]
        # set value in column to day if 1 and and compare with day
        # fahrplan_dates_all_dates['monday'] = fahrplan_dates_all_dates['monday'].apply(
        #     lambda x: 'Monday' if x == '1' else '-')
        # fahrplan_dates_all_dates['tuesday'] = fahrplan_dates_all_dates['tuesday'].apply(
        #     lambda x: 'Tuesday' if x == '1' else '-')
        # fahrplan_dates_all_dates['wednesday'] = fahrplan_dates_all_dates['wednesday'].apply(
        #     lambda x: 'Wednesday' if x == '1' else '-')
        # fahrplan_dates_all_dates['thursday'] = fahrplan_dates_all_dates['thursday'].apply(
        #     lambda x: 'Thursday' if x == '1' else '-')
        # fahrplan_dates_all_dates['friday'] = fahrplan_dates_all_dates['friday'].apply(
        #     lambda x: 'Friday' if x == '1' else '-')
        # fahrplan_dates_all_dates['saturday'] = fahrplan_dates_all_dates['saturday'].apply(
        #     lambda x: 'Saturday' if x == '1' else '-')
        # fahrplan_dates_all_dates['sunday'] = fahrplan_dates_all_dates['sunday'].apply(
        #     lambda x: 'Sunday' if x == '1' else '-')
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
        print(f'requested_directiondf: {requested_directiondf}')

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
        last_time = time.time()

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

        zeit = time.time() - last_time
        print("time: {} ".format(zeit))
        last_time = time.time()

        # need to convert the date after using iterows (itertuples might be faster)
        self.fahrplan_dates = None
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y%m%d')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['day'] = fahrplan_dates_all_dates['date'].dt.day_name()

        fahrplan_dates_all_dates['monday'] = ['Monday' if x == '1' else '-' for x in fahrplan_dates_all_dates['monday']]
        fahrplan_dates_all_dates['tuesday'] = ['Tuesday' if x == '1' else '-' for x  in fahrplan_dates_all_dates['tuesday']]
        fahrplan_dates_all_dates['wednesday'] = ['Wednesday' if x == '1' else '-' for x  in fahrplan_dates_all_dates['wednesday']]
        fahrplan_dates_all_dates['thursday'] = ['Thursday' if x == '1' else '-' for x  in fahrplan_dates_all_dates['thursday']]
        fahrplan_dates_all_dates['friday'] = ['Friday' if x == '1' else '-' for x  in fahrplan_dates_all_dates['friday']]
        fahrplan_dates_all_dates['saturday'] = ['Saturday' if x == '1' else '-' for x  in fahrplan_dates_all_dates['saturday']]
        fahrplan_dates_all_dates['sunday'] = ['Sunday' if x == '1' else '-' for x  in fahrplan_dates_all_dates['sunday']]


        # set value in column to day if 1 and and compare with day
        # fahrplan_dates_all_dates['monday'] = fahrplan_dates_all_dates['monday'].apply(
        #     lambda x: 'Monday' if x == '1' else '-')
        # fahrplan_dates_all_dates['tuesday'] = fahrplan_dates_all_dates['tuesday'].apply(
        #     lambda x: 'Tuesday' if x == '1' else '-')
        # fahrplan_dates_all_dates['wednesday'] = fahrplan_dates_all_dates['wednesday'].apply(
        #     lambda x: 'Wednesday' if x == '1' else '-')
        # fahrplan_dates_all_dates['thursday'] = fahrplan_dates_all_dates['thursday'].apply(
        #     lambda x: 'Thursday' if x == '1' else '-')
        # fahrplan_dates_all_dates['friday'] = fahrplan_dates_all_dates['friday'].apply(
        #     lambda x: 'Friday' if x == '1' else '-')
        # fahrplan_dates_all_dates['saturday'] = fahrplan_dates_all_dates['saturday'].apply(
        #     lambda x: 'Saturday' if x == '1' else '-')
        # fahrplan_dates_all_dates['sunday'] = fahrplan_dates_all_dates['sunday'].apply(
        #     lambda x: 'Sunday' if x == '1' else '-')
        fahrplan_dates_all_dates = fahrplan_dates_all_dates.set_index('date')

        print(fahrplan_dates_all_dates['monday'])
        zeit = time.time() - last_time
        print("time: {} ".format(zeit))
        last_time = time.time()

        # delete exceptions = 2 or add exceptions = 1
        fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_2, locals())
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'],
                                                          format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'],
                                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'],
                                                              format='%Y-%m-%d %H:%M:%S.%f')
        zeit = time.time() - last_time
        print("time: {} ".format(zeit))

        last_time = time.time()

        self.fahrplan_dates_all_dates = fahrplan_dates_all_dates

    def datesWeekday_select_stops_for_trips(self):

        cond_select_stops_for_trips = '''
                    select  
                            (select st_dfStopTimes.arrival_time 
                                    from dfStopTimes st_dfStopTimes
                                    where st_dfStopTimes.stop_sequence = 0
                                      and dfStopTimes.trip_id = st_dfStopTimes.trip_id) as start_time, 
                            dfTrips.trip_id,
                            dfStops.stop_name,
                            dfStopTimes.stop_sequence, 
                            dfStopTimes.arrival_time, 
                            dfTrips.service_id, 
                            dfStops.stop_id                        
                    from dfStopTimes 
                    inner join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
                    inner join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                    inner join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                    inner join route_short_namedf on dfRoutes.route_short_name = route_short_namedf.route_short_name
                    inner join varTestAgency on dfRoutes.agency_id = varTestAgency.agency_id
                    inner join requested_directiondf on dfTrips.direction_id = requested_directiondf.direction_id
                    where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                      and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                      and dfTrips.direction_id = requested_directiondf.direction_id -- shows the direction of the line 
                    ;
                   '''


        dfTrips = self.dfTrips
        dfRoutes = self.dfRoutes
        dfStops = self.dfStops
        dfStopTimes = self.dfStopTimes
        route_short_namedf = self.route_short_namedf
        varTestAgency = self.varTestAgency
        requested_directiondf = self.requested_directiondf

        last_time = time.time()
        # get all stop_times and stops for every stop of one route
        self.fahrplan_calendar_weeks = sqldf(cond_select_stops_for_trips, locals())

        zeit = time.time() - last_time
        print("time: {} ".format(zeit))
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
        self.fahrplan_sorted_stops = sqldf(cond_select_stop_sequence_stop_name_sorted_, locals())

        # fahrplan_sorted_stops.to_csv('C:Temp/' + 'routeName' + 'nameprefix' + 'pivot_table.csv', header=True, quotechar=' ',
        #                       index=True, sep=';', mode='a', encoding='utf8')

    # tried to get all data in one variable but then I need to create a new index for every dict again
    # maybe I try to get change it later
    def datesWeekday_create_fahrplan(self):

        cond_stop_name_sorted_trips_with_dates = '''
                    select  fahrplan_calendar_weeks.date,
                            fahrplan_calendar_weeks.day,
                            fahrplan_calendar_weeks.start_time, 
                            fahrplan_calendar_weeks.trip_id,
                            fahrplan_calendar_weeks.stop_name,
                            df_deleted_dupl_stop_names.stop_sequence as stop_sequence_sorted,
                            fahrplan_calendar_weeks.stop_sequence,
                            fahrplan_calendar_weeks.arrival_time, 
                            fahrplan_calendar_weeks.service_id, 
                            fahrplan_calendar_weeks.stop_id                        
                    from fahrplan_calendar_weeks 
                    left join df_deleted_dupl_stop_names on fahrplan_calendar_weeks.stop_id = df_deleted_dupl_stop_names.stop_id  
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

        deleted_dupl_stop_names = self.filterStopSequence(self.fahrplan_sorted_stops)
        df_deleted_dupl_stop_names = pd.DataFrame.from_dict(deleted_dupl_stop_names)
        # df_deleted_dupl_stop_names["stop_name"] = df_deleted_dupl_stop_names["stop_name"].astype('string')
        df_deleted_dupl_stop_names["stop_sequence"] = df_deleted_dupl_stop_names["stop_sequence"].astype('int32')
        df_deleted_dupl_stop_names = df_deleted_dupl_stop_names.set_index("stop_sequence")
        df_deleted_dupl_stop_names = df_deleted_dupl_stop_names.sort_index(axis=0)
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
        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].astype('string')

        self.fahrplan_calendar_filter_days_pivot = fahrplan_calendar_weeks.pivot(
            index=['date', 'day', 'stop_sequence_sorted', 'stop_name', 'stop_id'], columns=['start_time', 'trip_id'],
            values='arrival_time')

        # fahrplan_calendar_filter_days_pivot['date'] = pd.to_datetime(fahrplan_calendar_filter_days_pivot['date'], format='%Y-%m-%d %H:%M:%S.%f')
        self.fahrplan_calendar_filter_days_pivot = self.fahrplan_calendar_filter_days_pivot.sort_index(axis=1)
        self.fahrplan_calendar_filter_days_pivot = self.fahrplan_calendar_filter_days_pivot.sort_index(axis=0)

        # releae some memory
        self.zeit = time.time() - self.last_time
        print("time: {} ".format(self.zeit))
        now = datetime.now()
        self.now = now.strftime("%Y_%m_%d_%H_%M_%S")

    def datesWeekday_create_output_fahrplan(self):
        # save as csv
        self.dfheader_for_export_data.to_csv(
            self.output_path + str(self.route_short_namedf.route_short_name[0]) + 'dates_' + str(
                self.now) + 'pivot_table.csv', header=True,
            quotechar=' ', sep=';', mode='w', encoding='utf8')
        self.fahrplan_calendar_filter_days_pivot.to_csv(
            self.output_path + str(self.route_short_namedf.route_short_name[0]) + 'dates_' + str(
                self.now) + 'pivot_table.csv', header=True, quotechar=' ',
            index=True, sep=';', mode='a', encoding='utf8')
