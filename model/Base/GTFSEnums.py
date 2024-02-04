from enum import Enum, auto

class CreatePlanMode(Enum):
    """ Types of methods """
    date = 'date'
    weekday = 'weekday'



class Gtfs_Column_Names(Enum):
    stopsList = 'stopsList'
    stopTimesList = 'stopTimesList'
    tripsList = 'tripsList'
    calendarList = 'calendarList'
    calendar_datesList = 'calendar_datesList'
    routesList = 'routesList'
    agencyList = 'agencyList'
    feed_info  = 'feed_info'
class Gtfs_Df_Names(Enum):
    Routes = 'Routes'
    Trips = 'Trips'
    Stoptimes = 'Stoptimes'
    Stops = 'Stops ='
    Calendarweeks = 'Calendarweeks'
    Calendardates = 'Calendardates'
    Agencies = 'Agencies'
    Feedinfos = 'Feedinfos'