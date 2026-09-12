"""Database layout version and the supported GTFS projection.

Increment DATABASE_LAYOUT_VERSION when changing physical tables and provide a
layout migration. Increment CURRENT_GTFS_SCHEMA_VERSION (gtfs_feed.py) when
changing import semantics; older feeds will then require re-importing.
"""
DATABASE_LAYOUT_VERSION = 1
DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

# CSV identifiers remain strings, preserving leading zeroes and mixed IDs.
TABLE_COLUMNS = {
    "agency": {"agency_id": "VARCHAR", "agency_name": "VARCHAR", "agency_url": "VARCHAR",
               "agency_timezone": "VARCHAR"},
    "routes": {"route_id": "VARCHAR", "agency_id": "VARCHAR", "route_short_name": "VARCHAR",
               "route_long_name": "VARCHAR", "route_type": "INTEGER"},
    "trips": {"trip_id": "VARCHAR", "route_id": "VARCHAR", "service_id": "VARCHAR",
              "direction_id": "INTEGER", "block_id": "VARCHAR", "trip_headsign": "VARCHAR"},
    "stops": {"stop_id": "VARCHAR", "stop_name": "VARCHAR", "stop_lat": "DOUBLE",
              "stop_lon": "DOUBLE", "parent_station": "VARCHAR", "location_type": "INTEGER"},
    "stop_times": {"trip_id": "VARCHAR", "arrival_time": "VARCHAR", "departure_time": "VARCHAR",
                   "stop_id": "VARCHAR", "stop_sequence": "INTEGER",
                   "arrival_seconds": "BIGINT", "departure_seconds": "BIGINT"},
    "calendar": {"service_id": "VARCHAR", **{day: "INTEGER" for day in DAYS},
                 "start_date": "DATE", "end_date": "DATE"},
    "calendar_dates": {"service_id": "VARCHAR", "date": "DATE", "exception_type": "INTEGER"},
    "feed_info": {"feed_publisher_name": "VARCHAR", "feed_publisher_url": "VARCHAR",
                  "feed_lang": "VARCHAR", "feed_start_date": "DATE", "feed_end_date": "DATE"},
}

REQUIRED_COLUMNS = {
    "agency": {"agency_name"},
    "routes": {"route_id"},
    "trips": {"trip_id", "route_id", "service_id"},
    "stops": {"stop_id", "stop_name"},
    "stop_times": {"trip_id", "stop_id", "stop_sequence"},
    "calendar": {"service_id", "start_date", "end_date", *DAYS},
    "calendar_dates": {"service_id", "date", "exception_type"},
    "feed_info": set(),
}
REQUIRED_TABLES = {"agency", "routes", "trips", "stops", "stop_times"}
