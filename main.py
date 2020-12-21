# -*- coding: utf-8 -*-
import csv
import json

busFahrt = []
stopFahrt = []
stopZeit = []

busFahrt_dict = []

# read every line and save in variable
with open("GTFS_VBB_bereichsscharf/stops.txt", "r", encoding="utf8") as stops:
    stopsList = stops.readlines()
with open("GTFS_VBB_bereichsscharf/stop_times.txt", "r", encoding="utf8") as stopTimes:
    stopTimesList = stopTimes.readlines()
with open("GTFS_VBB_bereichsscharf/trips.txt", "r", encoding="utf8") as trips:
    tripsList = trips.readlines()

for trip in tripsList:
    trip = trip.replace(", ", " ")
    data = trip.split(",")
    busFahrt.append(data)

for stopTime in stopTimesList:
    data = stopTime.split(",")


    """
    for fahrt in busFahrt:
        if data[0] == fahrt[2]:
            print(fahrt[3])
        
    for stop in stopFahrt
        if stop[0]
    """
for fahrt in busFahrt:
    """
    "route_id","service_id","trip_id","trip_headsign","trip_short_name","direction_id","block_id","shape_id","wheelchair_accessible","bikes_allowed"
    """
    busFahrtJson = {"Route_ID": fahrt[0], "Trip_ID": fahrt[2], "Beschilderung": fahrt[3]}
    busFahrt_dict.append(busFahrtJson)

# print(busFahrt_dict)
