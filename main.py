# -*- coding: utf-8 -*-
import sys

import networkx as nx
import matplotlib.pyplot as plt

from viewmodel import ViewModel
from view.view import View
from model.model import Model
from model.Base.GTFSEnums import ModelTriggerActionsEnum
from view.splash_screen import SplashScreen

from PyQt5.QtWidgets import *

if __name__ == '__main__':
    gtfs_app = QApplication(sys.argv)
    model = Model(gtfs_app)
    viewModel = ViewModel(app=gtfs_app, model=model)
    view = View(viewModel=viewModel)
    # show a nice loading window first
    window = SplashScreen(view)

    sys.exit(gtfs_app.exec_())
