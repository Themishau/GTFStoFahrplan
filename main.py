# -*- coding: utf-8 -*-
import sys
from viewmodel import ViewModel
from viewmodel import View
from viewmodel import Model
from model.Base.GTFSEnums import ModelTriggerActionsEnum
from view.splash_screen import SplashScreen

from PyQt5.QtWidgets import *

if __name__ == '__main__':
    gtfs_app = QApplication(sys.argv)
    model = Model(gtfs_app)
    viewModel = ViewModel(model=model)
    view = View(viewModel=viewModel)
    # show a nice loading window first
    window = SplashScreen(viewModel.view)

    sys.exit(gtfs_app.exec_())
