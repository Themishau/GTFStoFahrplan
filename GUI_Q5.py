import asyncio
import threading

from analyzeGTFS import *
from observer import Publisher, Subscriber
import datetime as dt
import time
import sys
from PyQt5 import uic, QtGui, QtCore
from PyQt5.Qt import *
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import QSize, Qt

delimiter = " "

class Model(Publisher, Subscriber):
    def __init__(self, events, name):
        Publisher.__init__(self, events)
        Subscriber.__init__(self, name)
        self.input_path = None
        self.output_path = None
        self.options_dates_weekday = ['Dates', 'Weekday']
        self.selected_option_dates_weekday = 1
        self.selected_Direction = 0
        self.time = None
        self.processing = None

        """ dicts for create and listbox """
        self.stopsdict = None
        self.stopTimesdict = None
        self.tripdict = None
        self.calendarWeekdict = None
        self.calendarDatesdict = None
        self.routesFahrtdict = None
        self.agencyFahrtdict = None

        """ loaded GTFSData """
        self.GTFSData = None

        """ loaded data for listbox """
        self.agenciesList = None
        self.routesList = None
        self.weekdayList = None

        """ loaded data for create """
        self.selectedAgency = None
        self.selectedRoute = None
        self.selected_weekday = None
        self.selected_dates = None

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

    # checks if all data is avalibale before creation
    def data_loaded_and_available(self):
        if (self.stopsdict is None
                or self.stopTimesdict is None
                or self.tripdict is None
                or self.calendarWeekdict is None
                or self.calendarDatesdict is None
                or self.routesFahrtdict is None
                or self.selectedRoute is None
                or self.selected_Direction is None):
            return False
        else:
            return True

    # reads the files
    async def read_gfts(self):
        if self.input_path is None:
            self.dispatch('message','Error. No input path!')
            return
        self.GTFSData = await read_gtfs_data(self.input_path)

    # import routine and
    async def import_gtfs(self):
        self.processing = "loading"
        await self.read_gfts()

        if self.GTFSData == -1:
            self.dispatch('message','Error in read_gtfs_data. Wrong path!')
            return -1

        await self.get_gtfs()
        self.agenciesList = await read_gtfs_agencies(self.agencyFahrtdict)
        print("self.agenciesList = await read_gtfs_agencies(self.agencyFahrtdict)")
        self.dispatch("update_agency_List",
                      "update_agency_List routine started! Notify subscriber!")
        self.processing = None

    # gets the data out of GTFSData and releases some memory
    async def get_gtfs(self):
        self.stopsdict, \
        self.stopTimesdict, \
        self.tripdict, \
        self.calendarWeekdict, \
        self.calendarDatesdict, \
        self.routesFahrtdict, \
        self.agencyFahrtdict = await get_gtfs(self.GTFSData)

        # clear some variables not needed anymore
        self.GTFSData = None

    def get_routes_of_agency(self, agency):
        self.selectedAgency = agency
        self.routesList = select_gtfs_routes_from_agancy(agency, self.routesFahrtdict)
        self.dispatch("update_routes_List",
                      "update_routes_List routine started! Notify subscriber!")

    def set_routes(self, route):
        self.selectedRoute = route
        self.dispatch("update_weekday_list",
                      "update_weekday_list routine started! Notify subscriber!")


    async def createFahrplan_dates(self):
        self.processing = "creating"
        route_name = [self.selectedRoute]
        if (self.data_loaded_and_available()
                and self.selectedRoute is not None
                and self.selected_dates is not None
                and self.options_dates_weekday[self.selected_option_dates_weekday] == 'Dates'):
            tasks_date = [create_fahrplan_dates(name[0],
                                                self.selectedAgency[0],
                                                self.selected_dates,
                                                self.selected_Direction,
                                                self.stopsdict,
                                                self.stopTimesdict,
                                                self.tripdict,
                                                self.calendarWeekdict,
                                                self.calendarDatesdict,
                                                self.routesFahrtdict,
                                                self.agencyFahrtdict,
                                                self.output_path) for name in route_name]

            # stores results and some information
            # try:
            completed, pending = await asyncio.wait(tasks_date)
            results = [task.result() for task in completed]
            self.time = "time: {} ".format(results[0][0])
            create_output_fahrplan(route_name[0][0], 'dates_' + str(results[0][1]), results[0][2], results[0][3],
                                   self.output_path)
            self.processing = None
            self.dispatch('message','create fahrplan: Done!')
            # except ValueError as e:
            #     print(ValueError)
            #     messagebox.showerror('Error in Create Fahrplan', 'Wrong data! Check input data and output path!')
        else:
            self.dispatch('message','Error in Create Fahrplan. Wrong data! Check input data and output path!')
            self.processing = None
            return

    async def createFahrplan_weekday(self):
        self.processing = "creating"
        selected_weekday_option = self.selected_weekday
        route_name = [self.selectedRoute]
        if (self.data_loaded_and_available()
                and self.selectedRoute is not None
                and self.options_dates_weekday[self.selected_option_dates_weekday] == 'Weekday'):
            tasks_weekday = [create_fahrplan_weekday(name[0],
                                                     self.selectedAgency[0],
                                                     selected_weekday_option,
                                                     self.selected_Direction,
                                                     self.stopsdict,
                                                     self.stopTimesdict,
                                                     self.tripdict,
                                                     self.calendarWeekdict,
                                                     self.calendarDatesdict,
                                                     self.routesFahrtdict,
                                                     self.agencyFahrtdict,
                                                     self.output_path) for name in route_name]

            # stores results and some information
            completed, pending = await asyncio.wait(tasks_weekday)
            results_weekday = [task.result() for task in completed]
            self.time = "time: {} ".format(results_weekday[0][0])

            create_output_fahrplan(route_name[0][0], 'weekday_' + str(results_weekday[0][1]), results_weekday[0][2],
                                   results_weekday[0][3], self.output_path)
            self.processing = None
            self.dispatch('message', 'Done')

        else:
            self.dispatch('message', 'Error in Create Fahrplan. Check input data and output path!')
            self.processing = None
            return

    def set_process(self, task):
        self.dispatch("data_changed", "{} started".format(task))
        self.processing = task

    def delete_process(self):
        self.dispatch("data_changed", "{} finished".format(self.processing))
        self.processing = None


class Gui(QWidget, Publisher, Subscriber):
    def __init__(self, events, name, *args, **kwargs):
        print(*args)
        print('hi')
        print(events)
        print('hi')
        print(name)
        print('hi')
        super().__init__(events=events, name=name)
        # Publisher.__init__(self, events)
        # Subscriber.__init__(self, name)
        # QWidget.__init__(self)

        self.messageBox_model = QMessageBox()

        uic.loadUi("GTFSQT5Q.ui", self)
        self.setStyleSheet("background: #161219;")

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


        self.refresh_time = self.get_current_time()



        self.show()


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



    def send_message_box(self, text):
        self.messageBox_model.setText(text)

    def update(self, *args):
        print(*args)

        # hidden and shown widgets
        self.hiddenwidgets = {}

        # bind events to lists
        self.main.routes_List.bind('<<ListboxSelect>>', self.select_route)
        self.main.agency_List.bind('<<ListboxSelect>>', self.select_agency)
        self.hide_instance_attribute(self.main.dates, 'self.main.dates')

        # bind events to buttons
        self.main.mainStartButton.bind("<Button>", self.start)
        self.main.LoadGTFSButton.bind("<Button>", self.load_gtfsdata_event)
        self.main.quitButton.bind("<Button>", self.close_program)

        self.main.toogle_btn_DateWeek.bind("<Button>", self.select_option_button_date_week)
        self.main.toogle_btn_direction.bind("<Button>", self.select_option_button_direction)

    def select_route(self, event):
        print("dispatch select_route")
        self.dispatch("select_route", "select_route routine started! Notify subscriber!")

    def select_agency(self, event):
        print("dispatch select_agency")
        self.dispatch("select_agency", "select_agency routine started! Notify subscriber!")

    def start(self, event):
        self.dispatch("start", "start routine started! Notify subscriber!")

    def load_gtfsdata_event(self, event):
        self.dispatch("load_gtfsdata_event", "load_gtfsdata_event routine started! Notify subscriber!")

    def select_option_button_date_week(self, event):
        self.dispatch("select_option_button_date_week", "select_option_button_date_week routine started! Notify subscriber!")

    def select_option_button_direction(self, event):
        self.dispatch("select_option_button_direction", "select_option_button_direction routine started! Notify subscriber!")

    def close_program(self, event):
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