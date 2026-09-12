# Dto for GTFS Column Names
class GtfsListDto:
    def __init__(self, stopsList, stopTimesList, tripsList, calendarList, calendar_datesList, routesList, agencyList,
                 feed_info):
        self.stopsList = stopsList
        self.stopTimesList = stopTimesList
        self.tripsList = tripsList
        self.calendarList = calendarList
        self.calendar_datesList = calendar_datesList
        self.routesList = routesList
        self.agencyList = agencyList
        self.feed_info = feed_info

# Dto for GTFS DataFrame Names
class GtfsDataFrameDto:
    """Legacy in-memory source. Planners must treat source frames as read-only."""
    def __init__(self, Routes, Trips, Stoptimes, Stops, Calendarweeks, Calendardates, Agencies, Feedinfos):
        self.Routes = Routes
        self.Trips = Trips
        self.Stoptimes = Stoptimes
        self.Stops = Stops
        self.Calendarweeks = Calendarweeks
        self.Calendardates = Calendardates
        self.Agencies = Agencies
        self.Feedinfos = Feedinfos

    def get_trips(self, route_id=None, direction_id=None, service_ids=None):
        trips = self.Trips
        if route_id is not None:
            trips = trips[trips.route_id == route_id]
        if direction_id is not None:
            trips = trips[trips.direction_id == direction_id]
        if service_ids is not None:
            trips = trips[trips.service_id.isin(service_ids)]
        return trips

    def get_stop_times_for_trips(self, trip_ids):
        return self.Stoptimes[self.Stoptimes.trip_id.isin(trip_ids)]

    def get_stops(self, stop_ids=None):
        return self.Stops if stop_ids is None else self.Stops[self.Stops.stop_id.isin(stop_ids)]

