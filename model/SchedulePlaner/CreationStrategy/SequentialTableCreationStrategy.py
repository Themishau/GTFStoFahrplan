from typing import List, Optional
import copy
from PySide6.QtCore import QObject, Signal
from model.Base.Progress import ProgressSignal
from model.Enum.GTFSEnums import CreatePlanMode
from model.SchedulePlaner.CreationStrategy.DateTableCreationStrategy import DateTableCreationStrategy
from model.SchedulePlaner.CreationStrategy.IndividualDateTableCreationStrategy import IndividualDateTableCreationStrategy
from model.SchedulePlaner.CreationStrategy.IndividualWeekdayTableCreationStrategy import IndividualWeekdayTableCreationStrategy
from model.SchedulePlaner.CreationStrategy.TableCreationContext import TableCreationContext
from model.SchedulePlaner.CreationStrategy.TableCreationStrategy import TableCreationStrategy
from model.SchedulePlaner.CreationStrategy.WeekdayTableCreationStrategy import WeekdayTableCreationStrategy
from model.SchedulePlaner.UmplaufPlaner.UmlaufPlaner import UmlaufPlaner

class SequentialTableCreationStrategy(QObject, TableCreationStrategy):
    progress_Update = Signal(ProgressSignal)
    create_sorting = Signal()
    error_occured = Signal(str)
    def __init__(self, app, create_settings_for_table_dto, gtfs_data_frame_dto):
        super().__init__()
        self.app = app
        self.create_settings_for_table_dto = create_settings_for_table_dto
        self.gtfs_data_frame_dto = gtfs_data_frame_dto
        self.plans: Optional[UmlaufPlaner] = None
        self.progress = 0

    def create_table(self) -> None:
        self.plans = UmlaufPlaner()
        self.plans.create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
        self.plans.gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)
        strategy = None
        if (self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.date and self.create_settings_for_table_dto.individual_sorting):
            strategy = IndividualDateTableCreationStrategy(self.plans)
            strategy.create_sorting.connect(self.update_progress)
        elif (self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.weekday and self.create_settings_for_table_dto.individual_sorting):
            strategy = IndividualWeekdayTableCreationStrategy(self.plans)
            strategy.create_sorting.connect(self.update_progress)
        elif (self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.date):
            strategy = DateTableCreationStrategy(self.plans)
        elif (self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.weekday):
            strategy = WeekdayTableCreationStrategy(self.plans)

        strategy.progress_Update.connect(self.update_progress)

        # Create context with selected strategy
        context = TableCreationContext(strategy)
        context.create_table()

    def update_progress(self, value):
        self.progress_Update.emit(copy.deepcopy(value))