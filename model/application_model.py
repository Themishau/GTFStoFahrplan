from __future__ import annotations

import logging

from PySide6.QtCore import QCoreApplication, QObject, QThread, Signal, Slot

from model.planning.progress_update import ProgressUpdate

from .enums import ModelAction, PlanMode
from .infrastructure.paths.app_paths import AppPaths
from .planning.schedule_planner import SchedulePlanner
from .services.gtfs_cache_service import GtfsCacheService

logger = logging.getLogger(__name__)


class ModelWorker(QObject):
    finished = Signal()
    error = Signal(object)

    def __init__(
            self,
            model: ApplicationModel,
            action: ModelAction,
            gui_thread: QThread,
            arguments: tuple[object, ...] = (),
    ) -> None:
        super().__init__()
        self.model = model
        self.action = action
        self.gui_thread = gui_thread
        self.arguments = arguments

    @Slot()
    def run(self) -> None:
        try:
            if QThread.currentThread().isInterruptionRequested():
                raise InterruptedError("Operation cancelled.")
            self.model._dispatch_planner_action(self.action, *self.arguments)
        except Exception as error:
            emitted_error = (
                InterruptedError("Operation cancelled.")
                if QThread.currentThread().isInterruptionRequested()
                else error
            )
            self.error.emit(emitted_error)
        finally:
            self.model._move_planner_to_thread(self.gui_thread)
            self.finished.emit()


class ApplicationModel(QObject):
    progress_updated = Signal(ProgressUpdate)
    import_finished = Signal(bool)
    planning_finished = Signal(bool)
    error_occurred = Signal(str)
    sorting_requested = Signal()
    busy_changed = Signal(bool)
    feed_deleted = Signal(str)
    cache_cleared = Signal()

    def __init__(
            self,
            application: QCoreApplication,
            cache_service: GtfsCacheService | None = None,
    ) -> None:
        super().__init__(application)
        self.worker: ModelWorker | None = None
        self.application = application
        self.thread: QThread | None = None
        self.cache_service = cache_service or GtfsCacheService.for_paths(AppPaths.for_user())
        self.planner = SchedulePlanner(self.cache_service)
        self._connect_planner_signals()

    def _connect_planner_signals(self) -> None:
        self.planner.progress_updated.connect(self._on_planner_progress_updated)
        self.planner.import_finished.connect(self._on_planner_import_finished)
        self.planner.planning_finished.connect(self._on_planner_planning_finished)
        self.planner.error_occurred.connect(self._on_planner_error_occurred)
        self.planner.sorting_requested.connect(self._on_planner_sorting_requested)

    @Slot(ProgressUpdate)
    def _on_planner_progress_updated(self, value: ProgressUpdate) -> None:
        self.progress_updated.emit(value)

    @Slot(bool)
    def _on_planner_import_finished(self, value: bool) -> None:
        self.import_finished.emit(value)

    @Slot(bool)
    def _on_planner_planning_finished(self, value: bool) -> None:
        self.planning_finished.emit(value)

    @Slot(str)
    def _on_planner_error_occurred(self, value: str) -> None:
        self.error_occurred.emit(value)

    @Slot()
    def _on_planner_sorting_requested(self) -> None:
        self.sorting_requested.emit()

    def start_action(self, action: ModelAction, *arguments: object) -> bool:
        if self.thread is not None:
            logger.warning("A worker thread is already running.")
            return False

        thread = QThread()
        worker = ModelWorker(self, action, self.application.thread(), arguments)
        self.thread = thread
        self.worker = worker
        self._move_planner_to_thread(thread)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_worker_refs)
        worker.error.connect(self._handle_worker_error)

        self.busy_changed.emit(True)
        thread.start()
        return True

    def _clear_worker_refs(self) -> None:
        self.worker = None
        self.thread = None
        self.busy_changed.emit(False)

    def _move_planner_to_thread(self, target_thread: QThread) -> None:
        self.planner.moveToThread(target_thread)

        children: tuple[QObject | None, ...] = (
            self.planner.data_loader,
            self.planner.plan_exporter,
            self.planner.timetable_creator,
            self.planner.circulation_planner,
        )
        for child in children:
            if child is None:
                continue
            child.moveToThread(target_thread)

        strategy = self.planner.timetable_creator.strategy
        if isinstance(strategy, QObject):
            strategy.moveToThread(target_thread)

    def _dispatch_planner_action(self, action: ModelAction, *arguments: object) -> None:
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
                    self.planner.prepare_timetable_for_sorting()
                elif self.planner.planning_settings.plan_mode in (
                        PlanMode.CIRCULATION_DATE,
                        PlanMode.CIRCULATION_WEEKDAY,
                ):
                    self.planner.create_and_export_circulation_plan()
                else:
                    self.planner.create_and_export_timetable()
            case ModelAction.CONTINUE_TIMETABLE:
                self.planner.continue_and_export_timetable()
            case _:
                raise ValueError(f"Unknown model action: {action!r}")

    def _handle_worker_error(self, error: Exception) -> None:
        if isinstance(error, InterruptedError):
            logger.info("%s", error)
            return

        logger.error("Worker encountered an error: %s (%s)", error, type(error).__name__)
        self.error_occurred.emit(str(error))

    def cancel_current_action(self) -> None:
        if self.thread is not None and self.thread.isRunning():
            logger.info("Cancelling ongoing operation...")
            self.thread.requestInterruption()
            self.cache_service.repository.interrupt()

    def close(self) -> None:
        if self.thread is not None:
            raise RuntimeError("Wait for the worker to finish before closing the database")
        self.cache_service.close()

    def reset_schedule_planner(self) -> None:
        self.planner = SchedulePlanner(self.cache_service)
        self._connect_planner_signals()
