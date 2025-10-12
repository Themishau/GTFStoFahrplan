from typing import List
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import copy

import logging
from model.Base.Progress import ProgressSignal
from PySide6.QtCore import Signal, QObject

from model.Enum.GTFSEnums import CreatePlanMode
from model.SchedulePlaner.CreationStrategy.CommonMeta import CommonMeta
from model.SchedulePlaner.CreationStrategy.DateTableCreationStrategy import DateTableCreationStrategy
from model.SchedulePlaner.CreationStrategy.IndividualWeekdayTableCreationStrategy import \
    IndividualWeekdayTableCreationStrategy
from model.SchedulePlaner.CreationStrategy.TableCreationContext import TableCreationContext
from model.SchedulePlaner.CreationStrategy.TableCreationStrategy import TableCreationStrategy
from model.SchedulePlaner.CreationStrategy.WeekdayTableCreationStrategy import WeekdayTableCreationStrategy
from model.SchedulePlaner.UmplaufPlaner.UmlaufPlaner import UmlaufPlaner


class ParallelTableCreationStrategy(QObject, TableCreationStrategy, metaclass=CommonMeta):
    progress_Update = Signal(ProgressSignal)
    error_occured = Signal(str)
    def __init__(self, app, create_settings_for_table_dto, gtfs_data_frame_dto):
        super().__init__()
        self.app = app
        self.create_settings_for_table_dto = create_settings_for_table_dto
        self.gtfs_data_frame_dto = gtfs_data_frame_dto
        self.plans: List[UmlaufPlaner] = []
        self.progress = ProgressSignal()


    def create_table(self) -> None:
        self.plans = [UmlaufPlaner(), UmlaufPlaner()]

        # Configure plans
        self.plans[0].create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
        self.plans[0].gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)

        self.plans[1].create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
        self.plans[1].create_settings_for_table_dto.direction = 1
        self.plans[1].gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)

        strategy_direction_1 = None
        strategy_direction_2 = None

        if self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_date and self.create_settings_for_table_dto.use_individual_sorting:
            strategy_direction_1 = IndividualWeekdayTableCreationStrategy(self.app, self.plans[0])
            strategy_direction_2 = IndividualWeekdayTableCreationStrategy(self.app, self.plans[1])
        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_weekday and self.create_settings_for_table_dto.use_individual_sorting:
            strategy_direction_1 = IndividualWeekdayTableCreationStrategy(self.app, self.plans[0])
            strategy_direction_2 = IndividualWeekdayTableCreationStrategy(self.app, self.plans[1])
        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_date:
            strategy_direction_1 = DateTableCreationStrategy(self.app, self.plans[0])
            strategy_direction_2 = DateTableCreationStrategy(self.app, self.plans[1])
        elif self.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_weekday:
            strategy_direction_1 = WeekdayTableCreationStrategy(self.app, self.plans[0])
            strategy_direction_2 = WeekdayTableCreationStrategy(self.app, self.plans[1])

        strategy_direction_1.progress_Update.connect(self.update_progress)
        strategy_direction_2.progress_Update.connect(self.update_progress)

        context_1 = TableCreationContext(strategy_direction_1)
        context_2 = TableCreationContext(strategy_direction_2)

        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(context_1.create_table),
                    executor.submit(context_2.create_table)
                ]

                for future in concurrent.futures.as_completed(futures):
                    try:
                        _ = future.result()
                    except Exception as exc:
                        logging.debug(f'Thread generated an exception: {exc}')
        except Exception as exc:
            logging.debug(f'An error occurred during execution: {exc}')

    def create_table_continue(self):
        self.plans[0].datesWeekday_create_fahrplan_continue()
        self.plans[1].datesWeekday_create_fahrplan_continue()

    def update_progress(self, value):
        self.progress_Update.emit(copy.deepcopy(value))
