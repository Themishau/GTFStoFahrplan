from enum import Enum, auto


class CreatePlanMode(Enum):
    """ Types of methods """
    date = 'date'
    weekday = 'weekday'


class GtfsColumnNames(Enum):
    stopsList = 'stopsList'
    stopTimesList = 'stopTimesList'
    tripsList = 'tripsList'
    calendarList = 'calendarList'
    calendar_datesList = 'calendar_datesList'
    routesList = 'routesList'
    agencyList = 'agencyList'
    feed_info = 'feed_info'


class GtfsDfNames(Enum):
    Routes = 'Routes'
    Trips = 'Trips'
    Stoptimes = 'Stoptimes'
    Stops = 'Stops ='
    Calendarweeks = 'Calendarweeks'
    Calendardates = 'Calendardates'
    Agencies = 'Agencies'
    Feedinfos = 'Feedinfos'


class SchedulePlanerFunctionEnum(Enum):
    import_GTFS = 'import_GTFS'
    update_routes_list = 'update_routes_list'
    update_stopname_create_list = 'update_stopname_create_list'
    update_date_range = 'update_date_range'
    update_weekday_list = 'update_weekday_list'
    update_agency_list = 'update_agency_list'
    update_weekdate_option = 'update_weekdate_option'
    message = 'message'
    update_progress_bar = 'update_progress_bar'


class ImportDataFuncitonEnum(Enum):
    import_GTFS = 'import_GTFS'
    update_progress_bar = 'update_progress_bar'
