"""Mutable result assembled while creating a timetable."""

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class TimetableData:
    header: pd.DataFrame | None = None
    direction: pd.DataFrame | None = None
    requested_dates: pd.DataFrame | None = None
    requested_weekdays: Any = None
    selected_route: pd.DataFrame | None = None
    selected_agency: pd.DataFrame | None = None
    timetable_dates: pd.DataFrame | None = None
    timetable_stops: pd.DataFrame | None = None
    sorted_stops: pd.DataFrame | None = None
    filtered_stop_names: pd.DataFrame | None = None
    gtfs_table_data: pd.DataFrame | None = None
    timetable: pd.DataFrame | None = None
