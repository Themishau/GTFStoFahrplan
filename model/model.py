import logging
from PySide6.QtCore import QObject, QThread
from model.SchedulePlaner.SchedulePlaner import SchedulePlaner
from model.Enum.GTFSEnums import CreatePlanMode

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

# noinspection PyUnresolvedReferences
class Model(QObject):
    def __init__(self, event_loop):
        super().__init__()
        self.event_loop = event_loop
        self.planer = None
        # we use this thread, to start processes not in the main gui thread
        self.thread = None

    def set_up_schedule_planer(self):
        self.planer = SchedulePlaner(self.event_loop)
        self.planer.initilize_scheduler()

    def set_up_umlauf_planer(self):
        NotImplemented

    def start_function_async(self, function_name):
        """
        pass argument via getattr (object_name: self.model, function_name: foo)
        :param function_name: getattr (object_name: self.model, function_name: foo)
        :return:
        """
        self.thread = QThread()
        self.moveToThread(self.thread)

        self.thread.started.connect(getattr(self, function_name))
        self.thread.start()

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

