"""Planner-facing contract shared by in-memory and DuckDB data sources."""

from collections.abc import Iterable
from typing import Protocol

import pandas as pd


class GtfsDataSource(Protocol):
    @property
    def agencies(self) -> pd.DataFrame: ...

    @property
    def routes(self) -> pd.DataFrame: ...

    @property
    def calendar(self) -> pd.DataFrame: ...

    @property
    def calendar_dates(self) -> pd.DataFrame: ...

    @property
    def feed_info(self) -> pd.DataFrame | None: ...

    def get_trips(
            self,
            route_id: str | None = None,
            direction_id: int | None = None,
            service_ids: Iterable[str] | None = None,
    ) -> pd.DataFrame: ...

    def get_stop_times_for_trips(self, trip_ids: Iterable[str]) -> pd.DataFrame: ...

    def get_stops(self, stop_ids: Iterable[str] | None = None) -> pd.DataFrame: ...
