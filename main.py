# -*- coding: utf-8 -*-
import sys
from model import Model
from viewmodel import ViewModel
from view import SplashScreen
from view import View
from PySide6.QtWidgets import *


if __name__ == '__main__':
    gtfs_app = QApplication(sys.argv)
    model = Model(gtfs_app)
    viewModel = ViewModel(app=gtfs_app, model=model)
    view = View(viewModel=viewModel)
    # show a nice loading window first
    window = SplashScreen(view)

    sys.exit(gtfs_app.exec())
