from typing import List, Optional
import copy
from PySide6.QtCore import Signal, QObject
from model.Base.Progress import ProgressSignal
from model.Enum.GTFSEnums import ProcessType
from model.SchedulePlaner.CreationStrategy.CommonMeta import CommonMeta
from model.SchedulePlaner.CreationStrategy.TableCreationStrategy import TableCreationStrategy
from model.SchedulePlaner.UmplaufPlaner.UmlaufPlaner import UmlaufPlaner

class WeekdayTableCreationStrategy(QObject, TableCreationStrategy, metaclass=CommonMeta):
    progress_Update = Signal(ProgressSignal)
    error_occured = Signal(str)
    def __init__(self, app, umlauf_planer: UmlaufPlaner):
        super().__init__()
        self.app = app
        self.progress = ProgressSignal()
        self.process = 10
        self.plan = umlauf_planer

    def create_table(self) -> None:
        steps = [
            (self.plan.weekday_prepare_data_fahrplan, "weekday_prepare_data_fahrplan"),
            (self.plan.datesWeekday_select_dates_for_date_range, "datesWeekday_select_dates_for_date_range"),
            (self.plan.weekday_select_weekday_exception_2, "weekday_select_weekday_exception_2"),
            (self.plan.datesWeekday_select_stops_for_trips, "datesWeekday_select_stops_for_trips"),
            (self.plan.datesWeekday_select_for_every_date_trips_stops, "datesWeekday_select_for_every_date_trips_stops"),
            (self.plan.datesWeekday_create_fahrplan, "datesWeekday_create_fahrplan")
        ]

        for step, description in steps:
            self.process = self.process + 10
            self.progress_Update.emit(self.progress.set_progress(self.process, ProcessType.create_plan, description))
            step()

    def update_progress(self, progress: int) -> None:
        self.progress = progress