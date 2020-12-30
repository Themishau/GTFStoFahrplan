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

class SidePanel():
    def __init__(self, root):
        self.sidepanelFrame = tk.Frame(root)
        self.sidepanelFrame.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.sidepanelButton = tk.Button(self.sidepanelFrame, text="Start")
        self.sidepanelButton.pack(side="top", fill=tk.BOTH)
        self.LoadGTFSButton = tk.Button(self.sidepanelFrame, text="Load/Check GTFS")
        self.LoadGTFSButton.pack(side="top", fill=tk.BOTH)
        self.quitButton = tk.Button(self.sidepanelFrame, text="Quit")
        self.quitButton.pack(side="bottom", fill=tk.BOTH)

class Main():
    def __init__(self, root):
        self.mainFrame = tk.Frame(root)
        self.namelbl = tk.Label(self.mainFrame, text="Name")
        self.namelbl.pack(side="left")
        self.entryRoute = tk.Entry(self.mainFrame)
        self.entryRoute.pack(side="right", fill=tk.BOTH)
        self.mainFrame.pack(side=tk.TOP)

class Model():
    def __init__(self):
        self.xpoint = 200
        self.ypoint = 200
        self.res = None
        self.GTFSData = None
        self.routeNames = '100'
        self.stopsdict = None
        self.stopTimesdict = None
        self.tripdict = None
        self.calendarWeekdict = None
        self.calendarDatesdict = None
        self.routesFahrtdict = None

    async def import_GTFS(self):
        await self.readGFTS()
        await self.getGTFS()
        print("GTFS imported")

    async def readGFTS(self):
        self.GTFSData = await read_gtfs_data()

    async def getGTFS(self):
        self.stopsdict, self.stopTimesdict, self.tripdict, self.calendarWeekdict, self.calendarDatesdict, self.routesFahrtdict = await get_gtfs(self.GTFSData)
        self.GTFSData = None

    async def createFahrplan(self):
        if (self.stopsdict == None or self.stopTimesdict== None or self.tripdict == None or self.calendarWeekdict == None or self.calendarDatesdict == None or self.routesFahrtdict == None):
            messagebox.showerror( 'Fehler', 'Noch keine Daten')
            return
        routeName = ['100','1']
        tasks = [get_fahrt_ofroute_fahrplan(name, self.stopsdict, self.stopTimesdict, self.tripdict, self.calendarWeekdict, self.calendarDatesdict, self.routesFahrtdict) for name in routeName]
        completed, pending = await asyncio.wait(tasks)
        #results = [task.result() for task in completed]

        #get_fahrt_ofroute_fahrplan(routeName, stopsdict, stopTimesdict, tripdict, calendarWeekdict, calendarDatesdict, routesFahrtdict)
        #get_fahrt_ofroute_fahrplan(routeName2, stopsdict, stopTimesdict, tripdict, calendarWeekdict, calendarDatesdict, routesFahrtdict)
        #slow_get_gtf_sdict(GTFSData)


class Controller():
    def __init__(self):

        #init tk
        self.root = tk.Tk()

        #init window size
        self.root.geometry("250x250+300+300")

        self.runningAsync = 0
        #init model and viewer
        self.model = Model()
        self.view = View(self.root)

        #bind side panel buttons and functions
        self.view.sidePanel.sidepanelButton.bind("<Button>", self.start)
        self.view.sidePanel.LoadGTFSButton.bind("<Button>", self.loadGTFSDATA)
        self.view.sidePanel.quitButton.bind("<Button>", self.closeprogram)

        #bind tool bar buttons and functions
        self.view.toolbar.filemenu.add_command(label="Start", command=self.analyze_gtfs)
        self.view.toolbar.filemenu.add_command(label="Exit", command=self.closeprogrammenu)
        self.root.config(menu=self.view.toolbar.menubar)


    def async_loadGTFS(self):
        if(self.runningAsync > 0):
            messagebox.showerror( 'Error', 'Program is already running')
            return

        loop = asyncio.new_event_loop()
        self.runningAsync = self.runningAsync + 1
        loop.run_until_complete(self.model.import_GTFS())
        loop.close()

        self.runningAsync = self.runningAsync - 1

    def async_create_Fahrplan(self):
        if(self.runningAsync > 0):
            messagebox.showerror( 'Error', 'Program is already running')
            return

        loop = asyncio.new_event_loop()
        self.runningAsync = self.runningAsync + 1
        loop.run_until_complete(self.model.createFahrplan())
        loop.close()

        self.runningAsync = self.runningAsync - 1

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
        self.frame.grid(sticky="NSEW")
        self.frame.pack(fill=tk.BOTH)
        self.sidePanel = SidePanel(parent)
        self.statusbar = Statusbar(parent)
        self.toolbar = Toolbar(parent)
        self.navbar = Navbar(parent)
        self.main = Main(parent)


