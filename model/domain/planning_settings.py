"""Observable user settings used to create and export a timetable."""

import copy

import pandas as pd
from PySide6.QtCore import QObject, Signal

from model.enums import PlanMode


class PlanningSettings(QObject):
    settings_changed = Signal()

    def __init__(self):
        super().__init__()
        self._agency = None
        self._route = None
        self._weekday = None
        self._dates = None
        self._date = ""
        self._direction = 0
        self._use_individual_sorting = False
        self._time_format = 1
        self._create_plan_mode = PlanMode.DATE
        self._date_range = None
        self._sample_date = None
        self._selected_route_date_range = None
        self._selected_routes = None
        self._selected_agency_text = ""
        self._selected_route_text = ""
        self._output_path = ""
        self._full_output_path = ""

    def __deepcopy__(self, memo):
        copied = type(self)()
        for name, value in vars(self).items():
            if name.startswith("_"):
                setattr(copied, name, copy.deepcopy(value, memo))
        return copied

    @property
    def full_output_path(self):
        return self._full_output_path
    @full_output_path.setter
    def full_output_path(self, value):
        self._full_output_path = value
        self.settings_changed.emit()

    @property
    def output_path(self):
        return self._output_path
    @output_path.setter
    def output_path(self, value):
        self._output_path = value
        self.settings_changed.emit()

    @property
    def agency(self) :
        return self._agency

    @agency.setter
    def agency(self, value):
        self._agency = value
        if value is not None and not value.empty:
            self.selected_agency_text = f"{value.iloc[0]['agency_id']}, {value.iloc[0]['agency_name']}"
        else:
            self.selected_agency_text = ""
        self.settings_changed.emit()

    @property
    def route(self) :
        return self._route

    @route.setter
    def route(self, value):
        self._route = value
        if value is not None and not value.empty:
            row = value.iloc[0]
            self.selected_route_text = (
                f"{row['route_id']}, {row['route_short_name']}, {row['route_long_name']}"
            )
        else:
            self.selected_route_text = ""
        self.settings_changed.emit()

    @property
    def weekday(self) :
        return self._weekday

    @weekday.setter
    def weekday(self, value):
        self._weekday = value
        self.settings_changed.emit()

    @property
    def dates(self):
        return self._dates

    @dates.setter
    def dates(self, value):
            self._dates = value
            self.settings_changed.emit()

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value
        self.settings_changed.emit()
        
    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value
        self.settings_changed.emit()

    @property
    def use_individual_sorting(self) :
        return self._use_individual_sorting

    @use_individual_sorting.setter
    def use_individual_sorting(self, value):
        self._use_individual_sorting = bool(value)
        self.settings_changed.emit()

    @property
    def create_plan_mode(self) :
        return self._create_plan_mode

    @create_plan_mode.setter
    def create_plan_mode(self, value):
        self._create_plan_mode = value
        self.settings_changed.emit()

    @property
    def time_format(self):
        return self._time_format

    @time_format.setter
    def time_format(self, value):
        self._time_format = value
        self.settings_changed.emit()

    @property
    def date_range(self):
        return self._date_range

    @date_range.setter
    def date_range(self, value):
            self._date_range = value
            self.settings_changed.emit()

    @property
    def sample_date(self):
        return self._sample_date

    @sample_date.setter
    def sample_date(self, value):
            self._sample_date = value
            self.settings_changed.emit()

    @property
    def selected_route_date_range(self):
        return self._selected_route_date_range

    @selected_route_date_range.setter
    def selected_route_date_range(self, value):
        self._selected_route_date_range = value
        self.settings_changed.emit()

    @property
    def selected_routes(self):
        return self._selected_routes

    @selected_routes.setter
    def selected_routes(self, value):
        if isinstance(value, pd.DataFrame):
            self._selected_routes = value
        else:
            raise TypeError("selected_routes must be a pandas DataFrame")
        self.settings_changed.emit()

    @property
    def selected_agency_text(self):
        return self._selected_agency_text

    @selected_agency_text.setter
    def selected_agency_text(self, value):
        self._selected_agency_text = value
        self.settings_changed.emit()

    @property
    def selected_route_text(self):
        return self._selected_route_text

    @selected_route_text.setter
    def selected_route_text(self, value):
        self._selected_route_text = value
        self.settings_changed.emit()

