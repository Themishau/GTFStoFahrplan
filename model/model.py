import logging

from PySide6.QtCore import QObject, QThread, Signal, Slot

from .Enum.GTFSEnums import CreatePlanMode
from .SchedulePlaner.SchedulePlaner import SchedulePlaner

logger = logging.getLogger(__name__)

class Worker(QObject):
    finished = Signal()
    error = Signal(Exception)

    def __init__(self, model, function_name, main_thread):
        super().__init__()
        self.model = model
        self.function_name = function_name
        self.main_thread = main_thread

    def run(self):
        try:
            if QThread.currentThread().isInterruptionRequested():
                raise InterruptedError("Operation cancelled.")
            self.model._dispatch_planer_action(self.function_name)
        except Exception as e:
            self.error.emit(e)
        finally:
            self.model._move_planer_to_thread(self.main_thread)
            self.finished.emit()

class Model(QObject):
    progress_updated = Signal(object)
    import_finished = Signal(bool)
    create_finished = Signal(bool)
    error_occurred = Signal(str)
    create_sorting_signal = Signal()

    def __init__(self, event_loop):
        super().__init__(event_loop)
        self.worker = None
        self.event_loop = event_loop
        self.planer = None
        self.thread = None

    def set_up_schedule_planer(self):
        self.planer = SchedulePlaner(self.event_loop)
        self.planer.initilize_scheduler()
        self._connect_planer_signals()

    def _connect_planer_signals(self):
        self.planer.progress_Update.connect(self._on_planer_progress_updated)
        self.planer.import_finished.connect(self._on_planer_import_finished)
        self.planer.create_finished.connect(self._on_planer_create_finished)
        self.planer.error_occured.connect(self._on_planer_error_occurred)
        self.planer.create_sorting_signal.connect(self._on_planer_create_sorting_signal)

    @Slot(object)
    def _on_planer_progress_updated(self, value):
        self.progress_updated.emit(value)

    @Slot(bool)
    def _on_planer_import_finished(self, value):
        self.import_finished.emit(value)

    @Slot(bool)
    def _on_planer_create_finished(self, value):
        self.create_finished.emit(value)

    @Slot(str)
    def _on_planer_error_occurred(self, value):
        self.error_occurred.emit(value)

    @Slot()
    def _on_planer_create_sorting_signal(self):
        self.create_sorting_signal.emit()

    def start_function_async(self, function_name):
        if self.thread is not None and self.thread.isRunning():
            logger.warning("A worker thread is already running.")
            return

        self.thread = QThread()
        self.worker = Worker(self, function_name, self.event_loop.thread())
        self._move_planer_to_thread(self.thread)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self._clear_worker_refs)
        self.worker.error.connect(self.handle_worker_error)

        self.thread.start()

    def _clear_worker_refs(self):
        self.worker = None
        self.thread = None

    def _move_planer_to_thread(self, target_thread):
        if self.planer is None:
            return

        self.planer.moveToThread(target_thread)

        for attribute_name in ("import_Data", "analyze_data", "export_plan", "create_plan", "circle_plan"):
            obj = getattr(self.planer, attribute_name, None)
            if obj is None:
                continue
            obj.moveToThread(target_thread)

        strategy = getattr(getattr(self.planer, "create_plan", None), "strategy", None)
        if isinstance(strategy, QObject):
            strategy.moveToThread(target_thread)

    def _dispatch_planer_action(self, function_name):
        match function_name:
            case "planer_start_load_data":
                self.planer.import_gtfs_data()
            case "planer_start_create_table":
                if self.planer.create_settings_for_table_dto.use_individual_sorting:
                    self.planer.create_table_individual_sorting()
                elif self.planer.create_settings_for_table_dto.create_plan_mode in (
                    CreatePlanMode.umlauf_date,
                    CreatePlanMode.umlauf_weekday,
                ):
                    self.planer.create_umlaufplan()
                else:
                    self.planer.create_table()
            case "planer_start_create_table_continue":
                self.planer.create_table_continue()
            case "planer_start_create_umlaufplan":
                self.planer.create_table_continue()
            case "planer_start_create_umlaufplan_continue":
                if self.planer.create_settings_for_table_dto.use_individual_sorting:
                    self.planer.create_table_individual_sorting()
                else:
                    self.planer.create_table()
            case _:
                raise AttributeError(f"Unknown async function '{function_name}'")

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
            if not self.thread.wait(2000):
                logger.warning("Worker did not stop within timeout.")
            else:
                logger.info("Operation cancelled.")

    def planer_start_load_data(self):
        self.planer.import_gtfs_data()

    def planer_start_create_table(self):
        if self.planer.create_settings_for_table_dto.use_individual_sorting:
            if(self.planer.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_date
                    or self.planer.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_weekday):
                self.planer.create_table_individual_sorting()
            else:
                self.planer.create_table_individual_sorting()
        else:
            if(self.planer.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_date
                    or self.planer.create_settings_for_table_dto.create_plan_mode == CreatePlanMode.umlauf_weekday):
                self.planer.create_umlaufplan()
            else:
                self.planer.create_table()

    def  planer_start_create_table_continue(self):
        self.planer.create_table_continue()

    def  planer_start_create_umlaufplan(self):
        self.planer.create_table_continue()

    def  planer_start_create_umlaufplan_continue(self):
        if self.planer.create_settings_for_table_dto.use_individual_sorting:
            self.planer.create_table_individual_sorting()
        else:
            self.planer.create_table()

    def trigger_action_reset_schedule_planer(self):
        self.planer = None
        self.set_up_schedule_planer()

    def sub_worker_load_gtfsdata(self):
        self.planer.import_gtfs_data()

