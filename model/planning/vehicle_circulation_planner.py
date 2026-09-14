"""Combine two direction timetables into a vehicle circulation plan."""

from __future__ import annotations

import pandas as pd
from PySide6.QtCore import QObject

from model.enums import ErrorMessage
from model.planning.timetable_planner import TimetablePlanner


class VehicleCirculationPlanner(QObject):
    def __init__(self, plans: list[TimetablePlanner]) -> None:
        super().__init__()
        self.plans = plans

    def create_circulation_plan(self) -> None:
        if len(self.plans) != 2:
            raise ValueError(ErrorMessage.PLAN_CREATION_FAILED)
        merged_stops = self._add_vehicle_numbers()
        self._rebuild_direction_timetables(merged_stops)

    def _rebuild_direction_timetables(self, merged_stops: pd.DataFrame) -> None:
        for direction, plan in enumerate(self.plans):
            direction_stops = merged_stops[
                merged_stops["direction"].eq(direction)
            ].reset_index(drop=True)
            plan.timetable_data.timetable = direction_stops.pivot(
                index=[
                    "sorted_date",
                    "sorted_day",
                    "stop_sequence",
                    "sorted_stop_name",
                    "sorted_stop_id",
                ],
                columns=[
                    "sorted_start_time",
                    "sorted_trip_id",
                    "vehicle_number",
                ],
                values="sorted_arrival_time",
            ).sort_index(axis=1).sort_index(axis=0)

    def _add_vehicle_numbers(self) -> pd.DataFrame:
        direction_frames: list[pd.DataFrame] = []
        for direction, plan in enumerate(self.plans):
            timetable_rows = plan.timetable_data.timetable_rows.copy()
            timetable_rows["vehicle_number"] = 0
            timetable_rows["direction"] = direction
            timetable_rows["first_vehicle_trip"] = ""
            direction_frames.append(timetable_rows)

        all_stops = pd.concat(direction_frames, ignore_index=True)
        all_stops["trip_sequence_id"] = (
                all_stops["sorted_trip_id"].astype(str)
                + "_"
                + all_stops["sorted_stop_sequence"].astype(str)
        )

        sequence_by_trip = all_stops.groupby(
            "sorted_trip_id",
            as_index=False,
        )["sorted_stop_sequence"]
        first_stops = sequence_by_trip.min()
        last_stops = sequence_by_trip.max()
        trip_endpoints = pd.concat(
            [first_stops, last_stops],
            ignore_index=True,
        )
        trip_endpoints["trip_sequence_id"] = (
                trip_endpoints["sorted_trip_id"].astype(str)
                + "_"
                + trip_endpoints["sorted_stop_sequence"].astype(str)
        )
        endpoint_rows = all_stops[
            all_stops["trip_sequence_id"].isin(
                trip_endpoints["trip_sequence_id"]
            )
        ]
        return self._assign_vehicle_numbers(endpoint_rows, all_stops)

    def _assign_vehicle_numbers(
            self,
            trip_endpoints: pd.DataFrame,
            all_stops: pd.DataFrame,
    ) -> pd.DataFrame:
        trip_endpoints = trip_endpoints.sort_values(
            by=[
                "sorted_start_time",
                "sorted_trip_id",
                "sorted_stop_sequence",
            ]
        )
        assignments = trip_endpoints.copy(deep=True).sort_values(
            by=[
                "sorted_start_time",
                "sorted_stop_sequence",
                "sorted_trip_id",
            ]
        )

        vehicle_number = 1
        for _, trip in trip_endpoints.iterrows():
            if vehicle_number != 1 and self._is_trip_assigned(trip, assignments):
                continue

            current_trip = trip
            trip_id = current_trip["sorted_trip_id"]
            first_stop = (
                    assignments["sorted_trip_id"].eq(trip_id)
                    & assignments["sorted_stop_sequence"].eq(0)
            )
            assignments.loc[first_stop, "first_vehicle_trip"] = "*"
            all_stops.loc[
                all_stops["sorted_trip_id"].eq(trip_id)
                & all_stops["sorted_stop_sequence"].eq(0),
                "first_vehicle_trip",
            ] = "*"

            while True:
                trip_id = current_trip["sorted_trip_id"]
                assignments.loc[
                    assignments["sorted_trip_id"].eq(trip_id),
                    "vehicle_number",
                ] = vehicle_number
                all_stops.loc[
                    all_stops["sorted_trip_id"].eq(trip_id),
                    "vehicle_number",
                ] = vehicle_number

                last_stops = assignments[
                    assignments["sorted_trip_id"].eq(trip_id)
                    & assignments["sorted_stop_sequence"].ne(0)
                    ]
                if last_stops.empty:
                    break

                last_stop = last_stops.iloc[0]
                next_trips = assignments[
                    assignments["sorted_trip_id"].ne(
                        last_stop["sorted_trip_id"]
                    )
                    & assignments["direction"].ne(last_stop["direction"])
                    & assignments["sorted_stop_sequence"].eq(0)
                    & assignments["sorted_start_time"].ge(
                        last_stop["sorted_arrival_time"]
                    )
                    & assignments["vehicle_number"].eq(0)
                    ]
                if next_trips.empty:
                    break

                current_trip = next_trips.sort_values(
                    "sorted_start_time"
                ).iloc[0]

            vehicle_number += 1

        return all_stops

    @staticmethod
    def _is_trip_assigned(
            trip: pd.Series,
            assignments: pd.DataFrame,
    ) -> bool:
        return assignments[
            assignments["sorted_trip_id"].eq(trip["sorted_trip_id"])
            & assignments["vehicle_number"].eq(0)
            ].empty
