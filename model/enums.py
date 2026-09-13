"""Enums and GTFS column names used by the application."""

from enum import IntEnum, StrEnum


class ProcessKind(StrEnum):
    """Long-running operations displayed in the progress history."""

    IMPORT_DATA = "import_data"
    CREATE_TIMETABLE = "create_timetable"
    EXPORT_PLAN = "export_plan"


class PlanMode(IntEnum):
    """Timetable creation mode selected by its UI index."""

    DATE = 0
    WEEKDAY = 1
    CIRCULATION_DATE = 2
    CIRCULATION_WEEKDAY = 3


class DirectionIndex(IntEnum):
    """Direction selected by its UI index."""

    FIRST = 0
    SECOND = 1


class TimeFormat(StrEnum):
    """Display format for exported stop times."""

    HOURS_MINUTES = "HH:mm"
    HOURS_MINUTES_SECONDS = "HH:mm:ss"


class RouteColumn(StrEnum):
    ROUTE_ID = "route_id"
    SHORT_NAME = "route_short_name"
    LONG_NAME = "route_long_name"
    AGENCY_ID = "agency_id"


class ModelAction(StrEnum):
    """Commands that may run on the model worker thread."""

    IMPORT_GTFS = "import_gtfs"
    OPEN_CACHED_FEED = "open_cached_feed"
    DELETE_CACHED_FEED = "delete_cached_feed"
    DELETE_ALL_CACHED_FEEDS = "delete_all_cached_feeds"
    CREATE_TIMETABLE = "create_timetable"
    CONTINUE_TIMETABLE = "continue_timetable"


class ErrorMessage(StrEnum):
    NO_IMPORTED_DATA = "No GTFS data is open."
    IMPORT_FAILED = "GTFS data could not be imported."
    PLAN_CREATION_FAILED = "The timetable could not be created."
    INVALID_PATH = "The selected path is not valid."
    NO_TRIPS_IN_DATE_RANGE = "No trips were found in the selected date range."
