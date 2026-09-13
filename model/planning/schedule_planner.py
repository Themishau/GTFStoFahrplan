import copy
import logging

from PySide6.QtCore import QObject, Signal

from model.domain.import_settings import ImportSettings
from model.domain.planning_settings import PlanningSettings
from model.enums import ErrorMessages
from model.planning.analyzer import DataAnalyzer
from model.planning.creator import PlanCreator
from model.planning.exporter import PlanExporter
from model.planning.progress import ProgressUpdate
from model.planning.vehicle_circulation_planner import VehicleCirculationPlanner
from model.services.gtfs_data_loader import GtfsDataLoader

logger = logging.getLogger(__name__)


class SchedulePlanner(QObject):
    progress_updated = Signal(ProgressUpdate)
    import_finished = Signal(bool)
    create_finished = Signal(bool)
    error_occurred = Signal(str)
    settings_changed = Signal()
    create_sorting_signal = Signal()

    def __init__(self, app, cache_service):
        super().__init__()
        self.app = app
        self.cache_service = cache_service
        self.circle_planner = None
        self.plan_creator = None
        self.plan_exporter = None
        self.data_analyzer = None
        self.data_loader = None

        self.gtfs_data = None
        self.import_settings = ImportSettings()
        self.planning_settings = PlanningSettings()

    def send_error(self, error):
        self.error_occurred.emit(str(error))

    def update_progress(self, value):
        self.progress_updated.emit(copy.deepcopy(value))

    def initialize(self):
        self.data_loader = GtfsDataLoader(self.app, self.cache_service)
        self.data_loader.progress_updated.connect(self.update_progress)
        self.data_loader.error_occurred.connect(self.send_error)
        self.data_analyzer = DataAnalyzer()
        self.plan_exporter = PlanExporter(self.app)
        self.plan_exporter.progress_updated.connect(self.update_progress)
        self.plan_exporter.error_occurred.connect(self.send_error)
        self.initialize_plan_creator()

    def initialize_circle_planner(self):
        self.circle_planner = VehicleCirculationPlanner(
            plans=self.plan_creator.strategy.plans,
            app=self.app,
        )
        self.circle_planner.progress_updated.connect(self.update_progress)
        self.circle_planner.error_occurred.connect(self.send_error)

    def initialize_plan_creator(self):
        self.plan_creator = PlanCreator(self.app)
        self.plan_creator.progress_updated.connect(self.update_progress)
        self.plan_creator.error_occurred.connect(self.send_error)
        self.plan_creator.planning_settings = copy.deepcopy(self.planning_settings)
        self.plan_creator.gtfs_data = self.gtfs_data

    def update_settings_for_create_table(self):
        self.initialize_plan_creator()

    def create_table(self) -> bool:
        try:
            self.plan_creator.create_timetable()
            self.plan_exporter.export_plan(
                self.planning_settings,
                self.plan_creator.strategy.plans.timetable_data,
            )
            self.create_finished.emit(True)
            return True
        except InterruptedError:
            raise
        except Exception as error:
            logger.exception("Timetable creation failed")
            self.error_occurred.emit(f"{ErrorMessages.PLAN_CREATION_FAILED}:\n{error}")
            return False

    def create_table_individual_sorting(self) -> bool:
        self.plan_creator.create_timetable()
        self.create_sorting_signal.emit()
        return True

    def create_table_continue(self):
        try:
            self.plan_creator.continue_timetable()
            self.plan_exporter.export_plan(
                self.planning_settings,
                self.plan_creator.strategy.plans.timetable_data,
            )
            self.create_finished.emit(True)
            return True
        except InterruptedError:
            raise
        except Exception as error:
            logger.exception("Timetable continuation failed")
            self.error_occurred.emit(f"{ErrorMessages.PLAN_CREATION_FAILED}:\n{error}")
            return False

    def create_circulation_plan(self):
        try:
            self.plan_creator.create_timetable()
            self.initialize_circle_planner()
            self.circle_planner.create_circulation_plan()
            self.plan_exporter.export_circle_plan(self.planning_settings, self.circle_planner.plans)
            self.create_finished.emit(True)
            return True
        except InterruptedError:
            raise
        except Exception as error:
            logger.exception("Vehicle circulation creation failed")
            self.error_occurred.emit(f"{ErrorMessages.PLAN_CREATION_FAILED}:\n{error}")
            return False

    def import_gtfs_data(self):
        try:
            self._activate_data(self.data_loader.import_gtfs(self.import_settings))

            if self.gtfs_data is None:
                self.error_occurred.emit(str(ErrorMessages.NO_IMPORTED_DATA))
                return False
            self.import_finished.emit(True)
            return True
        except InterruptedError:
            raise
        except Exception as error:
            logger.exception("GTFS import failed")
            self.error_occurred.emit(f"{ErrorMessages.IMPORT_FAILED}:\n{error}")
            return False

    def open_cached_feed(self, feed_id):
        self._activate_data(self.data_loader.open_feed(feed_id))
        self.import_finished.emit(True)

    def _activate_data(self, data):
        self.gtfs_data = data
        self.circle_planner = None
        self.planning_settings = PlanningSettings()
        self.planning_settings.output_path = self.cache_service.settings.default_export_path
        self.planning_settings.time_format = (
            1 if self.cache_service.settings.time_format == 'HH:mm' else 2)
        start = data.feed.metadata.feed_start_date
        if start is not None:
            self.planning_settings.sample_date = start.strftime('%Y%m%d')
            self.planning_settings.date = start.strftime('%Y%m%d')
        self.initialize_plan_creator()

    def delete_cached_feed(self, feed_id):
        self.cache_service.delete_feed(feed_id)
        if self.gtfs_data is not None and self.gtfs_data.feed.feed_id == feed_id:
            self._clear_active_data()

    def delete_all_cached_feeds(self):
        self.cache_service.delete_all_feeds()
        self._clear_active_data()

    def _clear_active_data(self):
        self.gtfs_data = None
        self.planning_settings = PlanningSettings()
        self.circle_planner = None
        self.initialize_plan_creator()
