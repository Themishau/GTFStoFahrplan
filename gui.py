# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from analyzeGTFS import *
import asyncio
import threading

log = {
        "Message": [],
        "Error_Message": []
      }

class Navbar(tk.Frame):
    def __init__(self, root):
        self.navbarFrame = tk.Frame(root)
        self.navbarFrame.pack(side=tk.LEFT, fill=tk.BOTH)

class Statusbar(tk.Frame):
    def __init__(self, root):
        self.statusbarFrame = tk.Frame(root)
        self.statusbarFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)

class SidePanel(tk.Frame):
    def __init__(self, root):
        self.sidepanelFrame = tk.Frame(root)
        self.sidepanelFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.log = tk.Listbox(self.sidepanelFrame, width=40)
        self.log_scroll = tk.Scrollbar(self.sidepanelFrame, orient="vertical")
        self.log.config(yscrollcommand=self.log_scroll.set)
        self.log_scroll.config(command=self.log.yview)
        self.log.pack(side=tk.BOTTOM)


class Main(tk.Frame):
    def __init__(self, root):

        self.mainFrame = tk.Frame(root)
        self.mainFrame.pack(side=tk.TOP, fill=tk.BOTH)

        #textfield
        self.namelbl = tk.Label(self.mainFrame, text="Enter path to GTFS-ZIP-File and click on load GTFS")
        self.namelbl.pack(side=tk.TOP)

        #entry
        self.path = tk.Entry(self.mainFrame, width=80)
        self.path.insert(0,'E:/onedrive/1_Daten_Dokumente_Backup/1_Laptop_Backup_PC/1000_Programmieren und Wirtschaftsinformatik/Praxisarbeit/GTFStoFahrplan/GTFS.zip')
        self.path.pack(side=tk.TOP)

        #button quit
        self.quitButton = tk.Button(self.mainFrame, text="Quit", width=30, borderwidth=5)
        self.quitButton.pack(side=tk.BOTTOM )
        #button start
        self.mainStartButton = tk.Button(self.mainFrame, text="Start", width=30, borderwidth=5)
        self.mainStartButton.pack(side=tk.BOTTOM)

        #lists of services
        self.services_List = tk.Listbox(self.mainFrame, width=55)
        self.services_List_scrollbar = tk.Scrollbar(self.services_List, orient="vertical")
        self.services_List.config(yscrollcommand=self.services_List_scrollbar.set)
        self.services_List_scrollbar.config(command=self.services_List.yview)
        self.services_List.pack(side=tk.BOTTOM, fill=tk.X)

        #lists of routes
        self.routes_List = tk.Listbox(self.mainFrame, width=20)
        self.routes_List_scrollbar = tk.Scrollbar(self.routes_List, orient="vertical")
        self.routes_List.config(yscrollcommand=self.routes_List_scrollbar.set)
        self.routes_List_scrollbar.config(command=self.routes_List.yview)
        self.routes_List.pack(side=tk.BOTTOM, fill=tk.X)

        #lists of agency
        self.agency_List = tk.Listbox(self.mainFrame, width=40)
        self.agency_List_scrollbar = tk.Scrollbar(self.agency_List, orient="vertical")
        self.agency_List.config(yscrollcommand=self.agency_List_scrollbar.set)
        self.agency_List_scrollbar.config(command=self.agency_List.yview)
        self.agency_List.pack(side=tk.BOTTOM, fill=tk.X)

        #button load gtfs
        self.LoadGTFSButton = tk.Button(self.mainFrame, text="Load/Check GTFS", width=30, borderwidth=5)
        self.LoadGTFSButton.pack(side=tk.TOP)


class Model():
    def __init__(self):
        self.path = None
        self.GTFSData = None
        self.stopsdict = None
        self.stopTimesdict = None
        self.tripdict = None
        self.calendarWeekdict = None
        self.calendarDatesdict = None
        self.routesFahrtdict = None
        self.agencyFahrtdict = None

        self.agenciesList = None
        self.routesList = None
        self.servicesList = None

        self.selectedAgency = None
        self.selectedRoute = None
        self.selectedService = None


    def dataLoadedAndAvailable(self):
        if (self.stopsdict == None
         or self.stopTimesdict == None
         or self.tripdict == None
         or self.calendarWeekdict == None
         or self.calendarDatesdict == None
         or self.routesFahrtdict == None
         or self.selectedService == None
         or self.selectedRoute == None):
            return False
        else:
            return True

    #import the data into the data framework
    async def import_GTFS(self):
        await self.readGFTS()
        await self.getGTFS()
        self.agenciesList = await read_gtfs_agencies(self.agencyFahrtdict)
        print("GTFS imported")

    #reads the files
    async def readGFTS(self):
        if (self.path == None):
            messagebox.showerror( 'Error', 'no path!')
            return
        self.GTFSData = await read_gtfs_data(self.path)

    #gets the data out of the files
    async def getGTFS(self):
        self.stopsdict, self.stopTimesdict, self.tripdict, self.calendarWeekdict, self.calendarDatesdict, self.routesFahrtdict, self.agencyFahrtdict = await get_gtfs(self.GTFSData)
        #clear some variables not needed anymore
        self.GTFSData = None

    def getRoutesOfAgency(self, agency):
        print('agencies loading...')
        self.selectedAgency = agency
        self.routesList = select_gtfs_routes_from_agancy(agency, self.routesFahrtdict)
        print("routes of agencies loaded")

    def getServicesOfRoutes(self, route):
        print('services loading...')
        self.selectedRoute = route
        self.servicesList = select_gtfs_services_from_routes(route, self.tripdict, self.calendarWeekdict)
        print("services of routes loaded")

    async def createFahrplan(self):
        print('fahrplan creating...')
        if (self.dataLoadedAndAvailable() and self.selectedRoute != None and self.selectedService != None):
            selectedService = self.selectedService.split(",")
            routeName = [self.selectedRoute]
            tasks = [get_fahrt_ofroute_fahrplan(name[0], self.selectedAgency[0],  selectedService[0], self.stopsdict, self.stopTimesdict, self.tripdict, self.calendarWeekdict, self.calendarDatesdict, self.routesFahrtdict, self.agencyFahrtdict) for name in routeName]
            completed, pending = await asyncio.wait(tasks)
            results = [task.result() for task in completed]
            print ("time: {} ".format(results[0]))
            print()
        else:
            messagebox.showerror( 'Error in Create Fahrplan', 'Missing Data!')
            return

class Controller():
    def __init__(self):

        #init tk
        self.root = tk.Tk()

        #init window size
        self.root.geometry("500x650+200+200")
        self.root.resizable(0, 0)
        #counts running threads
        self.runningAsync = 0

        #init model and viewer
        self.model = Model()
        self.view = View(self.root)

        #bind side panel buttons and functions
        self.view.main.routes_List.bind('<<ListboxSelect>>', self.selection_route)
        self.view.main.agency_List.bind('<<ListboxSelect>>', self.selection_agency)

        self.view.main.mainStartButton.bind("<Button>", self.start)
        self.view.main.LoadGTFSButton.bind("<Button>", self.loadGTFSDATA)
        self.view.main.quitButton.bind("<Button>", self.closeprogram)

    def selection_route(self, event):
        try:
            selection_route = None
            for route in self.model.routesList:
                if (route[0] == self.view.main.routes_List.selection_get()):
                    print(self.view.main.routes_List.selection_get())
                    selection_route = route
            if (selection_route == None):
                return
            self.model.getServicesOfRoutes(selection_route)
            self.model.selectedRoute = selection_route
            self.update_services_List()
        except:
            messagebox.showerror('Error SELECT ROUTE', 'Nothing Selected!')

    def selection_agency(self, event):
        try:
            selected_agency = None
            for agency in self.model.agenciesList:
                if (agency[1] == self.view.main.agency_List.selection_get()):
                    print(self.view.main.agency_List.selection_get())
                    selected_agency = agency
            if (selected_agency == None):
                return
            self.model.getRoutesOfAgency(selected_agency)
            self.update_routes_List()


        except:
            messagebox.showerror('Error SELECT AGENCY', 'Nothing Selected!')

    def selectionBindings(self):
        #bind list selections
        self.view.main.routes_List.bind('<<ListboxSelect>>', self.selection_route)
        self.view.main.agency_List.bind('<<ListboxSelect>>', self.selection_agency)
        #self.view.main.agency_List.unbind_all(self)

    def update_services_List(self):
        if (self.view.main.services_List != None):
            self.view.main.services_List.delete(0,'end')
        for services in self.model.servicesList:
            stringWeekdays = ''
            stringWeekdays = stringWeekdays + ('Monday, ' if services[1] == '1' else '')
            stringWeekdays = stringWeekdays + ('Tuesday, ' if services[2] == '1' else '')
            stringWeekdays = stringWeekdays + ('Wednesday, ' if services[3] == '1' else '')
            stringWeekdays = stringWeekdays + ('Thursday, ' if services[4] == '1'  else '')
            stringWeekdays = stringWeekdays + ('Friday, ' if services[5] == '1' else '')
            stringWeekdays = stringWeekdays + ('Saturday, ' if services[6] == '1' else '')
            stringWeekdays = stringWeekdays + ('Sunday, ' if services[7] == '1' else '')
            self.view.main.services_List.insert("end", str(services[0]) + ', ' + stringWeekdays)
            #self.view.main.agency_List.grid(row=0, column=0, columnspan=1)
        print("services list updated")

    def update_routes_List(self):
        if (self.view.main.routes_List != None):
            self.view.main.routes_List.delete(0,'end')
        for routes in self.model.routesList:
            self.view.main.routes_List.insert("end", routes[0])
            #self.view.main.agency_List.grid(row=0, column=0, columnspan=1)
        print("routes list updated")

    def update_agency_List(self):
        for agency in self.model.agenciesList:
            #printAgency = agency[0] + ", " + agency[1]
            self.view.main.agency_List.insert("end", agency[1])
            #self.view.main.agency_List.grid(row=0, column=0, columnspan=1)
        print("agency list updated")

    def async_loadGTFS(self):
        #clear list
        if (self.view.main.agency_List != None):
            self.view.main.agency_List.delete(0,'end')
            self.view.main.routes_List.delete(0,'end')

        #check if program is already running
        if(self.runningAsync > 0):
            messagebox.showerror('Error', 'Program is already running')
            return

        loop = asyncio.new_event_loop()
        self.runningAsync = self.runningAsync + 1
        loop.run_until_complete(self.model.import_GTFS())
        self.update_agency_List()
        loop.close()

        self.runningAsync = self.runningAsync - 1

    def service_route_selected(self):
        try:
            selected_route = None
            selected_route = self.model.selectedRoute
            selected_service = None
            selected_service = self.view.main.services_List.selection_get()
            self.model.selectedService = self.view.main.services_List.selection_get()

            if (selected_route == None or selected_service == None):
                print("error no route / service selected")
                return False

            return True
        except:
            messagebox.showerror('Error', 'Something went wrong!')

    def async_create_Fahrplan(self):
        if(self.runningAsync > 0):
            messagebox.showerror( 'Error', 'Program is already running')
            return

        #checks and sets the selected route for fahrplan
        if (self.service_route_selected()):
            loop = asyncio.new_event_loop()
            self.runningAsync = self.runningAsync + 1
            loop.run_until_complete(self.model.createFahrplan())
            loop.close()
            self.runningAsync = self.runningAsync - 1
        else:
            messagebox.showerror( 'Error', 'no route/service selected')


    def do_tasks(self, button):
        """ Function/Button starting the asyncio part. """
        if (button == "loadGTFS"):
            threading.Thread(target= self.async_loadGTFS, args=()).start()
        elif (button == "loadFahrplan"):
            print('start creating fahrplan')
            threading.Thread(target=self.async_create_Fahrplan, args=()).start()

    def run(self):
        self.root.title("GTFS to Fahrplan")
        #sets the window in focus
        self.root.deiconify()
        self.root.mainloop()

    def loadGTFSDATA(self, event):
        try:
            self.model.path = self.view.main.path.get()
        except:
            messagebox.showerror( 'Error', 'no path input')
        button = "loadGTFS"
        self.do_tasks(button)


    def start(self, event):
        button = "loadFahrplan"
        self.do_tasks(button)

    def analyze_gtfs(self):
        button = "loadFahrplan"
        self.do_tasks(button)

    def about(self):
        print ("This is a simple example of a menu")

    def closeprogram(self, event):
        self.root.destroy()

    def closeprogrammenu(self):
        self.root.destroy()

class View():
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        #self.frame.grid(sticky="NSEW")
        self.frame.pack(fill=tk.BOTH)
        self.sidePanel = SidePanel(parent)
        self.main = Main(parent)

        self.statusbar = Statusbar(parent)
        self.navbar = Navbar(parent)

def fillLog(message, error_message):
    log["log_id"].append(message)
    log["log_id"].append(error_message)

def writelog():
    print('writelog')
