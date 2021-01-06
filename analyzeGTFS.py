# -*- coding: utf-8 -*-
import time
import pandas as pd
from pandasql import sqldf
import asyncio
import threading
import zipfile
import io


async def read_gtfs_data (path):

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

async def get_gtfs_stopb(inputgtfsData):
    print("get_gtfs_stop start")
    stopsdict = []
    for haltestellen in inputgtfsData:
        haltestellen = haltestellen.replace(", ", " ")
        haltestellen = haltestellen.replace('"', "")
        haltestellen = haltestellen.replace('\n', "")
        stopData = haltestellen.split(",")
        dataDict = {
            "stop_id": stopData[0],
            "stop_code": stopData[1],
            "stop_name": stopData[2],
            "stop_desc": stopData[3],
            "stop_lat": stopData[4],
            "stop_lon": stopData[5],
            "location_type": stopData[6],
            "parent_station": stopData[7],
            "wheelchair_accessible": stopData[8],
            "platform_code": stopData[9],
            "zone_id": stopData[10]
        }
        stopsdict.append(dataDict)
    stopsList = None
    print("get_gtfs_stop loaded")
    return stopsdict

async def get_gtfs_stoptimeb(inputgtfsData):
    print("get_gtfs_stoptime start")
    stopTimesdict = []
    for stopTime in inputgtfsData:
        stopTime = stopTime.replace(", ", " ")
        stopTime = stopTime.replace('"', "")
        stopTime = stopTime.replace('\n', "")
        stopTimeData = stopTime.split(",")
        dataDict = {
            "trip_id": stopTimeData[0],
            "arrival_time": stopTimeData[1],
            "departure_time": stopTimeData[2],
            "stop_id": stopTimeData[3],
            "stop_sequence": stopTimeData[4],
            "pickup_type": stopTimeData[5],
            "drop_off_type": stopTimeData[6],
            "stop_headsign": stopTimeData[7],

        }
        stopTimesdict.append(dataDict)
    stopTimesList = None
    print("get_gtfs_stoptime loaded")
    return stopTimesdict

async def get_gtfs_tripb(inputgtfsData):
    print("get_gtfs_trip start")
    tripdict = []
    for trip in inputgtfsData:
        trip = trip.replace(", ", " ")
        trip = trip.replace('"', "")
        trip = trip.replace('\n', "")
        data = trip.split(",")
        dataDict = {
            "route_id": data[0],
            "service_id": data[1],
            "trip_id": data[2],
            "trip_headsign": data[3],
            "trip_short_name": data[4],
            "direction_id": data[5],
            "block_id": data[6],
            "shape_id": data[7],
            "wheelchair_accessible": data[8],
            "bikes_allowed": data[9]
        }
        tripdict.append(dataDict)
    tripsList = None
    print("get_gtfs_trip loaded")
    return tripdict

async def get_gtfs_calendarWeekb(inputgtfsData):
    print("get_gtfs_calendarWeek start")
    calendarWeekdict = []
    for calendarDate in inputgtfsData:
        calendarDate = calendarDate.replace(", ", " ")
        calendarDate = calendarDate.replace('"', "")
        calendarDate = calendarDate.replace('\n', "")
        calendarData = calendarDate.split(",")
        dataDict = {
            "service_id": calendarData[0],
            "monday": calendarData[1],
            "tuesday": calendarData[2],
            "wednesday": calendarData[3],
            "thursday": calendarData[4],
            "friday": calendarData[5],
            "saturday": calendarData[6],
            "sunday": calendarData[7],
            "start_date": calendarData[8],
            "end_date": calendarData[9]
        }
        calendarWeekdict.append(dataDict)
    calendarList = None
    print("get_gtfs_calendarWeek loaded")
    return calendarWeekdict

async def get_gtfs_calendarDatesb(inputgtfsData):
    print("get_gtfs_calendarDates start")
    calendarDatesdict = []
    for calendarDate in inputgtfsData:
        calendarDate = calendarDate.replace(", ", " ")
        calendarDate = calendarDate.replace('"', "")
        calendarDate = calendarDate.replace('\n', "")
        calendarDatesData = calendarDate.split(",")
        dataDict = {
            "service_id": calendarDatesData[0],
            "date": calendarDatesData[1],
            "exception_type": calendarDatesData[2],
        }
        calendarDatesdict.append(dataDict)
    calendar_datesList = None
    print("get_gtfs_calendarDates loaded")
    return calendarDatesdict

async def get_gtfs_routesb(inputgtfsData):
    print("get_gtfs_routes start")
    routesFahrtdict = []
    for routes in inputgtfsData:
        routes = routes.replace(", ", " ")
        routes = routes.replace('"', "")
        routes = routes.replace('\n', "")
        routesData = routes.split(",")
        dataDict = {
            "route_id": routesData[0],
            "agency_id": routesData[1],
            "route_short_name": routesData[2],
            "route_long_name": routesData[3],
            "route_type": routesData[4],
            "route_color": routesData[5],
            "route_text_color": routesData[6],
            "route_desc": routesData[7]
        }
        routesFahrtdict.append(dataDict)
    routesList = None
    print("get_gtfs_routes loaded")
    return routesFahrtdict

async def get_gtfs_agenciesb(inputgtfsData):
    print("get_gtfs_agencies start")
    agencyFahrtdict = []
    for agency in inputgtfsData:
        agency = agency.replace(", ", " ")
        agency = agency.replace('"', "")
        agency = agency.replace('\n', "")
        agencyData = agency.split(",")
        dataDict = {
            "agency_id": agencyData[0],
            "agency_name": agencyData[1],
            "agency_url": agencyData[2],
            "agency_timezone": agencyData[3],
            "agency_lang": agencyData[4],
            "agency_phone": agencyData[5],

        }
        agencyFahrtdict.append(dataDict)
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
    #await get_fahrt_ofroute_fahrplan(routeName, stopsdict, stopTimesdict, tripdict, calendarWeekdict, calendarDatesdict, routesFahrtdict)
    #await get_fahrt_ofroute_fahrplan(routeName2, stopsdict, stopTimesdict, tripdict, calendarWeekdict, calendarDatesdict, routesFahrtdict)

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
    #print (agency_list.values.tolist())
    return routes_list.values.tolist()

def select_gtfs_services_from_routes(route, tripdict, calendarWeekdict):
    print('looking for services')
    inputVar = [{'route_id': route[1]}]
    varTest = pd.DataFrame(inputVar).set_index('route_id')

    dfTrips = pd.DataFrame.from_dict(tripdict)

    #DataFrame with every service weekly
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
    #print (agency_list.values.tolist())
    return agency_list.values.tolist()

# tried to get all data in one variable but then I need to create a new index for every dict again
# maybe I try to get change it later
async def get_fahrt_ofroute_fahrplan(routeName, agencyName, serviceName, stopsdict, stopTimesdict, tripdict, calendarWeekdict, calendarDatesdict, routesFahrtdict, agencyFahrtdict):
    print("get_fahrt_ofroute_fahrplan start")
    print(routeName)
    print(agencyName)
    print(serviceName)
    last_time = time.time()

    #DataFrame for every route
    dfRoutes = pd.DataFrame.from_dict(routesFahrtdict)

    #DataFrame with every trip
    #dfTrips = pd.DataFrame.from_dict(tripdict, orient='index') #if you want to have every trip as an row
    dfTrips = pd.DataFrame.from_dict(tripdict)

    try:
        #dfTrips['trip_id'] = pd.to_numeric(dfTrips['trip_id'])
        dfTrips['trip_id'] = dfTrips['trip_id'].astype(int)
    except:
        print("can not convert dfTrips: trip_id into int")

    #DataFrame with every stop (time)
    #dfStopTimes = pd.DataFrame.from_dict(stopTimesdict).set_index('stop_id', 'trip_id')
    dfStopTimes = pd.DataFrame.from_dict(stopTimesdict)
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

    #DataFrame with every stop
    dfStops = pd.DataFrame.from_dict(stopsdict)
    try:
        dfStops['stop_id'] = dfStops['stop_id'].astype(int)
    except:
        print("can not convert dfStops: stop_id into int ")

    #DataFrame with every service weekly
    dfWeek = pd.DataFrame.from_dict(calendarWeekdict)

    #DataFrame with every service dates
    dfDates = pd.DataFrame.from_dict(calendarDatesdict)

    #DataFrame with every agency
    df_agency = pd.DataFrame.from_dict(agencyFahrtdict)

    weekDay = [{'Monday': 'Monday'},
               {'Tuesday': 'Tuesday'},
               {'Wednesday': 'Wednesday'},
               {'Thursday': 'Thursday'},
               {'Friday': 'Friday'},
               {'Saturday': 'Saturday'},
               {'Sunday': 'Sunday'}]
    weekDaydf = pd.DataFrame(weekDay)

    # dataframe with the (bus) lines
    inputVar = [{'route_short_name': routeName}]
    varTest = pd.DataFrame(inputVar).set_index('route_short_name')
    inputVarAgency = [{'agency_id': agencyName}]
    varTestAgency = pd.DataFrame(inputVarAgency).set_index('agency_id')
    inputVarService = [{'service_id': serviceName}]
    varTestService = pd.DataFrame(inputVarService).set_index('service_id')


    #conditions for searching in dfs
    cond_FahrplanWeekDays= '''
                select dfTrips.trip_id, dfStops.stop_name, dfStopTimes.stop_sequence, dfStopTimes.arrival_time, dfTrips.service_id, dfStops.stop_id
                from dfStopTimes 
                left join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
                left join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                left join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                left join dfWeek on  dfWeek.service_id = dfTrips.service_id
                left join varTest
                left join varTestAgency
                where dfRoutes.route_short_name = varTest.route_short_name -- in this case the bus line number
                  and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                  and  ( dfWeek.monday=1 
                     and dfWeek.tuesday=1
                     and dfWeek.wednesday=1
                     and dfWeek.thursday=1
                     and dfWeek.friday=1
                      )     
                and dfTrips.direction_id = 0 -- shows the direction of the line 
                order by dfTrips.trip_id;
               '''

    cond_Fahrplan= '''
                select dfTrips.trip_id, dfStops.stop_name, dfStopTimes.stop_sequence, dfStopTimes.arrival_time, dfTrips.service_id, dfStops.stop_id
                from dfStopTimes 
                left join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
                left join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                left join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                left join varTest
                left join varTestAgency
                left join varTestService
                where dfRoutes.route_short_name = varTest.route_short_name -- in this case the bus line number
                  and dfRoutes.agency_id = varTestAgency.agency_id -- in this case the bus line number
                  and dfTrips.service_id = varTestService.service_id
                  and dfTrips.direction_id = 0 -- shows the direction of the line 
                order by dfStopTimes.stop_sequence, dfStopTimes.arrival_time, dfTrips.trip_id;
               '''

    print("dataframes created")
    fahrplan = sqldf(cond_Fahrplan, locals())
    fahrplan.to_csv(routeName + 'TRIPSRoh.csv', header=True, quotechar=' ', index='', sep=';', mode='w', encoding='utf8')
    #fahrplan_pivot = fahrplan.groupby('stop_sequence')['trip_id'].apply(list).reset_index(name='Trips_stops')
    #fahrplan_pivot = fahrplan.unstack(level=0, fill_value=0)
    fahrplan_pivot = fahrplan.pivot(index=['stop_sequence','stop_name'], columns='trip_id', values='arrival_time')
    fahrplan_pivot.to_csv(routeName + 'pivot_table.csv', header=True, quotechar=' ', index='stop_name', sep=';', mode='w', encoding='utf8')

    #releae some memory
    dfTrips = None
    dfStopTimes = None
    dfStops = None
    dfRoutes = None
    dfWeek = None

    zeit = time.time() - last_time
    print("time: {} ".format(zeit))
    return zeit

