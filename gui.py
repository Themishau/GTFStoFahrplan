# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import asyncio
import threading
from analyzeGTFS import *
from observer import Publisher, Subscriber

delimiter = " "


# not in use
class Navbar(tk.Frame):
    def __init__(self, root, **kw):
        super().__init__(**kw)
        self.navbarFrame = tk.Frame(root)


# not in use
class Statusbar(tk.Frame):
    def __init__(self, root, **kw):
        super().__init__(**kw)
        self.statusbarFrame = tk.Frame(root)


class InfoBottomPanel(tk.Frame):
    def __init__(self, root, **kw):
        super().__init__(**kw)
        self.sidepanel_frame = tk.Frame(root)
        self.sidepanel_frame.grid(sticky="NSEW")
        self.entry = tk.Label(self.sidepanel_frame, text="Log")
        self.entry.grid(row=0, column=0, sticky=tk.N, pady=0, columnspan=4)
        self.log = tk.Listbox(self.sidepanel_frame, width=80)
        self.log_scroll = tk.Scrollbar(self.sidepanel_frame, orient="vertical")
        self.log.config(yscrollcommand=self.log_scroll.set)
        self.log_scroll.config(command=self.log.yview)
        self.log.grid(row=1, column=0, sticky=tk.N, pady=0, columnspan=4)


class Main(tk.Frame):
    def __init__(self, root, **kw):
        super().__init__(**kw)
        self.main_frame = tk.Frame(root)
        self.main_frame.grid(sticky="NSEW")

        """ Path: Input / Output """
        # label input_path
        self.input = tk.Label(self.main_frame, text="Enter path to GTFS-ZIP-File and click on load GTFS")
        self.input.grid(row=0, column=0, sticky=tk.N, pady=2, columnspan=4)

        # entry input_path
        self.input_path = tk.Entry(self.main_frame, width=80)
        self.input_path.insert(0,
                               'C:/Temp/GTFS.zip')
        self.input_path.grid(row=1, column=0, sticky=tk.N, pady=2, columnspan=4)

        # label output_path
        self.output = tk.Label(self.main_frame, text="Enter path for output")
        self.output.grid(row=2, column=0, sticky=tk.N, pady=2, columnspan=4)

        # entry output_path
        self.output_path = tk.Entry(self.main_frame, width=80)
        self.output_path.insert(0,
                                'C:/Temp/')
        self.output_path.grid(row=3, column=0, sticky=tk.N, pady=2, columnspan=4)

        # entry output_path
        self.dates = tk.Entry(self.main_frame, width=80)
        self.dates.insert(0, '20210324')
        self.dates.grid(row=6, column=0, sticky=tk.N, pady=4, columnspan=4)

        """ Button """
        # button quit
        self.quitButton = tk.Button(self.main_frame, text="Quit", width=30, borderwidth=5, bg='#FBD975')
        self.quitButton.grid(row=7, column=2, sticky=tk.N, pady=0)

        # button start
        self.mainStartButton = tk.Button(self.main_frame, text="Start", width=30, borderwidth=5, bg='#FBD975')
        self.mainStartButton.grid(row=7, column=1, sticky=tk.N, pady=0)

        # button load gtfs
        self.LoadGTFSButton = tk.Button(self.main_frame, text="Load/Check GTFS", width=30, borderwidth=5, bg='#FBD975')
        self.LoadGTFSButton.grid(row=7, column=0, sticky=tk.N, pady=0)

        # state button date pr weekday
        self.toogle_btn_DateWeek = tk.Button(text="WeekDay", width=12)
        self.toogle_btn_DateWeek.grid(row=6, column=0, sticky=tk.N, pady=4, columnspan=4)

        # state button direction
        self.toogle_btn_direction = tk.Button(text="Direction 0", width=12)
        self.toogle_btn_direction.grid(row=7, column=0, sticky=tk.N, pady=4, columnspan=4)

        """ Listbox """
        # lists of weekdays
        self.weekday_list = tk.Listbox(self.main_frame, width=100)
        self.weekday_List_scrollbar = tk.Scrollbar(self.weekday_list, orient="vertical")
        self.weekday_list.config(yscrollcommand=self.weekday_List_scrollbar.set)
        self.weekday_List_scrollbar.config(command=self.weekday_list.yview)
        self.weekday_list.grid(row=6, column=0, sticky=tk.N, pady=4, columnspan=4)

        # lists of routes
        self.routes_List = tk.Listbox(self.main_frame, width=100)
        self.routes_List_scrollbar = tk.Scrollbar(self.routes_List, orient="vertical")
        self.routes_List.config(yscrollcommand=self.routes_List_scrollbar.set)
        self.routes_List_scrollbar.config(command=self.routes_List.yview)
        self.routes_List.grid(row=5, column=0, sticky=tk.N, pady=4, columnspan=4)

        # lists of agency
        self.agency_List = tk.Listbox(self.main_frame, width=100)
        self.agency_List_scrollbar = tk.Scrollbar(self.agency_List, orient="vertical")
        self.agency_List.config(yscrollcommand=self.agency_List_scrollbar.set)
        self.agency_List_scrollbar.config(command=self.agency_List.yview)
        self.agency_List.grid(row=4, column=0, sticky=tk.N, pady=4, columnspan=4)


class View(Publisher, Subscriber):
    def __init__(self, parent, model, events, name):
        Publisher.__init__(self, events)
        Subscriber.__init__(self, name)

        self.model = model

        self.frame = tk.Frame(parent)
        self.main = Main(parent)
        self.sidePanel = InfoBottomPanel(parent)
        self.statusbar = Statusbar(parent)
        self.navbar = Navbar(parent)

        self.process = "initilizing"


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
        self.dispatch("select_route", "select_route routine started! Notify subscriber!")

    def select_agency(self, event):
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
            messagebox.showerror('Error show_instance_attribute', 'contact developer')


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

    # update write_log
    def update(self, event, message):

        if event == "data_changed":
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
                messagebox.showerror('Error toggle', 'contact developer')

        elif option == 1:
            try:
                self.main.toogle_btn_direction.config(text='Direction 1')
            except TypeError:
                messagebox.showerror('Error toggle', 'contact developer')

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
                messagebox.showerror('Error toggle', 'contact developer')
            self.update_weekday_list()
        elif  option == 'Weekday':
            self.main.toogle_btn_DateWeek.config(text='Weekday')
            self.hide_instance_attribute(self.main.dates, 'self.main.dates')
            self.show_instance_attribute('self.main.weekday_list')
            self.update_weekday_list()


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
            messagebox.showerror('Error', 'no path!')
            return
        self.GTFSData = await read_gtfs_data(self.input_path)

    # import routine and
    async def import_gtfs(self):
        self.processing = "loading"
        await self.read_gfts()

        if self.GTFSData == -1:
            messagebox.showerror('Error in read_gtfs_data', 'wrong path!')
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
            messagebox.showinfo('create fahrplan:', 'Done!')
            # except ValueError as e:
            #     print(ValueError)
            #     messagebox.showerror('Error in Create Fahrplan', 'Wrong data! Check input data and output path!')
        else:
            messagebox.showerror('Error in Create Fahrplan', 'Wrong data! Check input data and output path!')
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
            messagebox.showinfo('create fahrplan:', 'Done!')

        else:
            messagebox.showerror('Error in Create Fahrplan', 'Wrong data! Check input data and output path!')
            self.processing = None
            return

    def set_process(self, task):
        self.dispatch("data_changed", "{} started".format(task))
        self.processing = task

    def delete_process(self):
        self.dispatch("data_changed", "{} finished".format(self.processing))
        self.processing = None


class Controller(Publisher, Subscriber):
    def __init__(self, events, name):
        Publisher.__init__(self, events)
        Subscriber.__init__(self, name)

        # init tk
        self.root = tk.Tk()

        # init window size
        self.root.geometry("675x900+0+0")
        self.root.resizable(0, 0)

        # counts running threads
        self.runningAsync = 0

        self.process = "initializing"

        # init model and viewer with publisher
        self.model = Model(['update_weekday_list',
                            'update_routes_List',
                            'update_agency_List',
                            'data_changed'], 'model')

        self.view = View(self.root, self.model, ['select_route',
                                                 'select_agency',
                                                 'start',
                                                 'load_gtfsdata_event',
                                                 'close_program',
                                                 'select_option_button_date_week',
                                                 'select_option_button_direction'
                                                ], 'viewer')

        # init Observer viewer -> controller
        self.view.register('select_route', self)  # Achtung, sich selbst angeben und nicht self.controller
        self.view.register('select_agency', self)  # Achtung, sich selbst angeben und nicht self.controller
        self.view.register('start', self)  # Achtung, sich selbst angeben und nicht self.controller
        self.view.register('load_gtfsdata_event', self)
        self.view.register('select_option_button_date_week', self)
        self.view.register('select_option_button_direction', self)
        self.view.register('close_program', self)

        # init Observer controller -> viewer
        self.register("update_process", self.view)
        self.register('toggle_button_direction_event', self.view)
        self.register('toggle_button_date_week_event', self.view)
        # init Observer model -> viewer
        self.model.register('update_routes_List', self.view)  # Achtung, sich selbst angeben und nicht self.controller
        self.model.register('update_weekday_list', self.view)
        self.model.register('update_agency_List', self.view)
        self.model.register('data_changed', self.view)

    def update(self, event, message):
        if event == "select_route":
            self.select_route()

        elif event == "select_agency":
            self.select_agency()

        elif event == "select_option_button_date_week":
            self.select_option_button_date_week()

        elif event == "select_option_button_direction":
            self.select_option_button_direction()

        elif event == "start":
            self.start()

        elif event == "load_gtfsdata_event":
            self.load_gtfsdata_event()

        elif event == 'close_program':
            self.destroy_info(event)

        self.do_tasks(event)

    async def info(self, message, title="ShowInfo"):
        root = tk.Tk()
        root.overrideredirect(1)
        root.withdraw()
        messagebox.showinfo(title, message)
        return root

    async def destroy_info(self, root):
        root.destroy()

    def select_option_button_direction(self):
        if self.model.selectedRoute is not None:
            try:
                selected_option = self.model.selected_Direction
                if selected_option == 1:
                    self.model.selected_Direction = 0
                elif selected_option == 0:
                    self.model.selected_Direction = 1
                self.dispatch("toggle_button_direction_event",
                              "toggle_button_direction_event routine started! Notify subscriber!")

            except TypeError:
                messagebox.showerror('Error SELECT ROUTE', 'Nothing Selected!')

    def select_option_button_date_week(self):
        if self.model.selectedRoute is not None:
            try:
                options = len(self.model.options_dates_weekday)
                selected_option = self.model.selected_option_dates_weekday
                if selected_option == (options - 1):
                    self.model.selected_option_dates_weekday = 0
                else:
                    self.model.selected_option_dates_weekday = self.model.selected_option_dates_weekday = + 1

                self.dispatch("toggle_button_date_week_event",
                              "toggle_button_date_week_event routine started! Notify subscriber!")
            except TypeError:
                messagebox.showerror('Error SELECT ROUTE', 'Nothing Selected!')

    # loads and updates weekdays list based on selected route
    def select_route(self):
        try:
            selection_route = None
            for route in self.model.routesList:
                if route[0] == self.view.main.routes_List.selection_get():
                    print(self.view.main.routes_List.selection_get())
                    selection_route = route
            if selection_route is None:
                return
            # loads weekdays
            self.model.set_routes(selection_route)

        except TypeError:
            messagebox.showerror('Error SELECT ROUTE', 'Nothing Selected!')

    def select_agency(self):
        try:
            selected_agency = None
            for agency in self.model.agenciesList:
                if agency[1] == self.view.main.agency_List.selection_get():
                    print(self.view.main.agency_List.selection_get())
                    selected_agency = agency
            if selected_agency is None:
                return
            self.model.get_routes_of_agency(selected_agency)
        except TypeError:
            messagebox.showerror('Error SELECT AGENCY', 'Nothing Selected!')

    def get_requested_dates(self):
        try:
            selected_route = self.model.selectedRoute
            print('getreq' + self.view.main.dates.get())
            requested_dates = self.view.main.dates.get()
            self.model.selected_dates = self.view.main.dates.get()
            print('getreq' + self.model.selected_dates)
            if selected_route is None or requested_dates is None:
                print("error no route / wrong dates format ")
                return False
            return True
        except TypeError:
            messagebox.showerror('Error', 'Something went wrong!')

    def get_selected_weekday(self):
        try:
            selected_route = self.model.selectedRoute
            selected_weekday = self.view.main.weekday_list.selection_get()
            for key, value in self.model.weekDayOptions.items():
                if value[1] == self.view.main.weekday_list.selection_get():
                    self.model.selected_weekday = key
            if selected_route is None or selected_weekday is None:
                print("error no route / weekdays selected")
                return False
            return True
        except TypeError:
            messagebox.showerror('Error', 'Something went wrong!')

    def do_tasks(self, button):
        if button == "loadGTFS":
            threading.Thread(target=self.async_task_load_GTFS_data, args=()).start()
        elif button == "loadFahrplan":
            print('start creating fahrplan')
            threading.Thread(target=self.async_task_create_Fahrplan, args=()).start()

    async def task(self, task):
        # create an generic method call
        # self.model_grey -> model_grey
        # self       -> controller
        visit_task = getattr(self.model, task, self.generic_task)
        return await visit_task(task)

    async def generic_task(self, name):
        raise Exception('No model_grey.{} method'.format(name))

    # loads data from zip
    def async_task_load_GTFS_data(self):
        self.set_process("loading GTFS data...")

        # clear list
        if self.view.main.agency_List is not None:
            self.view.main.agency_List.delete(0, 'end')
            self.view.main.routes_List.delete(0, 'end')

        # check if program is already running
        if self.runningAsync > 0:
            messagebox.showerror('Error', 'Program is already running')
            return

        loop = asyncio.new_event_loop()
        self.runningAsync = self.runningAsync + 1
        loop.run_until_complete(self.model.import_gtfs())
        loop.close()
        self.runningAsync = self.runningAsync - 1
        self.set_process("GTFS data loaded")

    # routine to create fahrplan
    def async_task_create_Fahrplan(self):
        if self.runningAsync > 0:
            messagebox.showerror('Error', 'Program is already running')
            return
        print('selection:' + self.model.options_dates_weekday[self.model.selected_option_dates_weekday])
        # checks and sets the selected route for fahrplan
        if self.model.options_dates_weekday[self.model.selected_option_dates_weekday] == 'Weekday':
            if self.get_selected_weekday():
                self.set_process(
                    "creating...: " + self.model.selectedAgency[1] + delimiter + self.model.selectedRoute[
                        0] + delimiter + str(self.model.selected_weekday) + delimiter + str(
                        self.model.selected_Direction))
                loop = asyncio.new_event_loop()
                self.runningAsync = self.runningAsync + 1
                loop.run_until_complete(self.model.createFahrplan_weekday())
                loop.close()
                self.runningAsync = self.runningAsync - 1
                self.set_process("created,  " + str(self.model.time) + " seconds")
            else:
                messagebox.showerror('Error', 'no route/weekday')

        elif self.model.options_dates_weekday[self.model.selected_option_dates_weekday] == 'Dates':
            if self.get_requested_dates():
                self.set_process(
                    "creating...: " + self.model.selectedAgency[1] + delimiter + self.model.selectedRoute[
                        0] + delimiter + str(self.model.selected_dates) + delimiter + str(
                        self.model.selected_Direction))
                loop = asyncio.new_event_loop()
                self.runningAsync = self.runningAsync + 1
                loop.run_until_complete(self.model.createFahrplan_dates())
                loop.close()
                self.runningAsync = self.runningAsync - 1
                self.set_process("created,  " + str(self.model.time) + " seconds")
            else:
                messagebox.showerror('Error', 'no route/dates')

    def load_gtfsdata_event(self):
        try:
            self.model.input_path = self.view.main.input_path.get()
            self.model.output_path = self.view.main.output_path.get()
        except TypeError:
            messagebox.showerror('Error', 'check path')
        button = "loadGTFS"
        self.do_tasks(button)

    def start(self):
        self.set_process("start: create fahrplan...")
        button = "loadFahrplan"
        self.do_tasks(button)

    def close_program(self):
        self.root.destroy()

    def set_process(self, task):
        self.dispatch("update_process", "{} started".format(task))
        self.process = task

    def update_log(self, task):
        self.dispatch("update_process", "{}".format(task))
        self.process = task

    def delete_process(self):
        self.dispatch("update_process", "{} finished".format(self.process))
        self.process = None

    def run(self):
        self.root.title("GTFS to Fahrplan")
        # sets the window in focus
        self.root.deiconify()
        self.root.mainloop()
