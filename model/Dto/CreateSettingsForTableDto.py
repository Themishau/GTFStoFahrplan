import copy
from model.Enum.GTFSEnums import CreatePlanMode
from PySide6.QtCore import QObject
from PySide6.QtCore import Signal, Slot
import pandas as pd
from typing import Optional

class CreateSettingsForTableDto(QObject):
    settingsChanged = Signal()

    def __init__(self, other=None):
        super().__init__()
        self._agency =  None
        self._route =  None
        self._weekday = None
        self._dates = None
        self._date = pd.DataFrame(columns=['date'])
        self._direction =  None
        self._individual_sorting =  False
        self._timeformat =  1
        self._create_plan_mode = CreatePlanMode.date
        self._date_range = None
        self._sample_date = None
        self._date_range_df_format = None
        self._df_selected_routes = None
        self._selected_agency_text = ""
        self._selected_route_text = ""
        self._output_path = ""
        self._full_output_path = ""

    def __deepcopy__(self, memo):
        copied = CreateSettingsForTableDto()
        copied._agency = copy.deepcopy(self._agency, memo)
        copied._route = copy.deepcopy(self._route, memo)
        copied._weekday = copy.deepcopy(self._weekday, memo)
        copied._dates = copy.deepcopy(self._dates, memo)
        copied._date = copy.deepcopy(self._date, memo)
        copied._direction = copy.deepcopy(self._direction, memo)
        copied._individual_sorting = copy.deepcopy(self._individual_sorting, memo)
        copied._timeformat = copy.deepcopy(self._timeformat, memo)
        copied._create_plan_mode = copy.deepcopy(self._create_plan_mode, memo)
        copied._output_path = copy.deepcopy(self._output_path, memo)
        copied._date_range = copy.deepcopy(self._date_range, memo)
        copied._sample_date = copy.deepcopy(self._sample_date, memo)
        copied._date_range_df_format = copy.deepcopy(self._date_range_df_format, memo)
        copied._df_selected_routes = copy.deepcopy(self._df_selected_routes, memo)
        copied._selected_agency_text = copy.deepcopy(self._selected_agency_text, memo)
        copied._selected_route_text = copy.deepcopy(self._selected_route_text, memo)
        copied._output_path = copy.deepcopy(self._output_path, memo)
        copied._full_output_path = copy.deepcopy(self._full_output_path, memo)
        return copied


    @property
    def full_output_path(self):
        return self._full_output_path
    @full_output_path.setter
    def full_output_path(self, value):
        self._full_output_path = value
        self.settingsChanged.emit()

    @property
    def output_path(self):
        return self._output_path
    @output_path.setter
    def output_path(self, value):
        self._output_path = value
        self.settingsChanged.emit()

    @property
    def agency(self) :
        return self._agency

    @agency.setter
    def agency(self, value):
            self._agency = value
            if value is not None:
                self.selected_agency_text = f"{value.iloc[0]['agency_id']}, {value.iloc[0]['agency_name']}"
            else:
                self.selected_agency_text = ""
            self.settingsChanged.emit()

    @property
    def route(self) :
        return self._route

    @route.setter
    def route(self, value):
            self._route = value
            if value is not None:
                self.selected_route_text = f"{value.iloc[0]['route_id']}, {value.iloc[0]['route_short_name']}, {value.iloc[0]['route_long_name']}"
            else:
                self.selected_route_text = ""
            self.settingsChanged.emit()

    @property
    def weekday(self) :
        return self._weekday

    @weekday.setter
    def weekday(self, value):
            self._weekday = value
            self.settingsChanged.emit()

    @property
    def dates(self):
        return self._dates

    @dates.setter
    def dates(self, value):
            self._dates = value
            self.settingsChanged.emit()

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
            self._date = value
            self.settingsChanged.emit()
        
    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
            self._direction = value
            self.settingsChanged.emit()

    @property
    def individual_sorting(self) :
        return self._individual_sorting

    @individual_sorting.setter
    def individual_sorting(self, value):
            self._individual_sorting = value
            self.settingsChanged.emit()

    @property
    def create_plan_mode(self) :
        return self._create_plan_mode

    @create_plan_mode.setter
    def create_plan_mode(self, value):
            self._create_plan_mode = value
            self.settingsChanged.emit()

    @property
    def timeformat(self):
        return self._timeformat

    @timeformat.setter
    def timeformat(self, value):
            self._timeformat = value
            self.settingsChanged.emit()

    @property
    def date_range(self):
        return self._date_range

    @date_range.setter
    def date_range(self, value):
            self._date_range = value
            self.settingsChanged.emit()

    @property
    def sample_date(self):
        return self._sample_date

    @sample_date.setter
    def sample_date(self, value):
            self._sample_date = value
            self.settingsChanged.emit()

    @property
    def date_range_df_format(self):
        return self._date_range_df_format

    @date_range_df_format.setter
    def date_range_df_format(self, value):
            self._date_range_df_format = value
            self.settingsChanged.emit()

    @property
    def df_selected_routes(self):
        return self._df_selected_routes

    @df_selected_routes.setter
    def df_selected_routes(self, value):
        if isinstance(value, pd.DataFrame):
            self._df_selected_routes = value
        else:
            raise ValueError("df_selected_routes must be a pandas DataFrame")
        self.settingsChanged.emit()

    @property
    def selected_agency_text(self):
        return self._selected_agency_text

    @selected_agency_text.setter
    def selected_agency_text(self, value):
        self._selected_agency_text = value
        self.settingsChanged.emit()

    @property
    def selected_route_text(self):
        return self._selected_route_text

    @selected_route_text.setter
    def selected_route_text(self, value):
        self._selected_route_text = value
        self.settingsChanged.emit()

    @Slot()
    def on_nested_settings_change(self):
        self.settingsChanged.emit()
