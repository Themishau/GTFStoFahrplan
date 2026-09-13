"""In-memory GTFS data source used by tests and direct integrations."""

from collections.abc import Iterable

import pandas as pd


class InMemoryGtfsData:
    """Expose data frames through the same query API as the DuckDB adapter."""

    def __init__(
            self,
            routes: pd.DataFrame,
            trips: pd.DataFrame,
            stop_times: pd.DataFrame,
            stops: pd.DataFrame,
            calendar: pd.DataFrame,
            calendar_dates: pd.DataFrame,
            agencies: pd.DataFrame,
            feed_info: pd.DataFrame | None,
    ) -> None:
        self.routes = routes
        self.trips = trips
        self.stop_times = stop_times
        self.stops = stops
        self.calendar = calendar
        self.calendar_dates = calendar_dates
        self.agencies = agencies
        self.feed_info = feed_info

    def get_trips(
            self,
            route_id: str | None = None,
            direction_id: int | None = None,
            service_ids: Iterable[str] | None = None,
    ) -> pd.DataFrame:
        trips = self.trips
        if route_id is not None:
            trips = trips[trips.route_id == route_id]
        if direction_id is not None:
            trips = trips[trips.direction_id == direction_id]
        if service_ids is not None:
            trips = trips[trips.service_id.isin(service_ids)]
        return trips

    def get_stop_times_for_trips(self, trip_ids: Iterable[str]) -> pd.DataFrame:
        return self.stop_times[self.stop_times.trip_id.isin(trip_ids)]

    def get_stops(self, stop_ids: Iterable[str] | None = None) -> pd.DataFrame:
        if stop_ids is None:
            return self.stops
        return self.stops[self.stops.stop_id.isin(stop_ids)]
