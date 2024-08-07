import logging
from PyQt5.Qt import QThread, QObject
from model.Base.GTFSEnums import *
from model.SchedulePlaner.SchedulePlaner import SchedulePlaner

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
delimiter = " "
lineend = '\n'

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

    def planer_start_load_data(self):
        self.planer.import_gtfs_data()

    def planer_start_create_table(self):
        self.planer.create_table()

    def trigger_action_reset_schedule_planer(self):
        self.planer = None
        self.set_up_schedule_planer()

    def error_reset_model(self):
        NotImplemented()

    def sub_worker_load_gtfsdata(self):
        self.planer.import_gtfs_data()

    def sub_worker_update_routes_list(self):
        self.gtfs.get_routes_of_agency()

    def sub_worker_load_gtfsdata_indi(self):
        print('sub_worker_load_gtfsdata_indi')
        NotImplemented()

    def sub_worker_create_output_fahrplan_weekday(self):
        self.gtfs.sub_worker_create_output_fahrplan_weekday()

    def sub_worker_create_output_fahrplan_date(self):
        self.gtfs.sub_worker_create_output_fahrplan_date()

    def sub_worker_create_output_fahrplan_date_indi(self):
        self.gtfs.sub_worker_create_output_fahrplan_date_indi()

    def sub_worker_create_output_fahrplan_date_indi_continue(self):
        self.gtfs.sub_worker_create_output_fahrplan_date_indi_continue()

    def sub_select_date_event(self):
        self.gtfs.selected_weekday = None

    def sub_start_create_table_continue(self):
        self.gtfs.processing = "continue..."
        logging.debug(f'continue...: {self.gtfs.selected_dates}')
        self.worker = GTFSWorker(['sub_worker_create_output_fahrplan_date_indi_continue'], 'Worker',
                                 'create_table_date_individual_continue')
        self.worker.register('sub_worker_create_output_fahrplan_date_indi_continue', self)
        self.worker.start()
        self.worker.finished.connect(self.finished_create_table)

    def sub_start_create_table(self):
        self.gtfs.processing = "create table"
        logging.debug(f'create table date: {self.gtfs.selected_dates}')
        logging.debug(f'create table weekday: {self.gtfs.selected_weekday}')
        logging.debug(f'create table individualsorting: {self.gtfs.individualsorting}')
        if self.gtfs.selected_weekday is None and self.gtfs.individualsorting is True:
            self.worker = GTFSWorker(['sub_worker_create_output_fahrplan_date_indi'], 'Worker',
                                     'create_table_date_individual')
            self.worker.register('sub_worker_create_output_fahrplan_date_indi', self)

        elif self.gtfs.selected_weekday is None:
            self.worker = GTFSWorker(['sub_worker_create_output_fahrplan_date'], 'Worker', 'create_table_date')
            self.worker.register('sub_worker_create_output_fahrplan_date', self)

        else:
            self.worker = GTFSWorker(['sub_worker_create_output_fahrplan_weekday'], 'Worker', 'create_table_weekday')
            self.worker.register('sub_worker_create_output_fahrplan_weekday', self)

        self.worker.start()
        if self.gtfs.selected_weekday is None and self.gtfs.individualsorting is True:
            self.worker.finished.connect(self.update_sorting_table)
        else:
            self.worker.finished.connect(self.finished_create_table)

    def finished_create_table(self):
        self.notify_finished()

    def update_sorting_table(self):
        self.worker = None


    def notify_set_process(self, task):
        self.gtfs.processing = task

    def notify_delete_process(self):
        self.gtfs.processing = None

    def notify_update_stopname_create_list(self):
        NotImplemented()
        return self.dispatch("update_stopname_create_list",
                             "update_stopname_create_list routine started! Notify subscriber!")

    def notify_update_routes_List(self):
        NotImplemented()
        return self.dispatch("update_routes_list",
                             "update_routes_list routine started! Notify subscriber!")

    def notify_update_weekdate_option(self):
        NotImplemented()
        return self.dispatch("update_weekdate_option",
                             "update_weekdate_option routine started! Notify subscriber!")

    def notify_finished(self):
        NotImplemented()
        return self.dispatch("message",
                             "Table created!")
