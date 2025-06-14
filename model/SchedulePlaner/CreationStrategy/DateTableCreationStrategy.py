from PySide6.QtCore import Signal, QObject
import copy
from model.Base.Progress import ProgressSignal
from model.Enum.GTFSEnums import ProcessType
from model.SchedulePlaner.CreationStrategy.CommonMeta import CommonMeta
from model.SchedulePlaner.CreationStrategy.TableCreationStrategy import TableCreationStrategy
from model.SchedulePlaner.UmplaufPlaner.UmlaufPlaner import UmlaufPlaner

class DateTableCreationStrategy(QObject, TableCreationStrategy, metaclass=CommonMeta):
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
            (self.plan.dates_prepare_data_fahrplan, "dates_prepare_data_fahrplan"),
            (self.plan.datesWeekday_select_dates_for_date_range, "datesWeekday_select_dates_for_date_range"),
            (self.plan.dates_select_dates_delete_exception_2, "dates_select_dates_delete_exception_2"),
            (self.plan.datesWeekday_select_stops_for_trips, "datesWeekday_select_stops_for_trips"),
            (self.plan.datesWeekday_select_for_every_date_trips_stops, "datesWeekday_select_for_every_date_trips_stops"),
            (self.plan.datesWeekday_create_sort_stopnames, "datesWeekday_create_sort_stopnames"),
            (self.plan.datesWeekday_create_fahrplan, "datesWeekday_create_fahrplan")
        ]

        for step, description in steps:
            self.process = self.process + 10
            self.progress_Update.emit(self.progress.set_progress(self.process, ProcessType.create_plan, description))
            step()

    def update_progress(self, value):
        self.progress_Update.emit(copy.deepcopy(value))