import copy
from model.Enum.GTFSEnums import CreatePlanMode
from PySide6.QtCore import QObject
from PySide6.QtCore import Signal, Slot
import pandas as pd
from typing import Optional

class CreateSettingsForTableDTO(QObject):
    settingsChanged = Signal()

    def __init__(self, other=None):
        super().__init__()
        self._agency =  None
        self._route =  None
        self._weekday = None
        self._dates = pd.DataFrame(columns=['date'])
        self._direction =  None
        self._individual_sorting =  False
        self._timeformat =  1
        self._create_plan_mode = CreatePlanMode.date
        self._output_path =  ''

    def __deepcopy__(self, memo):
        copied = CreateSettingsForTableDTO()
        copied._agency = copy.deepcopy(self._agency, memo)
        copied._route = copy.deepcopy(self._route, memo)
        copied._weekday = copy.deepcopy(self._weekday, memo)
        copied._dates = copy.deepcopy(self._dates, memo)
        copied._direction = copy.deepcopy(self._direction, memo)
        copied._individual_sorting = copy.deepcopy(self._individual_sorting, memo)
        copied._timeformat = copy.deepcopy(self._timeformat, memo)
        copied._create_plan_mode = copy.deepcopy(self._create_plan_mode, memo)
        copied._output_path = copy.deepcopy(self._output_path, memo)


        return copied
    @property
    def agency(self) :
        return self._agency

    @agency.setter
    def agency(self, value):
            self._agency = value
            self.settingsChanged.emit()

    @property
    def route(self) :
        return self._route

    @route.setter
    def route(self, value):
            self._route = value
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
    def output_path(self) :
        return self._output_path

    @output_path.setter
    def output_path(self, value):
            self._output_path = value
            self.settingsChanged.emit()

    @Slot()
    def on_nested_settings_change(self):
        self.settingsChanged.emit()
