import logging

from PySide6.QtCore import QObject, QThread, Signal

from .Enum.GTFSEnums import CreatePlanMode
from .SchedulePlaner.SchedulePlaner import SchedulePlaner

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


class Worker(QObject):
    finished = Signal()
    error = Signal(Exception)

    def __init__(self, function):
        super().__init__()
        self.function = function

    def run(self):
        try:
            self.function()
            self.finished.emit()
        except Exception as e:
            self.error.emit(e)

# noinspection PyUnresolvedReferences
class Model(QObject):
    def __init__(self, event_loop):
        super().__init__()
        self.worker = None
        self.event_loop = event_loop
        self.planer = None
        self.thread = None

    def set_up_schedule_planer(self):
        self.planer = SchedulePlaner(self.event_loop)
        self.planer.initilize_scheduler()

    def set_up_umlauf_planer(self):
        NotImplemented

    def start_function_async(self, function_name):
        # Create a thread
        self.thread = QThread()

        worker_function = getattr(self, function_name)
        # Create Worker and move it to the thread
        self.worker = Worker(worker_function)
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)  # Start worker when the thread starts
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self.handle_worker_error)

        # Start the thread
        self.thread.start()

    # def start_function_async(self, function_name):
    #     # this is fine!
    #
    #     # Create a thread
    #     self.thread = QThread()
    #     # self.moveToThread(self.thread)
    #     # # Ensure the correct function is passed
    #     # self.thread.started.connect(getattr(self, function_name))
    #     # self.thread.start()
    #
    #     worker_function = getattr(self, function_name)
    #     # Create Worker and move it to the thread
    #     self.worker = Worker(worker_function)
    #     self.worker.moveToThread(self.thread)
    #
    #     # Connect signals and slots
    #     self.thread.started.connect(self.worker.run)  # Start worker when the thread starts
    #     self.worker.finished.connect(self.thread.quit)
    #     self.worker.finished.connect(self.worker.deleteLater)
    #     self.thread.finished.connect(self.thread.deleteLater)
    #     self.worker.error.connect(self.handle_worker_error)
    #
    #     # Start the thread
    #     self.thread.start()

    def handle_worker_error(self, error):
        logging.error(f"Worker encountered an error: {error}. {type(error).__name__}")
        #self.error.emit(f"Failed. Create table failed. Error: {error}  {type(error).__name__}")

    def cancel_async_operation(self):
        if self.thread.isRunning():
            logging.info("Cancelling ongoing operation...")
            self.cancel_event.set()
            self.thread.quit()
            self.thread.wait()
            logging.info("Operation cancelled.")

    def planer_start_load_data(self):
        self.planer.import_gtfs_data()

    def planer_start_create_table(self):
        if self.planer.create_settings_for_table_dto.individual_sorting:
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
        if self.planer.create_settings_for_table_dto.individual_sorting:
            self.planer.create_table_individual_sorting()
        else:
            self.planer.create_table()

    def trigger_action_reset_schedule_planer(self):
        self.planer = None
        self.set_up_schedule_planer()

    def sub_worker_load_gtfsdata(self):
        self.planer.import_gtfs_data()

