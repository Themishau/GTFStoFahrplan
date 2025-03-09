from PySide6.QtCore import Signal
import copy
from model.Base.Progress import ProgressSignal
from model.SchedulePlaner.CreationStrategy.TableCreationStrategy import TableCreationStrategy
from model.SchedulePlaner.UmplaufPlaner.UmlaufPlaner import UmlaufPlaner

class IndividualDateTableCreationStrategy(TableCreationStrategy):
    progress_Update = Signal(ProgressSignal)
    create_sorting = Signal()
    error_occured = Signal(str)
    def __init__(self, UmlaufPlaner: UmlaufPlaner):
        """ visual internal property """
        self.progress = ProgressSignal()
        self.process = 10
        self.plan = UmlaufPlaner


    def create_table(self) -> None:
        steps = [
            (self.plan.dates_prepare_data_fahrplan, "dates_prepare_data_fahrplan"),
            (self.plan.datesWeekday_select_dates_for_date_range, "datesWeekday_select_dates_for_date_range"),
            (self.plan.dates_select_dates_delete_exception_2, "dates_select_dates_delete_exception_2"),
            (self.plan.datesWeekday_select_stops_for_trips, "datesWeekday_select_stops_for_trips"),
            (self.plan.datesWeekday_select_for_every_date_trips_stops, "datesWeekday_select_for_every_date_trips_stops"),
            (self.plan.datesWeekday_create_sort_stopnames, "datesWeekday_create_sort_stopnames"),
        ]

        for step, description in steps:
            self.progress_Update.emit(self.progress.set_progress(self.process + 10, description))
            step()

        self.create_sorting.emit()

    def update_progress(self, value):
        self.progress_Update.emit(copy.deepcopy(value))