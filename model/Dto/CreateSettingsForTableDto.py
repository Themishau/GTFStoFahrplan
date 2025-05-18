from model.Enum.GTFSEnums import CreatePlanMode
from PySide6.QtCore import QObject
from PySide6.QtCore import Signal, Slot
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
    def agency(self) -> Optional[str]:
        return self._agency

    @agency.setter
    def agency(self, value: Optional[str]):
        if self._agency != value:
            self._agency = value
            self.settingsChanged.emit()

    @property
    def route(self) -> Optional[str]:
        return self._route

    @route.setter
    def route(self, value: Optional[str]):
        if self._route != value:
            self._route = value
            self.settingsChanged.emit()

    @property
    def weekday(self) -> Optional[str]:
        return self._agency

    @weekday.setter
    def weekday(self, value: Optional[str]):
        if self._agency != value:
            self._agency = value
            self.settingsChanged.emit()

    @property
    def dates(self) -> Optional[str]:
        return self._route

    @dates.setter
    def dates(self, value: Optional[str]):
        if self._route != value:
            self._route = value
            self.settingsChanged.emit()
    @property
    def direction(self) -> Optional[int]:
        return self._agency

    @direction.setter
    def direction(self, value: Optional[int]):
        if self._agency != value:
            self._agency = value
            self.settingsChanged.emit()

    @property
    def individual_sorting(self) -> Optional[str]:
        return self._route

    @individual_sorting.setter
    def individual_sorting(self, value: Optional[str]):
        if self._route != value:
            self._route = value
            self.settingsChanged.emit()

    @property
    def create_plan_mode(self) -> Optional[str]:
        return self._route

    @create_plan_mode.setter
    def create_plan_mode(self, value: Optional[str]):
        if self._route != value:
            self._route = value
            self.settingsChanged.emit()

    @property
    def timeformat(self) -> Optional[int]:
        return self._route

    @timeformat.setter
    def timeformat(self, value: Optional[int]):
        if self._route != value:
            self._route = value
            self.settingsChanged.emit()

    @property
    def output_path(self) -> Optional[str]:
        return self._route

    @output_path.setter
    def output_path(self, value: Optional[str]):
        if self._route != value:
            self._route = value
            self.settingsChanged.emit()



    @Slot()
    def on_nested_settings_change(self):
        self.settingsChanged.emit()
