"""User settings used to create and export a timetable."""

from dataclasses import dataclass

import pandas as pd

from model.enums import PlanMode, TimeFormat


@dataclass(slots=True)
class PlanningSettings:
    agency: pd.DataFrame | None = None
    route: pd.DataFrame | None = None
    weekday: pd.DataFrame | None = None
    date: str | None = ""
    direction: int = 0
    use_individual_sorting: bool = False
    time_format: TimeFormat = TimeFormat.HOURS_MINUTES
    plan_mode: PlanMode = PlanMode.DATE
    sample_date: str | None = None
    selected_route_date_range: pd.DataFrame | None = None
    selected_routes: pd.DataFrame | None = None
    output_path: str = ""
    full_output_path: str = ""

    @property
    def selected_agency_text(self) -> str:
        if self.agency is None or self.agency.empty:
            return ""
        agency = self.agency.iloc[0]
        return f"{agency['agency_id']}, {agency['agency_name']}"

    @property
    def selected_route_text(self) -> str:
        if self.route is None or self.route.empty:
            return ""
        route = self.route.iloc[0]
        return (
            f"{route['route_id']}, {route['route_short_name']}, "
            f"{route['route_long_name']}"
        )
