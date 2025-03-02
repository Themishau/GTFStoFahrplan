from typing import List
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import copy

import logging
from model.Base.Progress import ProgressSignal
from PySide6.QtCore import Signal
from model.SchedulePlaner.CreationStrategy.TableCreationStrategy import TableCreationStrategy
from model.SchedulePlaner.UmplaufPlaner.UmlaufPlaner import UmlaufPlaner


class ParallelTableCreationStrategy(TableCreationStrategy):
    progress_Update = Signal(ProgressSignal)
    error_occured = Signal(str)
    def __init__(self, create_settings_for_table_dto, gtfs_data_frame_dto):
        self.create_settings_for_table_dto = create_settings_for_table_dto
        self.gtfs_data_frame_dto = gtfs_data_frame_dto
        self.plans: List[UmlaufPlaner] = []


    def create_table(self) -> None:
        self.plans = [UmlaufPlaner(), UmlaufPlaner()]

        # Configure plans
        self.plans[0].create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
        self.plans[0].gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)

        self.plans[1].create_settings_for_table_dto = copy.deepcopy(self.create_settings_for_table_dto)
        self.plans[1].create_settings_for_table_dto.direction = 1
        self.plans[1].gtfs_data_frame_dto = copy.deepcopy(self.gtfs_data_frame_dto)

        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(self.plans[0].create_table),
                    executor.submit(self.plans[1].create_table)
                ]

                for future in concurrent.futures.as_completed(futures):
                    try:
                        _ = future.result()
                    except Exception as exc:
                        logging.debug(f'Thread generated an exception: {exc}')
        except Exception as exc:
            logging.debug(f'An error occurred during execution: {exc}')

    def update_progress(self, value):
        self.progress_Update.emit(copy.deepcopy(value))
