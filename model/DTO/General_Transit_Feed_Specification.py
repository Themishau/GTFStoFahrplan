# DTO for GTFS Column Names
class GtfsListDto:
    def __init__(self, stopsList, stopTimesList, tripsList, calendarList, calendar_datesList, routesList, agencyList, feed_info):
        self.stopsList = stopsList
        self.stopTimesList = stopTimesList
        self.tripsList = tripsList
        self.calendarList = calendarList
        self.calendar_datesList = calendar_datesList
        self.routesList = routesList
        self.agencyList = agencyList
        self.feed_info = feed_info

# DTO for GTFS DataFrame Names
class GtfsDataFrameDto:
    def __init__(self, Routes, Trips, Stoptimes, Stops, Calendarweeks, Calendardates, Agencies, Feedinfos):
        self.Routes = Routes
        self.Trips = Trips
        self.Stoptimes = Stoptimes
        self.Stops = Stops
        self.Calendarweeks = Calendarweeks
        self.Calendardates = Calendardates
        self.Agencies = Agencies
        self.Feedinfos = Feedinfos