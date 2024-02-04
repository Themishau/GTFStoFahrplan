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
