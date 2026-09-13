import logging

from PySide6.QtCore import QObject, QThread, Signal, Slot

from .enums import ModelAction, PlanMode
from .infrastructure.paths.app_paths import AppPaths
from .planning.schedule_planner import SchedulePlanner
from .services.gtfs_cache_service import GtfsCacheService

logger = logging.getLogger(__name__)

class ModelWorker(QObject):
    finished = Signal()
    error = Signal(Exception)

    def __init__(self, model, function_name, main_thread, arguments=()):
        super().__init__()
        self.model = model
        self.function_name = function_name
        self.main_thread = main_thread
        self.arguments = arguments

    def run(self):
        try:
            if QThread.currentThread().isInterruptionRequested():
                raise InterruptedError("Operation cancelled.")
            self.model._dispatch_planner_action(self.function_name, *self.arguments)
        except Exception as e:
            self.error.emit(InterruptedError('Operation cancelled.')
                            if QThread.currentThread().isInterruptionRequested() else e)
        finally:
            self.model._move_planner_to_thread(self.main_thread)
            self.finished.emit()

class ApplicationModel(QObject):
    progress_updated = Signal(object)
    import_finished = Signal(bool)
    create_finished = Signal(bool)
    error_occurred = Signal(str)
    create_sorting_signal = Signal()
    busy_changed = Signal(bool)
    feed_deleted = Signal(str)
    cache_cleared = Signal()

    def __init__(self, event_loop, cache_service=None):
        super().__init__(event_loop)
        self.worker = None
        self.event_loop = event_loop
        self.planner = None
        self.thread = None
        self.cache_service = cache_service or GtfsCacheService.for_paths(AppPaths.for_user())

    def setup_schedule_planner(self):
        self.planner = SchedulePlanner(self.event_loop, self.cache_service)
        self.planner.initialize()
        self._connect_planner_signals()

    def _connect_planner_signals(self):
        self.planner.progress_updated.connect(self._on_planner_progress_updated)
        self.planner.import_finished.connect(self._on_planner_import_finished)
        self.planner.create_finished.connect(self._on_planner_create_finished)
        self.planner.error_occurred.connect(self._on_planner_error_occurred)
        self.planner.create_sorting_signal.connect(self._on_planner_sorting_requested)

    @Slot(object)
    def _on_planner_progress_updated(self, value):
        self.progress_updated.emit(value)

    @Slot(bool)
    def _on_planner_import_finished(self, value):
        self.import_finished.emit(value)

    @Slot(bool)
    def _on_planner_create_finished(self, value):
        self.create_finished.emit(value)

    @Slot(str)
    def _on_planner_error_occurred(self, value):
        self.error_occurred.emit(value)

    @Slot()
    def _on_planner_sorting_requested(self):
        self.create_sorting_signal.emit()

    def start_function_async(self, function_name, *arguments):
        if self.thread is not None:
            logger.warning("A worker thread is already running.")
            return False

        self.thread = QThread()
        self.worker = ModelWorker(self, function_name, self.event_loop.thread(), arguments)
        self._move_planner_to_thread(self.thread)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self._clear_worker_refs)
        self.worker.error.connect(self.handle_worker_error)

        self.busy_changed.emit(True)
        self.thread.start()
        return True

    def _clear_worker_refs(self):
        self.worker = None
        self.thread = None
        self.busy_changed.emit(False)

    def _move_planner_to_thread(self, target_thread):
        if self.planner is None:
            return

        self.planner.moveToThread(target_thread)

        for attribute_name in ("data_loader", "plan_exporter", "plan_creator", "circle_planner"):
            obj = getattr(self.planner, attribute_name, None)
            if obj is None:
                continue
            obj.moveToThread(target_thread)

        strategy = getattr(getattr(self.planner, "plan_creator", None), "strategy", None)
        if isinstance(strategy, QObject):
            strategy.moveToThread(target_thread)

    def _dispatch_planner_action(self, action, *arguments):
        match action:
            case ModelAction.IMPORT_GTFS:
                self.planner.import_gtfs_data()
            case ModelAction.OPEN_CACHED_FEED:
                self.planner.open_cached_feed(*arguments)
            case ModelAction.DELETE_CACHED_FEED:
                self.planner.delete_cached_feed(*arguments)
                self.feed_deleted.emit(arguments[0])
            case ModelAction.DELETE_ALL_CACHED_FEEDS:
                self.planner.delete_all_cached_feeds()
                self.cache_cleared.emit()
            case ModelAction.CREATE_TIMETABLE:
                if self.planner.planning_settings.use_individual_sorting:
                    self.planner.create_table_individual_sorting()
                elif self.planner.planning_settings.create_plan_mode in (
                        PlanMode.CIRCULATION_DATE,
                        PlanMode.CIRCULATION_WEEKDAY,
                ):
                    self.planner.create_circulation_plan()
                else:
                    self.planner.create_table()
            case ModelAction.CONTINUE_TIMETABLE:
                self.planner.create_table_continue()
            case _:
                raise ValueError(f"Unknown model action: {action!r}")

    def handle_worker_error(self, error):
        if isinstance(error, InterruptedError):
            logging.info(str(error))
            return

        logger.error(f"Worker encountered an error: {error}. {type(error).__name__}")
        self.error_occurred.emit(str(error))

    def cancel_async_operation(self):
        if self.thread is not None and self.thread.isRunning():
            logger.info("Cancelling ongoing operation...")
            self.thread.requestInterruption()
            self.cache_service.repository.interrupt()

    def close(self):
        if self.thread is not None:
            raise RuntimeError('Wait for the worker to finish before closing the database')
        self.cache_service.close()

    def reset_schedule_planner(self):
        self.planner = None
        self.setup_schedule_planner()

