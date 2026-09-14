"""Temporary bridge for the Pandas planner. This object stores no GTFS rows.

Source frames must be treated as read-only. Large stop times are available only
through an explicit trip query. The in-memory adapter exposes the same query
methods for tests and direct integrations.
"""
from collections.abc import Iterable

import pandas as pd

from model.domain.gtfs_feed import GtfsFeed
from model.infrastructure.database.gtfs_repository import GtfsRepository
from model.infrastructure.database.schema import DAYS


class CachedGtfsData:
    def __init__(self, feed: GtfsFeed, repository: GtfsRepository) -> None:
        self.feed = feed
        self.repository = repository

    @property
    def agencies(self) -> pd.DataFrame:
        return self.repository.get_agencies(self.feed.feed_id)

    @property
    def routes(self) -> pd.DataFrame:
        return self.repository.get_routes(self.feed.feed_id).sort_values("route_short_name")

    @property
    def calendar(self) -> pd.DataFrame:
        calendar = self.repository.get_calendar(self.feed.feed_id)
        exceptions = self.repository.get_calendar_dates(self.feed.feed_id)
        # GTFS permits services defined exclusively by calendar_dates. Supply a
        # zero-weekday calendar envelope for the legacy exception-handling code.
        additions = exceptions[(exceptions.exception_type == 1) & ~exceptions.service_id.isin(calendar.service_id)]
        if not additions.empty:
            extra = additions.groupby("service_id")["date"].agg(start_date="min", end_date="max").reset_index()
            for day in DAYS:
                extra[day] = 0
            calendar = pd.concat([calendar, extra], ignore_index=True)
        for column in ("start_date", "end_date"):
            calendar[column] = pd.to_datetime(calendar[column]).dt.strftime("%Y%m%d")
        for day in DAYS:
            calendar[day] = calendar[day].astype("string")
        return calendar

    @property
    def calendar_dates(self) -> pd.DataFrame:
        result = self.repository.get_calendar_dates(self.feed.feed_id)
        result["date"] = pd.to_datetime(result["date"])
        result["date_day_format"] = result["date"]
        result["day"] = result["date"].dt.day_name()
        return result

    @property
    def feed_info(self) -> pd.DataFrame | None:
        result = self.repository.get_feed_info(self.feed.feed_id)
        return None if result.empty else result

    def get_trips(
            self,
            route_id: str | None = None,
            direction_id: int | None = None,
            service_ids: Iterable[str] | None = None,
    ) -> pd.DataFrame:
        return self.repository.get_trips(self.feed.feed_id, route_id, direction_id, service_ids)

    def get_stop_times_for_trips(self, trip_ids: Iterable[str]) -> pd.DataFrame:
        return self.repository.get_stop_times_for_trips(self.feed.feed_id, trip_ids)

    def get_stops(self, stop_ids: Iterable[str] | None = None) -> pd.DataFrame:
        return self.repository.get_stops(self.feed.feed_id, stop_ids)
