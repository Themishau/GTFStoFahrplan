import copy
import logging

from PySide6.QtCore import QObject, Signal

from model.domain.import_settings import ImportSettings
from model.domain.planning_settings import PlanningSettings
from model.enums import ErrorMessage, TimeFormat
from model.planning.gtfs_data_analyzer import GtfsDataAnalyzer
from model.planning.plan_exporter import PlanExporter
from model.planning.progress import ProgressUpdate
from model.planning.timetable_creator import TimetableCreator
from model.planning.vehicle_circulation_planner import VehicleCirculationPlanner
from model.services.gtfs_data_loader import GtfsDataLoader

logger = logging.getLogger(__name__)


class SchedulePlanner(QObject):
    progress_updated = Signal(ProgressUpdate)
    import_finished = Signal(bool)
    planning_finished = Signal(bool)
    error_occurred = Signal(str)
    sorting_requested = Signal()

    def __init__(self, cache_service):
        super().__init__()
        self.cache_service = cache_service
        self.circulation_planner: VehicleCirculationPlanner | None = None
        self.gtfs_data = None
        self.import_settings = ImportSettings()
        self.planning_settings = PlanningSettings()
        self.data_loader = GtfsDataLoader(self.cache_service)
        self.data_analyzer = GtfsDataAnalyzer()
        self.plan_exporter = PlanExporter()
        self.data_loader.progress_updated.connect(self.update_progress)
        self.plan_exporter.progress_updated.connect(self.update_progress)
        self.initialize_timetable_creator()

    def update_progress(self, value: ProgressUpdate) -> None:
        self.progress_updated.emit(copy.deepcopy(value))

    def _initialize_circulation_planner(self) -> None:
        self.circulation_planner = VehicleCirculationPlanner(
            plans=self.timetable_creator.strategy.plans,
        )

    def initialize_timetable_creator(self) -> None:
        self.timetable_creator = TimetableCreator()
        self.timetable_creator.progress_updated.connect(self.update_progress)
        self.timetable_creator.planning_settings = copy.deepcopy(self.planning_settings)
        self.timetable_creator.gtfs_data = self.gtfs_data

    def refresh_timetable_creator(self) -> None:
        self.initialize_timetable_creator()

    def create_and_export_timetable(self) -> bool:
        try:
            self.timetable_creator.create_timetable()
            self.plan_exporter.export_timetable(
                self.planning_settings,
                self.timetable_creator.strategy.plans.timetable_data,
            )
            self.planning_finished.emit(True)
            return True
        except InterruptedError:
            raise
        except Exception as error:
            logger.exception("Timetable creation failed")
            self.error_occurred.emit(f"{ErrorMessage.PLAN_CREATION_FAILED}:\n{error}")
            return False

    def prepare_timetable_for_sorting(self) -> bool:
        self.timetable_creator.create_timetable()
        self.sorting_requested.emit()
        return True

    def continue_and_export_timetable(self) -> bool:
        try:
            self.timetable_creator.continue_timetable()
            self.plan_exporter.export_timetable(
                self.planning_settings,
                self.timetable_creator.strategy.plans.timetable_data,
            )
            self.planning_finished.emit(True)
            return True
        except InterruptedError:
            raise
        except Exception as error:
            logger.exception("Timetable continuation failed")
            self.error_occurred.emit(f"{ErrorMessage.PLAN_CREATION_FAILED}:\n{error}")
            return False

    def create_and_export_circulation_plan(self) -> bool:
        try:
            self.timetable_creator.create_timetable()
            self._initialize_circulation_planner()
            self.circulation_planner.create_circulation_plan()
            self.plan_exporter.export_circulation_plan(
                self.planning_settings,
                self.circulation_planner.plans,
            )
            self.planning_finished.emit(True)
            return True
        except InterruptedError:
            raise
        except Exception as error:
            logger.exception("Vehicle circulation creation failed")
            self.error_occurred.emit(f"{ErrorMessage.PLAN_CREATION_FAILED}:\n{error}")
            return False

    def import_gtfs_data(self) -> bool:
        try:
            self._activate_data(self.data_loader.import_gtfs(self.import_settings))

            if self.gtfs_data is None:
                self.error_occurred.emit(ErrorMessage.NO_IMPORTED_DATA)
                return False
            self.import_finished.emit(True)
            return True
        except InterruptedError:
            raise
        except Exception as error:
            logger.exception("GTFS import failed")
            self.error_occurred.emit(f"{ErrorMessage.IMPORT_FAILED}:\n{error}")
            return False

    def open_cached_feed(self, feed_id: str) -> None:
        self._activate_data(self.data_loader.open_feed(feed_id))
        self.import_finished.emit(True)

    def _activate_data(self, data):
        self.gtfs_data = data
        self.circulation_planner = None
        self.planning_settings = PlanningSettings()
        self.planning_settings.output_path = self.cache_service.settings.default_export_path
        self.planning_settings.time_format = TimeFormat(self.cache_service.settings.time_format)
        start = data.feed.metadata.feed_start_date
        if start is not None:
            self.planning_settings.sample_date = start.strftime('%Y%m%d')
            self.planning_settings.date = start.strftime('%Y%m%d')
        self.initialize_timetable_creator()

    def delete_cached_feed(self, feed_id: str) -> None:
        self.cache_service.delete_feed(feed_id)
        if self.gtfs_data is not None and self.gtfs_data.feed.feed_id == feed_id:
            self._clear_active_data()

    def delete_all_cached_feeds(self) -> None:
        self.cache_service.delete_all_feeds()
        self._clear_active_data()

    def _clear_active_data(self) -> None:
        self.gtfs_data = None
        self.planning_settings = PlanningSettings()
        self.circulation_planner = None
        self.initialize_timetable_creator()
