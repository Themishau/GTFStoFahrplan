from typing import List, Optional
import copy
from PySide6.QtCore import Signal
from model.Base.Progress import ProgressSignal
from model.SchedulePlaner.CreationStrategy.TableCreationStrategy import TableCreationStrategy
from model.SchedulePlaner.UmplaufPlaner.UmlaufPlaner import UmlaufPlaner

class SequentialTableCreationStrategy(TableCreationStrategy):
    progress_Update = Signal(ProgressSignal)
    error_occured = Signal(str)
    def __init__(self, create_settings_for_table_dto, gtfs_data_frame_dto):
        self.create_settings_for_table_dto = create_settings_for_table_dto
        self.gtfs_data_frame_dto = gtfs_data_frame_dto
        self.plans: Optional[UmlaufPlaner] = None
        self.progress = 0

    def create_table(self) -> None:
        self.plans = UmlaufPlaner()
        self.plans.progress_Update.connect(self.update_progress)
        self.plans.create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
        self.plans.gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)
        self.plans.create_table()

    def update_progress(self, value):
        self.progress_Update.emit(copy.deepcopy(value))