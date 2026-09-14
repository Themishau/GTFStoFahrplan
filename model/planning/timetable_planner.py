"""Create timetable data frames from a planner-facing GTFS data source."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Final, cast

import pandas as pd

from model.domain.gtfs_data_source import GtfsDataSource
from model.domain.planning_settings import PlanningSettings
from model.domain.timetable_data import TimetableData
from model.enums import ErrorMessage, TimeFormat
from model.services.gtfs_time import gtfs_time_to_seconds

DAY_COLUMNS: Final = {
    "Monday": "monday",
    "Tuesday": "tuesday",
    "Wednesday": "wednesday",
    "Thursday": "thursday",
    "Friday": "friday",
    "Saturday": "saturday",
    "Sunday": "sunday",
}
SERVICE_DATE_COLUMNS: Final = [
    "date",
    "day",
    "trip_id",
    "service_id",
    "route_id",
    "start_date",
    "end_date",
    *DAY_COLUMNS.values(),
]


class TimetablePlanner:
    def __init__(self) -> None:
        self.planning_settings = PlanningSettings()
        self.timetable_data = TimetableData()
        self._gtfs_data: GtfsDataSource | None = None

    @property
    def gtfs_data(self) -> GtfsDataSource:
        if self._gtfs_data is None:
            raise RuntimeError("Open a GTFS feed before creating a timetable")
        return self._gtfs_data

    @gtfs_data.setter
    def gtfs_data(self, value: GtfsDataSource) -> None:
        self._gtfs_data = value

    def prepare_date_data(self) -> None:
        self.timetable_data = TimetableData(
            header=pd.DataFrame(
                {
                    "Agency": [self.planning_settings.selected_agency_text],
                    "Route": [self._selected_route_id()],
                    "Dates": [self.planning_settings.date],
                }
            )
        )

    def prepare_weekday_data(self) -> None:
        weekday = self.planning_settings.weekday
        weekday_label = ""
        if weekday is not None and not weekday.empty:
            weekday_label = str(weekday.iloc[0].get("category", weekday.iloc[0].get("day", "")))

        self.timetable_data = TimetableData(
            header=pd.DataFrame(
                {
                    "Agency": [self.planning_settings.selected_agency_text],
                    "Route": [self._selected_route_id()],
                    "WeekdayOption": [weekday_label],
                }
            )
        )

    def select_dates_for_range(self) -> None:
        trips = self.gtfs_data.get_trips(
            route_id=self._selected_route_id(),
            direction_id=self.planning_settings.direction,
        )
        calendar = self.gtfs_data.calendar
        calendar = calendar[calendar["service_id"].isin(trips["service_id"])]

        service_dates = calendar.merge(
            trips[["trip_id", "service_id", "route_id"]],
            on="service_id",
            how="inner",
        )
        selected_columns = [
            "trip_id",
            "service_id",
            "route_id",
            "start_date",
            "end_date",
            *DAY_COLUMNS.values(),
        ]
        service_dates = service_dates[selected_columns].sort_values("service_id")
        if service_dates.empty:
            raise ValueError(ErrorMessage.NO_TRIPS_IN_DATE_RANGE)

        service_dates = service_dates.copy()
        service_dates["start_date"] = pd.to_datetime(
            service_dates["start_date"],
            format="%Y%m%d",
        )
        service_dates["end_date"] = pd.to_datetime(
            service_dates["end_date"],
            format="%Y%m%d",
        )
        self.timetable_data.service_dates = service_dates

    def apply_weekday_exceptions(self) -> None:
        expanded_dates = self._expand_service_dates()
        selected_days = self._selected_weekdays()

        regular_service = pd.Series(False, index=expanded_dates.index)
        for day_name, column in DAY_COLUMNS.items():
            if day_name in selected_days:
                regular_service |= (
                        expanded_dates["day"].eq(day_name)
                        & expanded_dates[column].astype("string").eq("1")
                )

        additions = self._exception_keys(expanded_dates, exception_type=1)
        removals = self._exception_keys(expanded_dates, exception_type=2)
        selected = expanded_dates[
            (regular_service | self._matches_exception(expanded_dates, additions))
            & expanded_dates["day"].isin(selected_days)
            & ~self._matches_exception(expanded_dates, removals)
            ]
        self.timetable_data.service_dates = (
            selected.drop_duplicates(subset=["service_id"])
            .drop_duplicates()
            .reset_index(drop=True)
        )

    def apply_date_exceptions(self) -> None:
        selected_date = self.planning_settings.date
        if not selected_date:
            raise ValueError("Select a date before creating a timetable")

        requested_date = pd.to_datetime(selected_date, format="%Y%m%d")
        expanded_dates = self._expand_service_dates()
        weekday_column = DAY_COLUMNS[requested_date.day_name()]
        requested_mask = expanded_dates["date"].eq(requested_date)
        regular_service = (
                requested_mask
                & expanded_dates[weekday_column].astype("string").eq("1")
        )

        additions = self._exception_keys(expanded_dates, exception_type=1)
        removals = self._exception_keys(expanded_dates, exception_type=2)
        selected = expanded_dates[
            requested_mask
            & (regular_service | self._matches_exception(expanded_dates, additions))
            & ~self._matches_exception(expanded_dates, removals)
            ]
        self.timetable_data.service_dates = (
            selected.drop_duplicates(subset=["trip_id"])
            .drop_duplicates()
            .reset_index(drop=True)
        )

    def _expand_service_dates(self) -> pd.DataFrame:
        service_dates = self.timetable_data.service_dates
        frames: list[pd.DataFrame] = []
        services = cast(
            list[dict[str, Any]],
            service_dates.to_dict(orient="records"),
        )
        for service in services:
            dates = pd.date_range(
                service["start_date"],
                service["end_date"],
                freq="D",
            )
            frame = pd.DataFrame(
                {
                    "date": dates,
                    "trip_id": service["trip_id"],
                    "service_id": service["service_id"],
                    "route_id": service["route_id"],
                    "start_date": service["start_date"],
                    "end_date": service["end_date"],
                    **{
                        column: service[column]
                        for column in DAY_COLUMNS.values()
                    },
                }
            )
            frames.append(frame)

        if not frames:
            raise ValueError(ErrorMessage.NO_TRIPS_IN_DATE_RANGE)

        expanded = pd.concat(frames, ignore_index=True)
        expanded["date"] = pd.to_datetime(expanded["date"])
        expanded["start_date"] = pd.to_datetime(expanded["start_date"])
        expanded["end_date"] = pd.to_datetime(expanded["end_date"])
        expanded["day"] = expanded["date"].dt.day_name()
        return expanded[SERVICE_DATE_COLUMNS]

    def _selected_weekdays(self) -> set[str]:
        weekday = self.planning_settings.weekday
        if weekday is None or weekday.empty:
            raise ValueError("Select a weekday option before creating a timetable")

        return {
            day_name
            for day_name in DAY_COLUMNS
            if day_name in weekday
               and weekday[day_name].astype("string").eq(day_name).any()
        }

    def _exception_keys(
            self,
            service_dates: pd.DataFrame,
            *,
            exception_type: int,
    ) -> set[tuple[str, pd.Timestamp]]:
        exceptions = self.gtfs_data.calendar_dates.copy()
        if exceptions.empty:
            return set()

        exceptions["date"] = pd.to_datetime(exceptions["date"])
        exceptions = exceptions[
            exceptions["service_id"].isin(service_dates["service_id"])
            & exceptions["exception_type"].eq(exception_type)
            ]
        return {
            (str(service_id), self._to_timestamp(date).normalize())
            for service_id, date in exceptions[["service_id", "date"]].itertuples(
                index=False,
                name=None,
            )
        }

    @staticmethod
    def _matches_exception(
            service_dates: pd.DataFrame,
            exception_keys: set[tuple[str, pd.Timestamp]],
    ) -> pd.Series:
        if not exception_keys:
            return pd.Series(False, index=service_dates.index)
        keys = zip(
            service_dates["service_id"].astype("string"),
            pd.to_datetime(service_dates["date"]).dt.normalize(),
        )
        return pd.Series(
            (key in exception_keys for key in keys),
            index=service_dates.index,
        )

    def select_stops_for_trips(self) -> None:
        trips = self.gtfs_data.get_trips(
            route_id=self._selected_route_id(),
            direction_id=self.planning_settings.direction,
        )
        trips = trips[
            trips["trip_id"].isin(self.timetable_data.service_dates["trip_id"])
        ].copy()
        if trips.empty:
            raise ValueError(ErrorMessage.NO_TRIPS_IN_DATE_RANGE)

        stop_times = self.gtfs_data.get_stop_times_for_trips(
            trips["trip_id"].unique()
        ).copy()
        stop_times["trip_id"] = stop_times["trip_id"].astype("string")
        trips["trip_id"] = trips["trip_id"].astype("string")

        joined = stop_times.merge(
            trips[["trip_id", "service_id"]],
            on="trip_id",
            how="inner",
        )
        stops = self.gtfs_data.get_stops(joined["stop_id"].unique())
        joined = joined.merge(
            stops[["stop_id", "stop_name"]],
            on="stop_id",
            how="inner",
        )
        if joined.empty:
            raise ValueError(ErrorMessage.NO_TRIPS_IN_DATE_RANGE)

        first_stop_indices = joined.groupby("trip_id")["stop_sequence"].idxmin()
        first_stops = joined.loc[first_stop_indices, ["arrival_time", "trip_id"]]
        first_stops = first_stops.rename(columns={"arrival_time": "start_time"})
        joined = joined.merge(first_stops, on="trip_id", how="left")

        self.timetable_data.trip_stops = joined[
            [
                "start_time",
                "trip_id",
                "stop_name",
                "stop_sequence",
                "arrival_time",
                "service_id",
                "stop_id",
            ]
        ].copy()

    def build_daily_trip_stops(self) -> None:
        trip_stops = self.timetable_data.trip_stops.copy()
        trip_stops["trip_id"] = trip_stops["trip_id"].astype("string")
        service_dates = self.timetable_data.service_dates.copy()
        service_dates["trip_id"] = service_dates["trip_id"].astype("string")

        joined = service_dates.merge(
            trip_stops,
            on=["trip_id", "service_id"],
            how="left",
        ).dropna(subset=["stop_id"])
        joined = joined.sort_values(
            by=["date", "stop_sequence", "start_time", "trip_id"]
        )
        joined["arrival_time"] = joined["arrival_time"].map(
            self._normalize_gtfs_time
        )
        joined["start_time"] = joined["start_time"].map(
            self._normalize_gtfs_time
        )
        self.timetable_data.sorted_stops = joined[
            [
                "date",
                "day",
                "start_time",
                "arrival_time",
                "stop_name",
                "stop_sequence",
                "stop_id",
                "trip_id",
            ]
        ].sort_values(by=["trip_id", "date", "stop_sequence"])

    def prepare_stop_sorting(self) -> None:
        ordered_stops = pd.DataFrame.from_dict(
            self._filter_stop_sequence(self.timetable_data.sorted_stops)
        )
        ordered_stops["stop_sequence"] = ordered_stops["stop_sequence"].astype(
            "int32"
        )
        self.timetable_data.ordered_stops = ordered_stops.sort_index(axis=0)

    def create_timetable_after_sorting(self) -> None:
        self._build_timetable(keep_source_rows=False)

    def create_timetable(self) -> None:
        self._build_timetable(keep_source_rows=True)

    def _build_timetable(self, *, keep_source_rows: bool) -> None:
        sorted_stops = self.timetable_data.sorted_stops
        ordered_stops = self.timetable_data.ordered_stops
        if sorted_stops.empty or ordered_stops.empty:
            raise ValueError(ErrorMessage.NO_TRIPS_IN_DATE_RANGE)

        joined = sorted_stops.add_prefix("sorted_").merge(
            ordered_stops,
            left_on="sorted_stop_id",
            right_on="stop_id",
            how="left",
        )
        group_columns = [
            "sorted_date",
            "sorted_day",
            "sorted_start_time",
            "sorted_arrival_time",
            "sorted_trip_id",
            "sorted_stop_name",
            "stop_sequence",
            "sorted_stop_sequence",
            "sorted_stop_id",
        ]
        timetable_rows = (
            joined.groupby(group_columns)
            .size()
            .reset_index(name="count")
            .sort_values(
                by=[
                    "sorted_date",
                    "sorted_stop_sequence",
                    "sorted_start_time",
                    "sorted_trip_id",
                ]
            )
        )
        timetable_rows = timetable_rows[group_columns].copy()
        timetable_rows["sorted_date"] = pd.to_datetime(
            timetable_rows["sorted_date"]
        )
        timetable_rows["sorted_arrival_time"] = timetable_rows[
            "sorted_arrival_time"
        ].astype("string")
        timetable_rows["sorted_start_time"] = timetable_rows[
            "sorted_start_time"
        ].astype("string")
        if not keep_source_rows:
            timetable_rows = timetable_rows.drop(columns=["sorted_stop_sequence"])

        pivot_index = [
            "sorted_date",
            "sorted_day",
            "stop_sequence",
            "sorted_stop_name",
            "sorted_stop_id",
        ]
        trip_columns = ["sorted_start_time", "sorted_trip_id"]
        timetable_rows = (
            timetable_rows.groupby([*pivot_index, *trip_columns])
            .first()
            .reset_index()
        )
        if self.planning_settings.time_format == TimeFormat.HOURS_MINUTES:
            timetable_rows["sorted_arrival_time"] = timetable_rows[
                "sorted_arrival_time"
            ].map(self._remove_seconds)

        if keep_source_rows:
            self.timetable_data.timetable_rows = timetable_rows

        timetable = timetable_rows.pivot(
            index=pivot_index,
            columns=trip_columns,
            values="sorted_arrival_time",
        )
        self.timetable_data.timetable = timetable.sort_index(
            axis=1
        ).sort_index(axis=0)

    def _filter_stop_sequence(
            self,
            data: pd.DataFrame,
    ) -> dict[str, list[object]]:
        candidates: dict[object, dict[str, Any]] = {}
        rows = data.to_dict(orient="records")

        for initial_stop in rows:
            stop_id = initial_stop["stop_id"]
            if stop_id in candidates:
                continue

            initial_start = self._service_datetime(
                initial_stop["date"],
                initial_stop["start_time"],
            )
            candidate = {
                "stop_sequence": initial_stop["stop_sequence"],
                "stop_name": initial_stop["stop_name"],
                "start_time": initial_start,
            }

            for compared_stop in rows:
                if stop_id != compared_stop["stop_id"]:
                    continue

                compared_start = self._service_datetime(
                    compared_stop["date"],
                    compared_stop["start_time"],
                )
                if (
                        compared_start < initial_start
                        and compared_start < candidate["start_time"]
                        and compared_stop["stop_sequence"]
                        > initial_stop["stop_sequence"]
                        and compared_stop["stop_sequence"]
                        > candidate["stop_sequence"]
                ):
                    candidate["start_time"] = compared_start
                    candidate["stop_sequence"] = compared_stop["stop_sequence"]

            candidates[stop_id] = candidate

        ordered = sorted(
            (
                {"stop_id": stop_id, **values}
                for stop_id, values in candidates.items()
            ),
            key=lambda stop: (stop["stop_sequence"], stop["start_time"]),
        )
        return {
            "stop_id": [stop["stop_id"] for stop in ordered],
            "stop_sequence": list(range(len(ordered))),
            "stop_name": [stop["stop_name"] for stop in ordered],
            "start_time": [stop["start_time"] for stop in ordered],
        }

    def _selected_route_id(self) -> str:
        route = self.planning_settings.route
        if route is None or route.empty:
            raise ValueError("Select a route before creating a timetable")
        return str(route.iloc[0]["route_id"])

    @staticmethod
    def _service_datetime(
            service_date: str | datetime | pd.Timestamp,
            value: str,
    ) -> datetime:
        seconds = gtfs_time_to_seconds(value)
        if seconds is None:
            raise ValueError("A stop time cannot be empty")
        service_day = TimetablePlanner._to_timestamp(service_date)
        return service_day.normalize().to_pydatetime() + timedelta(seconds=seconds)

    @staticmethod
    def _to_timestamp(
            value: str | datetime | pd.Timestamp,
    ) -> pd.Timestamp:
        timestamp = pd.Timestamp(value)
        if pd.isna(timestamp):
            raise ValueError("A service date cannot be empty")
        return cast(pd.Timestamp, timestamp)

    @staticmethod
    def _normalize_gtfs_time(value: str | int | float) -> str:
        """Pad a one-digit GTFS hour for stable lexical sorting."""
        text = str(value)
        return f"0{text}" if re.fullmatch(r"\d:\d{2}:\d{2}", text) else text

    @staticmethod
    def _remove_seconds(value: str) -> str:
        return value[:-3]
