import asyncio
import threading

from gtfs import gtfs
from observer import Publisher, Subscriber
import datetime as dt
import time
import sys
from datetime import datetime, timedelta
from PyQt5 import uic, QtGui, QtCore
from PyQt5.Qt import *
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QLabel

delimiter = " "

class Model(Publisher, Subscriber):
    def __init__(self, events, name):
        Publisher.__init__(self, events)
        Subscriber.__init__(self, name)
        self.gtfs = gtfs()


        self.weekDayOptions = {0: [0, 'Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday'],
                               1: [1, 'Monday, Tuesday, Wednesday, Thursday, Friday'],
                               2: [2, 'Monday'],
                               3: [3, 'Tuesday'],
                               4: [4, 'Wednesday'],
                               5: [5, 'Thursday'],
                               6: [6, 'Friday'],
                               7: [7, 'Saturday'],
                               8: [8, 'Sunday'],
                               }


    def set_paths(self, input_path, output_path):
        try:
            self.gtfs.set_paths(input_path, output_path)
        except:
            print('error setting paths')

    # reads the files
    async def read_gfts(self):
        if self.gtfs.input_path is None\
                or self.gtfs.output_path is None:
            self.dispatch('message','Error. Check Paths!')
            return
        await self.gtfs.read_gtfs_data()

    # import routine and
    async def import_gtfs(self):
        self.processing = "loading"
        await self.read_gfts()
        await self.gtfs.get_gtfs()

        self.agenciesList = await self.gtfs.read_gtfs_agencies()
        print("self.agenciesList = await read_gtfs_agencies(self.agencyFahrtdict)")
        self.dispatch("update_agency_List",
                      "update_agency_List routine started! Notify subscriber!")
        self.processing = None



    def get_routes_of_agency(self, agency):
        self.selectedAgency = agency
        self.routesList = self.gtfs.select_gtfs_routes_from_agancy(agency)
        self.dispatch("update_routes_List",
                      "update_routes_List routine started! Notify subscriber!")

    def set_routes(self, route):
        self.selectedRoute = route
        self.dispatch("update_weekday_list",
                      "update_weekday_list routine started! Notify subscriber!")

    def set_process(self, task):
        self.dispatch("data_changed", "{} started".format(task))
        self.processing = task

    def delete_process(self):
        self.dispatch("data_changed", "{} finished".format(self.processing))
        self.processing = None

    def notify_model(self, event, message):
        print(event)
        if event == 'message_test':
            self.message_test('message event')

    def message_test(self, message):
        if message is None:
            print(message)
        else:
            print('empty message')
        self.dispatch('message', message)


class Gui(QWidget, Publisher, Subscriber):
    def __init__(self, events, name, *args, **kwargs):
        super().__init__(events=events, name=name)
        uic.loadUi("GTFSQT5Q.ui", self)

        # self.setStyleSheet("background: #ebecff;")


        self.setFixedSize(910, 703)

        pixmap = QPixmap('assets/5282.jpg')
        self.label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.center()
        self.oldPos = self.pos()


        self.messageBox_model = QMessageBox()

        self.btnImport.clicked.connect(self.load_gtfsdata_event)

        # init model and viewer with publisher
        self.model = Model(['update_weekday',
                            'update_routes',
                            'update_agency',
                            'error_message',
                            'message',
                            'data_changed'], 'model')

        # init Observer model -> controller
        self.model.register('update_routes', self)  # Achtung, sich selbst angeben und nicht self.controller
        self.model.register('update_weekday', self)
        self.model.register('update_agency', self)
        self.model.register('message', self)
        self.model.register('data_changed', self)

        self.register('message_test', self.model)


        self.refresh_time = self.get_current_time()

        self.print_me()

    def btn_test(self, event):
        print('clicked: {}'.format(event))


    def notify_model(self, event, message):
        if event == "message":
            self.messageBox_model.setText(message)
        elif event == "data_changed":
            self.write_gui_log("{}".format(message))
        elif event == "update_process":
            self.write_gui_log("{}".format(message))
        elif event == "toggle_button_direction_event":
            self.toggle_button_direction_event()
        elif event == "toggle_button_date_week_event":
            self.toggle_button_date_week_event()
        elif event == "update_routes_List":
            self.update_routes_List()
        elif event == "update_weekday_list":
            self.update_weekday_list()
        elif event == "update_agency_List":
            self.update_agency_List()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def send_message_box(self, text):
        self.messageBox_model.setText(text)

    def select_route(self):
        print("dispatch select_route")
        self.dispatch("select_route", "select_route routine started! Notify subscriber!")

    def select_agency(self):
        print("dispatch select_agency")
        self.dispatch("select_agency", "select_agency routine started! Notify subscriber!")

    def start(self):
        self.dispatch("start", "start routine started! Notify subscriber!")

    def load_gtfsdata_event(self):
        print('loading data!')
        self.dispatch("message_test", "load_gtfsdata_event routine started! Notify subscriber!")
        # threading.Thread(target=self.async_task_load_GTFS_data, args=()).start()

    def select_option_button_date_week(self):
        self.dispatch("select_option_button_date_week", "select_option_button_date_week routine started! Notify subscriber!")

    def select_option_button_direction(self):
        self.dispatch("select_option_button_direction", "select_option_button_direction routine started! Notify subscriber!")

    def close_program(self):
        self.dispatch("close_program", "close_program routine started! Notify subscriber!")

    def hide_instance_attribute(self, instance_attribute, widget_variablename):
        print(instance_attribute)
        self.hiddenwidgets[widget_variablename] = instance_attribute.grid_info()
        instance_attribute.grid_remove()

    def show_instance_attribute(self, widget_variablename):
        try:
            # gets the information stored in
            widget_grid_information = self.hiddenwidgets[widget_variablename]
            print(widget_grid_information)
            # gets variable and sets grid
            eval(widget_variablename).grid(row=widget_grid_information['row'], column=widget_grid_information['column'],
                                           sticky=widget_grid_information['sticky'],
                                           pady=widget_grid_information['pady'],
                                           columnspan=widget_grid_information['columnspan'])
        except TypeError:
            self.send_message_box('Error show_instance_attribute')

    def bind_selection_to_Listbox(self):
        # bind list selections
        self.main.routes_List.bind('<<ListboxSelect>>', self.select_route)
        self.main.agency_List.bind('<<ListboxSelect>>', self.select_agency)
        # self.view.main.agency_List.unbind_all(self)

    # loads data from zip
    def async_task_load_GTFS_data(self):
        self.set_process("loading GTFS data...")

        # clear list
        if self.view.main.agency_List is not None:
            self.view.main.agency_List.delete(0, 'end')
            self.view.main.routes_List.delete(0, 'end')

        # check if program is already running
        if self.runningAsync > 0:
            return

        loop = asyncio.new_event_loop()
        self.runningAsync = self.runningAsync + 1
        loop.run_until_complete(self.model.import_gtfs())
        loop.close()
        self.runningAsync = self.runningAsync - 1
        self.set_process("GTFS data loaded")


    def update_weekday_list(self):
        self.set_process("updating weekdays list...")
        if self.model.options_dates_weekday[self.model.selected_option_dates_weekday] == 'Weekday':
            if self.main.weekday_list is not None:
                self.main.weekday_list.delete(0, 'end')
                for x in range(0, 9):
                    self.main.weekday_list.insert("end", str(self.model.weekDayOptions[x][1]))
                # self.view.main.agency_List.grid(row=0, column=0, columnspan=1)
            self.set_process("weekdays list updated")
        elif self.model.options_dates_weekday[self.model.selected_option_dates_weekday] == 'Dates':
            if self.main.weekday_list is not None:
                self.main.weekday_list.delete(0, 'end')

    def update_routes_List(self):
        self.set_process("updating routes list...")
        if self.main.routes_List is not None:
            self.main.routes_List.delete(0, 'end')
        for routes in self.model.routesList:
            self.main.routes_List.insert("end", routes[0])
            # self.view.main.agency_List.grid(row=0, column=0, columnspan=1)
        self.set_process("routes list updated")

    def update_agency_List(self):
        self.set_process("updating agencies list...")
        for agency in self.model.agenciesList:
            # printAgency = agency[0] + ", " + agency[1]
            self.main.agency_List.insert("end", agency[1])
            # self.view.main.agency_List.grid(row=0, column=0, columnspan=1)
        self.set_process("agencies list updated")


    def set_process(self, task):
        self.update("update_process", "{} started".format(task))
        self.process = task

    def delete_process(self):
        self.update("update_process", "{} finished".format(self.process))
        self.process = None

    def toggle_button_direction_event(self):
        option = self.model.selected_Direction
        if option == 0:
            try:
                self.main.toogle_btn_direction.config(text='Direction 0')
            except TypeError:
                self.send_message_box('Error toggle')

        elif option == 1:
            try:
                self.main.toogle_btn_direction.config(text='Direction 1')
            except TypeError:
                self.send_message_box('Error toggle')

    def write_gui_log(self, text):
        time_now = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
        self.sidePanel.log.insert("end", str(time_now) + ': ' + text)
        self.sidePanel.log.yview("end")

    def toggle_button_date_week_event(self):
        option = self.model.options_dates_weekday[self.model.selected_option_dates_weekday]
        if option == 'Dates':
            self.main.toogle_btn_DateWeek.config(text='Dates')
            try:
                self.hide_instance_attribute(self.main.weekday_list, 'self.main.weekday_list')
                self.show_instance_attribute('self.main.dates')
            except TypeError:
                self.send_message_box('Error toggle')
            self.update_weekday_list()
        elif  option == 'Weekday':
            self.main.toogle_btn_DateWeek.config(text='Weekday')
            self.hide_instance_attribute(self.main.dates, 'self.main.dates')
            self.show_instance_attribute('self.main.weekday_list')
            self.update_weekday_list()

    def get_current_time(self):
        """ Helper function to get the current time in seconds. """

        now = dt.datetime.now()
        total_time = (now.hour * 3600) + (now.minute * 60) + now.second
        return total_time

    def refresh_data(self):
        if (self.get_current_time() - self.refresh_time) > 10:
            time.sleep(1)
            self.refresh_time = self.get_current_time()
        self.update_log(("still processing. Please wait...", "{} finished".format(self.process)))

def main(events, name):
    app = QApplication(sys.argv)
    window = Gui(events=events, name=name)
    window.show()
    app.exec_()





# class Controller(Gui, Publisher, Subscriber):
#     def __init__(self, events, name):
#         QMainWindow.__init__(self, Gui)
#         Publisher.__init__(self, events)
#         Subscriber.__init__(self, name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Gui(events=['update_process', 'toggle_button_direction_event', 'toggle_button_date_week_event'], name='controller')
    app.exec_()