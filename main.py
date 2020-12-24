# -*- coding: utf-8 -*-
import csv
import json
import time
import itertools
import pandas as pd
from pandasql import sqldf
from collections import defaultdict

d1 = {1: 2, 3: 4}
d2 = {1: 6, 2: 5, 3: 7}

dd = defaultdict(list)

for d in (d1, d2): # you can list as many input dicts as you want here
    for key, value in d.items():
        dd[key].append(value)

print(dd)


def readGTFSData ():
    # read every line and save in variable
    with open("GTFS_VBB_bereichsscharf/stops.txt", "r", encoding="utf8") as stops:
        stopsList = stops.readlines()
    with open("GTFS_VBB_bereichsscharf/stop_times.txt", "r", encoding="utf8") as stopTimes:
        stopTimesList = stopTimes.readlines()
    with open("GTFS_VBB_bereichsscharf/trips.txt", "r", encoding="utf8") as trips:
        tripsList = trips.readlines()
    with open("GTFS_VBB_bereichsscharf/calendar.txt", "r", encoding="utf8") as calendar:
        calendarList = calendar.readlines()
    with open("GTFS_VBB_bereichsscharf/calendar_dates.txt", "r", encoding="utf8") as calendar_dates:
        calendar_datesList = calendar_dates.readlines()
    with open("GTFS_VBB_bereichsscharf/routes.txt", "r", encoding="utf8") as routes:
        routesList = routes.readlines()
    return stopsList, stopTimesList, tripsList, calendarList, calendar_datesList, routesList

# these are some attempts to get the data fast
def maybefasterGetGTFS(tripsList, stopsList, stopTimesList, calendarList, calendar_datesList):
    last_time = time.time()

    busFahrt_dict = []
    for trip in tripsList:
        trip = trip.replace(", ", " ")
        trip = trip.replace('"', "")
        trip = trip.split(",")
        if trip[0] == '17416_900':
            for stopTime in stopTimesList:
                stopTime = stopTime.replace(", ", " ")
                stopTime = stopTime.replace('"', "")
                stopTime = stopTime.split(",")
                if trip[2] == stopTime[0]:
                    for stops in stopsList:
                        stops = stops.replace(", ", " ")
                        stops = stops.replace('"', "")
                        stops = stops.split(",")
                        busFahrtJson = {"Route_ID": trip[0],
                                        "Trip_ID": trip[2],
                                        "Richtung": trip[3],
                                        "Haltestelle": stops[3],
                                        "Ankunftszeit": stopTime[1],
                                        "Abfahrtzeit": stopTime[2]
                                        }
                        busFahrt_dict.append(busFahrtJson)
    zeit = time.time() - last_time
    print("time: {} ".format(zeit))
def slowGetGTFSList(tripsList, stopsList, stopTimesList, calendarList, calendar_datesList):
    last_time = time.time()
    busFahrt = []
    busFahrtDict = []
    stopFahrt = []
    stopZeit = []

    calendarWeek = []
    calendarDates = []

    for trip in tripsList:
        trip = trip.replace(", ", " ")
        trip = trip.replace('"', "")
        trip = trip.replace('\n', "")
        data = trip.split(",")
        dataDict = {
            "route_id": trip[0],
            "service_id": trip[1],
            "trip_id": trip[2],
            "trip_headsign": trip[3],
            "trip_short_name": trip[4],
            "direction_id": trip[5],
            "block_id": trip[6],
            "shape_id": trip[7],
            "wheelchair_accessible": trip[8],
            "bikes_allowed": trip[9]
        }
        busFahrtDict.append(dataDict)
        busFahrt.append(data)
    print("trips loaded")
    tripsList = ""

    for haltestellen in stopsList:
        haltestellen = haltestellen.replace(", ", " ")
        haltestellen = haltestellen.replace('"', "")
        haltestellen = haltestellen.replace('\n', "")
        stopData = haltestellen.split(",")
        stopFahrt.append(stopData)
    print("stops loaded")
    stopsList = ""

    for stopTime in stopTimesList:
        stopTime = stopTime.replace(", ", " ")
        stopTime = stopTime.replace('"', "")
        stopTime = stopTime.replace('\n', "")
        stopTimeData = stopTime.split(",")
        stopZeit.append(stopTimeData)
    print("stop times loaded")
    stopTimesList = ""

    for calendarDate in calendarList:
        calendarDate = calendarDate.replace(", ", " ")
        calendarDate = calendarDate.replace('"', "")
        calendarDate = calendarDate.replace('\n', "")
        calendarData = calendarDate.split(",")
        calendarWeek.append(calendarData)
    print("calendar loaded")
    calendarList = ""

    for calendarDate in calendar_datesList:
        calendarDate = calendarDate.replace(", ", " ")
        calendarDate = calendarDate.replace('"', "")
        calendarDate = calendarDate.replace('\n', "")
        calendarDatesData = calendarDate.split(",")

        calendarDates.append(calendarDatesData)
    print("calendar dates loaded")
    calendar_datesList = ""

    tripID = '146410555'
    routeID = '17416_900'
    #getTrips(tripID, stopZeit, busFahrt, stopFahrt)
    #getStopstoRoute(routeID, stopZeit, busFahrt, stopFahrt)
    getFahrtOfrouteFahrplan(routeID, stopZeit, busFahrt, stopFahrt)
    #getStopstoTripBIN(routeID, stopZeit, busFahrt, stopFahrt)
    #getAllStops(stopZeit, busFahrt, stopFahrt)
def getTripsFOR(tripID, stopZeit, busFahrt, stopFahrt):
    last_time = time.time()
    busFahrt_dict = []
    tripData = {}
    for fahrt in busFahrt:
        if tripID == fahrt[2]:
            tripData["Route_ID"] = fahrt[0]
            tripData["Trip_ID"] = fahrt[2]
            tripData["Richtung"] = fahrt[3]

    for stopsTimes in stopZeit:
        if stopsTimes[0] == tripID:
            for haltestellen in stopFahrt:
                if haltestellen[0] == stopsTimes[3]:
                    busFahrtJson = {"Route_ID": tripData.get('Route_ID'),
                                    "Trip_ID": tripData.get('Trip_ID'),
                                    "Richtung": tripData.get('Richtung'),
                                    "Haltestelle": haltestellen[2],
                                    "Ankunftszeit": stopsTimes[1],
                                    "Abfahrtzeit": stopsTimes[2]
                                    }
                    busFahrt_dict.append(busFahrtJson)
                    break

    zeit = time.time() - last_time
    print("time: {} ".format(zeit))
    with open("halt.json", "w", encoding="utf8") as json_output:
        json.dump(busFahrt_dict, json_output, indent=2)

def slowGetGTFSdict(stopsList, stopTimesList, tripsList, calendarList, calendar_datesList, routesList):
    busFahrt = []
    stopFahrt = []
    stopZeit = []

    calendarWeek = []
    calendarDates = []
    routesFahrt = []

    for trip in tripsList:
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
        busFahrt.append(dataDict)
    print("trips loaded")
    tripsList = None

    for haltestellen in stopsList:
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
        stopFahrt.append(dataDict)
    print("stops loaded")
    stopsList = None

    for stopTime in stopTimesList:
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
        stopZeit.append(dataDict)
    print("stop times loaded")
    stopTimesList = None

    for calendarDate in calendarList:
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
        calendarWeek.append(dataDict)
    print("calendar loaded")
    calendarList = None

    for calendarDate in calendar_datesList:
        calendarDate = calendarDate.replace(", ", " ")
        calendarDate = calendarDate.replace('"', "")
        calendarDate = calendarDate.replace('\n', "")
        calendarDatesData = calendarDate.split(",")
        dataDict = {
            "service_id": calendarDatesData[0],
            "date": calendarDatesData[1],
            "exception_type": calendarDatesData[2],
        }
        calendarDates.append(dataDict)
    print("calendar dates loaded")
    calendar_datesList = None

    for routes in routesList:
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
        routesFahrt.append(dataDict)
    print("routes loaded")
    routesList = None

    tripID = '146410555'
    routeID = '17416_900'
    routeName = '100'
    #getFahrtOfroute_short_name(routeName, stopZeit, busFahrt, stopFahrt, routesFahrt)
    getFahrtOfrouteFahrplan(routeName, stopZeit, busFahrt, stopFahrt, routesFahrt, calendarWeek)


def getFahrtOfrouteFahrplan(routeName, stopZeit, busFahrt, stopFahrt, routesFahrt, calendarWeek):
    last_time = time.time()

    #DataFrame for every route
    dfRoutes = pd.DataFrame(routesFahrt).set_index('route_id')

    #DataFrame with every trip
    dfTrips = pd.DataFrame(busFahrt).set_index('trip_id')

    #DataFrame with every stop (time)
    dfStopTimes = pd.DataFrame(stopZeit).set_index(['trip_id', 'stop_id'])

    #DataFrame with every stop
    dfStops = pd.DataFrame(stopFahrt).set_index('stop_id')

    #DataFrame with every service weekly
    dfWeek = pd.DataFrame(calendarWeek).set_index('service_id')

    inputVar = [{'route_id': routeName}]
    weekDay = [{'Monday': 'Monday'},
               {'Tuesday': 'Tuesday'},
               {'Wednesday': 'Wednesday'},
               {'Thursday': 'Thursday'},
               {'Friday': 'Friday'},
               {'Saturday': 'Saturday'},
               {'Sunday': 'Sunday'}]

    varTest = pd.DataFrame(inputVar).set_index('route_id')
    weekDaydf = pd.DataFrame(weekDay)
    cond_join= '''
                select dfTrips.trip_id, dfTrips.route_id, dfStops.stop_name, dfStopTimes.arrival_time
                from dfStopTimes 
                left join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
                left join dfWeek on  dfWeek.service_id = dfTrips.service_id
                left join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                left join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                left join varTest
                left join weekDaydf
                where dfRoutes.route_short_name = varTest.route_id;
               '''

    combo = sqldf(cond_join, locals())
    #releae some memory
    dfTrips = None
    dfStopTimes = None
    dfStops = None
    dfRoutes = None
    dfWeek = None

    combo.to_csv(r'pandas.txt', header=True, index='dfTrips.trip_id', sep=' ', mode='w', encoding='utf8')

    zeit = time.time() - last_time
    print("time: {} ".format(zeit))




def main():
    #maybefasterGetGTFS(tripsList, stopsList, stopTimesList, calendarList, calendar_datesList)
    GTFSData = readGTFSData()
    slowGetGTFSdict(GTFSData[0], GTFSData[1], GTFSData[2], GTFSData[3], GTFSData[4], GTFSData[5])

if __name__ == '__main__':
    print("start")
    main()

# attempts to parse through the data fast
def getFahrtOfroute_short_name(routeName, stopZeit, busFahrt, stopFahrt, routesFahrt):
    last_time = time.time()

    dataFrameroutesFahrt = pd.DataFrame(routesFahrt).set_index('route_id')
    dataFramebusFahrt = pd.DataFrame(busFahrt).set_index('trip_id')
    dataFramestopZeitTRIP = pd.DataFrame(stopZeit).set_index('trip_id', 'stop_id')
    dataFramestop = pd.DataFrame(stopFahrt).set_index('stop_id')
    inputVar = [{'route_id': routeName}]
    varTest = pd.DataFrame(inputVar).set_index('route_id')

    cond_join= '''
                select dataFramebusFahrt.trip_id, dataFramebusFahrt.route_id,dataFrameroutesFahrt.route_short_name 
                from dataFramebusFahrt 
                left join dataFrameroutesFahrt 
                left join varTest
                on dataFramebusFahrt.route_id = dataFrameroutesFahrt.route_id 
                where dataFrameroutesFahrt.route_short_name = varTest.route_id;
               '''

    combo = sqldf(cond_join, locals())

    dataFramebusFahrt = None
    dataFramestopZeitTRIP = None
    dataFramestop = None


    combo.to_csv(r'pandas.txt', header=True, index='dataFramebusFahrt.trip_id', sep=' ', mode='w', encoding='utf8')
    zeit = time.time() - last_time
    print("time: {} ".format(zeit))
def getFahrtOfroute_short_nameKURZ(routeName, stopZeit, busFahrt, stopFahrt, routesFahrt):
    last_time = time.time()

    dataFrameroutesFahrt = pd.DataFrame(routesFahrt).set_index('route_id')
    dataFramebusFahrt = pd.DataFrame(busFahrt).set_index('trip_id')
    dataFramestopZeitTRIP = pd.DataFrame(stopZeit).set_index('trip_id', 'stop_id')
    dataFramestop = pd.DataFrame(stopFahrt).set_index('stop_id')
    inputVar = [{'route_id': routeName}]
    varTest = pd.DataFrame(inputVar).set_index('route_id')

    cond_join= '''
                select dataFramebusFahrt.trip_id, dataFramebusFahrt.route_id,dataFrameroutesFahrt.route_short_name 
                from dataFramebusFahrt 
                left join dataFrameroutesFahrt 
                left join varTest
                on dataFramebusFahrt.route_id = dataFrameroutesFahrt.route_id 
                where dataFrameroutesFahrt.route_short_name = varTest.route_id;
               '''

    combo = sqldf(cond_join, locals())

    dataFramebusFahrt = None
    dataFramestopZeitTRIP = None
    dataFramestop = None
    combo.to_csv(r'pandas.txt', header=True, index='dataFramebusFahrt.trip_id', sep=' ', mode='w', encoding='utf8')
    zeit = time.time() - last_time
    print("time: {} ".format(zeit))
def getStopstoRouteFOR(routeID, stopZeit, busFahrt, haltestellen):
    last_time = time.time()
    busFahrt_dict = []
    bufFahrtcurrentFahrtJson = {}
    currentStops = []


    for fahrt in busFahrt:
        if fahrt[0] == routeID:
            bufFahrtcurrentFahrtJson["Route_ID"] = fahrt[0]
            bufFahrtcurrentFahrtJson["Trip_ID"] = fahrt[2]
            bufFahrtcurrentFahrtJson["Richtung"] = fahrt[3]
            busFahrt_dict.append(bufFahrtcurrentFahrtJson)
            bufFahrtcurrentFahrtJson = {}

    for stopZeiten in stopZeit:
        for fahrten in busFahrt_dict:
            if fahrten['Trip_ID'] == stopZeiten[0]:
                for haltestelle in haltestellen:
                    if haltestellen[0] == stopZeiten[3]:
                        stopJson = {"Haltestelle": haltestelle[2],
                                    "Ankunftszeit": stopZeiten[1],
                                    "Abfahrtzeit": stopZeiten[2]
                                    }
                        currentStops.append(stopJson)
                        break
                        # print(busFahrtJson)
                fahrten["Haltestellen"] = currentStops
                currentStops = []

    zeit = time.time() - last_time
    print("time: {} ".format(zeit))
    with open("halt.json", "w", encoding="utf8") as json_output:
        json.dump(busFahrt_dict, json_output, indent=2)
def getAllStopsFOR(stopZeit, busFahrt, stopFahrt):
    last_time = time.time()
    busFahrt_dict = []
    bufFahrtcurrentFahrtJson = {}
    currentStops = []

    for fahrt in busFahrt:
        bufFahrtcurrentFahrtJson["Route_ID"] = fahrt[0]
        bufFahrtcurrentFahrtJson["Trip_ID"] = fahrt[2]
        bufFahrtcurrentFahrtJson["Richtung"] = fahrt[3]
        for stopsTimes in stopZeit:
            if fahrt[2] == stopsTimes[0]:
                for haltestellen in stopFahrt:
                    if haltestellen[0] == stopsTimes[3]:
                        stopJson = {"Haltestelle": haltestellen[2],
                                    "Ankunftszeit": stopsTimes[1],
                                    "Abfahrtzeit": stopsTimes[2]
                                    }
                        currentStops.append(stopJson)
                        break
                        # print(busFahrtJson)

        bufFahrtcurrentFahrtJson["Haltestellen"] = currentStops
        busFahrt_dict.append(bufFahrtcurrentFahrtJson)
        bufFahrtcurrentFahrtJson = {}
    zeit = time.time() - last_time
    print("time: {} ".format(zeit / 60))

    with open("halt.json", "w", encoding="utf8") as json_output:
        json.dump(busFahrt_dict, json_output, indent=2)
def getAllStopsNEWFOR(stopZeit, busFahrt, stopFahrt):
    last_time = time.time()
    length = len(stopZeit)

    firstPosition = 0
    lastPosition = len(stopZeit)

    midPosition = (lastPosition / 2) if (lastPosition % 2) == 0 else (lastPosition / 2) + 1
    busFahrt_dict = []
    bufFahrtcurrentFirstFahrtJson = {}
    bufFahrtcurrentLastFahrtJson = {}

    while firstPosition <= midPosition:
        currentStopsFirst = []
        currentStopsLast = []
        firstStop = stopZeit[firstPosition]
        lastStop = stopZeit[lastPosition]
        for fahrt in busFahrt:
            if fahrt[2] == firstStop[0]:
                bufFahrtcurrentFirstFahrtJson["Route_ID"] = fahrt[0]
                bufFahrtcurrentFirstFahrtJson["Trip_ID"] = fahrt[2]
                bufFahrtcurrentFirstFahrtJson["Richtung"] = fahrt[3]
                for stop in stopFahrt:
                    if stop[0] == firstStop[3]:
                        stopJson = {"Haltestelle": stop[2],
                                    "Ankunftszeit": firstStop[1],
                                    "Abfahrtzeit": firstStop[2]
                                    }
                        currentStopsFirst.append(stopJson)
                        break
            if fahrt[2] == lastStop[0]:
                bufFahrtcurrentLastFahrtJson["Route_ID"] = fahrt[0]
                bufFahrtcurrentLastFahrtJson["Trip_ID"] = fahrt[2]
                bufFahrtcurrentLastFahrtJson["Richtung"] = fahrt[3]
                for stop in stopFahrt:
                    if stop[0] == lastStop[3]:
                        stopJson = {"Haltestelle": stop[2],
                                    "Ankunftszeit": lastStop[1],
                                    "Abfahrtzeit": lastStop[2]
                                    }
                        currentStopsLast.append(stopJson)
                        break
        firstPosition += 1
        lastPosition -= 1
    zeit = time.time() - last_time
    print("time: {} ".format(zeit / 60))
def getStopstoTripBINFOR(routeID, stopZeit, busFahrt, stopFahrt):
    last_time = time.time()
    length = len(stopZeit)

    firstPosition = 0
    lastPosition = len(stopZeit) - 1

    midPosition = (lastPosition / 2) if (lastPosition % 2) == 0 else ((lastPosition - 1) / 2)
    busFahrt_dict = []
    bufFahrtcurrentFirstFahrtJson = {}
    bufFahrtcurrentLastFahrtJson = {}
    print (midPosition)
    while firstPosition <= midPosition:
        firstStop = stopZeit[firstPosition]
        lastStop = stopZeit[lastPosition]
        for fahrt in busFahrt:
            if fahrt[0] == routeID:
                if fahrt[2] == firstStop[0]:
                    bufFahrtcurrentFirstFahrtJson["Route_ID"] = fahrt[0]
                    bufFahrtcurrentFirstFahrtJson["Trip_ID"] = fahrt[2]
                    bufFahrtcurrentFirstFahrtJson["Richtung"] = fahrt[3]
                    for stop in stopFahrt:
                        if stop[0] == firstStop[3]:
                            bufFahrtcurrentFirstFahrtJson["Haltestelle"] = stop[2]
                            bufFahrtcurrentFirstFahrtJson["Ankunftszeit"] = firstStop[1]
                            bufFahrtcurrentFirstFahrtJson["Abfahrtzeit"] = firstStop[2]
                            busFahrt_dict.append(bufFahrtcurrentFirstFahrtJson)
                            print(busFahrt_dict)
                            break
                    break
                if fahrt[2] == lastStop[0]:
                    bufFahrtcurrentLastFahrtJson["Route_ID"] = fahrt[0]
                    bufFahrtcurrentLastFahrtJson["Trip_ID"] = fahrt[2]
                    bufFahrtcurrentLastFahrtJson["Richtung"] = fahrt[3]
                    for stop in stopFahrt:
                        if stop[0] == lastStop[3]:
                            bufFahrtcurrentFirstFahrtJson["Haltestelle"] = stop[2]
                            bufFahrtcurrentFirstFahrtJson["Ankunftszeit"] = lastStop[1]
                            bufFahrtcurrentFirstFahrtJson["Abfahrtzeit"] = lastStop[2]
                            busFahrt_dict.append(bufFahrtcurrentLastFahrtJson)
                            print(busFahrt_dict)
                            break
                    break


        firstPosition += 1
        lastPosition -= 1
        if firstPosition % 10000 == 0:
            print(str(firstPosition) + " Haltestellen done"  " Zeit: "  + str((time.time() - last_time)))

    zeit = time.time() - last_time
    print("time: {} ".format(zeit / 60))

"""
# Make your pysqldf object:
pysqldf = lambda q: sqldf(q, globals())

# Write your query in SQL syntax, here you can use df as a normal SQL table
cond_join= '''
    select 
        df_left.*,
        df_right.*
    from df as df_left
    join df as df_right
    on
        df_left.[Amount] > (df_right.[Amount]+10)

'''

# Now, get your queries results as dataframe using the sqldf object that you created
pysqldf(cond_join)

    id  Name    Amount  id    Name  Amount
0   A003    C   120    A001   A   100
1   A005    D   150    A001   A   100
2   A005    D   150    A002   B   110
3   A005    D   150    A003   C   120


"""