# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog
from analyzeGTFS import *

class Navbar(tk.Frame):
    def __init__(self, root):
        self.navbarFrame = tk.Frame(root)
        self.navbarFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

class Toolbar(tk.Frame):
    def __init__(self, root):
        self.toolbarFrame = tk.Frame(root)
        self.menubar = tk.Menu(self.toolbarFrame)
        self.filemenu = tk.Menu(self.menubar)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.toolbarFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

class Statusbar(tk.Frame):
    def __init__(self, root):
        self.statusbarFrame = tk.Frame(root)
        self.statusbarFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

class SidePanel():
    def __init__(self, root):
        self.sidepanelFrame = tk.Frame(root)
        self.sidepanelFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.sidepanelButton = tk.Button(self.sidepanelFrame, text="SidePanel ")
        self.sidepanelButton.pack(side="top", fill=tk.BOTH)
        self.clearButton = tk.Button(self.sidepanelFrame, text="Clear")
        self.clearButton.pack(side="top", fill=tk.BOTH)

class Main():
    def __init__(self, root):
        self.mainFrame = tk.Frame(root)
        self.mainFrame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)
        self.quitButton = tk.Button(self.mainFrame, text = "Quit")
        self.quitButton.pack(side="top", fill=tk.BOTH)

class Model():
    def __init__(self):
        self.xpoint = 200
        self.ypoint = 200
        self.res = None

class Controller():
    def __init__(self):

        self.root = tk.Tk()
        #init window size
        self.root.geometry("250x150+300+300")

        self.model = Model()
        self.view = View(self.root)

        #bind side panel functions
        self.view.sidePanel.sidepanelButton.bind("<Button>", self.my_plot)
        self.view.sidePanel.clearButton.bind("<Button>", self.clear)
        #bind main menu button
        self.view.main.quitButton.bind("<Button>", self.close_program)

        #bind tool bar functions
        self.view.toolbar.filemenu.add_command(label="Start", command=self.analyzeGTFS)
        self.view.toolbar.filemenu.add_command(label="Exit", command=self.close_program_menu)
        self.root.config(menu=self.view.toolbar.menubar)

    def run(self):
        self.root.title("GTFS to Fahrplan")
        self.root.deiconify()
        self.root.mainloop()

    def clear(self, event):
        print('clear')

    def my_plot(self, event):
        print('my_plot')

    def OpenFile(self):
        name = tk.filedialog()
        print (name)

    def About(self):
        print ("This is a simple example of a menu")

    def close_program(self, event):
        self.root.destroy()

    def close_program_menu(self):
        self.root.destroy()

    def analyzeGTFS(self):
        #maybefasterGetGTFS(tripsList, stopsList, stopTimesList, calendarList, calendar_datesList)
        GTFSData = readGTFSData()
        slowGetGTFSdict(GTFSData)

class View():
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.sidePanel = SidePanel(parent)
        self.statusbar = Statusbar(parent)
        self.toolbar = Toolbar(parent)
        self.navbar = Navbar(parent)
        self.main = Main(parent)

        #self.statusbar.pack(side="bottom", fill="x")
        #self.toolbar.pack(side="top", fill="x")
        #self.navbar.pack(side="left", fill="y")
        #self.main.pack(side="right", fill="both", expand=True)