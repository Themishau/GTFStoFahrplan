# -*- coding: utf-8 -*-
import time
import pandas as pd
from pandasql import sqldf
import zipfile
import io
from datetime import datetime, timedelta
import re





class gtfs:
    input_path: str
    output_path: str
    gtfs_data_list: list[list[str]]
    options_dates_weekday: list[str]
    selected_Direction: int


    def __init__(self):
        self.input_path = None
        self.output_path = None
        self.options_dates_weekday = ['Dates', 'Weekday']
        self.selected_option_dates_weekday = 1
        self.selected_Direction = 0
        self.time = None
        self.processing = None

        """ dicts for create and listbox """
        self.stopsdict = None
        self.stopTimesdict = None
        self.tripdict = None
        self.calendarWeekdict = None
        self.calendarDatesdict = None
        self.routesFahrtdict = None
        self.agencyFahrtdict = None

        """ loaded GTFSData """
        self.GTFSData = None

        """ loaded data for listbox """
        self.agenciesList = None
        self.routesList = None
        self.weekdayList = None

        """ loaded data for create """
        self.selectedAgency = None
        self.selectedRoute = None
        self.selected_weekday = None
        self.selected_dates = None

    # gets the data out of GTFSData and releases some memory
    async def get_gtfs(self):
        await self.get_gtfs()

    def set_paths(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    async def createFahrplan_dates(self):
        self.processing = "creating"
        route_name = [self.selectedRoute]
        if (self.data_loaded_and_available()
                and self.selectedRoute is not None
                and self.selected_dates is not None
                and self.options_dates_weekday[self.selected_option_dates_weekday] == 'Dates'):
            tasks_date = [self.create_fahrplan_dates(name[0],
                                                self.selectedAgency[0],
                                                self.selected_dates,
                                                self.selected_Direction) for name in route_name]

            # stores results and some information
            # try:
            completed, pending = await asyncio.wait(tasks_date)
            results = [task.result() for task in completed]
            self.time = "time: {} ".format(results[0][0])
            self.create_output_fahrplan(route_name[0][0], 'dates_' + str(results[0][1]), results[0][2], results[0][3],
                                   self.output_path)

        else:
            self.dispatch('message','Error in Create Fahrplan. Wrong data! Check input data and output path!')
            self.processing = None
            return

    async def createFahrplan_weekday(self):
        self.processing = "creating"
        selected_weekday_option = self.selected_weekday
        route_name = [self.selectedRoute]
        if (self.data_loaded_and_available()
                and self.selectedRoute is not None
                and self.options_dates_weekday[self.selected_option_dates_weekday] == 'Weekday'):
            tasks_weekday = [create_fahrplan_weekday(name[0],
                                                     self.selectedAgency[0],
                                                     selected_weekday_option,
                                                     self.selected_Direction,
                                                     self.stopsdict,
                                                     self.stopTimesdict,
                                                     self.tripdict,
                                                     self.calendarWeekdict,
                                                     self.calendarDatesdict,
                                                     self.routesFahrtdict,
                                                     self.agencyFahrtdict,
                                                     self.output_path) for name in route_name]

            # stores results and some information
            completed, pending = await asyncio.wait(tasks_weekday)
            results_weekday = [task.result() for task in completed]
            self.time = "time: {} ".format(results_weekday[0][0])

            create_output_fahrplan(route_name[0][0], 'weekday_' + str(results_weekday[0][1]), results_weekday[0][2],
                                   results_weekday[0][3], self.output_path)
            self.processing = None
            self.dispatch('message', 'Done')

        else:
            self.dispatch('message', 'Error in Create Fahrplan. Check input data and output path!')
            self.processing = None
            return


    # checks if all data is avalibale before creation
    def data_loaded_and_available(self):
        if (self.stopsdict is None
                or self.stopTimesdict is None
                or self.tripdict is None
                or self.calendarWeekdict is None
                or self.calendarDatesdict is None
                or self.routesFahrtdict is None
                or self.selectedRoute is None
                or self.selected_Direction is None):
            return False
        else:
            return True


    def SortStopSequence(self, data):
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
                    comparetime_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'))) + ' 0' + str(int(stop_name_i.start_time.split(':')[0]) - 24) + ':' + \
                                    stop_name_i.start_time.split(':')[1]
                    time_i = datetime.strptime(comparetime_i, '%Y-%m-%d %H:%M')
                    time_i = time_i + timedelta(days=1)
                else:
                    comparetime_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'))) + ' ' + stop_name_i.start_time
                    time_i = datetime.strptime(comparetime_i, '%Y-%m-%d %H:%M')

                if self.check_hour_24(stop_name_i.arrival_time):
                    time_arrival_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'))) + ' 0' + str(int(stop_name_i.arrival_time.split(':')[0]) - 24) + ':' + \
                                     stop_name_i.arrival_time.split(':')[1]
                    time_arrival_i = datetime.strptime(time_arrival_i, '%Y-%m-%d %H:%M')
                    time_arrival_i = time_arrival_i + timedelta(days=1)
                else:
                    time_arrival_i = str((datetime.strptime(stop_name_i.date, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'))) + ' ' + stop_name_i.arrival_time
                    time_arrival_i = datetime.strptime(time_arrival_i, '%Y-%m-%d %H:%M')


                temp["start_time"] = time_i
                temp["arrival_time"] = time_arrival_i

                # search in data and compare the ids
                for stop_name_j in data.itertuples():
                    # if ids match continue comparison
                    if stop_name_i.stop_id == stop_name_j.stop_id:

                        if self.check_hour_24(stop_name_j.start_time):
                            comparetime_j = str((datetime.strptime(stop_name_j.date, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'))) + ' 0' + str(int(stop_name_j.start_time.split(':')[0]) - 24) + ':' + \
                                            stop_name_j.start_time.split(':')[1]
                            time_j = datetime.strptime(comparetime_j, '%Y-%m-%d %H:%M')
                            time_j = time_j + timedelta(days=1)
                        else:
                            comparetime_j = str((datetime.strptime(stop_name_j.date, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'))) + ' ' + stop_name_j.start_time
                            time_j = datetime.strptime(comparetime_j, '%Y-%m-%d %H:%M')

                        time_temp = temp["start_time"]

                        if self.check_hour_24(stop_name_j.arrival_time):
                            time_arrival_j = str((datetime.strptime(stop_name_j.date, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'))) + ' 0' + str(int(stop_name_j.arrival_time.split(':')[0]) - 24) + ':' + \
                                             stop_name_j.arrival_time.split(':')[1]
                            time_arrival_j = datetime.strptime(time_arrival_j, '%Y-%m-%d %H:%M')
                            time_arrival_j = time_arrival_j + timedelta(days=1)
                        else:
                            time_arrival_j = str((datetime.strptime(stop_name_j.date, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d'))) + ' ' + stop_name_j.arrival_time
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

                stopsequence[stop_name_i.stop_id] = temp



        new_stopsequence = self.sortStopSequence(stopsequence)


        for stop_sequence in new_stopsequence.keys():
            sorted_stopsequence['stop_id'].append(new_stopsequence[stop_sequence]['stop_id'])
            sorted_stopsequence['stop_sequence'].append(stop_sequence)
            sorted_stopsequence['start_time'].append(new_stopsequence[stop_sequence]['start_time'])

        print (new_stopsequence)
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

        # bubble sort
        for i in range(sequence_count - 1):
            for j in range(0,sequence_count-i-1):
                if  d[str(j)]["stop_sequence"] > d[str(j + 1)]["stop_sequence"]:
                    d[str(j)], d[str(j + 1)] = d[str(j + 1)], d[str(j)]
                elif d[str(j)]["stop_sequence"] == d[str(j + 1)]["stop_sequence"]:
                    if d[str(j)]["start_time"] > d[str(j + 1)]["start_time"]:
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

        if (pattern):
            return '0' + time[:-3]
        else:
            return time[:-3]

    # checks if date string
    def check_dates_input(self, dates):
        pattern1 = re.findall('^\d{8}(?:\d{8})*(?:,\d{8})*$', dates)
        if (pattern1):
            return True
        else:
            return False

    # checks if time-string exceeds 24 hour
    def check_hour_24(self, time):
        pattern1 = re.findall('^2{1}[4-9]{1}:[0-9]{2}', time)
        if (pattern1):
            return True
        else:
            return False

    # read zip-data
    async def read_gtfs_data(self, path):
        try:
            with zipfile.ZipFile(path) as zf:
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
            return -1

        gtfsData = [stopsList, stopTimesList, tripsList, calendarList, calendar_datesList, routesList, agencyList]

        stopsList = None
        stopTimesList = None
        tripsList = None
        calendarList = None
        calendar_datesList = None
        routesList = None
        agencyList = None
        return gtfsData


    async def get_gtfs_trip(self, inputgtfsData):
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
        for trip in inputgtfsData:
            trip = trip.replace(", ", " ")
            trip = trip.replace('"', "")
            trip = trip.replace('\n', "")
            data = trip.split(",")
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
        tripsList = None
        return tripdict


    async def get_gtfs_stop(self, inputgtfsData):
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
        for haltestellen in inputgtfsData:
            haltestellen = haltestellen.replace(", ", " ")
            haltestellen = haltestellen.replace('"', "")
            haltestellen = haltestellen.replace('\n', "")
            stopData = haltestellen.split(",")
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
            stopsdict["zone_id"].append(stopData[10])

        self.stopsdict = stopsdict


    async def get_gtfs_stoptime(self, inputgtfsData):
        stopTimesdict = {
            "trip_id": [],
            "arrival_time": [],
            "departure_time": [],
            "stop_id": [],
            "stop_sequence": [],
            "pickup_type": [],
            "drop_off_type": [],
            "stop_headsign": []
        }
        for stopTime in inputgtfsData:
            stopTime = stopTime.replace(", ", " ")
            stopTime = stopTime.replace('"', "")
            stopTime = stopTime.replace('\n', "")
            stopTimeData = stopTime.split(",")
            stopTimesdict["trip_id"].append(stopTimeData[0])
            stopTimesdict["arrival_time"].append(stopTimeData[1])
            stopTimesdict["departure_time"].append(stopTimeData[2])
            stopTimesdict["stop_id"].append(stopTimeData[3])
            stopTimesdict["stop_sequence"].append(stopTimeData[4])
            stopTimesdict["pickup_type"].append(stopTimeData[5])
            stopTimesdict["drop_off_type"].append(stopTimeData[6])
            stopTimesdict["stop_headsign"].append(stopTimeData[7])

        self.stopTimesdict = stopTimesdict
        return stopTimesdict


    async def get_gtfs_calendarWeek(self, inputgtfsData):
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
        for calendarDate in inputgtfsData:
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
        return calendarWeekdict


    async def get_gtfs_calendarDates(self, inputgtfsData):
        calendarDatesdict = {
            "service_id": [],
            "date": [],
            "exception_type": [],
        }
        for calendarDate in inputgtfsData:
            calendarDate = calendarDate.replace(", ", " ")
            calendarDate = calendarDate.replace('"', "")
            calendarDate = calendarDate.replace('\n', "")
            calendarDatesData = calendarDate.split(",")
            calendarDatesdict["service_id"].append(calendarDatesData[0])
            calendarDatesdict["date"].append(calendarDatesData[1])
            calendarDatesdict["exception_type"].append(calendarDatesData[2])

        self.calendarDatesdict= calendarDatesdict
        return calendarDatesdict


    async def get_gtfs_routes(self, inputgtfsData):
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
        for routes in inputgtfsData:
            routes = routes.replace(", ", " ")
            routes = routes.replace('"', "")
            routes = routes.replace('\n', "")
            routesData = routes.split(",")
            routesFahrtdict["route_id"].append(routesData[0])
            routesFahrtdict["agency_id"].append(routesData[1])
            routesFahrtdict["route_short_name"].append(routesData[2])
            routesFahrtdict["route_long_name"].append(routesData[3])
            routesFahrtdict["route_type"].append(routesData[4])
            routesFahrtdict["route_color"].append(routesData[5])
            routesFahrtdict["route_text_color"].append(routesData[6])
            routesFahrtdict["route_desc"].append(routesData[7])

        self.routesFahrtdict = routesFahrtdict
        return routesFahrtdict


    async def get_gtfs_agencies(self, inputgtfsData):
        agencyFahrtdict = {
            "agency_id": [],
            "agency_name": [],
            "agency_url": [],
            "agency_timezone": [],
            "agency_lang": [],
            "agency_phone": []
        }
        for agency in inputgtfsData:
            agency = agency.replace(", ", " ")
            agency = agency.replace('"', "")
            agency = agency.replace('\n', "")
            agencyData = agency.split(",")
            agencyFahrtdict["agency_id"].append(agencyData[0])
            agencyFahrtdict["agency_name"].append(agencyData[1])
            agencyFahrtdict["agency_url"].append(agencyData[2])
            agencyFahrtdict["agency_timezone"].append(agencyData[3])
            agencyFahrtdict["agency_lang"].append(agencyData[4])
            agencyFahrtdict["agency_phone"].append(agencyData[5])

        self.agencyFahrtdict = agencyFahrtdict
        return agencyFahrtdict


    async def get_gtfs(self, inputgtfsData):
        """ Creating and starting 10 tasks.
        tasks = get_gtfs_stop(inputgtfsData[0]),\
                get_gtfs_stoptime(inputgtfsData[1]),\
                get_gtfs_trip(inputgtfsData[2]),\
                get_gtfs_calendarWeek(inputgtfsData[3]),\
                get_gtfs_calendarDates(inputgtfsData[4]),\
                get_gtfs_routes(inputgtfsData[5])

        """
        await self.get_gtfs_stop(inputgtfsData[0])
        await self.get_gtfs_stoptime(inputgtfsData[1])
        await self.get_gtfs_trip(inputgtfsData[2])
        await self.get_gtfs_calendarWeek(inputgtfsData[3])
        await self.get_gtfs_calendarDates(inputgtfsData[4])
        await self.get_gtfs_routes(inputgtfsData[5])
        await self.get_gtfs_agencies(inputgtfsData[6])


    def select_gtfs_routes_from_agancy(self, agency, routesFahrtdict):
        inputVar = [{'agency_id': agency[0]}]
        varTest = pd.DataFrame(inputVar).set_index('agency_id')
        dfRoutes = pd.DataFrame(routesFahrtdict).set_index('route_id')
        cond_routes_of_agency = '''
                    select dfRoutes.route_short_name, dfRoutes.route_id
                    from dfRoutes 
                    left join varTest
                    where varTest.agency_id = dfRoutes.agency_id
                    order by dfRoutes.route_short_name;
                   '''
        routes_list = sqldf(cond_routes_of_agency, locals())
        routes_list.values.tolist()
        return routes_list.values.tolist()


    def select_gtfs_services_from_routes(self, route, tripdict, calendarWeekdict):
        print('looking for services')
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
        services_list.values.tolist()
        return services_list.values.tolist()


    async def read_gtfs_agencies(self, agencies_dict):
        df_agency = pd.DataFrame(agencies_dict).set_index('agency_id')
        cond_agencies = '''
                    select df_agency.agency_id, df_agency.agency_name
                    from df_agency 
                    order by df_agency.agency_id;
                   '''
        agency_list = sqldf(cond_agencies, locals())
        agency_list.values.tolist()
        # print (agency_list.values.tolist())
        return agency_list.values.tolist()


    # tried to get all data in one variable but then I need to create a new index for every dict again
    # maybe I try to get change it later
    async def create_fahrplan_dates(self,
                                    routeName,
                                    agencyName,
                                    dates,
                                    selected_direction):
        # name[0],
        # self.selectedAgency[0],
        # self.selected_dates,
        # self.selected_Direction,
        # self.stopsdict,
        # self.stopTimesdict,
        # self.tripdict,
        # self.calendarWeekdict,
        # self.calendarDatesdict,
        # self.routesFahrtdict,
        # self.agencyFahrtdict,
        # self.output_path

        print('Route: ' + routeName)
        print('Agency: ' + agencyName)
        print('Dates: ' + dates)
        print('Direction: ' + str(selected_direction))
        last_time = time.time()

        if not self.check_dates_input(dates):
            return

        # DataFrame for header information
        header_for_export_data = {'Agency': [agencyName],
                                  'Route': [routeName],
                                  'Dates': [dates]
                                  }
        dfheader_for_export_data = pd.DataFrame.from_dict(header_for_export_data)

        # DataFrame for every route
        dfRoutes = pd.DataFrame.from_dict(routesFahrtdict).set_index(['route_id','agency_id'])

        # DataFrame with every trip
        dfTrips = pd.DataFrame.from_dict(tripdict).set_index('trip_id')

        try:
            # dfTrips['trip_id'] = pd.to_numeric(dfTrips['trip_id'])
            dfTrips['trip_id'] = dfTrips['trip_id'].astype('int32')
        except KeyError:
            print("can not convert dfTrips: trip_id into int")



        # DataFrame with every stop (time)
        dfStopTimes = pd.DataFrame.from_dict(stopTimesdict).set_index(['trip_id', 'stop_id'])
        try:
            dfStopTimes['arrival_time'] = dfStopTimes['arrival_time'].apply(lambda x: self.time_in_string(x))
            dfStopTimes['arrival_time'] = dfStopTimes['arrival_time'].astype('string')
        except KeyError:
            print("can not convert dfStopTimes: arrival_time into string and change time")

        try:
            dfStopTimes['stop_sequence'] = dfStopTimes['stop_sequence'].astype('int32')
        except KeyError:
            print("can not convert dfStopTimes: stop_sequence into int")
        try:
            dfStopTimes['stop_id'] = dfStopTimes['stop_id'].astype('int32')
        except KeyError:
            print("can not convert dfStopTimes: stop_id into int")
        except OverflowError:
            print("can not convert dfStopTimes: stop_id into int")
        try:
            dfStopTimes['trip_id'] = dfStopTimes['trip_id'].astype('int32')
        except KeyError:
            print("can not convert dfStopTimes: trip_id into int")

        # DataFrame with every stop
        dfStops = pd.DataFrame.from_dict(stopsdict).set_index('stop_id')
        try:
            dfStops['stop_id'] = dfStops['stop_id'].astype('int32')
        except KeyError:
            print("can not convert dfStops: stop_id into int ")


        # DataFrame with every service weekly
        dfWeek = pd.DataFrame.from_dict(calendarWeekdict).set_index('service_id')

        # DataFrame with every service dates
        dfDates = pd.DataFrame.from_dict(calendarDatesdict).set_index('service_id')
        dfDates['exception_type'] = dfDates['exception_type'].astype('int32')
        dfDates['date'] = pd.to_datetime(dfDates['date'], format='%Y%m%d')

        # DataFrame with every agency
        df_agency = pd.DataFrame.from_dict(agencyFahrtdict).set_index('agency_id')

        dummy_direction = 0
        direction = [{'direction_id': dummy_direction}
                     ]
        dfdirection = pd.DataFrame(direction)

        # dataframe with requested data
        requested_dates = {'date': [dates]}
        requested_datesdf = pd.DataFrame.from_dict(requested_dates)
        requested_datesdf['date'] = pd.to_datetime(requested_datesdf['date'], format='%Y%m%d')

        requested_direction = {'direction_id': [selected_direction]}
        requested_directiondf = pd.DataFrame.from_dict(requested_direction)

        inputVar = [{'route_short_name': routeName}]
        route_short_namedf = pd.DataFrame(inputVar).set_index('route_short_name')

        inputVarAgency = [{'agency_id': agencyName}]
        varTestAgency = pd.DataFrame(inputVarAgency).set_index('agency_id')

        # conditions for searching in dfs
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
                    order by dfStopTimes.stop_sequence, start_time;
                   '''

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

        # cond_select_stop_sequence_stop_name_sorted_ = '''
        #             select  fahrplan_calendar_weeks.date,
        #                     fahrplan_calendar_weeks.day,
        #                     fahrplan_calendar_weeks.start_time,
        #                     fahrplan_calendar_weeks.stop_name,
        #                     fahrplan_calendar_weeks.stop_sequence,
        #                     fahrplan_calendar_weeks.stop_id
        #             from fahrplan_calendar_weeks
        #             group by fahrplan_calendar_weeks.stop_sequence, fahrplan_calendar_weeks.stop_name, fahrplan_calendar_weeks.stop_id, fahrplan_calendar_weeks.trip_id
        #             order by fahrplan_calendar_weeks.trip_id, fahrplan_calendar_weeks.date, fahrplan_calendar_weeks.stop_sequence;
        #            '''

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
        fahrplan_dates = sqldf(cond_select_dates_for_date_range, locals())

        # change format
        fahrplan_dates['start_date'] = pd.to_datetime(fahrplan_dates['start_date'], format='%Y%m%d')
        fahrplan_dates['end_date'] = pd.to_datetime(fahrplan_dates['end_date'], format='%Y%m%d')

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
                                        }) for i, row in fahrplan_dates.iterrows()], ignore_index=True)

        # need to convert the date after using iterows (itertuples might be faster)
        fahrplan_dates = None
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y%m%d')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['day'] = fahrplan_dates_all_dates['date'].dt.day_name()

        # set value in column to day if 1 and and compare with day
        fahrplan_dates_all_dates['monday'] = fahrplan_dates_all_dates['monday'].apply(
            lambda x: 'Monday' if x == '1' else '-')
        fahrplan_dates_all_dates['tuesday'] = fahrplan_dates_all_dates['tuesday'].apply(
            lambda x: 'Tuesday' if x == '1' else '-')
        fahrplan_dates_all_dates['wednesday'] = fahrplan_dates_all_dates['wednesday'].apply(
            lambda x: 'Wednesday' if x == '1' else '-')
        fahrplan_dates_all_dates['thursday'] = fahrplan_dates_all_dates['thursday'].apply(
            lambda x: 'Thursday' if x == '1' else '-')
        fahrplan_dates_all_dates['friday'] = fahrplan_dates_all_dates['friday'].apply(
            lambda x: 'Friday' if x == '1' else '-')
        fahrplan_dates_all_dates['saturday'] = fahrplan_dates_all_dates['saturday'].apply(
            lambda x: 'Saturday' if x == '1' else '-')
        fahrplan_dates_all_dates['sunday'] = fahrplan_dates_all_dates['sunday'].apply(
            lambda x: 'Sunday' if x == '1' else '-')
        fahrplan_dates_all_dates = fahrplan_dates_all_dates.set_index('date')

        # delete exceptions = 2 or add exceptions = 1
        fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_2, locals())
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'],
                                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'],
                                                              format='%Y-%m-%d %H:%M:%S.%f')

        # get all stop_times and stops for every stop of one route
        fahrplan_calendar_weeks = sqldf(cond_select_stops_for_trips, locals())


        # combine dates and trips to get a df with trips for every date
        fahrplan_calendar_weeks = sqldf(cond_select_for_every_date_trips_stops, locals())

        #########################

        # group stop_sequence and stop_names, so every stop_name appears only once
        fahrplan_sorted_stops = sqldf(cond_select_stop_sequence_stop_name_sorted_, locals())

        # fahrplan_sorted_stops.to_csv('C:Temp/' + 'routeName' + 'nameprefix' + 'pivot_table.csv', header=True, quotechar=' ',
        #                       index=True, sep=';', mode='a', encoding='utf8')

        deleted_dupl_stop_names = self.SortStopSequence(fahrplan_sorted_stops)
        df_deleted_dupl_stop_names = pd.DataFrame.from_dict(deleted_dupl_stop_names)
        # df_deleted_dupl_stop_names["stop_name"] = df_deleted_dupl_stop_names["stop_name"].astype('string')
        df_deleted_dupl_stop_names["stop_sequence"] = df_deleted_dupl_stop_names["stop_sequence"].astype('int32')
        df_deleted_dupl_stop_names = df_deleted_dupl_stop_names.set_index("stop_sequence")
        df_deleted_dupl_stop_names = df_deleted_dupl_stop_names.sort_index(axis=0)
        fahrplan_calendar_weeks = sqldf(cond_stop_name_sorted_trips_with_dates, locals())

        ###########################


        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype('int32')
        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].astype('string')
        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].astype('string')

        # fahrplan_calendar_weeks = fahrplan_calendar_weeks.drop(columns=['stop_sequence', 'service_id', 'stop_id'])
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.drop(columns=['stop_sequence', 'service_id'])
        fahrplan_calendar_weeks = fahrplan_calendar_weeks.groupby(
            ['date', 'day', 'stop_sequence_sorted', 'stop_name', 'stop_id', 'start_time', 'trip_id']).first().reset_index()


        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d')
        fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype('int32')
        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].astype('string')
        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].astype('string')


        fahrplan_calendar_filter_days_pivot = fahrplan_calendar_weeks.pivot(
            index=['date', 'day', 'stop_sequence_sorted', 'stop_name', 'stop_id'], columns=['start_time', 'trip_id'], values='arrival_time')


        # fahrplan_calendar_filter_days_pivot['date'] = pd.to_datetime(fahrplan_calendar_filter_days_pivot['date'], format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_calendar_filter_days_pivot = fahrplan_calendar_filter_days_pivot.sort_index(axis=1)
        fahrplan_calendar_filter_days_pivot = fahrplan_calendar_filter_days_pivot.sort_index(axis=0)


        # releae some memory
        dfTrips = None
        dfStopTimes = None
        dfStops = None
        dfRoutes = None
        dfWeek = None
        zeit = time.time() - last_time
        print("time: {} ".format(zeit))
        now = datetime.now()
        now = now.strftime("%Y_%m_%d_%H_%M_%S")
        return zeit, now, dfheader_for_export_data, fahrplan_calendar_filter_days_pivot


    async def create_fahrplan_weekday(self,
                                      routeName,
                                      agencyName,
                                      selected_weekdayOption,
                                      selected_direction,
                                      stopsdict,
                                      stopTimesdict,
                                      tripdict,
                                      calendarWeekdict,
                                      calendarDatesdict,
                                      routesFahrtdict,
                                      agencyFahrtdict,
                                      output_path):
        print('Route: ' + routeName)
        print('Agency: ' + agencyName)
        print('WeekdayOption: ' + str(selected_weekdayOption))
        print('Direction: ' + str(selected_direction))
        last_time = time.time()

        header_for_export_data = {'Agency': [agencyName],
                                  'Route': [routeName],
                                  'WeekdayOption': [selected_weekdayOption]
                                  }
        dfheader_for_export_data = pd.DataFrame.from_dict(header_for_export_data)

        # DataFrame for every route
        dfRoutes = pd.DataFrame.from_dict(routesFahrtdict).set_index('route_id')
        # DataFrame with every trip
        dfTrips = pd.DataFrame.from_dict(tripdict)

        try:
            # dfTrips['trip_id'] = pd.to_numeric(dfTrips['trip_id'])
            dfTrips['trip_id'] = dfTrips['trip_id'].astype(int)
        except:
            print("can not convert dfTrips: trip_id into int")

        # DataFrame with every stop (time)
        dfStopTimes = pd.DataFrame.from_dict(stopTimesdict)
        try:
            dfStopTimes['arrival_time'] = dfStopTimes['arrival_time'].apply(lambda x: time_in_string(x))
            dfStopTimes['arrival_time'] = dfStopTimes['arrival_time'].apply(str)
        except:
            print("can not convert dfStopTimes: arrival_time into string and change time")

        try:
            dfStopTimes['stop_sequence'] = dfStopTimes['stop_sequence'].astype(int)
        except:
            print("can not convert dfStopTimes: stop_sequence into int")

        try:
            dfStopTimes['stop_id'] = dfStopTimes['stop_id'].astype(int)
        except:
            print("can not convert dfStopTimes: stop_id into int")

        try:
            dfStopTimes['trip_id'] = dfStopTimes['trip_id'].astype(int)
        except:
            print("can not convert dfStopTimes: trip_id into int")

        # DataFrame with every stop
        dfStops = pd.DataFrame.from_dict(stopsdict).set_index('stop_id')
        try:
            dfStops['stop_id'] = dfStops['stop_id'].astype(int)
        except:
            print("can not convert dfStops: stop_id into int ")

        # try to set some more indeces
        try:
            dfTrips = dfTrips.set_index('trip_id')
            dfStopTimes = dfStopTimes.set_index(['trip_id', 'stop_id'])
            dfStops = dfStops.set_index('stop_id')
        except:
            print("can not set index: stop_id into int ")

        # DataFrame with every service weekly
        dfWeek = pd.DataFrame.from_dict(calendarWeekdict).set_index('service_id')

        # DataFrame with every service dates
        dfDates = pd.DataFrame.from_dict(calendarDatesdict).set_index('service_id')
        dfDates['exception_type'] = dfDates['exception_type'].astype(int)
        dfDates['date'] = pd.to_datetime(dfDates['date'], format='%Y%m%d')
        # DataFrame with every agency
        df_agency = pd.DataFrame.from_dict(agencyFahrtdict).set_index('agency_id')

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

        weekcond_df = weekDayOptionList[selected_weekdayOption]
        dummy_direction = 0

        requested_direction = {'direction_id': [selected_direction]}
        requested_directiondf = pd.DataFrame.from_dict(requested_direction)

        # dataframe with the (bus) lines
        inputVar = [{'route_short_name': routeName}]
        route_short_namedf = pd.DataFrame(inputVar).set_index('route_short_name')

        inputVarAgency = [{'agency_id': agencyName}]
        varTestAgency = pd.DataFrame(inputVarAgency).set_index('agency_id')

        inputVarService = [{'weekdayOption': selected_weekdayOption}]
        varTestService = pd.DataFrame(inputVarService).set_index('weekdayOption')

        # conditions for searching in dfs
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
                    order by dfStopTimes.stop_sequence, start_time;
                   '''

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
                    order by fahrplan_dates_all_dates.date, fahrplan_calendar_weeks.stop_sequence, fahrplan_calendar_weeks.start_time;
                   '''

        # get dates for start and end dates for date range function
        fahrplan_dates = sqldf(cond_select_dates_for_date_range, locals())
        fahrplan_dates['start_date'] = pd.to_datetime(fahrplan_dates['start_date'], format='%Y%m%d')
        fahrplan_dates['end_date'] = pd.to_datetime(fahrplan_dates['end_date'], format='%Y%m%d')
        # add date column for every date in date range
        fahrplan_dates_all_dates = pd.concat([pd.DataFrame({'date': pd.date_range(row.start_date, row.end_date, freq='D'),
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
                                                            }
                                                           )
                                              for i, row in fahrplan_dates.iterrows()], ignore_index=True)
        # I need to convert the date after every sqldf for some reason
        fahrplan_dates = None
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y%m%d')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y%m%d')
        fahrplan_dates_all_dates['day'] = fahrplan_dates_all_dates['date'].dt.day_name()
        # set value in column to day if 1 and and compare with day
        fahrplan_dates_all_dates['monday'] = fahrplan_dates_all_dates['monday'].apply(
            lambda x: 'Monday' if x == '1' else '-')
        fahrplan_dates_all_dates['tuesday'] = fahrplan_dates_all_dates['tuesday'].apply(
            lambda x: 'Tuesday' if x == '1' else '-')
        fahrplan_dates_all_dates['wednesday'] = fahrplan_dates_all_dates['wednesday'].apply(
            lambda x: 'Wednesday' if x == '1' else '-')
        fahrplan_dates_all_dates['thursday'] = fahrplan_dates_all_dates['thursday'].apply(
            lambda x: 'Thursday' if x == '1' else '-')
        fahrplan_dates_all_dates['friday'] = fahrplan_dates_all_dates['friday'].apply(
            lambda x: 'Friday' if x == '1' else '-')
        fahrplan_dates_all_dates['saturday'] = fahrplan_dates_all_dates['saturday'].apply(
            lambda x: 'Saturday' if x == '1' else '-')
        fahrplan_dates_all_dates['sunday'] = fahrplan_dates_all_dates['sunday'].apply(
            lambda x: 'Sunday' if x == '1' else '-')

        # delete exceptions = 2 or add exceptions = 1
        fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_2, locals())
        fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'],
                                                                format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'],
                                                              format='%Y-%m-%d %H:%M:%S.%f')
        # fahrplan_dates_all_dates = fahrplan_dates_all_dates.set_index('trip_id')

        # get all stop_times and stops for every stop of one route
        fahrplan_calendar_weeks = sqldf(cond_select_stops_for_trips, locals())

        # fahrplan_calendar_weeks = fahrplan_calendar_weeks.set_index('trip_id')

        # combine dates and trips to get a df with trips for every date
        fahrplan_calendar_weeks = sqldf(cond_select_for_every_date_trips_stops, locals())
        fahrplan_dates_all_dates = None
        fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d %H:%M:%S.%f')
        fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype(int)
        fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].apply(str)
        fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].apply(str)

        # creating a pivot table
        fahrplan_calendar_filter_days_pivot = fahrplan_calendar_weeks.pivot(
            index=['date', 'day', 'stop_sequence', 'stop_name'], columns=['start_time', 'trip_id'], values='arrival_time')
        fahrplan_calendar_weeks = None
        fahrplan_calendar_filter_days_pivot = fahrplan_calendar_filter_days_pivot.sort_index(axis=1)
        fahrplan_calendar_filter_days_pivot = fahrplan_calendar_filter_days_pivot.sort_index(axis=0)

        # releae some memory
        dfTrips = None
        dfStopTimes = None
        dfStops = None
        dfRoutes = None
        dfWeek = None
        zeit = time.time() - last_time
        print("time: {} ".format(zeit))
        now = datetime.now()
        now = now.strftime("%Y_%m_%d_%H_%M_%S")
        return zeit, now, dfheader_for_export_data, fahrplan_calendar_filter_days_pivot


    def create_output_fahrplan(self,
                               routeName,
                               nameprefix,
                               dfheader_for_export_data,
                               fahrplan_pivot,
                               output_path):
        # save as csv
        dfheader_for_export_data.to_csv(output_path + routeName + nameprefix + 'pivot_table.csv', header=True,
                                        quotechar=' ', sep=';', mode='w', encoding='utf8')
        fahrplan_pivot.to_csv(output_path + routeName + nameprefix + 'pivot_table.csv', header=True, quotechar=' ',
                              index=True, sep=';', mode='a', encoding='utf8')
