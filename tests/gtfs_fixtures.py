import csv
import io
import zipfile
from pathlib import Path


def make_feed(path: Path, *, publisher='Transit, "City"', optional=True, calendar=True,
              invalid_stop_sequence=False, extra_trip=True):
    tables = {
        "agency": (["agency_id", "agency_name", "agency_url", "agency_timezone"],
                   [["001", publisher, "https://example.test", "Europe/Berlin"]]),
        "routes": (["route_id", "agency_id", "route_short_name", "route_long_name", "route_type"],
                   [["r1", "001", "10", "City line", 3], ["r2", "001", "20", "Other line", 3]]),
        "trips": (["trip_id", "route_id", "service_id", "direction_id", "block_id"],
                  [["t1", "r1", "s1", 0, "vehicle-01"], ["t2", "r1", "s1", 1, "vehicle-01"]] +
                  ([["t3", "r2", "s1", 0, "vehicle-02"]] if extra_trip else [])),
        "stops": (["stop_id", "stop_name"], [["01", 'Central, "A"'], ["02", "Market"]]),
        "stop_times": (["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence", "unused"],
                       [["t1", "06:30:00", "06:30:00", "01", "bad" if invalid_stop_sequence else 1, "x,y"],
                        ["t1", "06:40:00", "06:40:00", "02", 2, ""],
                        ["t2", "06:45:00", "06:45:00", "02", 1, ""],
                        ["t2", "06:55:00", "06:55:00", "01", 2, ""]] +
                       ([["t3", "24:15:00", "25:30:00", "01", 1, ""]] if extra_trip else [])),
        "calendar_dates": (["service_id", "date", "exception_type"], [["s1", "20260912", 1]]),
        "feed_info": (["feed_publisher_name", "feed_start_date", "feed_end_date"],
                      [[publisher, "20260912", "20260913"]]),
    }
    if calendar:
        tables["calendar"] = (
            ["service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
             "start_date", "end_date"],
            [["s1", 1, 1, 1, 1, 1, 1, 1, "20260912", "20260913"]])
    if not optional:
        for table, remove in {"agency": {"agency_id"}, "routes": {"agency_id"},
                              "trips": {"direction_id", "block_id"}}.items():
            header, rows = tables[table]
            indices = [i for i, column in enumerate(header) if column not in remove]
            tables[table] = ([header[i] for i in indices], [[row[i] for i in indices] for row in rows])
        del tables["feed_info"]
    with zipfile.ZipFile(path, "w") as archive:
        for table, (header, rows) in tables.items():
            stream = io.StringIO(newline="")
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)
            archive.writestr(f"{table}.txt", stream.getvalue().encode("utf-8-sig"))
    return path
