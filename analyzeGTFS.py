# -*- coding: utf-8 -*-
import time
import pandas as pd
from pandasql import sqldf
import asyncio
import threading
import zipfile
import io

import re


# the is the one way to add a 0 to the time hh:mm:ss, if 0 is missing like in 6:44:33
def time_in_string(time):
    pattern = re.findall('^\d{1}:\d{2}:\d{2}$', time)

    if (pattern):
        return '0' + time
    else:
        return time

def check_dates_input(dates):
    pattern1 = re.findall('^\d{8}(?:\d{8})*(?:,\d{8})*$', dates)
    print(dates)
    if (pattern1):
        return True
    else:
        return False

async def read_gtfs_data(path):
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


async def get_gtfs_trip(inputgtfsData):
    print("get_gtfs_trip start")
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
    print(tripdict['route_id'][1])
    print("get_gtfs_trip loaded")
    return tripdict


async def get_gtfs_stop(inputgtfsData):
    print("get_gtfs_stop start")
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
    stopsList = None
    print("get_gtfs_stop loaded")
    return stopsdict


async def get_gtfs_stoptime(inputgtfsData):
    print("get_gtfs_stoptime start")
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
    stopTimesList = None
    print("get_gtfs_stoptime loaded")
    return stopTimesdict


async def get_gtfs_calendarWeek(inputgtfsData):
    print("get_gtfs_calendarWeek start")
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
    calendarList = None
    print("get_gtfs_calendarWeek loaded")
    return calendarWeekdict


async def get_gtfs_calendarDates(inputgtfsData):
    print("get_gtfs_calendarDates start")
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
    calendar_datesList = None
    print("get_gtfs_calendarDates loaded")
    return calendarDatesdict


async def get_gtfs_routes(inputgtfsData):
    print("get_gtfs_routes start")
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
    routesList = None
    print("get_gtfs_routes loaded")
    return routesFahrtdict


async def get_gtfs_agencies(inputgtfsData):
    print("get_gtfs_agencies start")
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
    routesList = None
    print("get_gtfs_agencies loaded")
    return agencyFahrtdict


async def get_gtfs(inputgtfsData):
    """ Creating and starting 10 tasks.
    tasks = get_gtfs_stop(inputgtfsData[0]),\
            get_gtfs_stoptime(inputgtfsData[1]),\
            get_gtfs_trip(inputgtfsData[2]),\
            get_gtfs_calendarWeek(inputgtfsData[3]),\
            get_gtfs_calendarDates(inputgtfsData[4]),\
            get_gtfs_routes(inputgtfsData[5])

    """
    stopsdict = await get_gtfs_stop(inputgtfsData[0])
    stopTimesdict = await get_gtfs_stoptime(inputgtfsData[1])
    tripdict = await get_gtfs_trip(inputgtfsData[2])
    calendarWeekdict = await get_gtfs_calendarWeek(inputgtfsData[3])
    calendarDatesdict = await get_gtfs_calendarDates(inputgtfsData[4])
    routesFahrtdict = await get_gtfs_routes(inputgtfsData[5])
    agencyFahrtdict = await get_gtfs_agencies(inputgtfsData[6])

    return stopsdict, stopTimesdict, tripdict, calendarWeekdict, calendarDatesdict, routesFahrtdict, agencyFahrtdict
    # await get_fahrt_ofroute_fahrplan(routeName, stopsdict, stopTimesdict, tripdict, calendarWeekdict, calendarDatesdict, routesFahrtdict)
    # await get_fahrt_ofroute_fahrplan(routeName2, stopsdict, stopTimesdict, tripdict, calendarWeekdict, calendarDatesdict, routesFahrtdict)


def select_gtfs_routes_from_agancy(agency, routesFahrtdict):
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
    # print (agency_list.values.tolist())
    return routes_list.values.tolist()


def select_gtfs_services_from_routes(route, tripdict, calendarWeekdict):
    print('looking for services')
    inputVar = [{'route_id': route[1]}]
    varTest = pd.DataFrame(inputVar).set_index('route_id')

    dfTrips = pd.DataFrame.from_dict(tripdict)

    # DataFrame with every service weekly
    dfWeek = pd.DataFrame.from_dict(calendarWeekdict)
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


async def read_gtfs_agencies(agencies_dict):
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
async def create_fahrplan_dates(routeName,
                                agencyName,
                                dates,
                                stopsdict,
                                stopTimesdict,
                                tripdict,
                                calendarWeekdict,
                                calendarDatesdict,
                                routesFahrtdict,
                                agencyFahrtdict,
                                output_path):
    print("get_fahrt_ofroute_fahrplan start")
    print(routeName)
    print(agencyName)
    print(dates)
    last_time = time.time()

    if not check_dates_input(dates):
        return

    # DataFrame for header information
    header_for_export_data = {'Agency': [agencyName],
                              'Route': [routeName],
                              'Dates': [dates]
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

    dummy_direction = 0
    direction = [{'direction_id': dummy_direction}
                 ]
    dfdirection = pd.DataFrame(direction)

    # dataframe with requested data
    requested_dates = {'date': [dates]}
    requested_datesdf = pd.DataFrame.from_dict(requested_dates)
    requested_datesdf['date'] = pd.to_datetime(requested_datesdf['date'], format='%Y%m%d')

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
                left join dfTrips on dfWeek.service_id = dfTrips.service_id
                left join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                left join route_short_namedf
                left join varTestAgency
                where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                  and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                  and dfTrips.direction_id = 0 -- shows the direction of the line 
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
                                                                  and dfDates.exception_type = 2 
                                                            )
                 and fahrplan_dates_all_dates.date in (select requested_datesdf.date 
                                                              from requested_datesdf                                                            
                                                                where fahrplan_dates_all_dates.date = requested_datesdf.date
                                                            )
                 and (fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.monday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.tuesday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.wednesday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.thursday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.friday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.saturday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.sunday
                     )  
                order by fahrplan_dates_all_dates.service_id;
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
                left join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
                left join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                left join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                left join varTestAgency 
                left join route_short_namedf
                where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                  and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                  and dfTrips.direction_id = 0 -- shows the direction of the line 
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
    fahrplan_dates['end_date']   = pd.to_datetime(fahrplan_dates['end_date'], format='%Y%m%d')
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
    fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y-%m-%d %H:%M:%S.%f')
    fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y-%m-%d %H:%M:%S.%f')
    #fahrplan_dates_all_dates = fahrplan_dates_all_dates.set_index('trip_id')

    #
    # fahrplan_dates_all_dates.to_csv( 'CSV/TESTDATES.csv', header=True, quotechar=' ',
    #                       index=True, sep=';', mode='w', encoding='utf8')

    # get all stop_times and stops for every stop of one route
    fahrplan_calendar_weeks = sqldf(cond_select_stops_for_trips, locals())
    #fahrplan_calendar_weeks = fahrplan_calendar_weeks.set_index('trip_id')

    # combine dates and trips to get a df with trips for every date
    fahrplan_calendar_weeks = sqldf(cond_select_for_every_date_trips_stops, locals())
    fahrplan_calendar_weeks['date']         = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d %H:%M:%S.%f')
    fahrplan_calendar_weeks['trip_id']      = fahrplan_calendar_weeks['trip_id'].astype(int)
    fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].apply(str)
    fahrplan_calendar_weeks['start_time']   = fahrplan_calendar_weeks['start_time'].apply(str)
    # creating a pivot table
    fahrplan_calendar_filter_days_pivot = fahrplan_calendar_weeks.pivot(index=['date', 'day', 'stop_sequence', 'stop_name'],columns=['start_time', 'trip_id'],values='arrival_time')

    #fahrplan_calendar_filter_days_pivot['date'] = pd.to_datetime(fahrplan_calendar_filter_days_pivot['date'], format='%Y-%m-%d %H:%M:%S.%f')
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
    return zeit, dfheader_for_export_data, fahrplan_calendar_filter_days_pivot



async def create_fahrplan_weekday(routeName,
                                  agencyName,
                                  selected_weekdayOption,
                                  stopsdict,
                                  stopTimesdict,
                                  tripdict,
                                  calendarWeekdict,
                                  calendarDatesdict,
                                  routesFahrtdict,
                                  agencyFahrtdict,
                                  output_path):
    print(routeName)
    print(agencyName)
    print(selected_weekdayOption)
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

    weekDayOption_1         = {'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
    weekDayOption_2         = {'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
    weekDayOption_monday    = {'day': ['Monday']}
    weekDayOption_tuesday   = {'day': ['Tuesday']}
    weekDayOption_wednesday = {'day': ['Wednesday']}
    weekDayOption_thursday  = {'day': ['Thursday']}
    weekDayOption_friday    = {'day': ['Friday']}
    weekDayOption_saturday  = {'day': ['Saturday']}
    weekDayOption_sunday    = {'day': ['Sunday']}

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
    direction = [{'direction_id': dummy_direction}
                 ]
    dfdirection = pd.DataFrame(direction)

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
                left join dfTrips on dfWeek.service_id = dfTrips.service_id
                left join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                left join route_short_namedf
                left join varTestAgency
                where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                  and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                  and dfTrips.direction_id = 0 -- shows the direction of the line 
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
                                                                  and dfDates.exception_type = 2
                                                            )                
                and (fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.monday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.tuesday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.wednesday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.thursday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.friday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.saturday
                      or fahrplan_dates_all_dates.day = fahrplan_dates_all_dates.sunday
                     )
                 and fahrplan_dates_all_dates.day in (select weekcond_df.day
                                                              from weekcond_df                                                            
                                                                where fahrplan_dates_all_dates.day = weekcond_df.day
                                                     )  
                order by fahrplan_dates_all_dates.service_id;
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
                left join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
                left join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                left join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                left join varTestAgency 
                left join route_short_namedf
                where dfRoutes.route_short_name = route_short_namedf.route_short_name -- in this case the bus line number
                  and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                  and dfTrips.direction_id = 0 -- shows the direction of the line 
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
    cond_filter_days_not_requested = '''
                select  fahrplan_calendar_weeks.day,
                        fahrplan_calendar_weeks.date,
                        fahrplan_calendar_weeks.start_time, 
                        fahrplan_calendar_weeks.trip_id,
                        fahrplan_calendar_weeks.stop_name,
                        fahrplan_calendar_weeks.stop_sequence, 
                        fahrplan_calendar_weeks.arrival_time, 
                        fahrplan_calendar_weeks.service_id, 
                        fahrplan_calendar_weeks.stop_id         
                from fahrplan_calendar_weeks
                where fahrplan_calendar_weeks.day  in (select weekcond_df.day
                                                              from weekcond_df                                                            
                                                                where fahrplan_calendar_weeks.day = weekcond_df.day
                                                     );
               '''



    # get dates for start and end dates for date range function
    fahrplan_dates = sqldf(cond_select_dates_for_date_range, locals())
    fahrplan_dates['start_date'] = pd.to_datetime(fahrplan_dates['start_date'], format='%Y%m%d')
    fahrplan_dates['end_date']   = pd.to_datetime(fahrplan_dates['end_date'], format='%Y%m%d')
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

    fahrplan_dates_all_dates = sqldf(cond_select_dates_delete_exception_2, locals())
    fahrplan_dates_all_dates['date'] = pd.to_datetime(fahrplan_dates_all_dates['date'], format='%Y-%m-%d %H:%M:%S.%f')
    fahrplan_dates_all_dates['start_date'] = pd.to_datetime(fahrplan_dates_all_dates['start_date'], format='%Y-%m-%d %H:%M:%S.%f')
    fahrplan_dates_all_dates['end_date'] = pd.to_datetime(fahrplan_dates_all_dates['end_date'], format='%Y-%m-%d %H:%M:%S.%f')
    # fahrplan_dates_all_dates = fahrplan_dates_all_dates.set_index('trip_id')

    # fahrplan_dates_all_dates.to_csv( 'CSV/TESTDATES.csv', header=True, quotechar=' ',
    #                       index=True, sep=';', mode='w', encoding='utf8')

    # get all stop_times and stops for every stop of one route
    fahrplan_calendar_weeks = sqldf(cond_select_stops_for_trips, locals())
    # fahrplan_calendar_weeks = fahrplan_calendar_weeks.set_index('trip_id')

    # combine dates and trips to get a df with trips for every date
    fahrplan_calendar_weeks = sqldf(cond_select_for_every_date_trips_stops, locals())
    fahrplan_calendar_weeks['date'] = pd.to_datetime(fahrplan_calendar_weeks['date'], format='%Y-%m-%d %H:%M:%S.%f')
    fahrplan_calendar_weeks['trip_id'] = fahrplan_calendar_weeks['trip_id'].astype(int)
    fahrplan_calendar_weeks['arrival_time'] = fahrplan_calendar_weeks['arrival_time'].apply(str)
    fahrplan_calendar_weeks['start_time'] = fahrplan_calendar_weeks['start_time'].apply(str)

    #filter days
    # fahrplan_calendar_filter_days  = sqldf(cond_filter_days_not_requested, locals())
    # fahrplan_calendar_filter_days['date'] = pd.to_datetime(fahrplan_calendar_filter_days['date'], format='%Y-%m-%d %H:%M:%S.%f')
    # fahrplan_calendar_filter_days['trip_id'] = fahrplan_calendar_filter_days['trip_id'].astype(int)
    # fahrplan_calendar_filter_days['arrival_time'] = fahrplan_calendar_filter_days['arrival_time'].apply(str)

    # creating a pivot table
    fahrplan_calendar_filter_days_pivot = fahrplan_calendar_weeks.pivot(index=['date', 'day', 'stop_sequence', 'stop_name'],columns=['start_time', 'trip_id'],values='arrival_time')
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
    return zeit, dfheader_for_export_data, fahrplan_calendar_filter_days_pivot


def create_output_fahrplan(routeName,
                           nameprefix,
                           dfheader_for_export_data,
                           fahrplan_pivot,
                           output_path):
    # save as csv
    dfheader_for_export_data.to_csv(output_path + routeName + nameprefix + 'pivot_table.csv', header=True,
                                    quotechar=' ', sep=';', mode='w', encoding='utf8')
    fahrplan_pivot.to_csv(output_path + routeName + nameprefix + 'pivot_table.csv', header=True, quotechar=' ',
                          index=True, sep=';', mode='a', encoding='utf8')
