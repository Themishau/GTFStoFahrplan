from model.Enum.GTFSEnums import CreatePlanMode
from PySide6.QtCore import QObject
from PySide6.QtCore import Signal, Slot
import pandas as pd
from typing import Optional

class CreateSettingsForTableDTO(QObject):
    settingsChanged = Signal()

    def __init__(self):
        super().__init__()
        self._initialize_all_properties()

    def _initialize_all_properties(self):
        # Initialize all properties with default values
        self._agency = None
        self._route = None
        self._weekday = None
        self._dates = None
        self._direction = 0
        self._individual_sorting = False
        self._timeformat = 1
        self._create_plan_mode = CreatePlanMode.date
        self._output_path = ""



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
        return self._agency

    @weekday.setter
    def weekday(self, value):
            self._agency = value
            self.settingsChanged.emit()

    @property
    def dates(self):
        return self._route

    @dates.setter
    def dates(self, value):
            self._route = value
            self.settingsChanged.emit()
        
    @property
    def direction(self):
        return self._agency

    @direction.setter
    def direction(self, value):
            self._agency = value
            self.settingsChanged.emit()

    @property
    def individual_sorting(self) :
        return self._route

    @individual_sorting.setter
    def individual_sorting(self, value):
            self._route = value
            self.settingsChanged.emit()

    @property
    def create_plan_mode(self) :
        return self._route

    @create_plan_mode.setter
    def create_plan_mode(self, value):
            self._route = value
            self.settingsChanged.emit()

    @property
    def timeformat(self):
        return self._route

    @timeformat.setter
    def timeformat(self, value):
            self._route = value
            self.settingsChanged.emit()

    @property
    def output_path(self) :
        return self._route

    @output_path.setter
    def output_path(self, value):
            self._route = value
            self.settingsChanged.emit()



    @Slot()
    def on_nested_settings_change(self):
        self.settingsChanged.emit()
