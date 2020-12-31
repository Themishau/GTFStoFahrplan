# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from analyzeGTFS import *
import asyncio
import threading

class Navbar(tk.Frame):
    def __init__(self, root):
        self.navbarFrame = tk.Frame(root)
        self.navbarFrame.pack(side=tk.LEFT, fill=tk.BOTH)

class Toolbar(tk.Frame):
    def __init__(self, root):
        self.toolbarFrame = tk.Frame(root)
        self.menubar = tk.Menu(self.toolbarFrame)
        self.filemenu = tk.Menu(self.menubar)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.toolbarFrame.pack(side=tk.TOP, fill=tk.BOTH)

class Statusbar(tk.Frame):
    def __init__(self, root):
        self.statusbarFrame = tk.Frame(root)
        self.statusbarFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)

class SidePanel(tk.Frame):
    def __init__(self, root):
        self.sidepanelFrame = tk.Frame(root)
        self.sidepanelFrame.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.quitButton = tk.Button(self.sidepanelFrame, text="Quit")
        self.quitButton.pack(side="bottom", fill=tk.BOTH)

        self.LoadGTFSButton = tk.Button(self.sidepanelFrame, text="Load/Check GTFS")
        self.LoadGTFSButton.pack(side="bottom", fill=tk.BOTH)

        self.sidepanelButton = tk.Button(self.sidepanelFrame, text="Start")
        self.sidepanelButton.pack(side="bottom", fill=tk.BOTH)



class Main(tk.Frame):
    def __init__(self, root):
        self.mainFrame = tk.Frame(root)
        self.namelbl = tk.Label(self.mainFrame, text="Agency and Routes")
        self.namelbl.pack(side="top")
        self.mainFrame.pack(side=tk.TOP)

        #lists of agency
        self.agency_List = tk.Listbox(self.mainFrame)
        self.agency_List_scrollbar = tk.Scrollbar(self.agency_List, orient="vertical")
        self.agency_List.config(yscrollcommand=self.agency_List_scrollbar.set)
        self.agency_List_scrollbar.config(command=self.agency_List.yview)
        self.agency_List.pack(side=tk.LEFT)

        #lists of routes
        self.routes_List = tk.Listbox(self.mainFrame)
        self.routes_List_scrollbar = tk.Scrollbar(self.routes_List, orient="vertical")
        self.routes_List.config(yscrollcommand=self.routes_List_scrollbar.set)
        self.routes_List_scrollbar.config(command=self.routes_List.yview)
        self.routes_List.pack(side=tk.RIGHT)

class Model():
    def __init__(self):
        self.GTFSData = None
        self.routeNames = '100'
        self.stopsdict = None
        self.stopTimesdict = None
        self.tripdict = None
        self.calendarWeekdict = None
        self.calendarDatesdict = None
        self.routesFahrtdict = None
        self.agencyFahrtdict = None
        self.agencies = None
        self.routesList = None
        self.selectedAgency = None
        self.selectedRoute = None


    def dataLoadedAndAvailable(self):
        if (self.stopsdict == None or self.stopTimesdict== None or self.tripdict == None or self.calendarWeekdict == None or self.calendarDatesdict == None or self.routesFahrtdict == None):
            return False
        return True

    #import the data into the data framework
    async def import_GTFS(self):
        await self.readGFTS()
        await self.getGTFS()
        self.agencies = await read_gtfs_agencies(self.agencyFahrtdict)
        print("GTFS imported")

    #reads the files
    async def readGFTS(self):
        self.GTFSData = await read_gtfs_data()

    #gets the data out of the files
    async def getGTFS(self):
        self.stopsdict, self.stopTimesdict, self.tripdict, self.calendarWeekdict, self.calendarDatesdict, self.routesFahrtdict, self.agencyFahrtdict = await get_gtfs(self.GTFSData)
        self.GTFSData = None

    def getRoutesOfAgency(self, agency):
        self.routesList = select_gtfs_routes_from_agancy(agency, self.routesFahrtdict)
        print("routes of agency loaded")

    async def createFahrplan(self):
        if (self.dataLoadedAndAvailable()):
            if (self.selectedRoute != None):
                routeName = [self.selectedRoute]
                tasks = [get_fahrt_ofroute_fahrplan(name, self.stopsdict, self.stopTimesdict, self.tripdict, self.calendarWeekdict, self.calendarDatesdict, self.routesFahrtdict, self.agencyFahrtdict) for name in routeName]
                completed, pending = await asyncio.wait(tasks)
        else:
            messagebox.showerror( 'Fehler', 'Noch keine Daten')
            return
        #results = [task.result() for task in completed]

        #get_fahrt_ofroute_fahrplan(routeName, stopsdict, stopTimesdict, tripdict, calendarWeekdict, calendarDatesdict, routesFahrtdict)
        #get_fahrt_ofroute_fahrplan(routeName2, stopsdict, stopTimesdict, tripdict, calendarWeekdict, calendarDatesdict, routesFahrtdict)
        #slow_get_gtf_sdict(GTFSData)



class Controller():
    def __init__(self):

        #init tk
        self.root = tk.Tk()

        #init window size
        self.root.geometry("500x300+400+400")

        self.runningAsync = 0
        #init model and viewer
        self.model = Model()
        self.view = View(self.root)


        #bind main buttions and functions
        self.view.main.agency_List.bind('<<ListboxSelect>>', self.selection_agency)

        #bind side panel buttons and functions
        self.view.sidePanel.sidepanelButton.bind("<Button>", self.start)
        self.view.sidePanel.LoadGTFSButton.bind("<Button>", self.loadGTFSDATA)
        self.view.sidePanel.quitButton.bind("<Button>", self.closeprogram)

        #bind tool bar buttons and functions
        self.view.toolbar.filemenu.add_command(label="Start", command=self.analyze_gtfs)
        self.view.toolbar.filemenu.add_command(label="Exit", command=self.closeprogrammenu)
        self.root.config(menu=self.view.toolbar.menubar)



    def selection_agency(self, event):
        try:
            selected_agency = None
            for agency in self.model.agencies:
                if (agency[1] == self.view.main.agency_List.selection_get()):
                    print(self.view.main.agency_List.selection_get())
                    selected_agency = agency
            if (selected_agency == None):
                print("error nothing found")
                return
            self.model.getRoutesOfAgency(selected_agency)
            self.update_routes_List()
        except:
            messagebox.showerror('Error', 'Nothing Selected!')

    def update_routes_List(self):
        if (self.view.main.routes_List != None):
            self.view.main.routes_List.delete(0,'end')
        for routes in self.model.routesList:
            self.view.main.routes_List.insert("end", routes[0])
            #self.view.main.agency_List.grid(row=0, column=0, columnspan=1)
        print("routes list updated")

    def update_agency_List(self):
        for agency in self.model.agencies:
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

    def select_route(self):
        try:
            selected_route = None
            selected_route = self.view.main.routes_List.selection_get()
            if (selected_route == None):
                print("error no route selected")
                return False
            self.model.selectedRoute = selected_route
            return True
        except:
            messagebox.showerror('Error', 'Something went wrong!')

    def async_create_Fahrplan(self):
        if(self.runningAsync > 0):
            messagebox.showerror( 'Error', 'Program is already running')
            return

        #checks and sets the selected route for fahrplan
        if (self.select_route()):
            loop = asyncio.new_event_loop()
            self.runningAsync = self.runningAsync + 1
            loop.run_until_complete(self.model.createFahrplan())
            loop.close()
            self.runningAsync = self.runningAsync - 1
        else:
            messagebox.showerror( 'Error', 'no route selected')


    def do_tasks(self, button):
        """ Function/Button starting the asyncio part. """
        if (button == "loadGTFS"):
            threading.Thread(target= self.async_loadGTFS, args=()).start()
        elif (button == "loadFahrplan"):
            threading.Thread(target=self.async_create_Fahrplan, args=()).start()

    def run(self):
        self.root.title("GTFS to Fahrplan")
        #sets the window in focus
        self.root.deiconify()
        self.root.mainloop()

    def loadGTFSDATA(self, event):
        button = "loadGTFS"
        self.do_tasks(button)


    def start(self, event):
        button = "loadFahrplan"
        self.do_tasks(button)

    def analyze_gtfs(self):
        button = "loadFahrplan"
        self.do_tasks(button)

    def open_file(self):
        name = tk.filedialog()
        print (name)

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
        self.main = Main(parent)
        self.sidePanel = SidePanel(parent)
        self.statusbar = Statusbar(parent)
        self.toolbar = Toolbar(parent)
        self.navbar = Navbar(parent)



