"""Mutable result assembled while creating a timetable."""

from dataclasses import dataclass, field
import pandas as pd


@dataclass(slots=True)
class TimetableData:
    header: pd.DataFrame = field(default_factory=pd.DataFrame)
    service_dates: pd.DataFrame = field(default_factory=pd.DataFrame)
    trip_stops: pd.DataFrame = field(default_factory=pd.DataFrame)
    sorted_stops: pd.DataFrame = field(default_factory=pd.DataFrame)
    ordered_stops: pd.DataFrame = field(default_factory=pd.DataFrame)
    timetable_rows: pd.DataFrame = field(default_factory=pd.DataFrame)
    timetable: pd.DataFrame = field(default_factory=pd.DataFrame)
