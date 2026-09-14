"""Queries used to populate planning choices from a GTFS source."""

import pandas as pd

from model.domain.gtfs_data_source import GtfsDataSource
from model.domain.planning_settings import PlanningSettings


class GtfsDataAnalyzer:
    @staticmethod
    def get_routes_for_agency(
            gtfs_data: GtfsDataSource,
            selected_agency: pd.DataFrame | None,
    ) -> pd.DataFrame | None:
        if selected_agency is None or selected_agency.empty:
            return None
        return gtfs_data.routes[
            gtfs_data.routes["agency_id"].isin(selected_agency["agency_id"])
        ]

    @staticmethod
    def update_selected_route_date_range(
            gtfs_data: GtfsDataSource,
            settings: PlanningSettings,
    ) -> None:
        selected_route = settings.route
        if selected_route is None or selected_route.empty:
            return
        trips_df = gtfs_data.get_trips(route_id=selected_route.iloc[0]["route_id"])
        calendar_dates = gtfs_data.calendar_dates
        calendar_dates = calendar_dates[calendar_dates.service_id.isin(trips_df.service_id)]
        calendar = gtfs_data.calendar
        calendar = calendar[calendar.service_id.isin(trips_df.service_id)]
        starts = pd.concat(
            [
                pd.to_datetime(calendar["start_date"], format="%Y%m%d"),
                pd.to_datetime(calendar_dates["date"]),
            ],
            ignore_index=True,
        )
        ends = pd.concat(
            [
                pd.to_datetime(calendar["end_date"], format="%Y%m%d"),
                pd.to_datetime(calendar_dates["date"]),
            ],
            ignore_index=True,
        )
        if starts.empty or ends.empty:
            settings.selected_route_date_range = None
            return

        date_range = pd.DataFrame(
            {
                "route_id": [selected_route.iloc[0]["route_id"]],
                "start_date": [starts.min()],
                "end_date": [ends.max()],
            }
        )
        settings.selected_route_date_range = date_range
        sample_date = date_range.iloc[0]["start_date"].strftime("%Y%m%d")
        settings.date = sample_date
        settings.sample_date = sample_date
