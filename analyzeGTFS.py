# -*- coding: utf-8 -*-
import time
import pandas as pd
from pandasql import sqldf

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

    gtfsData = [stopsList, stopTimesList, tripsList, calendarList, calendar_datesList, routesList]

    stopsList = None
    stopTimesList = None
    tripsList = None
    calendarList = None
    calendar_datesList = None
    routesList = None
    return gtfsData

def slowGetGTFSdict(inputgtfsData):
    tripdict = []
    stopsdict = []
    stopTimesdict = []

    calendarWeekdict = []
    calendarDatesdict = []
    routesFahrtdict = []

    for haltestellen in inputgtfsData[0]:
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

    for stopTime in inputgtfsData[1]:
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

    for trip in inputgtfsData[2]:
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

    for calendarDate in inputgtfsData[3]:
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

    for calendarDate in inputgtfsData[4]:
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

    for routes in inputgtfsData[5]:
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


    tripID = '146410555'
    routeID = '17416_900'
    routeName = '100'
    print("GTFS loaded")
    #getFahrtOfroute_short_name(routeName, stopTimesdict, tripdict, stopsdict, routesFahrtdict)
    getFahrtOfrouteFahrplan(routeName, stopsdict, stopTimesdict, tripdict, calendarWeekdict, calendarDatesdict, routesFahrtdict)

def getFahrtOfrouteFahrplan(routeName, stopsdict, stopTimesdict, tripdict, calendarWeekdict, calendarDatesdict, routesFahrtdict):
    last_time = time.time()

    #DataFrame for every route
    dfRoutes = pd.DataFrame(routesFahrtdict).set_index('route_id')

    #DataFrame with every trip
    dfTrips = pd.DataFrame(tripdict).set_index('trip_id')

    #DataFrame with every stop (time)
    dfStopTimes = pd.DataFrame(stopTimesdict).set_index(['trip_id', 'stop_id'])

    #DataFrame with every stop
    dfStops = pd.DataFrame(stopsdict).set_index('stop_id')

    #DataFrame with every service weekly
    dfWeek = pd.DataFrame(calendarWeekdict).set_index('service_id')

    #DataFrame with every service dates
    dfDates = pd.DataFrame(calendarDatesdict).set_index('service_id', 'date')

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



    cond_weekdays= '''
                select dfTrips.trip_id, dfTrips.route_id, dfStopTimes.stop_sequence, dfStops.stop_name, dfStopTimes.stop_headsign, dfStopTimes.arrival_time
                from dfStopTimes 
                inner join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
                inner join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                inner join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                inner join dfWeek on  dfWeek.service_id = dfTrips.service_id
                left join varTest
                where dfRoutes.route_short_name = varTest.route_short_name
                  and not ( dfWeek.saturday= 1 
                        OR dfWeek.sunday= 1 
                      )                
                and dfTrips.direction_id = 0
                order by dfTrips.trip_id, dfStopTimes.arrival_time;
               '''

    cond_Fahrplan= '''
                select dfStops.stop_name, GROUP_CONCAT(dfStopTimes.arrival_time, ';') as 'stop times mon-fri'
                from dfStopTimes 
                inner join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
                inner join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                inner join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                inner join dfWeek on  dfWeek.service_id = dfTrips.service_id
                left join varTest
                where dfRoutes.route_short_name = varTest.route_short_name -- in this case the bus line number
                  and  ( dfWeek.friday= 1  
                      )                
                and dfTrips.direction_id = 0 -- shows the direction of the line 
                group by dfStopTimes.stop_sequence
                order by dfTrips.trip_id, dfStopTimes.arrival_time;
               '''

    cond_exceptions ='''
                select dfTrips.trip_id, dfTrips.route_id, dfStops.stop_name, dfStopTimes.stop_headsign, dfStopTimes.arrival_time, dfWeek.monday, dfWeek.tuesday, dfWeek.wednesday, dfWeek.thursday, dfWeek.friday, dfWeek.saturday, dfWeek.sunday
                from dfStopTimes 
                left join dfTrips on dfStopTimes.trip_id = dfTrips.trip_id
                left join dfStops on dfStopTimes.stop_id = dfStops.stop_id
                left join dfRoutes on dfRoutes.route_id  = dfTrips.route_id
                left join dfWeek on  dfWeek.service_id = dfTrips.service_id
                left join varTest
                where dfRoutes.route_short_name = varTest.route_id
                  and dfTrips.direction_id = 0
                  and dfWeek.service_id in (select dfDates.service_id
                                            from dfDates
                                            where dfDates.exception_type = 1
                                            group by dfDates.service_id)
                  and ( dfWeek.monday= 1 
                        OR dfWeek.tuesday= 1 
                        OR dfWeek.wednesday= 1 
                        OR dfWeek.thursday= 1 
                        OR dfWeek.friday= 1
                      )
                order by dfTrips.trip_id;
               '''

    fahrplan = sqldf(cond_Fahrplan, locals())
    #fahrplanlike = sqldf(cond_Fahrplan, locals())
    #releae some memory
    dfTrips = None
    dfStopTimes = None
    dfStops = None
    dfRoutes = None
    dfWeek = None

    fahrplan.to_csv(routeName + '.csv', header=True, quotechar=' ', index='', sep=';', mode='w', encoding='utf8')

    zeit = time.time() - last_time
    print("time: {} ".format(zeit))