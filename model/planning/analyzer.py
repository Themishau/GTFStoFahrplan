"""Queries used to populate planning choices from a GTFS source."""

import pandas as pd

from model.domain.gtfs_data_source import GtfsDataSource
from model.domain.planning_settings import PlanningSettings


class DataAnalyzer:
    @staticmethod
    def get_routes_of_agency(gtfs_data: GtfsDataSource, selected_agency):
        if selected_agency is not None:
            return DataAnalyzer.find_routes_from_agency(gtfs_data, selected_agency)
        return None

    @staticmethod
    def find_routes_from_agency(gtfs_data: GtfsDataSource, selected_agency):
        return gtfs_data.routes[gtfs_data.routes["agency_id"].isin(selected_agency["agency_id"])]

    @staticmethod
    def read_gtfs_agencies(gtfs_data: GtfsDataSource):
        agencies = gtfs_data.agencies.sort_values(by="agency_id")
        return [f"{row[0]},{row[1]}" for row in agencies.values.tolist()]

    def get_date_range(self, gtfs_data: GtfsDataSource):
        feed_info = gtfs_data.feed_info
        if feed_info is None or feed_info.empty:
            return self.analyze_date_range_in_gtfs_data(gtfs_data)
        return f"{feed_info.iloc[0].feed_start_date}-{feed_info.iloc[0].feed_end_date}"

    @staticmethod
    def get_date_range_based_on_selected_trip(
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
            [pd.to_datetime(calendar.start_date, format="%Y%m%d"), calendar_dates["date"]]
        )
        ends = pd.concat(
            [pd.to_datetime(calendar.end_date, format="%Y%m%d"), calendar_dates["date"]]
        )
        if not starts.empty:
            settings.selected_route_date_range = pd.DataFrame(
                {
                    "route_id": [selected_route["route_id"]],
                    "start_date": [starts.min()],
                    "end_date": [ends.max()],
                }
            )
            sample_date = settings.selected_route_date_range.iloc[0].start_date.strftime("%Y%m%d")
            settings.date = sample_date
            settings.sample_date = sample_date

    @staticmethod
    def analyze_date_range_in_gtfs_data(gtfs_data: GtfsDataSource):
        if gtfs_data.calendar is not None:
            return gtfs_data.calendar.groupby(["start_date", "end_date"]).size().reset_index()
        return None

    @staticmethod
    def analyze_date_range_string(date_range):
        if date_range is None or date_range.empty:
            return "No date range available"
        return f"{date_range.iloc[0].start_date}-{date_range.iloc[0].end_date}"
