"""Planner-facing contract shared by the legacy DTO and cached feed adapter."""
from typing import Iterable, Protocol

import pandas as pd


class GtfsDataSource(Protocol):
    @property
    def Agencies(self) -> pd.DataFrame: ...

    @property
    def Routes(self) -> pd.DataFrame: ...

    @property
    def Calendarweeks(self) -> pd.DataFrame: ...

    @property
    def Calendardates(self) -> pd.DataFrame: ...

    @property
    def Feedinfos(self) -> pd.DataFrame | None: ...

    def get_trips(self, route_id: str | None = None, direction_id: int | None = None,
                  service_ids: Iterable[str] | None = None) -> pd.DataFrame: ...

    def get_stop_times_for_trips(self, trip_ids: Iterable[str]) -> pd.DataFrame: ...

    def get_stops(self, stop_ids: Iterable[str] | None = None) -> pd.DataFrame: ...
